"""Values quoted in the phase J interpretation guide (no statistic).

For each claim row, prints the lowest and highest stored per-seed point and
interval bound, and the count of each stored reading word. Rows are found and
checked against ``confirm.json`` by ``tools/phasej_figures.py``.

Usage: python docs/agent/notes/2026-10-29-phase-j-interpretation-guide.values.py promoted/phase-J
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
import phasej_figures as pf  # noqa: E402

seeds, confirm, table = pf.load(Path(sys.argv[1]))
rows = pf.claim_rows(table, confirm, seeds)
by_claim: dict[str, list[dict]] = {}
for row in rows:
    by_claim.setdefault(row["claim_id"], []).append(row)
for claim_id, group in by_claim.items():
    words = Counter(w for r in group for w in r["readings"])
    print(f"{claim_id}: {group[0]['statement']}; readings {dict(words)}")
    for r in group:
        points = [v["point"] for v in r["values"]]
        lower = min(v["ci"][0] for v in r["values"])
        upper = max(v["ci"][1] for v in r["values"])
        print(
            f"   {r['system']:9s} {r['profile']:10s} {r['verdict']:14s}"
            f" points {min(points):.4g} to {max(points):.4g};"
            f" lowest lower bound {lower:.4g}; highest upper bound {upper:.4g}"
        )
