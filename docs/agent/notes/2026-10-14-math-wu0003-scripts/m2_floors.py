"""M2: the ROADMAP 10x rule with and without scale floors, on a real platform pair.

Pair: smoke DEV-0 at 759d47b, default OpenBLAS kernel against forced Sandybridge (WU-0002.14 S3), a
T2/T3-type pair (W, U and network weights differ at the ulp level; trajectory equal). It stands in
for the GPU-to-GPU pair R1/R2, which does not exist yet.
rel = |a - b| / s, with s by leaf class (M2 of the note). Excluded from the max: integer-valued
leaves and discrete counts (their own rule), digests/strings, the V1 fixture leaves (absolute rule),
and fitted 'floor' parameters (chain heads).
DEVELOPMENT (DEV-0): not a hypothesis test. Reads results.json only.
"""
import json, math, re, sys
A = json.load(open(sys.argv[1])); B = json.load(open(sys.argv[2]))

def walk(a, b, path, parent_a, out):
    if isinstance(a, dict):
        for k in a:
            if k == "seconds" or (not path and k == "provenance") or k not in b:
                continue
            walk(a[k], b[k], path + (k,), a, out)
    elif isinstance(a, list):
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + (f"[{i}]",), a, out)
    elif isinstance(a, float) and isinstance(b, float) and a != b and not (math.isnan(a) and math.isnan(b)):
        out.append((path, a, b, parent_a))

out = []
walk(A, B, (), None, out)
CI_KEYS = ("ci", "range_ci", "interval", "ratio_ci", "mean_ci", "median_ci", "ci_inverse_dim")

def n_states(path):
    return 80  # smoke n_test; sweep 60 (floor uses the smaller share where it matters)

def classify(path, a, b, parent, root):
    p = "/".join(path)
    if re.search(r"median_iterations$", p):
        return "excluded: integer-valued (rule +-1)", None
    if re.search(r"validation/(delay_jacobian_rel_err|gain_rel_err)$", p):
        return "excluded: V1 fixture (absolute 1e-12)", None
    if re.search(r"fitted/.*/floor$", p):
        return "excluded: fitted floor parameter (chain head)", None
    # interval endpoints: scale max(|lo|,|hi|) of the interval
    if len(path) >= 2 and path[-2] in CI_KEYS:
        ci = parent
        return "interval endpoint", max(abs(ci[0]), abs(ci[1]))
    # point estimate with an interval sibling in the same dict
    d = root
    for k in path[:-1]:
        d = d[k] if not k.startswith("[") else d[int(k[1:-1])]
    if isinstance(d, dict):
        for ck in CI_KEYS:
            if ck in d and isinstance(d[ck], list) and len(d[ck]) == 2 and all(isinstance(v, float) for v in d[ck]):
                return "point with interval", max(abs(d[ck][0]), abs(d[ck][1]))
    if re.search(r"(weight_profile|median_w_by_noise|regime_weights|global_weight|agreement)", p):
        return "weight scale [0,1] (floor 0.01)", max(abs(a), 0.01)
    if re.search(r"(fraction|km_curves|survival|share)", p):
        return "fraction/probability (floor 1/n)", max(abs(a), 1 / n_states(path))
    if re.search(r"(spearman|corr|partial)", p, re.I):
        return "correlation (floor 1/sqrt n)", max(abs(a), 1 / math.sqrt(n_states(path)))
    if re.search(r"logrank_p", p):
        return "p-value (floor 1e-3)", max(abs(a), 1e-3)
    if re.search(r"delta_r2|r2_", p):
        return "R2-type without interval (floor 0.01)", max(abs(a), 0.01)
    return "other (relative, no floor)", abs(a)

rows = {}
for path, a, b, parent in out:
    cls, s = classify(path, a, b, parent, A)
    rel_nofloor = abs(a - b) / max(abs(a), abs(b)) if max(abs(a), abs(b)) > 0 else 0.0
    rel = None if s is None else (abs(a - b) / s if s > 0 else float("inf"))
    rows.setdefault(cls, []).append((rel_nofloor, rel, "/".join(path)))
allnof, allf = [], []
print(f"{'class':45s} {'n':>4s} {'max rel, no floor':>18s} {'max rel, M2 scale':>18s}  argmax (M2)")
for cls in sorted(rows):
    v = rows[cls]
    mn = max(v, key=lambda t: t[0]); allnof.append(mn[0])
    if v[0][1] is None:
        print(f"{cls:45s} {len(v):4d} {mn[0]:18.2e} {'(own rule)':>18s}  {mn[2]}")
        continue
    mf = max(v, key=lambda t: t[1]); allf.append(mf[1])
    print(f"{cls:45s} {len(v):4d} {mn[0]:18.2e} {mf[1]:18.2e}  {mf[2]}")
def rule(x):
    return 10 ** math.ceil(math.log10(10 * x)) if x > 0 else 0.0
print(f"\n10x rule, no floor, all float leaves:  max rel {max(allnof):.2e} -> declared tolerance {rule(max(allnof)):.0e}")
print(f"10x rule, M2 scales, eligible leaves: max rel {max(allf):.2e} -> declared tolerance {rule(max(allf)):.0e}")
