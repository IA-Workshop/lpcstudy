"""Opt-in dump of per-state arrays, ``states/<system>.npz`` (WU-0003.7b).

**Needs owner review before freeze.**

A normal run keeps only summary numbers in ``results.json``. The rehearsal
diagnostics (D1 to D6 of the WU-0003 plan, ``tools/rehearsal_diagnostics.py``)
need the numbers behind them, state by state, plus the per-estimate
Levenberg-Marquardt data (the iterative search that estimates each starting
state) of the reproducibility tiers. This module collects those arrays and
writes them to one file per core system. It is used only with the command-line
flag ``--states-dump``. The flag is refused together with the confirmatory
flag, before the seed is chosen, until the owner decides whether a
confirmatory run may carry it (O6).

``pipeline.Study.run_cell``, ``experiments`` and ``analysis`` hand arrays to
``StateDump``; ``__main__`` writes the file; ``tools/rehearsal_diagnostics.py``
reads it.

Bitwise neutrality
    The dump is a read-only collector. Every array is a copy of something the
    run computed anyway, or a pure function of such arrays; nothing flows back
    into the study. The only extra computation is the second moments of the
    two halves of the oracle draws (the same draws, summed in the same chunks,
    ``ensemble_moments(half_out=...)``) and the V4 forecasts at 2 and 4
    Lyapunov times (``experiments.convergence_check``, fed by the same noise
    and the same bootstrap index sets, so no random number is drawn). With the
    flag off, ``Study.dump`` is ``None`` and no line of this module runs. With
    it on, ``results.json`` is bitwise the same except one provenance leaf,
    ``provenance.states_dump``.

Schema version
    ``/2`` adds the ``h1c/`` and ``h1a/`` groups (WU-0003.7c); every key of
    ``/1`` keeps its name and meaning.

File format
    A NumPy ``.npz`` archive (uncompressed, ``allow_pickle`` never needed).
    Keys are ``/``-separated. Dtypes: float64, int64, bool, or a unicode
    string. Shapes below use ``n`` for the test states of the system in time
    order (``n_test``), ``E`` evaluation draws, ``M`` oracle draws, ``k`` the
    evaluation horizons, ``nS`` the test-sweep states (``n_test_sweep``), and
    ``R`` rules.

``meta/``
    ``schema`` (str, ``SCHEMA``), ``system``, ``seed_id``, ``preset`` (str);
    ``n_oracle_draws``, ``n_eval_draws``, ``steps_per_lyapunov``,
    ``reference_horizon`` (int64 scalars); ``draw_counters`` (str, ``(8,)``):
    the column names of every ``*_handled`` array.

``core/``
    The test split of the core cell; state ``i`` is the ``i``-th test state in
    time order.

    * ``horizons`` (int64 ``(k,)``, steps) and ``ref_index`` (int64 scalar:
      the position of ``H_ref`` in ``horizons``).
    * ``E_C``, ``E_P``, ``C`` (``(n, k)``): ``E[e_C^2]``, ``E[e_P^2]``,
      ``E[e_C e_P]`` over the ``M`` oracle draws, the ``sq_cp``, ``sq_plp``,
      ``cross`` of the moments.
    * ``w_star`` (``(n, k)``): the clipped oracle weight, ``oracle_weight`` of
      them.
    * The same four for the two halves of the draws: ``E_C_A``, ``E_P_A``,
      ``C_A``, ``w_star_A`` (draws ``[0, M/2)``) and ``E_C_B``, ``E_P_B``,
      ``C_B``, ``w_star_B`` (draws ``[M/2, M)``); ``half_n_draws`` (int64
      ``(2,)``) their sizes. For even ``M``, ``(E_C_A + E_C_B) / 2`` is
      ``E_C`` up to round-off.
    * ``abs_C`` (``(n, k)``): the mean absolute cross term
      ``mean |e_C e_P|`` over all the draws, the exact scale of that round-off
      bound for ``C`` (the squares are positive, so ``E_C`` and ``E_P`` are
      their own scale).
    * ``eps_s`` (``analog_seed``), ``delta`` (``est_seed``), ``N`` (the oracle
      noise sensitivity), ``nu``, ``Lambda_bar``, ``d`` (local dimension),
      ``g_H_ref`` (the oracle gain at ``H_ref``): each ``(n,)``.
    * ``R`` (``(n, E)``): the recurrence distance of the evaluation draws.
    * ``profile`` (``(n, E, 4)``): the deployable profile.
    * ``a5_leaf`` (int64 ``(n, E)``) and ``a5_leaf_calibration`` (int64
      ``(n_cal, E)``): the leaf id (``tree.apply``) of the chosen-K A5 tree
      for every (state, draw). The digest of ``a5_leaf_calibration`` followed
      by ``a5_leaf``, each in C order, is the leaf ``fitted/a5_leaf_digest``.
    * ``weight_href/<A2|A3|A4|A5>`` (``(n, E)``): the rule weight at ``H_ref``
      of every evaluation draw.
    * ``state_mse/<rule>`` (``(n, k)``, ``rule`` in A0 .. A5, A4o, A*): the
      realized squared error of the rule averaged over the ``E`` draws, per
      horizon; the ``H_ref`` column is the per-state score the verdicts use
      (``RuleScores.state_mse_ref``).
    * ``oracle_state`` (int64 ``(n, 3)``): the sentinel flags of the state
      oracles.

``handling/<construction|calibration|test>/``
    The clip and replacement counts of the core cell, for all three splits
    because the cell record of the run pools them.

    * ``oracle_handled`` and ``eval_handled`` (int64 ``(n_s, 8)``): the
      per-state ``handled`` counts, with the columns named in
      ``meta/draw_counters``, among them the clipped draws at ``H_ref``.
    * ``oracle_clip_entries`` and ``eval_clip_entries`` (int64 ``(3,)``): the
      totals over (state, draw, horizon) of the clipped CP, PLP and non-finite
      error entries (``clip_entry_names``, a str ``(3,)`` array in the group
      ``meta/``). Their sums over the splits are the counts of the same names
      in the cell record.

``lm/<construction|calibration|test>/``
    The Levenberg-Marquardt data of every estimate of the core cell, for all
    three splits because the LM summaries of the run pool them (``n_s`` is the
    number of states of the split).

    * ``oracle_residual`` (float64), ``oracle_accepted`` (int64) and
      ``oracle_late`` (bool or int64, as the run stored it), each
      ``(n_s, M)``; and ``eval_residual``, ``eval_accepted``, ``eval_late``,
      each ``(n_s, E)``.
    * For every estimate: the final cost ``c = ||X_t - G'(u_hat)||^2``
      (``lm_residual``; it is the ``c`` of ``c / rho^2``), the number of
      accepted iterations and the late-progress flag.

``sweep/rho=<g>|n_lib=<n>/``
    One group per distinct cell of the noise and library sweeps. The states
    are the first ``nS`` test states; the core cell appears as its own sweep
    view.

    * ``w_star_href`` and ``err_corr_href`` (``(nS,)``): ``w*(H_ref)`` and the
      correlation of the CP and PLP errors over the oracle draws.
    * ``E_C``, ``E_P``, ``C`` (``(nS,)``): the full second moments at
      ``H_ref``; ``abs_C``: the mean absolute cross term (the exact scale of
      the b4 bound for ``C``).
    * ``E_C_A``, ``E_P_A``, ``C_A``, ``E_C_B``, ``E_P_B``, ``C_B``
      (``(nS,)``): the half-draw second moments at ``H_ref``;
      ``half_n_draws`` (int64 ``(2,)``).

``v4/``
    The first ``convergence_states`` test states; ``nM`` is the number of
    convergence draw counts and ``nV`` the number of states.

    * ``M`` (int64 ``(nM,)``), ``horizons`` (int64 ``(3,)``: ``H_ref``, 2 and
      4 Lyapunov times).
    * ``w_hat`` (``(nM, nV, 3)``): the weight estimated from the first ``M``
      draws, per state and horizon.
    * ``half_width`` (same shape): half the 95% bootstrap interval of it (200
      resamples, the production indices).
    * ``signed_dev`` (same shape): ``w_hat`` minus the estimate from all the
      draws, signed.
    * ``w_ref`` (``(nV, 3)``): the estimate from all the draws.
    * The ``H_ref`` column comes from the production forecast; the other two
      from a second forecast of the same states and draws. The ``H_ref``
      column of the second forecast is compared bitwise with the production
      one: ``extra_href_equal`` (bool) and ``extra_href_diff`` (the number of
      entries that differ in their bit patterns or are NaN; the comparison is
      strict). Its handling is counted in ``extra_handled`` (int64
      ``(nV, 8)``) and ``extra_clip_entries`` (int64 ``(3,)``, over all three
      horizons, names ``extra_clip_entry_names``).
    * The median over states of ``half_width[m, :, 0]`` is the leaf
      ``validation/convergence/<M>/median_half_width``, and the mean of
      ``abs(signed_dev[m, :, 0])`` is ``mean_abs_dev_from_max``.

``h1c/``
    Schema /2; H1c, the test states in time order, ``nT`` the admissible
    thresholds.

    * ``thresholds`` (``(nT,)``).
    * For ``PLP`` and ``CP``: ``<name>/ratio`` (``(n,)``: the per-state ratio
      ``Lambda_bar x slope`` of every state, NaN where the state is not
      eligible) and ``<name>/eligible`` (bool ``(n,)``).
    * The ratios of the eligible states, in order, are the array that
      ``analysis.h1c_ratio_block`` receives; its median and interval are the
      H1c leaves.

``h1a/``
    Schema /2; H1a, the test-sweep states, ``nS`` of them, ``nL`` library
    sizes, ``nR`` noise levels.

    * ``noise_levels`` (float64 ``(nR,)``) and ``n_lib`` (float64 ``(nL,)``):
      the sorted levels and sizes.
    * ``local_dim`` and ``inverse_dim`` (``(nS,)``): the Levina-Bickel local
      dimension and its inverse (``S / (k - 1)``), before the finite filter.
    * ``rho=<g>/seed_sq`` (``(nS, nL)``, one per level): the squared analog
      seed errors of the library cells, before the filter.
    * The production keeps the states where every ``seed_sq`` and
      ``inverse_dim`` is finite; the medians, the reference
      ``mean(inverse_dim)`` and the fit statistics of the H1a leaves follow
      from these.

``qn/<oracle|deployable>/``
    Q-N, the test states in time order.

    * ``x_test`` (``(n, 4)``): the profile of the kind (the first evaluation
      draw for the deployable one).
    * ``w_star`` and ``log_t`` (``(n,)``: the log state horizon): the inputs
      of the targets.
    * Per target (``logit_w_interior``, ``w_zero_indicator``, ``log_horizon``):
      ``<target>/pred3`` and ``<target>/pred4`` (``(n,)``: the predictions of
      the model with three and with four profile coordinates, for every test
      state), ``<target>/y`` (``(n,)``: the target, with the placeholder
      ``0.0`` outside the domain, which is never read) and
      ``<target>/domain`` (bool ``(n,)``).
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import numpy as np

from .allocation import deployable_profile
from .config import StudyConfig
from .data import SPLITS
from .ensemble import DRAW_COUNTERS, ENTRY_COUNTERS
from .oracle import oracle_weight

SCHEMA = "lpcstudy.states/2"
"""Schema version key (``meta/schema``).

