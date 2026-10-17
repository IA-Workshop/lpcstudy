"""V4 (convergence in M) per-seed values and updated failure estimates. No random number drawn.

Reads, read-only: the P0 and P1 V4 values (as v4v2.py of 2026-10-13, cross-checked against the
run results), the R1 run results.json (DEV-1 pilot, GPU) and its states dump v4/half_width
(per-state bootstrap half-widths, M = 50, 200, 800 at H_ref), and R2 (DEV-1 repeat) if present.

1. Collects V4 (used_M, median half-width at each M, mean |w_M - w_800|, the pass flag) and the
   gate flags V1, V2, V4, V5, V6, V7 of R1 (and R2).
2. Checks that the median of the dump's per-state half-widths at M = 200 equals the gated value.
3. Within-seed (state-sampling) log-SE of the median of 40 half-widths: Maritz-Jarrett, on log
   values (the sample median commutes with the monotone log), plus the distribution-free 95% CI
   of the population median from order statistics (binomial ranks).
4. Between-seed log-SD from P0, P1, R1 (3 realizations per system; 6 pooled df), chi-square CI,
   and the per-seed failure probabilities as in v4v2.py (plug-in, predictive t, over the CI).
DEVELOPMENT. Usage: python -I v4_update.py <R1 pilot dir> [<R2 pilot dir>]
"""
import json
import sys

import numpy as np
from scipy import stats as st

r1_dir = sys.argv[1]
r2_dir = sys.argv[2] if len(sys.argv) > 2 else None
bar = 0.05
systems = ("lorenz63", "rossler", "chua")
runs = {"P0": "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/p0-1b20db9/runs/dev/p0/pilot",
        "P1": "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/p1-5b3fd8f/runs/dev/p1/pilot",
        "R1": r1_dir}
v4 = {s: {} for s in systems}
print("== V4 and gate flags per run (read-only)")
for name, d in list(runs.items()) + ([("R2", r2_dir)] if r2_dir else []):
    r = json.load(open(f"{d}/results.json"))
    sid = r["provenance"].get("seed_id", "?")
    com = str(r["provenance"].get("commit", "?"))[:8]
    for s in systems:
        val = r["systems"][s]["validation"]
        c = val["convergence"]
        gate = val.get("gate", {})
        v7 = r["systems"][s].get("V7", {})
        print(f"  {name} ({sid}, {com}) {s:9s} used_M {c['used_M']}  V4 = median half-width "
              + " ".join(f"M={m}: {c[m]['median_half_width']:.4f}" for m in ("50", "200", "800"))
              + "  mean|w_M - w_800| " + " ".join(f"{c[m]['mean_abs_dev_from_max']:.4f}"
                                                  for m in ("50", "200", "800"))
              + f"  pass {c['pass']}  margin x{bar / c['200']['median_half_width']:.2f}")
        print(f"      gate {gate}  V2 median {val['crlb_ratio_median']:.3f} "
              f"[min {val['crlb_ratio_min']:.3f}, max {val['crlb_ratio_max']:.3f}]  V5 "
              f"{val['km_max_abs_dev']:.4f}  V6 {val['integrator_max_dev_sigma']:.3e}  V7 slope "
              f"{v7.get('median_slope', float('nan')):.4f}")
        if name in runs:
            v4[s][name] = c["200"]["median_half_width"]

