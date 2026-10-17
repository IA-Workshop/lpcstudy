"""Q5: census of compare_pilot chain tags over the float leaves of a results.json, and of the leaves
that differ on the kernel pair, by tag and block. DEVELOPMENT (DEV-0): read-only; imports
tools/compare_runs.py (which imports tools/compare_pilot.py) as a module; nothing is written."""
import importlib.util, json, sys
from collections import Counter
from pathlib import Path

TOOLS = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("compare_runs", TOOLS / "compare_runs.py")
cr = importlib.util.module_from_spec(spec); sys.modules["compare_runs"] = cr; spec.loader.exec_module(cr)
flat_ref = cr.cp.flatten(json.load(open(sys.argv[2])))
flat_new = cr.cp.flatten(json.load(open(sys.argv[3]))) if len(sys.argv) > 3 else None
tags, diff = Counter(), Counter()
untagged_diff = Counter()
for p, v in flat_ref.items():
    if type(v) is not float or p[0] in ("provenance",) or "seconds" in p:
        continue
    t = cr.chain_of(p) or "(untagged)"
    blk = cr.loc(p)[1]
    tags[(t, blk)] += 1
    if flat_new is not None and p in flat_new and flat_new[p] != v:
        diff[(t, blk)] += 1
for t in sorted({k[0] for k in tags}):
    tot = sum(n for k, n in tags.items() if k[0] == t)
    dd = sum(n for k, n in diff.items() if k[0] == t)
    blocks = ", ".join(f"{b}:{n}" for (tt, b), n in sorted(tags.items()) if tt == t)
    print(f"{t:12s} float leaves {tot:5d}  differing on pair {dd:4d}  | {blocks[:400]}")
if flat_new is not None:
    print("\ncp/oracle-tagged leaves that differ (tag, path, rel to |ref|):")
    for p, v in sorted(flat_ref.items()):
        if type(v) is float and p in flat_new and flat_new[p] != v and cr.chain_of(p) in ("cp", "oracle", "fixture", "dynamics"):
            print(f"  {cr.chain_of(p):8s} {'/'.join(map(str, p))}  {abs(flat_new[p]-v)/abs(v):.3g}")

if flat_new is not None:
    print("\nuntagged float leaves that differ, grouped (block / leaf name): count, max rel to |ref|")
    groups = {}
    for p, v in sorted(flat_ref.items()):
        if type(v) is float and p in flat_new and flat_new[p] != v and not cr.chain_of(p) \
                and p[0] != "provenance" and "seconds" not in p:
            key = (cr.loc(p)[1], "/".join(str(x) for x in p[3:] if not str(x).startswith("[")))
            r = abs(flat_new[p] - v) / abs(v) if v else float("inf")
            n, m = groups.get(key, (0, 0.0))
            groups[key] = (n + 1, max(m, r))
    for (blk, name), (n, m) in sorted(groups.items()):
        print(f"  {blk:16s} {name[:70]:70s} {n:3d}  {m:.3g}")