A change of any key or shape in the module docstring changes the version."""

EXTRA_GROUPS: tuple[str, ...] = ("h1a/", "h1c/")
"""The key prefixes that ``StateDump.record_extra`` accepts.

These are the groups added in schema /2."""

V4_MULTIPLES: tuple[int, ...] = (2, 4)
"""Lyapunov times of the V4 arrays beyond ``H_ref``.

``H_ref`` itself is the first column."""

HALF_NAMES: tuple[tuple[str, str], ...] = (
    ("sq_cp", "E_C"),
    ("sq_plp", "E_P"),
    ("cross", "C"),
)
"""Pairs of ``ensemble_moments(half_out=...)`` key stem and dump name."""


def clean(name: str, value: object) -> np.ndarray:
    """Return a copy of ``value`` as a dump array.

    The result is float64, int64, bool or a unicode string. Anything else is
    refused rather than converted, so no value changes silently (PRIME.4).

    Parameters
    ----------
    name : str
        Key (for the error message).
    value : object
        Array-like.

    Returns
    -------
    np.ndarray
        An independent copy (writing to it never changes the array of the
        study).

    Raises
    ------
    TypeError
        If the dtype is not float64, a signed integer, bool or unicode string.
        Nothing is converted silently (PRIME.4): a float32 or an object array
        is refused.
    """
    array = np.array(value, copy=True)
    kind = array.dtype.kind
    if kind == "f" and array.dtype.itemsize == 8 or kind in "bU":
        return array
    if kind == "i":
        return array.astype(np.int64)
    raise TypeError(
        f"dump array {name!r} has dtype {array.dtype}; "
        "need float64, int, bool or str"
    )


class StateDump:
    """Collector of the per-state arrays of one run.

    See the module docstring for the schema. The run feeds the collector from
    four places: ``Study.run_cell`` (``record_halves``), ``convergence_check``
    (``record_v4``), ``qn_noise_redundancy`` (``record_qn``) and
    ``run_system`` (``record_extra`` for the H1a and H1c arrays of schema /2,
    then ``collect`` and ``write``). It never returns anything to the study.
    """

    def __init__(self) -> None:
        self._halves: dict[tuple, dict[str, np.ndarray]] = {}
        self._v4: dict[str, dict[str, np.ndarray]] = {}
        self._qn: dict[str, dict[str, np.ndarray]] = {}
        self._extra: dict[str, dict[str, np.ndarray]] = {}

    def record_halves(
        self,
        system: str,
        noise: float,
        library_size: int,
        core: bool,
        horizons: np.ndarray,
        halves: dict[str, np.ndarray],
    ) -> None:
        """Store (as copies) the half-draw moments of a cell's test split.

        Parameters
        ----------
        system : str
            System name.
        noise, library_size : float, int
            The cell.
        core : bool
            Core cell (all horizons, all test states) or sweep cell.
        horizons : np.ndarray
            The horizons (steps) of the columns.
        halves : dict[str, np.ndarray]
            The ``half_out`` of ``ensemble_moments``.
        """
        self._halves[(system, float(noise), int(library_size), bool(core))] = {
            "horizons": clean("horizons", horizons),
            **{k: clean(k, v) for k, v in halves.items()},
        }

    def record_v4(self, system: str, arrays: dict[str, np.ndarray]) -> None:
        """Store the V4 arrays of a system.

        The keys are those of the ``v4/`` group, without the prefix.
        """
        self._v4[system] = {k: clean(f"v4/{k}", v) for k, v in arrays.items()}

    def record_extra(self, system: str, arrays: dict[str, np.ndarray]) -> None:
        """Store arrays under their full keys (``h1a/`` and ``h1c/``).

        Only these two groups of schema /2 may be added this way, and a key can
        be recorded once: a key of schema ``/1`` (or any other) is never
        silently replaced (PRIME.4).

        Raises
        ------
        ValueError
            If a key is outside ``h1a/`` and ``h1c/``, or is already recorded
            for the system.
        """
        recorded = self._extra.get(system, {})
        for key in arrays:
            if not key.startswith(EXTRA_GROUPS):
                raise ValueError(
                    f"record_extra takes keys under {EXTRA_GROUPS}, got {key!r}"
                )
            if key in recorded:
                raise ValueError(
                    f"record_extra: {key!r} is already recorded for {system}"
                )
        self._extra.setdefault(system, {}).update(
            {k: clean(k, v) for k, v in arrays.items()}
        )

    def record_qn(
        self, system: str, kind: str, arrays: dict[str, np.ndarray]
    ) -> None:
        """Store the Q-N arrays of one profile kind.

        The keys are those of ``qn/<kind>/``, without that prefix.
        """
        self._qn.setdefault(system, {}).update(
            {
                f"{kind}/{k}": clean(f"qn/{kind}/{k}", v)
                for k, v in arrays.items()
            }
        )

    def _cell_halves(
        self, system: str, noise: float, library_size: int, rows: int | None
    ) -> dict[str, np.ndarray]:
        """Return the half moments of a sweep cell.

        This is its own record if there is one; otherwise the first ``rows``
        states of the core cell.
        """
        key = (system, float(noise), int(library_size))
        if (*key, False) in self._halves:
            return self._halves[(*key, False)]
        if (*key, True) in self._halves:
            core = self._halves[(*key, True)]
            if rows is None:
                return core
            return {
                k: v if k in ("horizons", "n_draws") else v[:rows]
                for k, v in core.items()
            }
        raise KeyError(
            f"no half-draw moments were recorded for {system} rho={noise:g} "
            f"n_lib={library_size}: Study.run_cell did not see it with the "
            "dump on"
        )

    def collect(
        self,
        system: str,
        core,
        rules,
        weights: dict[str, np.ndarray],
        scores: dict,
        noise_cells: dict,
        library_cells: dict,
        cfg: StudyConfig,
    ) -> dict[str, np.ndarray]:
        """Build every array of a system's file and drop its pending records.

        Parameters
        ----------
        system : str
            System name.
        core : Cell
            The core cell (all splits and horizons, with evaluation draws).
        rules : FittedRules
            The rules fitted on it.
        weights : dict[str, np.ndarray]
            Rule weights of the test split ``(n, E, nH)``
            (``experiments._evaluate``).
        scores : dict
            The rule scores of the test split.
        noise_cells, library_cells : dict
            The sweep cells, keyed by ``rho`` and by ``(rho, n_lib)``.
        cfg : StudyConfig
            Configuration.

        Returns
        -------
        dict[str, np.ndarray]
            The arrays, keyed as in the module docstring.

        Raises
        ------
        KeyError
            If a half-draw record, the V4 arrays, the Q-N arrays or the extra
            (``h1a/`` and ``h1c/``) arrays of the system are missing.
        ValueError
            If the core horizons are not 1..H_max, or the per-state MSE of a
            rule at ``H_ref`` differs from the score the verdicts use.
        TypeError
            If an array is not float64, int, bool or str (``clean``).
        """
        test = core.splits["test"]
        m, ev, oracles = test.moments, test.evals, core.oracles["test"]
        ref = cfg.reference_horizon
        cols = np.array(cfg.eval_horizons) - 1
        if not np.array_equal(
            np.asarray(core.horizons)[cols], np.array(cfg.eval_horizons)
        ):
            raise ValueError(
                "the core horizons are not 1..H_max, so the evaluation columns "
                "are not at h - 1"
            )
        ref_col = ref - 1
        halves = self._halves[
            (system, float(core.noise), int(core.library_size), True)
        ]
        out: dict[str, np.ndarray] = {}

        def put(name: str, value: object) -> None:
            out[name] = clean(name, value)

        put("meta/schema", SCHEMA)
        put("meta/system", system)
        put("meta/seed_id", cfg.seed_id)
        put("meta/preset", cfg.name)
        put("meta/n_oracle_draws", cfg.n_oracle_draws)
        put("meta/n_eval_draws", cfg.n_eval_draws)
        put("meta/steps_per_lyapunov", cfg.steps_per_lyapunov)
        put("meta/reference_horizon", ref)
        put("meta/draw_counters", np.array(DRAW_COUNTERS))
        put("meta/clip_entry_names", np.array(ENTRY_COUNTERS))
        put("core/horizons", np.array(cfg.eval_horizons))
        put("core/ref_index", cfg.eval_horizons.index(ref))
        for stem, name in HALF_NAMES:
            put(f"core/{name}", getattr(m, stem)[:, cols])
            for tag in ("A", "B"):
                put(f"core/{name}_{tag}", halves[f"{stem}_{tag}"][:, cols])
        put("core/abs_C", halves["abs_cross"][:, cols])
        put("core/w_star", oracle_weight(m)[:, cols])
        for tag in ("A", "B"):
            half = dataclasses.replace(
                m, **{stem: halves[f"{stem}_{tag}"] for stem, _ in HALF_NAMES}
            )
            put(f"core/w_star_{tag}", oracle_weight(half)[:, cols])
        put("core/half_n_draws", halves["n_draws"])
        put("core/eps_s", m.analog_seed)
        put("core/delta", m.est_seed)
        put("core/N", m.noise_sens)
        put("core/nu", oracles.nu)
        put("core/Lambda_bar", oracles.growth)
        put("core/d", oracles.local_dim)
        put("core/g_H_ref", oracles.gains[:, ref - 1])
        put("core/oracle_state", oracles.handled)
        put("core/R", ev.distance)
        profile = deployable_profile(
            ev, rules.proxies, core.noise, cfg.steps_per_lyapunov
        )
        put("core/profile", profile)
        tree = rules.regimes[rules.chosen_regimes].tree
        cal_profile = deployable_profile(
            core.splits["calibration"].evals,
            rules.proxies,
            core.noise,
            cfg.steps_per_lyapunov,
        )
        put(
            "core/a5_leaf",
            tree.apply(profile.reshape(-1, profile.shape[-1])).reshape(
                profile.shape[:2]
            ),
        )
        put(
            "core/a5_leaf_calibration",
            tree.apply(cal_profile.reshape(-1, cal_profile.shape[-1])).reshape(
                cal_profile.shape[:2]
            ),
        )
        for rule in ("A2", "A3", "A4", "A5"):
            put(f"core/weight_href/{rule}", weights[rule][:, :, ref_col])
        for rule, w in weights.items():
            err = w * ev.cp_err + (1 - w) * ev.plp_err  # as in score_rules
            sq = err**2
            put(
                f"core/state_mse/{rule}",
                np.stack([sq[:, :, c].mean(axis=1) for c in cols], axis=1),
            )
            if not np.array_equal(
                out[f"core/state_mse/{rule}"][:, int(out["core/ref_index"])],
                scores[rule].state_mse_ref,
                equal_nan=True,
            ):
                raise ValueError(
                    f"state_mse of {rule} at H_ref differs from the score the "
                    "verdicts use: a defect of the dump, not a tolerance"
                )
        # All three splits: the cell record of the run pools them (b3 of the
        # plan).
        for split in SPLITS:
            part = core.splits[split]
            for kind, source in (
                ("oracle", part.moments),
                ("eval", part.evals),
            ):
                put(f"handling/{split}/{kind}_handled", source.handled)
                put(
                    f"handling/{split}/{kind}_clip_entries",
                    [source.clip_entries[name] for name in ENTRY_COUNTERS],
                )
            for kind, source in (
                ("oracle", part.moments),
                ("eval", part.evals),
            ):
                for name in ("residual", "accepted", "late"):
                    put(
                        f"lm/{split}/{kind}_{name}",
                        getattr(source, f"lm_{name}"),
                    )

        done: set[tuple[float, int]] = set()
        for cell in (*noise_cells.values(), *library_cells.values()):
            key = (float(cell.noise), int(cell.library_size))
            if key in done:
                continue
            done.add(key)
            sm = cell.splits["test"].moments
            n_rows = len(sm.sq_cp)
            half = self._cell_halves(system, *key, rows=n_rows)
            hcol = int(np.nonzero(np.asarray(half["horizons"]) == ref)[0][0])
            group = f"sweep/rho={key[0]:g}|n_lib={key[1]}"
            put(f"{group}/w_star_href", oracle_weight(sm)[:, sm.at(ref)])
            put(f"{group}/err_corr_href", sm.err_corr[:, sm.at(ref)])
            for stem, name in HALF_NAMES:
                put(f"{group}/{name}", getattr(sm, stem)[:, sm.at(ref)])
            put(f"{group}/abs_C", half["abs_cross"][:n_rows, hcol])
            for stem, name in HALF_NAMES:
                for tag in ("A", "B"):
                    put(
                        f"{group}/{name}_{tag}",
                        half[f"{stem}_{tag}"][:n_rows, hcol],
                    )
            put(f"{group}/half_n_draws", half["n_draws"])

        for name, value in self._v4.pop(system).items():
            put(f"v4/{name}", value)
        for name, value in self._qn.pop(system).items():
            put(f"qn/{name}", value)
        for name, value in self._extra.pop(system).items():
            put(name, value)
        for key in [k for k in self._halves if k[0] == system]:
            del self._halves[key]
        return out

    @staticmethod
    def write(path: Path, arrays: dict[str, np.ndarray]) -> int:
        """Write the archive (uncompressed) and return its size in bytes.

        Parameters
        ----------
        path : Path
            ``<out>/states/<system>.npz``; the folder is created.
        arrays : dict[str, np.ndarray]
            The output of :meth:`collect`.

        Returns
        -------
        int
            File size in bytes.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, **arrays)
        return path.stat().st_size


def v4_arrays(cfg: StudyConfig) -> tuple[np.ndarray, np.ndarray]:
    """Return the horizons (steps) of the V4 arrays and of their extra forecast.

    The V4 horizons are ``H_ref``, 2 Lyapunov times and 4 Lyapunov times. The
    extra forecast covers the last two.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        ``(all three, the extra two)``.
    """
    extra = np.array(
        [int(round(k * cfg.steps_per_lyapunov)) for k in V4_MULTIPLES]
    )
    return np.concatenate([[cfg.reference_horizon], extra]), extra


def entry_names() -> np.ndarray:
    """Return the names of the clip-entry totals as a string array.

    The names are those of ``ENTRY_COUNTERS``.
    """
    return np.array(ENTRY_COUNTERS)
