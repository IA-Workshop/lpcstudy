#!/usr/bin/env python3
"""Extract the C7 inputs of the DEV-0 pilots P0 and P1 into small committed fixtures (WU-0003.3a).

What this script does for the study
-----------------------------------
``tools/rehearsal_report.py`` projects pilot results onto the pre-registered
criteria of the study (the "C7 projection"). To test that tool on real
numbers, the tests need pilot data, but the two full ``results.json`` files
are about 2 MB each and are not committed. This script copies out only the
few numbers the tool reads, so the tests can use small files (about 8 KB
each).

DEVELOPMENT (DEV-0): not a hypothesis test. The script reads the two
``results.json`` files read-only. It copies, bit for bit (JSON floats
round-trip exactly in Python, so nothing is rounded), only the leaves that
``tools/rehearsal_report.py`` reads:

* the configuration;
* a few provenance keys (``PROVENANCE``: which run it was, and which code);
* for each system, the interval, point estimate and level of the 18 primary
  and secondary criteria of the C7 projection (``LEAVES``).

Usage::

    python3 -I extract_p0p1.py P0_results.json P0_fixture.json
    python3 -I extract_p0p1.py P1_results.json P1_fixture.json

with ``P0`` = ``lpcstudy-wt/run/p0-1b20db9/runs/dev/p0/pilot/results.json``
(lpcstudy 1b20db9) and ``P1`` =
``lpcstudy-wt/run/p1-5b3fd8f/runs/dev/p1/pilot/results.json`` (lpcstudy
5b3fd8f). The fixtures are what the tests read: ``p0_pilot.json`` and
``p1_pilot.json`` in this folder.
"""

import json
import sys

PROVENANCE = (
    "schema",
    "seed_id",
    "seed_kind",
    "label",
    "promoted",
    "commit",
    "dirty",
    "preset",
)
# Keys of the "systems/<name>" tree: a path inside the tree -> the leaf names
# to copy from there (the criteria named after each hypothesis, such as H1b).
LEAVES = {
    "H1b/PLP": ("slope", "ci"),
    "H1c/PLP": ("median_ratio", "ci"),
    "H1d/rows/analog_seed": ("spearman", "interval"),
    "H1a": ("level",),
    "H1a/by_noise/0.01": ("ratio", "ratio_ci"),
    "Q-N/oracle/logit_w_interior": ("delta_r2", "ci"),
    "Q-N/oracle/w_zero_indicator": ("delta_r2", "ci"),
    "Q-N/oracle/log_horizon": ("delta_r2", "ci"),
    "H2a": ("median_range", "range_ci"),
    "H2a/part_ii/zero": ("partial_corr", "ci"),
    "H2a/part_ii/interior": ("partial_corr", "ci"),
    "H2b/noise": ("mean_state_spearman", "ci"),
    "H2b/library_change": ("mean_change", "ci", "level"),
    "H2c": ("best_single",),
    "H2c/A4_minus_A2": ("mean", "ci", "relative"),
    "H2c/A4_minus_A1": ("mean", "ci", "relative"),
    "H3a": ("chosen_K", "pairs", "logrank_p_raw"),
    "V7": (
        "median_slope",
        "ci",
        "efficiency_median_by_noise",
        "efficiency_ci_by_noise",
    ),
    "H2d": ("in_distribution_excess", "ci"),
    "H2e/by_noise/0.01": ("median_change", "ci", "level"),
    "H2e/by_noise/0.02": ("median_change", "ci", "level"),
    "H3c": ("A5_over_A4_mse", "ci", "level"),
}


def main(src: str, dst: str) -> None:
    """Copy the leaves listed in ``LEAVES`` from ``src`` into ``dst``.

    Parameters
    ----------
    src : str
        Path of a full pilot ``results.json`` (read only).
    dst : str
        Path of the small fixture file to write.
    """
    full = json.load(open(src))
    out = {
        "config": full["config"],
        "provenance": {k: full["provenance"][k] for k in PROVENANCE},
        "systems": {},
    }
    for system, tree in full["systems"].items():
        kept: dict = {}
        for path, names in LEAVES.items():
            node, target = tree, kept
            for key in path.split("/"):
                node = node[key]
                target = target.setdefault(key, {})
            for name in names:
                target[name] = node[name]
        out["systems"][system] = kept
    json.dump(out, open(dst, "w"), indent=0)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
