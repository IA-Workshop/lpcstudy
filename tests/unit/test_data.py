"""Seeded random streams (WU-0001.1)."""

from __future__ import annotations

import inspect
import json
import zlib

import numpy as np

from lpcstudy.config import SMOKE
from lpcstudy.data import build_context, make_rng
from lpcstudy.pipeline import Study
from lpcstudy.seeds import REGISTRY_PATH, with_seed


def test_make_rng_with_a_registry_seed_equals_numpy_directly() -> None:
    """``make_rng`` on a seed set by ``with_seed`` draws the stream NumPy gives for the key.

    Reference: ``np.random.default_rng([v, zlib.crc32(b"a|1")])``, NumPy used directly,
    with ``v`` the DEV-1 value read from the registry by ``json.load``. The streams are
    identical, so the comparison is exact (no tolerance), and the 62-bit seed is not
    narrowed on the way.
    """
    with REGISTRY_PATH.open() as handle:
        value = next(e["value"] for e in json.load(handle)["seeds"] if e["id"] == "DEV-1")
    config = with_seed(SMOKE, "DEV-1", value)
    assert config.seed == value
    ours = make_rng(config.seed, "a", 1).random(8)
    reference = np.random.default_rng([value, zlib.crc32(b"a|1")]).random(8)
    assert np.array_equal(ours, reference)


def test_no_delay_scale_parameter_remains() -> None:
    """``build_context``, ``Study.context`` and ``Study.run_cell`` have no ``delay_scale`` (WU-0002.1).

    Reference: the removal of the tau_d/2 robustness variant (v3 section 6, E6 lists D, k and
    +-5/10% only; Methods v2 section M15 item 9), written out in the test. Tolerance: none;
    equality of parameter-name sets (read with ``inspect.signature``). Recorded placement: this
    file, as the plan allows.
    """
    for function in (build_context, Study.context, Study.run_cell):
        assert "delay_scale" not in inspect.signature(function).parameters, function