print("\n== R1 per-state half-widths (states dump, M = 200, H_ref)")
z_info = {}
for s in systems:
    z = np.load(f"{r1_dir}/states/{s}.npz", allow_pickle=False)
    M = z["v4/M"]
    hw = z["v4/half_width"]  # (len(M), 40, horizons)
    w = z["v4/w_hat"]
    k200 = int(np.where(M == 200)[0][0])
    h = hw[k200, :, 0]
    eq = np.median(h) == v4[s]["R1"]
    n = h.size
    zero = int(np.sum(h <= 1e-12))
    clip = int(np.sum((w[k200, :, 0] <= 0) | (w[k200, :, 0] >= 1)))
    # Maritz-Jarrett SE of the sample median on the raw scale (the half-widths have an atom at 0,
    # the states whose weight sits at the clip, so the log scale is not usable for the SE itself);
    # converted to a log-SE by the delta method, SE / median
    hs = np.sort(h)
    mj = []
    for m in (n // 2, n // 2 + 1):  # the two middle order statistics (1-based ranks 20, 21)
        a, b = m - 1, n - m
        i = np.arange(1, n + 1)
        W = st.beta.cdf(i / n, a, b) - st.beta.cdf((i - 1) / n, a, b)
        c1, c2 = np.sum(W * hs), np.sum(W * hs ** 2)
        mj.append(np.sqrt(c2 - c1 ** 2))
    se_raw = float(np.mean(mj))
    se_log = se_raw / np.median(h)
    # distribution-free CI for the population median: ranks l, u with
    # P(l <= Bin(n, 1/2) < u) >= 0.95
    lo_rank = int(st.binom.ppf(0.025, n, 0.5))
    up_rank = n - lo_rank + 1
    cover = st.binom.cdf(up_rank - 1, n, 0.5) - st.binom.cdf(lo_rank - 1, n, 0.5)
    z_cov = st.norm.ppf(0.5 + cover / 2)
    se_log_os = np.log(hs[up_rank - 1] / hs[lo_rank - 1]) / (2 * z_cov)
    # exact bounds on the bootstrap probability that the median of 40 states resampled from this
    # seed's per-state law exceeds the bar: median* > c needs X*(21) > c and is implied by
    # X*(20) > c; X*(k) > c  <=>  #{resampled <= c} <= k - 1, #{...} ~ Bin(40, F(c))
    F = np.mean(h <= bar)
    p_lo = st.binom.cdf(n // 2 - 1, n, F)   # P(X*(20) > c)
    p_hi = st.binom.cdf(n // 2, n, F)       # P(X*(21) > c)
    z_info[s] = se_log_os
    print(f"  {s:9s} median {np.median(h):.4f} (== gated V4: {eq}); quartiles "
          f"{np.quantile(h, .25):.4f} / {np.quantile(h, .75):.4f}; min {h.min():.4f} max "
          f"{h.max():.4f}; states with half-width 0: {zero}; w_hat at the clip (0 or 1): {clip} "
          f"of {n}; states above 0.05: {int(np.sum(h > bar))}")
    print(f"      distribution-free {cover:.3f} CI of the population median [x({lo_rank}), "
          f"x({up_rank})] = [{hs[lo_rank - 1]:.4f}, {hs[up_rank - 1]:.4f}] -> log-SE "
          f"{se_log_os:.3f}; Maritz-Jarrett SE {se_raw:.4f} -> log-SE {se_log:.3f}")
    print(f"      state-resampling P(median of 40 > 0.05) in [{p_lo:.3f}, {p_hi:.3f}] "
          f"(exact binomial bounds, F(0.05) = {F:.3f})")

print("\n== Between-seed spread of log V4 (P0, P1, R1; one value per run)")
logs = {s: np.log(np.array([v4[s][k] for k in ("P0", "P1", "R1")])) for s in systems}
ss = {s: float(np.sum((x - x.mean()) ** 2)) for s, x in logs.items()}
df = sum(len(x) - 1 for x in logs.values())
s2 = sum(ss.values()) / df
s_pool = np.sqrt(s2)
lo = np.sqrt(df * s2 / st.chi2.ppf(.975, df))
hi = np.sqrt(df * s2 / st.chi2.ppf(.025, df))
print(f"  per-system SD: " + ", ".join(f"{s} {np.sqrt(ss[s] / 2):.3f}" for s in systems))
print(f"  pooled log-SD s = {s_pool:.3f} on {df} df, 95% CI [{lo:.3f}, {hi:.3f}] "
      f"(2026-10-13, n = 2: 0.314 on 3 df, CI [0.178, 1.169])")
bart = st.bartlett(*[x for x in logs.values()])
print(f"  Bartlett test of a common SD: stat {bart.statistic:.2f}, p = {bart.pvalue:.3f} (2 df each; "
      "low power)")
mean_within = float(np.sqrt(np.mean(np.array(list(z_info.values())) ** 2)))
print(f"  state-sampling log-SE from the R1 dump (RMS over systems) {mean_within:.3f}; "
      f"ratio s / within = {s_pool / mean_within:.2f}; F-type check: (s/within)^2 = "
      f"{s2 / mean_within ** 2:.2f}, P(chi2_{df}/{df} >= that) = "
      f"{st.chi2.sf(df * s2 / mean_within ** 2, df):.3f}")

print("\n== Per-seed P(V4 fails) (log-normal model, common SD; as v4v2.py)")
tot = {"plug": 1.0, "pred": 1.0, "within": 1.0, "lo": 1.0, "hi": 1.0}
for s in systems:
    x = logs[s]
    mu = x.mean()
    gap = np.log(bar) - mu
    plug = st.norm.sf(gap / s_pool)
    pred = st.t.sf(gap / (s_pool * np.sqrt(1 + 1 / len(x))), df)
    within = st.norm.sf(gap / mean_within)
    r_lo, r_hi = st.norm.sf(gap / lo), st.norm.sf(gap / hi)
    for k, v in (("plug", plug), ("pred", pred), ("within", within), ("lo", r_lo), ("hi", r_hi)):
        tot[k] *= 1 - v
    print(f"  {s:9s} values " + " ".join(f"{np.exp(v):.4f}" for v in x)
          + f"  geo-mean {np.exp(mu):.4f} margin x{bar / np.exp(mu):.2f}  plug-in {plug:.3f}  "
          f"predictive (t{df}) {pred:.3f}  over the SD CI [{r_lo:.3f}, {r_hi:.3f}]  "
          f"(state-sampling SD only: {within:.3f})")
print("  any system: plug-in {:.3f}, predictive {:.3f}, over the SD CI [{:.3f}, {:.3f}], "
      "state-sampling SD only {:.3f}".format(1 - tot["plug"], 1 - tot["pred"], 1 - tot["lo"],
                                              1 - tot["hi"], 1 - tot["within"]))

print("\n== Full preset (convergence_states = 100, pilot 40): V4 is a median of 100 states. If the")
print("   between-seed spread is state sampling (section 2.2), sigma scales by sqrt(40/100); the")
print("   location is carried over from the pilot values (assumption: same per-state law at full)")
scale = np.sqrt(40 / 100)
tot = {"plug": 1.0, "pred": 1.0, "lo": 1.0, "hi": 1.0}
for s in systems:
    x = logs[s]
    gap = np.log(bar) - x.mean()
    sf = s_pool * scale
    plug = st.norm.sf(gap / sf)
    pred = st.t.sf(gap / np.sqrt(sf ** 2 + s2 / len(x)), df)
    r_lo, r_hi = st.norm.sf(gap / (lo * scale)), st.norm.sf(gap / (hi * scale))
    for k, v in (("plug", plug), ("pred", pred), ("lo", r_lo), ("hi", r_hi)):
        tot[k] *= 1 - v
    print(f"  {s:9s} sigma_full {sf:.3f}  plug-in {plug:.3f}  predictive {pred:.3f}  over the CI "
          f"[{r_lo:.3f}, {r_hi:.3f}]")
print("  any system: plug-in {:.3f}, predictive {:.3f}, over the CI [{:.3f}, {:.3f}]".format(
    1 - tot["plug"], 1 - tot["pred"], 1 - tot["lo"], 1 - tot["hi"]))
