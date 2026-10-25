"""PLP state estimator ``psi``: a learned guess plus model-based refinement.

The physics-based forecaster (PLP) needs the current state of the system, but
it only sees a noisy delay vector (a few past observations stacked together).
``psi`` maps a noisy delay vector ``X_t`` to an estimate of the latent
(hidden) state in two stages:

1. An MLP (a small neural network from ``networks.py``, trained on a separate
   trajectory with fresh noise per minibatch) predicts the whitened state at
   the *start* of the delay window, ``u0 ~ s_bar_{t-(D-1) tau}``.
2. Levenberg-Marquardt (LM) iterations, a damped form of Gauss-Newton least
   squares, minimize ``||X_t - G'(u)||^2``. Here ``G'(u)`` is the noise-free
   delay vector made by integrating the known model forward from ``u``
   (forward parametrization: no backward integration). The refined
   window-start state is integrated over the window to give ``s_hat_t``.

Stage 2 is the maximum-likelihood estimate under Gaussian observation noise,
which attains the Cramer-Rao floor ``rho^2 nu^2`` (the smallest error any
unbiased estimator can reach) to first order in the noise level ``rho``
(validation V2); stage 1 only provides the basin of attraction. The
deployable observability proxy is ``nu`` evaluated at the refined estimate.

Stage 2 runs from the network start alone, except on a system whose
``SystemSpec.estimator_starts`` names more starts (WU-0039, fixes F1 and F2
of the V7 diagnosis note 2026-10-25). The refinement then runs from each
start and keeps the estimate with the strictly lowest final cost; ties go to
the network start. The choice is made in Python before tracing, so the
single-start systems compile the unchanged function.

``dynamics.py`` supplies the delay map and ``nu``; ``ensemble.py`` calls
``StateEstimator`` to build PLP forecasts; ``lm_summary`` condenses the LM
diagnostics for the reports.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import NamedTuple

import jax
import jax.numpy as jnp
import numpy as np
from scipy import stats
from scipy.spatial import cKDTree

from .data import SystemContext
from .dynamics import delay_map_forward, make_observability
from .networks import TrainedNetwork
from .systems import SINGLE_START, check_starts

LATE_WINDOW: int = 3
"""Last LM iterations that ``late_progress`` looks at (D1, DEC-0025)."""

LATE_DECREASE: float = 1e-6
"""Relative cost decrease that makes a late accepted step *material*."""

GOF_QUANTILE: float = 0.999
"""Level of the chi-square quantile ``gof_threshold`` (D3, DEC-0025)."""

CONTINUATION_STEPS: int = 5
"""LM iterations of each stage of the ``continuation`` start (F2, WU-0039).

The value is the one the V7 diagnosis tested (note 2026-10-25, section 3)."""

START_DECREASE: float = 1e-6
"""Relative cost decrease that makes a switch of start *material* (WU-0039).

