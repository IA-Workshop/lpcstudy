"""Tests for lpcstudy.systems: the registry of dynamical systems (WU-0002.1)."""

from __future__ import annotations

from lpcstudy import systems
from lpcstudy.systems import SYSTEMS


def test_registry_holds_exactly_the_three_v3_systems() -> None:
    """The registry is Lorenz-63, Rossler and Chua; Lorenz-96 and its field are gone.

    Reference: decision log D3 and proposal and methods v3 section 4 (three systems), written
    out in the test, not read from the code. Tolerance: none; equality of a set of strings.
    """
    assert set(SYSTEMS) == {"lorenz63", "rossler", "chua"}
    assert not hasattr(systems, "lorenz96_field")
