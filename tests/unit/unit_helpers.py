"""Shared builders of test data for the unit tests (WU-0010.2).

Several unit tests (oracle, allocation, experiments, dump) need an
``EnsembleMoments`` object: the table of averages (means, mean squares and cross
products of the errors of the analog forecaster CP and the physics-based
forecaster PLP) that the code under test turns into a blend weight. These
helpers build one directly from simple inputs, without running the real
``lpcstudy.ensemble`` code, so the tests have an independent route to the
numbers. Test modules import them with ``from unit_helpers import ...``.
"""

from __future__ import annotations

import numpy as np

from lpcstudy.ensemble import EnsembleMoments


def _moments_from_draws(cp: np.ndarray, plp: np.ndarray) -> EnsembleMoments:
    """Build moments from raw error draws by plain sample averages.

    Parameters
    ----------
    cp, plp : np.ndarray
        Error draws of CP and PLP, shape ``(n_states, n_draws, n_horizons)``.

    Returns
    -------
    EnsembleMoments
        Means, mean squares and cross product over the draw axis; the seed
        and noise fields are set to simple placeholder values.
    """
    return EnsembleMoments(
        horizons=np.arange(1, cp.shape[-1] + 1),
        mean_cp=cp.mean(1),
        mean_plp=plp.mean(1),
        sq_cp=(cp**2).mean(1),
        sq_plp=(plp**2).mean(1),
        cross=(cp * plp).mean(1),
        analog_seed=np.ones(len(cp)),
        est_seed=np.ones(len(cp)),
        noise_sens=np.zeros(len(cp)),
    )


def realizable_triples(
    rng: np.random.Generator,
    n_below: int,
    n_inside: int,
    n_above: int,
    inside: tuple[float, float] = (0.0, 1.0),
) -> dict[str, np.ndarray]:
    """Draw realizable second-moment triples ``(E_C, E_P, C)`` with a known ``u``.

    ``E_C`` and ``E_P`` are the mean squared errors of CP and PLP, and ``C`` is
    their mean cross product. A triple is "realizable" when it could come from
    real error draws, which means the matrix ``[[E_C, C], [C, E_P]]`` is
    positive semidefinite (a Gram matrix). The best blend weight ``u`` is
    known by construction, so a test can compare it with what the code finds
    (WU-0002.3).

    The triples are manufactured in four steps. Draw the curvature ``c``
    (log-uniform on [1e-3, 10]), the optimal-value scale ``V_u / c`` (uniform
    on [0, 10]) and the unconstrained optimum ``u`` (uniform on (-5, 0) for
    ``n_below``, on ``inside`` for ``n_inside``, on (1, 6) for ``n_above``).
    Then set ``E_C = c (1 - u)^2 + V_u``, ``E_P = c u^2 + V_u`` and
    ``C = (E_C + E_P - c) / 2``. This gives ``E_C E_P - C^2 = c V_u >= 0``, so
    the triple is realizable.

    Returns
    -------
    dict[str, np.ndarray]
        ``E_C``, ``E_P``, ``C`` (what code under test may see) and ``c``, ``u``
        (the design, for choosing weights and for preconditions only).
    """
    u = np.concatenate(
        [
            rng.uniform(-5.0, 0.0, n_below),
            rng.uniform(inside[0], inside[1], n_inside),
            rng.uniform(1.0, 6.0, n_above),
        ]
    )
    c = np.exp(rng.uniform(np.log(1e-3), np.log(10.0), len(u)))
    v_u = c * rng.uniform(0.0, 10.0, len(u))
    e_c = c * (1.0 - u) ** 2 + v_u
    e_p = c * u**2 + v_u
    return {"E_C": e_c, "E_P": e_p, "C": (e_c + e_p - c) / 2.0, "c": c, "u": u}


def moments_from_triples(
    e_c: np.ndarray, e_p: np.ndarray, cross: np.ndarray
) -> EnsembleMoments:
    """Wrap ``(n_states, n_horizons)`` arrays of ``E_C``, ``E_P``, ``C`` as moments.

    The fields the blend weight does not use (means, seeds, noise sensitivity)
    are filled with dummy values.
    """
    n_states, n_hor = e_c.shape
    return EnsembleMoments(
        horizons=np.arange(1, n_hor + 1),
        mean_cp=np.zeros_like(e_c),
        mean_plp=np.zeros_like(e_c),
        sq_cp=e_c,
        sq_plp=e_p,
        cross=cross,
        analog_seed=np.ones(n_states),
        est_seed=np.ones(n_states),
        noise_sens=np.zeros(n_states),
    )