A non-network start is selected whenever its final cost is strictly lower,
which happens often by round-off between two fits of the same minimum. Only
a decrease above this fraction of the network cost counts as a change of
basin (``lm_start_switched_material``; note 2026-10-25, section 6 item 4)."""


def gof_threshold(dof: int) -> float:
    """Return the 0.999 quantile of chi-square with ``dof`` degrees of freedom.

    To first order in ``rho`` a converged estimate in the right basin has
    ``c / rho^2 ~ chi2(D - m)``, with ``D`` delay coordinates and ``m`` fitted
    state components (4 at ``D = 7``, ``m = 3``; applied-mathematician M1,
    WU-0005.4). The robustness variants ``D = 5`` and ``D = 10`` have 2 and 7
    degrees of freedom, so the threshold depends on the cell. The value for 4
    is 18.4668 (18.47 to four digits). The fraction of estimates above it is
    printed as a goodness-of-fit diagnostic; it has no gate or verdict role
    (D3).

    Parameters
    ----------
    dof : int
        Degrees of freedom ``D - m``, at least 1.

    Returns
    -------
    float
        The quantile.

    Raises
    ------
    ValueError
        If ``dof`` is not a positive integer.
    """
    if int(dof) != dof or dof < 1:
        raise ValueError(
            f"degrees of freedom must be a positive integer, got {dof}"
        )
    return float(stats.chi2.ppf(GOF_QUANTILE, int(dof)))


GOF_EXCEED: float = gof_threshold(4)
"""The threshold for ``D = 7`` (``dof = 4``), 18.4668."""


@dataclass(frozen=True)
class LMDiagnostics:
    """Per-estimate diagnostics of the LM refinement (NVVUQ.10, WU-0005.4).

    The stopping criterion is a fixed ``refine_steps`` with no tolerance stop,
    and these arrays are the achieved residual and the iteration count that
    NVVUQ.10 asks for (DEC-0017 Q3; DEC-0025 for the corrections). They are
    report-only: no decision reads them. Needs owner review before freeze
    (LPC.PC.11).

    Attributes
    ----------
    residual : np.ndarray
        Final carried cost ``c = ||X_t - G'(u_hat)||^2``, float64 ``(n,)``, in
        normalized observation units (``sigma_x = 1``). ``inf`` where a cost
        evaluation was not finite and no step was accepted. With
        ``refine_steps = 0`` it is the cost at the network's start.
    accepted : np.ndarray
        Integer ``(n,)``: iterations whose candidate cost was strictly lower
        than the carried one. It includes round-off accepts after convergence
        (null steps), so it is an upper bound on the number of productive
        steps, not the number of iterations to convergence.
    nonfinite_cost : np.ndarray
        Bool ``(n,)``: at least one of the ``1 + refine_steps`` cost
        evaluations (the start and every candidate) was not finite (``cost``
        maps it to ``inf``; S3 of DEF-0001).
    nonfinite_jacobian : np.ndarray
        Bool ``(n,)``: at least one Jacobian entry was set to 0 in some
        iteration (S4).
    late_progress : np.ndarray
        Integer ``(n,)``, 0 or 1 (D1, DEC-0025): an accepted step in the last
        ``LATE_WINDOW`` iterations lowered the cost by more than
        ``LATE_DECREASE`` relative, or left an infinite cost (a non-finite
        start) for a finite one. A cheap screen for an estimate that was still
        moving at the iteration budget. Report-only. Without noise the cost
        sits at the round-off floor, where null-step accepts lower it by large
        relative amounts, so the flag means nothing there.
    start_selected : np.ndarray or None
        Integer ``(n,)``: the index into ``StateEstimator.starts`` of the
        selected start (0 is the network). ``None`` for a single start.
    start_material : np.ndarray or None
        Bool ``(n,)``: a non-network start was selected and its final cost is
        lower than the network run's by more than ``START_DECREASE``
        relative (or the network run's cost is infinite). ``None`` for a
        single start.

    Notes
    -----
    With several starts (WU-0039), ``residual``, ``accepted`` and
    ``late_progress`` are those of the selected run (for the continuation
    start, of its final full-window refinement). ``nonfinite_cost`` and
    ``nonfinite_jacobian`` are the union over every run and stage made for
    the estimate, so a handling event in a run that was not selected is
    still counted.
    """

    residual: np.ndarray
    accepted: np.ndarray
    nonfinite_cost: np.ndarray
    nonfinite_jacobian: np.ndarray
    late_progress: np.ndarray
    start_selected: np.ndarray | None = None
    start_material: np.ndarray | None = None


class Refinement(NamedTuple):
    """The compiled-loop pieces of one estimator (see ``refinement``)."""

    refine: Callable
    trace: Callable
    cost: Callable
    generate: Callable


@dataclass
class StateEstimator:
    """Two-stage estimator ``psi``.

    Attributes
    ----------
    ctx : SystemContext
        System context (embedding, normalization, whitening).
    network : TrainedNetwork
        MLP predicting the whitened window-start state.
    model_step : Callable
        Flow map of the model used for refinement and for ``nu``.
    refine_steps : int
        Levenberg-Marquardt iterations (0 disables refinement).
    starts : tuple[str, ...]
        Starts of the refinement (``systems.ESTIMATOR_STARTS``; WU-0039). The
        default ``("network",)`` builds the single-start function of the
        frozen pipeline, unchanged. With more starts the refinement runs
        ``refine_steps`` iterations from each and keeps the strictly lowest
        final cost (ties go to the earlier start, so to the network): see
        :meth:`pair_index` and :meth:`continuation`. Several starts need
        ``refine_steps >= 1``.
    start_counts : dict[str, int]
        Running tally of the start selections over every call of
        :meth:`estimate_counted` (several starts only; see
        :meth:`start_record`). Not an init argument, so
        ``dataclasses.replace`` starts a fresh tally.

    Notes
    -----
    Handling (DEF-0001, WU-0002.11, WU-0005.4). Inside the refinement, the
    ``1e-12`` added to the damping scale and the accept-or-reject step are
    part of the algorithm, not data handling. A non-finite candidate cost
    (mapped to ``inf``, so the step is rejected, S3) and a non-finite Jacobian
    entry (set to 0, S4) are algorithm-internal too, and are counted per
    estimate in the scan carry (``LMDiagnostics.nonfinite_cost`` and
    ``nonfinite_jacobian``). After the compiled function, a non-finite ``nu``
    and a non-finite state coordinate are replaced and counted by
    :meth:`estimate_counted`.

    Diagnostics (NVVUQ.10, DEC-0017 Q3, WU-0005.4). The stopping criterion is
    a fixed ``refine_steps`` iterations with no tolerance stop. Each estimate
    also reports the achieved residual, the number of accepted iterations
    (round-off accepts after convergence included) and ``late_progress``. None
    of them changes a value or a decision: the arithmetic of the loop is
    unchanged (the carry gains integer and boolean fields only).
    """

    ctx: SystemContext
    network: TrainedNetwork
    model_step: Callable
    refine_steps: int = 6
    starts: tuple[str, ...] = SINGLE_START
    _fn: Callable | None = field(default=None, repr=False)
    start_counts: dict[str, int] = field(
        default_factory=dict, init=False, repr=False
    )
    _tree: cKDTree | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Check ``starts`` (``systems.check_starts``) and the iterations.

        Raises
        ------
        ValueError
            If ``starts`` is invalid, or names several starts with
            ``refine_steps < 1`` (a selection by final cost needs a fit).
        """
        check_starts(self.starts)
        if self.starts != SINGLE_START and self.refine_steps < 1:
            raise ValueError(
                f"several starts {self.starts} need refine_steps >= 1, got "
                f"{self.refine_steps}"
            )

    @property
    def width(self) -> int:
        """Hidden width of the MLP."""
        return self.network.width

    def refinement(self) -> Refinement:
        """Build the LM loop of this estimator (one estimate, not vmapped).

        The production loop and the test trace share one step closure, so
        they run the same arithmetic. ``refine(u0, target)`` returns
        ``(u_final, diag)`` with ``diag`` the tuple ``(residual, accepted,
        nonfinite_cost, nonfinite_jacobian, late_progress)``.
        ``trace(u0, target)`` returns ``(u_final, diag, (u_k, c_k,
        accept_k))`` with the iterate, the carried cost and the accept flag of
        every iteration (for tests only: the pipeline never calls it).

        Returns
        -------
        Refinement
            ``refine``, ``trace``, ``cost`` and ``generate``.
        """
        ctx = self.ctx
        root = jnp.asarray(ctx.unwhiten)
        mean = jnp.asarray(ctx.state_mean)
        fwd = delay_map_forward(
            self.model_step,
            ctx.spec.observed_index,
            ctx.obs_mean,
            ctx.obs_scale,
            ctx.delay,
            ctx.embed_dim,
        )
        n_iter = self.refine_steps
        first_late = max(0, n_iter - LATE_WINDOW)

        def generate(u: jnp.ndarray) -> jnp.ndarray:
            return fwd(mean + root @ u)

        jac = jax.jacfwd(generate)

        def cost(u: jnp.ndarray, target: jnp.ndarray) -> jnp.ndarray:
            resid = target - generate(u)
            value = jnp.sum(resid**2)
            return jnp.where(jnp.isfinite(value), value, jnp.inf)

        def lm_step(carry, target):
            # The float expressions are those of the original loop, in the
            # same order. The carry gains integer and boolean fields only
            # (WU-0005.4, L4 and V1 check this).
            u, c_u, damping, n_acc, bad_cost, bad_jac, late, k = carry
            dim = u.shape[0]
            a_mat = jac(u)
            finite = jnp.isfinite(a_mat)
            a_mat = jnp.where(finite, a_mat, 0.0)
            normal = a_mat.T @ a_mat
            rhs = a_mat.T @ (target - generate(u))
            scale = jnp.trace(normal) / dim + 1e-12
            delta = jnp.linalg.solve(
                normal + damping * scale * jnp.eye(dim), rhs
            )
            cand = u + delta
            c_cand = cost(cand, target)
            accept = c_cand < c_u
            u_new = jnp.where(accept, cand, u)
            c_new = jnp.where(accept, c_cand, c_u)
            damping_new = jnp.where(accept, damping / 3.0, damping * 4.0)
            # An accept from an infinite carried cost (non-finite start) is a
            # finite candidate, so it is material by definition
            # (inf - c > 1e-6 inf is False in floating point).
            material = (
                accept
                & ((c_u - c_cand > LATE_DECREASE * c_u) | jnp.isinf(c_u))
                & (k >= first_late)
            )
            new = (
                u_new,
                c_new,
                damping_new,
                n_acc + accept.astype(jnp.int32),
                bad_cost | jnp.isinf(c_cand),
                bad_jac | ~jnp.all(finite),
                jnp.where(material, jnp.int32(1), late),
                k + 1,
            )
            return new, (u_new, c_new, accept)

        def start(u0: jnp.ndarray, target: jnp.ndarray):
            c0 = cost(u0, target)
            return (
                u0,
                c0,
                1e-3,
                jnp.int32(0),
                jnp.isinf(c0),
                jnp.bool_(False),
                jnp.int32(0),
                jnp.int32(0),
            )

        def diagnostics(carry):
            _, c_final, _, n_acc, bad_cost, bad_jac, late, _ = carry
            return c_final, n_acc, bad_cost, bad_jac, late

        def refine(u0: jnp.ndarray, target: jnp.ndarray):
            def body(carry, _):
                return lm_step(carry, target)[0], None

            carry, _ = jax.lax.scan(
                body, start(u0, target), None, length=n_iter
            )
            return carry[0], diagnostics(carry)

        def trace(u0: jnp.ndarray, target: jnp.ndarray):
            def body(carry, _):
                return lm_step(carry, target)

            carry, ys = jax.lax.scan(
                body, start(u0, target), None, length=n_iter
            )
            return carry[0], diagnostics(carry), ys

        return Refinement(
            refine=refine, trace=trace, cost=cost, generate=generate
        )

    def continuation(self) -> Callable:
        """Build the window-continuation start of F2 (one estimate).

        From a start ``u0`` it runs LM on the ``j`` oldest delay coordinates
        only, for ``j = m + 1, ..., D - 1`` in turn (``m`` state components),
        ``CONTINUATION_STEPS`` iterations per stage with the damping restarted
        at ``1e-3``. The newer coordinates are masked out of the residual and
        the Jacobian. The step arithmetic is that of :meth:`refinement` with
        the 0/1 mask applied, as in the V7 diagnosis (note 2026-10-25,
        section 3, ``cont``). With ``D <= m + 1`` there is no stage and the
        start is ``u0`` itself.

        Returns
        -------
        Callable
            ``settle(u0, target) -> (u, nonfinite_cost, nonfinite_jacobian)``.
            The flags say that some masked cost was not finite (mapped to
            ``inf``, the step rejected) or that some Jacobian entry, masked
            or not, was not finite (set to 0), in any stage.
        """
        ctx = self.ctx
        root = jnp.asarray(ctx.unwhiten)
        mean = jnp.asarray(ctx.state_mean)
        fwd = delay_map_forward(
            self.model_step,
            ctx.spec.observed_index,
            ctx.obs_mean,
            ctx.obs_scale,
            ctx.delay,
            ctx.embed_dim,
        )
        big_d = ctx.embed_dim
        dim = int(root.shape[1])
        # X_t[k] observes the window start advanced by (D - 1 - k) tau, so the
        # oldest coordinate is the last one (delay_map_forward).
        masks = [
            jnp.asarray(np.r_[np.zeros(big_d - j), np.ones(j)])
            for j in range(dim + 1, big_d)
        ]

        def generate(u: jnp.ndarray) -> jnp.ndarray:
            return fwd(mean + root @ u)

        jac = jax.jacfwd(generate)

        def cost(u, target, mask):
            resid = (target - generate(u)) * mask
            value = jnp.sum(resid**2)
            return jnp.where(jnp.isfinite(value), value, jnp.inf)

        def stage(u0, target, mask):
            def body(carry, _):
                u, c_u, damping, bad_cost, bad_jac = carry
                a_mat = jac(u)
                finite = jnp.isfinite(a_mat)
                a_mat = jnp.where(finite, a_mat, 0.0) * mask[:, None]
                normal = a_mat.T @ a_mat
                rhs = a_mat.T @ ((target - generate(u)) * mask)
                scale = jnp.trace(normal) / dim + 1e-12
                delta = jnp.linalg.solve(
                    normal + damping * scale * jnp.eye(dim), rhs
                )
                cand = u + delta
                c_cand = cost(cand, target, mask)
                accept = c_cand < c_u
                return (
                    jnp.where(accept, cand, u),
                    jnp.where(accept, c_cand, c_u),
                    jnp.where(accept, damping / 3.0, damping * 4.0),
                    bad_cost | jnp.isinf(c_cand),
                    bad_jac | ~jnp.all(finite),
                ), None

            c0 = cost(u0, target, mask)
            carry, _ = jax.lax.scan(
                body,
                (u0, c0, 1e-3, jnp.isinf(c0), jnp.bool_(False)),
                None,
                length=CONTINUATION_STEPS,
            )
            return carry[0], carry[3], carry[4]

        def settle(u0: jnp.ndarray, target: jnp.ndarray):
            u, bad_cost, bad_jac = u0, jnp.bool_(False), jnp.bool_(False)
            for mask in masks:
                u, stage_cost, stage_jac = stage(u, target, mask)
                bad_cost = bad_cost | stage_cost
                bad_jac = bad_jac | stage_jac
            return u, bad_cost, bad_jac

        return settle

    def pair_index(self, inputs: np.ndarray) -> np.ndarray:
        """Return the nearest estimator training pair of each input (F1).

        The search is over ``ctx.estimator_inputs``, the noise-free
        normalized delay vectors the network was trained on, by Euclidean
        distance (``scipy.spatial.cKDTree``, built once per estimator). It is
        exact, deterministic and host-side, and it draws no random number.
        The ``pair`` start of row ``i`` is ``ctx.estimator_targets[index[i]]``,
        a whitened window-start state on the attractor. It uses PLP's own
        training data only, never the analog library.

        Parameters
        ----------
        inputs : np.ndarray
            Noisy normalized delay vectors ``(n, D)``, finite.

        Returns
        -------
        np.ndarray
            Integer row indices ``(n,)``.

        Raises
        ------
        ValueError
            If ``inputs`` is not ``(n, D)`` or has a non-finite entry.
        """
        inputs = np.asarray(inputs, dtype=np.float64)
        if inputs.ndim != 2 or inputs.shape[1] != self.ctx.embed_dim:
            raise ValueError(
                f"inputs must be (n, {self.ctx.embed_dim}), got {inputs.shape}"
            )
        if not np.isfinite(inputs).all():
            raise ValueError("an input of the pair search is not finite")
        if self._tree is None:
            self._tree = cKDTree(
                np.asarray(self.ctx.estimator_inputs, dtype=np.float64)
            )
        _, index = self._tree.query(inputs, k=1)
        return np.asarray(index, dtype=np.int64)

    def start_record(self) -> dict:
        """Return the tally of the start selections (several starts only).

        Returns
        -------
        dict
            ``starts`` (the names), ``estimates`` (estimates made),
            ``selected`` (per start name, the estimates that kept it),
            ``lm_start_switched`` (estimates that kept a non-network start)
            and ``lm_start_switched_material`` (those whose cost was lower by
            more than ``START_DECREASE`` relative; see ``LMDiagnostics``).
            Every count is 0 before the first call.
        """
        counts = self.start_counts
        selected = {
            name: int(counts.get(f"selected/{name}", 0)) for name in self.starts
        }
        return {
            "starts": list(self.starts),
            "estimates": int(counts.get("estimates", 0)),
            "selected": selected,
            "lm_start_switched": int(counts.get("lm_start_switched", 0)),
            "lm_start_switched_material": int(
                counts.get("lm_start_switched_material", 0)
            ),
        }

    def _tally(self, lm: LMDiagnostics) -> None:
        """Add the start selections of one call to ``start_counts``."""
        picked = np.asarray(lm.start_selected).ravel()
        material = np.asarray(lm.start_material).ravel()
        counts = self.start_counts
        counts["estimates"] = counts.get("estimates", 0) + int(picked.size)
        for i, name in enumerate(self.starts):
            key = f"selected/{name}"
            counts[key] = counts.get(key, 0) + int(np.sum(picked == i))
        counts["lm_start_switched"] = counts.get(
            "lm_start_switched", 0
        ) + int(np.sum(picked != 0))
        counts["lm_start_switched_material"] = counts.get(
            "lm_start_switched_material", 0
        ) + int(np.sum(material))

    def _build_multi(self) -> Callable:
        """Compile the batched estimator with several starts (WU-0039).

        Every start is refined with the unchanged loop of :meth:`refinement`
        (``refine_steps`` iterations): ``network`` from the network's
        estimate, ``pair`` from the nearest training pair (:meth:`pair_index`)
        and ``continuation`` from the network's estimate after
        :meth:`continuation`. The estimate with the strictly lowest final
        cost is kept (``jnp.argmin``: ties go to the first start, the
        network); see ``LMDiagnostics`` for the diagnostics.
        """
        ctx = self.ctx
        root = jnp.asarray(ctx.unwhiten)
        mean = jnp.asarray(ctx.state_mean)
        span = ctx.history
        step = self.model_step
        nu_fn = make_observability(
            step,
            ctx.spec.observed_index,
            ctx.obs_scale,
            ctx.whiten,
            ctx.delay,
            ctx.embed_dim,
        )
        names = self.starts
        parts = self.refinement()
        settle = self.continuation() if "continuation" in names else None

        def advance(s_old: jnp.ndarray) -> jnp.ndarray:
            return jax.lax.fori_loop(0, span, lambda _, s: step(s), s_old)

        def single(x: jnp.ndarray, u_net: jnp.ndarray, u_pair: jnp.ndarray):
            finals, diags = [], []
            for name in names:
                if name == "network":
                    u, diag = parts.refine(u_net, x)
                elif name == "pair":
                    u, diag = parts.refine(u_pair, x)
                else:
                    u_cont, stage_cost, stage_jac = settle(u_net, x)
                    u, diag = parts.refine(u_cont, x)
                    diag = (
                        diag[0],
                        diag[1],
                        diag[2] | stage_cost,
                        diag[3] | stage_jac,
                        diag[4],
                    )
                finals.append(u)
                diags.append(diag)
            costs = jnp.stack([d[0] for d in diags])
            pick = jnp.argmin(costs)
            residual = costs[pick]
            c_net = costs[0]
            material = (pick > 0) & (
                (c_net - residual > START_DECREASE * c_net) | jnp.isinf(c_net)
            )
            diag = (
                residual,
                jnp.stack([d[1] for d in diags])[pick],
                jnp.any(jnp.stack([d[2] for d in diags])),
                jnp.any(jnp.stack([d[3] for d in diags])),
                jnp.stack([d[4] for d in diags])[pick],
            )
            s_old = mean + root @ jnp.stack(finals)[pick]
            return advance(s_old), s_old, diag, pick, material

        batched = jax.jit(jax.vmap(single))

        def run(
            inputs: np.ndarray,
        ) -> tuple[np.ndarray, np.ndarray, LMDiagnostics]:
            x = jnp.asarray(inputs)
            u_net = jnp.asarray(self.network.predict(x))
            u_pair = (
                jnp.asarray(ctx.estimator_targets[self.pair_index(inputs)])
                if "pair" in names
                else u_net
            )
            s_t, s_old, diag, pick, material = batched(x, u_net, u_pair)
            nu = nu_fn(s_old)
            residual, accepted, bad_cost, bad_jac, late = (
                np.asarray(d) for d in diag
            )
            return (
                np.asarray(s_t),
                np.asarray(nu),
                LMDiagnostics(
                    residual=residual,
                    accepted=accepted,
                    nonfinite_cost=bad_cost,
                    nonfinite_jacobian=bad_jac,
                    late_progress=late,
                    start_selected=np.asarray(pick),
                    start_material=np.asarray(material),
                ),
            )

        return run

    def _build(self) -> Callable:
        """Compile the batched estimator: inputs to states, ``nu``, LM info."""
        if self.starts != SINGLE_START:
            return self._build_multi()
        ctx = self.ctx
        root = jnp.asarray(ctx.unwhiten)
        mean = jnp.asarray(ctx.state_mean)
        span = ctx.history
        step = self.model_step
        nu_fn = make_observability(
            step,
            ctx.spec.observed_index,
            ctx.obs_scale,
            ctx.whiten,
            ctx.delay,
            ctx.embed_dim,
        )
        n_iter = self.refine_steps
        parts = self.refinement()

        def advance(s_old: jnp.ndarray) -> jnp.ndarray:
            return jax.lax.fori_loop(0, span, lambda _, s: step(s), s_old)

        def single(x: jnp.ndarray, u0: jnp.ndarray):
            if n_iter > 0:
                u, diag = parts.refine(u0, x)
            else:
                # Refinement disabled: the residual is the cost at the
                # start (defined, not used).
                c0 = parts.cost(u0, x)
                u, diag = u0, (
                    c0,
                    jnp.int32(0),
                    jnp.isinf(c0),
                    jnp.bool_(False),
                    jnp.int32(0),
                )
            s_old = mean + root @ u
            return advance(s_old), s_old, diag

        batched = jax.jit(jax.vmap(single))

        def run(
            inputs: np.ndarray,
        ) -> tuple[np.ndarray, np.ndarray, LMDiagnostics]:
            u0 = jnp.asarray(self.network.predict(jnp.asarray(inputs)))
            s_t, s_old, diag = batched(jnp.asarray(inputs), u0)
            nu = nu_fn(s_old)
            residual, accepted, bad_cost, bad_jac, late = (
                np.asarray(d) for d in diag
            )
            return (
                np.asarray(s_t),
                np.asarray(nu),
                LMDiagnostics(
                    residual=residual,
                    accepted=accepted,
                    nonfinite_cost=bad_cost,
                    nonfinite_jacobian=bad_jac,
                    late_progress=late,
                ),
            )

        return run

    def estimate_counted(
        self, inputs: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, LMDiagnostics]:
        """Estimate states and ``nu``, applying and flagging replacements.

        A non-finite ``nu`` becomes ``1e6`` and a non-finite coordinate
        becomes the invariant mean of that coordinate (a replacement, not a
        wrong-basin estimate: no finite state came back). The flags are taken
        on the host after the compiled function, so the values do not depend
        on them (DEF-0001).

        Parameters
        ----------
        inputs : np.ndarray
            Noisy normalized delay vectors ``(n, D)``.

        Returns
        -------
        states : np.ndarray
            Physical state estimates ``s_hat_t`` ``(n, m)`` after replacement.
        nu : np.ndarray
            ``nu(s_hat)`` ``(n,)`` after replacement.
        state_replaced : np.ndarray
            Boolean ``(n,)``: the estimate had at least one non-finite
            coordinate replaced (``invariant_mean_replacements`` counts these
            estimates, not coordinates).
        nu_replaced : np.ndarray
            Boolean ``(n,)``: ``nu`` was not finite and was replaced
            (``nu_replacements``).
        lm : LMDiagnostics
            Residual, accepted iterations, S3/S4 flags and ``late_progress``
            of the Levenberg-Marquardt refinement, per estimate (NVVUQ.10).
            With several starts it also carries the selected start, and the
            call adds the selections to ``start_counts``.
        """
        if self._fn is None:
            self._fn = self._build()
        states, nu, lm = self._fn(inputs)
        if lm.start_selected is not None:
            self._tally(lm)
        finite_nu = np.isfinite(nu)
        finite_state = np.isfinite(states)
        nu = np.where(finite_nu, nu, 1e6)
        states = np.where(finite_state, states, self.ctx.state_mean)
        return states, nu, ~finite_state.all(axis=1), ~finite_nu, lm

    def estimate(self, inputs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Estimate physical states and the observability factor.

        This calls :meth:`estimate_counted` and drops the flags.

        Parameters
        ----------
        inputs : np.ndarray
            Noisy normalized delay vectors ``(n, D)``.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Physical state estimates ``s_hat_t`` ``(n, m)`` and
            ``nu(s_hat)`` ``(n,)`` (non-finite values are replaced by a large
            number).
        """
        states, nu, *_ = self.estimate_counted(inputs)
        return states, nu


def lm_summary(
    residual: np.ndarray,
    accepted: np.ndarray,
    late_progress: np.ndarray,
    noise: float,
    dof: int,
) -> dict:
    """Summarize the LM diagnostics of a set of estimates (NVVUQ.10).

    Parameters
    ----------
    residual : np.ndarray
        Final cost ``c`` per estimate (normalized observation units); ``inf``
        allowed, NaN not.
    accepted : np.ndarray
        Accepted iterations per estimate, same size as ``residual``.
    late_progress : np.ndarray
        ``LMDiagnostics.late_progress`` (0 or 1), same size.
    noise : float
        Noise level ``rho`` (fraction of ``sigma_x``), positive: it scales the
        goodness-of-fit reading ``c / rho^2``.
    dof : int
        Degrees of freedom ``D - m`` of the first-order chi-square reference
        of ``c / rho^2`` (``D`` delay coordinates, ``m`` state components; 4
        for the main systems). It sets the threshold of
        ``fraction_above_chi2`` and is stored as ``gof_dof``.

    Returns
    -------
    dict
        * ``n_estimates``, ``noise``, ``gof_dof``;
        * ``median_residual`` (``np.median``) and ``p95_residual``
          (``np.quantile`` with ``method="inverted_cdf"``, the order statistic
          ``x_(ceil(0.95 n))``, which is finite whenever that order statistic
          is; the linear method returns NaN for a finite quantile next to an
          ``inf``). A value that is ``inf`` is reported as ``None``;
        * ``median_iterations``: the median of ``accepted``. It counts
          accepted steps, including the round-off accepts after the cost has
          converged (null steps whose candidate cost is an ulp lower), so it
          is an upper bound on the number of productive steps and not the
          number of iterations to convergence;
        * ``fraction_no_decrease``: the mean of ``accepted == 0``. With a
          fixed budget it is a failure indicator (non-finite cost, corrupted
          gradient, or a start already stationary), not a convergence
          indicator;
        * ``nonfinite_residuals``: the count of ``inf`` residuals;
        * ``fraction_late_progress`` (D1): the mean of ``late_progress``;
        * ``fraction_above_chi2`` (D3): the fraction with ``c / rho^2`` above
          the 0.999 quantile of chi-square with ``dof`` degrees of freedom
          (18.47 for 4; ``gof_threshold``). It is a diagnostic: it has no gate
          or verdict role. To first order a converged estimate in the right
          basin has ``c / rho^2 ~ chi2(dof)`` (for 4: median 3.36, p95 9.49),
          so the fraction is about 0.001 plus the unconverged and wrong-basin
          estimates.

        With no estimates, ``n_estimates`` is 0, ``nonfinite_residuals`` is 0
        and every other value is ``None``.

    Raises
    ------
    ValueError
        If the sizes differ, ``noise`` is not positive, ``dof`` is not a
        positive integer, or a residual is NaN (the loop maps every
        non-finite cost to ``inf``, so a NaN is a bug and is not summarized).

    Notes
    -----
    Needs owner review before freeze (LPC.PC.11): the keys are the schema of
    the NVVUQ.10 evidence. Across hosts these values are not bitwise
    (DEF-0023, DEF-0024); see WU-0005.4.
    """
    residual = np.asarray(residual, dtype=np.float64).ravel()
    accepted = np.asarray(accepted).ravel()
    late = np.asarray(late_progress).ravel()
    if not (residual.size == accepted.size == late.size):
        raise ValueError(
            f"sizes differ: {residual.size}, {accepted.size}, {late.size}"
        )
    if not noise > 0.0:
        raise ValueError(f"noise must be positive, got {noise}")
    if np.isnan(residual).any():
        raise ValueError(
            "a residual is NaN; the refinement maps non-finite costs to inf"
        )

    def finite_or_none(value: float) -> float | None:
        return float(value) if np.isfinite(value) else None

    threshold = gof_threshold(dof)
    out: dict = {
        "n_estimates": int(residual.size),
        "noise": float(noise),
        "gof_dof": int(dof),
        "median_residual": None,
        "p95_residual": None,
        "median_iterations": None,
        "fraction_no_decrease": None,
        "nonfinite_residuals": int(np.isinf(residual).sum()),
        "fraction_late_progress": None,
        "fraction_above_chi2": None,
    }
    if residual.size:
        out["median_residual"] = finite_or_none(np.median(residual))
        out["p95_residual"] = finite_or_none(
            np.quantile(residual, 0.95, method="inverted_cdf")
        )
        out["median_iterations"] = float(np.median(accepted))
        out["fraction_no_decrease"] = float(np.mean(accepted == 0))
        out["fraction_late_progress"] = float(np.mean(late))
        out["fraction_above_chi2"] = float(
            np.mean(residual > threshold * noise**2)
        )
    return out
