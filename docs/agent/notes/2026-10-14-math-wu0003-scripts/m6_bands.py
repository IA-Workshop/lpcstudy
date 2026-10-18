"""M6: predicted C4 bands from P0 and P1 (DEV-0 pilots) and the chi-square(4) contamination relation.

Relation checked: median c/rho^2 ~= Q_chi2_4( 0.5 / (1 - pi) ), pi = fraction_above - 0.001 (the
estimates outside the converged chi-square law), with its sampling SE sqrt(0.25/n)/f(Q).
DEVELOPMENT (DEV-0): not a hypothesis test. Reads results.json only.
"""
import json, math, sys
from scipy.stats import chi2
rows = {}
for path in sys.argv[1:]:
    tag = "P0" if "p0-" in path else "P1"
    r = json.load(open(path))
    for s, sd in r["systems"].items():
        for cid, cell in sd["handling"]["cells"].items():
            lm = cell.get("lm")
            if not lm:
                continue
            for kind in ("oracle", "eval"):
                k = lm["by_kind"].get(kind)
                if not k or not k["n_estimates"]:
                    continue
                rho = k["noise"]
                key = (s, cid.replace("base|", "").replace("|sweep", "").replace("|core", " core"), kind)
                rows.setdefault(key, {})[tag] = dict(n=k["n_estimates"], med=k["median_residual"] / rho**2,
                    above=k["fraction_above_chi2"], late=k["fraction_late_progress"],
                    nodec=k["fraction_no_decrease"], it=k["median_iterations"])
q50 = chi2.ppf(0.5, 4)
print(f"chi2_4 median {q50:.4f}, 0.999 quantile {chi2.ppf(0.999, 4):.4f}")
print(f"{'system':9s} {'cell':32s} {'kind':6s} run  {'med':>6s} {'pred':>6s} {'(o-p)/se':>8s} {'above':>7s} {'late':>7s} {'nodec':>8s} it")
worst = 0
for key in sorted(rows):
    for tag, v in sorted(rows[key].items()):
        pi = max(v["above"] - 0.001, 0.0)
        pred = chi2.ppf(0.5 / (1 - pi), 4)
        se = math.sqrt(0.25 / v["n"]) / chi2.pdf(pred, 4)
        z = (v["med"] - pred) / se
        worst = max(worst, abs(v["med"] - pred))
        print(f"{key[0]:9s} {key[1]:32s} {key[2]:6s} {tag}  {v['med']:6.3f} {pred:6.3f} {z:8.2f} {v['above']:7.4f} "
              f"{v['late']:7.4f} {v['nodec']:8.2e} {v['it']}")
print(f"largest |median - prediction| = {worst:.3f}")

# ---- predicted bands for the pilot-preset runs (R1 to R4): [min/2, 2 max] over P0, P1 per (system, cell, kind)
print("\nPredicted pilot bands (C4), oracle kind; [min/2, 2 max] of P0/P1; pooled per-run log-SD below")
lr = []
for key in sorted(rows):
    if len(rows[key]) < 2 or "n_lib=10000" not in key[1] or key[2] != "oracle":
        continue
    v0, v1 = rows[key]["P0"], rows[key]["P1"]
    for q in ("above", "late"):
        if v0[q] > 0 and v1[q] > 0:
            lr.append(math.log(v1[q] / v0[q]))
    lo_a, hi_a = min(v0["above"], v1["above"]) / 2, 2 * max(v0["above"], v1["above"])
    lo_l, hi_l = min(v0["late"], v1["late"]) / 2, 2 * max(v0["late"], v1["late"])
    nd = max(v0["nodec"], v1["nodec"])
    its = sorted({v0["it"], v1["it"]})
    print(f"{key[0]:9s} {key[1]:28s} above [{lo_a:.4f}, {hi_a:.4f}]  late [{lo_l:.4f}, {hi_l:.4f}]  "
          f"no_decrease <= {max(2*nd, 1e-4):.1e}  median_iterations {its[0]-1:.0f}..{its[-1]+1:.0f}")
s = math.sqrt(sum(x * x for x in lr) / len(lr)) / math.sqrt(2)
print(f"pooled per-run log-SD of the fractions: {s:.3f} over {len(lr)} log ratios; "
      f"new run vs geometric mean of two: SD {s*math.sqrt(1.5):.3f}, 3 SD = factor {math.exp(3*s*math.sqrt(1.5)):.2f}")
