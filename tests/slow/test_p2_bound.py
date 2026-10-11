"""S1: Theorem P2(c) on the development cell of every system (WU-0005.5b).

DEVELOPMENT (DEV-0): verification check, not a hypothesis test. Slow tier: the cost is
``build_context`` (Benettin over 10^5 steps and the trajectories) once per system, about a
minute each; the check itself is under 10 s per cell.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from lpcstudy.config import PILOT
from lpcstudy.data import SPLITS
from lpcstudy.embedding import delay_vectors
from lpcstudy.ensemble import AnalogLibrary
from lpcstudy.pipeline import Study
from lpcstudy.seeds import REGISTRY_PATH, load_registry, resolve_dev_seed, with_seed
from lpcstudy.validation import check_p2_bound

SYSTEMS = PILOT.core_systems
STRESS_NOISE = 0.05  # E1's largest level: switching is common here (Delta/rho well below 1)
MIN_SWITCHING = 100  # non-vacuity premise, fixed in WU-0005.5a (M8) before any result
SUMMARY_PATH = Path(__file__).resolve().parents[2] / "runs" / "tests" / "p2_bound_s1.json"
CONFIG = with_seed(PILOT, "DEV-0", resolve_dev_seed("DEV-0", load_registry(REGISTRY_PATH)))
RESULTS: dict[str, dict] = {}


@pytest.fixture(scope="module")
def study(tmp_path_factory: pytest.TempPathFactory) -> Study:
    """One study (contexts cached across the six tests) on the development seed DEV-0."""
    return Study(CONFIG, tmp_path_factory.mktemp("p2_bound"))


def _check(study: Study, system: str, noise: float, splits: tuple[str, ...]) -> dict:
    """The P2(c) block for a cell: library, clean queries and oracle draws only, no forecasts."""
    cfg = study.config
    ctx = study.context(system)
    library = AnalogLibrary.build(ctx, noise, cfg.core_library, cfg.horizon_max)
    cleans = {s: delay_vectors(ctx.eval_clean, ctx.split_indices[s], ctx.delay, ctx.embed_dim)
              for s in splits}
    noises = {s: study.unit_noise(ctx, s, "oracle", cfg.n_oracle_draws, ctx.embed_dim)
              for s in splits}
    start = time.time()
    out = check_p2_bound(library, cleans, noises, noise)
    out["seconds_check"] = time.time() - start
    return out


def _assert_clean(out: dict, label: str) -> None:
    """Non-vacuity first (a design finding), then zero violations (a defect, never a tolerance)."""
    assert out["n_switching_states"] >= MIN_SWITCHING, (
        f"{label}: only {out['n_switching_states']} switching states; the check is vacuous here "
        "(a design finding for /refer; the premise is not lowered)")
    assert out["n_violations"] == 0, f"{label}: P2(c) violated: {out}"
    assert out["n_headline_violations"] == 0 and not any(out["n_chain_violations"].values()), label


def _record(label: str, out: dict) -> None:
    RESULTS[label] = out
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(RESULTS, indent=1, sort_keys=True))


@pytest.mark.parametrize("system", SYSTEMS)
def test_p2c_holds_at_the_core_cell(study: Study, system: str) -> None:
    """N_M^2 <= A_M <= B_M in every state of all three splits at rho = 0.01 (v3 Theorem P2(c)).

    Reference: the theorem itself on the empirical law of the oracle draws, which holds exactly
    (a defect if violated; WU-0005.5a, M4: the only slack is the round-off bound of the check).
    Cell: ``PILOT`` on DEV-0, core noise 0.01, ``n_lib = 10^4``, k = 1, M = 200, 600 + 300 + 500
    states, the oracle noise of ``Study.unit_noise``. Premise (M8): at least 100 switching states.
    Reported (``runs/tests/p2_bound_s1.json``): switching states, states with B = 0, ties, band
    draws, N/sqrt(B) quantiles, the switch-indicator decomposition, ``sum N^2 / sum B_inf``, ``z_B``
    and the second moment of the noise. Zero tolerance beyond the derived slacks (PRIME.2).
    """
    out = _check(study, system, CONFIG.core_noise, SPLITS)
    _record(f"{system}|core|rho={CONFIG.core_noise}", out)
    assert out["n_states"] == CONFIG.n_construction + CONFIG.n_calibration + CONFIG.n_test
    _assert_clean(out, f"{system} core cell")


@pytest.mark.parametrize("system", SYSTEMS)
def test_p2c_holds_at_the_stress_cell(study: Study, system: str) -> None:
    """The same check at rho = 0.05 on the test split, where Delta/rho is often below 1.

    Reference and premise as the core cell (500 states, library and oracle draws only, no
    forecasts). It exercises the regime in which most states switch (WU-0005.5a, M8).
    """
    out = _check(study, system, STRESS_NOISE, ("test",))
    _record(f"{system}|stress|rho={STRESS_NOISE}", out)
    assert out["n_states"] == CONFIG.n_test
    _assert_clean(out, f"{system} stress cell")
