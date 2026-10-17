"""M1/M2: per-leaf relative differences between two runs that differ only in the platform.

Pair used: smoke DEV-0 at 759d47b, default OpenBLAS kernel (Haswell) against forced Sandybridge
(WU-0002.14 S3; same host, same commit; W/U digests and network weights differ, trajectory equal):
an empirical instance of tier T2/T3 of WU-0003 A6.
DEVELOPMENT (DEV-0): not a hypothesis test. Reads results.json only.
Usage: python -I m1_kernel_pair.py A.json B.json
"""
import json, math, sys, re
from collections import defaultdict

def flatten(t, p=()):
    out = {}
    if isinstance(t, dict):
        for k, v in t.items():
            if k in ("seconds",) or (not p and k == "provenance"):
                continue
            out.update(flatten(v, p + (str(k),)))
    elif isinstance(t, list):
        for i, v in enumerate(t):
            out.update(flatten(v, p + (f"[{i}]",)))
    else:
        out["/".join(p)] = t
    return out

a = flatten(json.load(open(sys.argv[1]))); b = flatten(json.load(open(sys.argv[2])))
common = sorted(set(a) & set(b))
diff = [k for k in common if isinstance(a[k], float) and isinstance(b[k], float) and a[k] != b[k]
        and not (math.isnan(a[k]) and math.isnan(b[k]))]
idiff = [k for k in common if not isinstance(a[k], float) and a[k] != b[k]]
print("leaves", len(common), "float diffs", len(diff), "non-float diffs", len(idiff))
for k in idiff[:40]:
    print("  NONFLOAT", k, a[k], b[k])
groups = defaultdict(list)
for k in diff:
    parts = k.split("/")
    g = parts[2] if parts[0] == "systems" and len(parts) > 2 else parts[0]
    if parts[0] == "systems" and len(parts) > 3 and parts[2] in ("handling", "validation", "H2a", "H2b"):
        g = parts[2] + "/" + parts[3]
    x, y = a[k], b[k]
    rel = abs(x - y) / max(abs(x), abs(y)) if max(abs(x), abs(y)) > 0 else 0.0
    groups[g].append((rel, abs(x - y), k))
print(f"{'group':34s} {'n':>5s} {'med rel':>9s} {'p90 rel':>9s} {'max rel':>9s}  max abs   argmax")
for g in sorted(groups):
    v = sorted(groups[g])
    rels = [r for r, _, _ in v]
    n = len(v)
    print(f"{g:34s} {n:5d} {rels[n//2]:9.2e} {rels[int(0.9*(n-1))]:9.2e} {rels[-1]:9.2e} "
          f"{max(d for _, d, _ in v):9.2e}  {v[-1][2]}")

# primaries: point and interval, relative to max(|lo|,|hi|) and to hw
prim = {
    "H2a(i)": ("H2a/median_range", "H2a/range_ci"),
    "H2a(ii) zero": ("H2a/part_ii/zero/partial_corr", "H2a/part_ii/zero/ci"),
    "H2a(ii) interior": ("H2a/part_ii/interior/partial_corr", "H2a/part_ii/interior/ci"),
    "H2b(i)": ("H2b/noise/mean_state_spearman", "H2b/noise/ci"),
    "H2b(ii)": ("H2b/library_change/mean_change", "H2b/library_change/ci"),
    "H3c": ("H3c/A5_over_A4_mse", "H3c/ci"),
    "H2c A4-A2": ("H2c/A4_minus_A2/estimate", "H2c/A4_minus_A2/ci"),
    "H2d": ("H2d/in_distribution_excess", "H2d/ci"),
}
ra = json.load(open(sys.argv[1]))["systems"]; rb = json.load(open(sys.argv[2]))["systems"]
def get(d, path):
    for p in path.split("/"):
        if not isinstance(d, dict) or p not in d:
            return None
        d = d[p]
    return d
print("\nprimaries: |d| / max(|lo|,|hi|) (T1-T3 tolerance 1e-4) and |d| / hw")
for s in ra:
    for name, (pt, ci) in prim.items():
        pa, pb, ca, cb = get(ra[s], pt), get(rb[s], pt), get(ra[s], ci), get(rb[s], ci)
        if not isinstance(ca, list) or None in ca or None in (cb or [None]):
            print(f"  {s:9s} {name:18s} n/a ({pa}, {ca})"); continue
        if pa is None or isinstance(pa, dict):
            pa = pb = float('nan')
        scale = max(abs(ca[0]), abs(ca[1])); hw = (ca[1] - ca[0]) / 2
        d = [abs(pa - pb), abs(ca[0] - cb[0]), abs(ca[1] - cb[1])]
        print(f"  {s:9s} {name:18s} scale {scale:.3g} hw {hw:.3g}  rel(pt,lo,hi) = "
              + ", ".join(f"{x/scale:.1e}" for x in d) + "   /hw = " + ", ".join(f"{x/hw:.1e}" for x in d))
