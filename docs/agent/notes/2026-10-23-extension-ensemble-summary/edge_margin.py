"""Bootstrap Monte Carlo margin of the primary interval endpoints against the band edges.

Diagnostic only (uq-budget row "bootstrap Monte Carlo error"): for each stored endpoint e
with stored Monte Carlo standard error s (leaf ``ci_mc_se``, order [lower, upper]) and each
band edge b of v3 §2, z = |e - b| / s. The minimum z over endpoints and edges says how many
Monte Carlo standard errors separate the stored word from a word change at the edge. It
changes no stored word. DEVELOPMENT seeds only. Run with ``python3 -I edge_margin.py``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract import ENSEMBLE, EXTENSION, load  # noqa: E402

EDGES = {
    "H2a(i)": ((("H2a",), "range_ci"), (0.1,)),
    "H2a(ii) zero": ((("H2a", "part_ii", "zero"), "ci"), (-0.1, 0.1)),
    "H2a(ii) interior": ((("H2a", "part_ii", "interior"), "ci"), (-0.1, 0.1)),
    "H2b(i)": ((("H2b", "noise"), "ci"), (0.0,)),
    "H2b(ii)": ((("H2b", "library_change"), "ci"), (0.0,)),
    "H3c": ((("H3c",), "ci"), (1.05,)),
}


def margins(name: str, res: dict) -> list[str]:
    """Minimum endpoint-to-edge distance in Monte Carlo standard errors, per primary part."""
    rows = []
    for system, block in res["systems"].items():
        for part, ((path, ci_key), edges) in EDGES.items():
            leaf = block
            for key in path:
                leaf = leaf[key]
            ci, se = leaf[ci_key], leaf["ci_mc_se"]
            z = min(abs(e - b) / s for e, s in zip(ci, se) for b in edges if s > 0)
            half = (ci[1] - ci[0]) / 2
            ratio = max(se) / half
            rows.append(
                f"| {name} | {system} | {part} | {z:.1f} | {ratio:.3f} |"
                + (" < 2: word within MC error of an edge |" if z < 2 else " |")
            )
    return rows


def main() -> int:
    """Print the margin table."""
    print("| run | system | part | min z (MC s.e.) | max MC s.e. / half-width | note |")
    print("|---|---|---|---|---|---|")
    for seed, folder in ENSEMBLE.items():
        print("\n".join(margins(f"ens-{seed}", load(folder)[0])))
    for system, folder in EXTENSION.items():
        print("\n".join(margins(system, load(folder)[0])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
