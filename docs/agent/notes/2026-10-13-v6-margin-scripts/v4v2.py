"""V4 and V2 per-seed failure estimates from the n = 2 independent realizations (P0, P1). DEVELOPMENT (DEV-0)."""
import numpy as np
from scipy import stats as st
v4 = {"lorenz63": (0.03702635809603885, 0.01866192462072521),
      "rossler": (0.039019737806647685, 0.03336877202614194),
      "chua": (0.03076962505339958, 0.04196494897726123)}
bar = 0.05
d = {s: np.log(a) - np.log(b) for s, (a, b) in v4.items()}
s2 = np.mean([x ** 2 for x in d.values()]) / 2  # pooled within-system variance, 3 df
s = np.sqrt(s2); df = 3
lo, hi = np.sqrt(df * s2 / st.chi2.ppf(.975, df)), np.sqrt(df * s2 / st.chi2.ppf(.025, df))
print(f"pooled log-SD s = {s:.3f} (3 df), 95% CI [{lo:.3f}, {hi:.3f}]; per-system |d|/sqrt2:", {k: round(abs(v)/np.sqrt(2),3) for k,v in d.items()})
# leave-Lorenz-out sensitivity
s_noL = np.sqrt(np.mean([d['rossler']**2, d['chua']**2]) / 2)
print(f"  without Lorenz: s = {s_noL:.3f} (2 df)")
tot = {"plug": 1.0, "pred": 1.0}
for k, (a, b) in v4.items():
    mu = 0.5 * (np.log(a) + np.log(b)); gap = np.log(bar) - mu
    plug = st.norm.sf(gap / s)
    pred = st.t.sf(gap / (s * np.sqrt(1 + 1 / 2)), df)
    rng_ = (st.norm.sf(gap / lo), st.norm.sf(gap / hi))
    tot["plug"] *= 1 - plug; tot["pred"] *= 1 - pred
    print(f"{k:9s} geo-mean {np.exp(mu):.4f}  margin x{bar/np.exp(mu):.2f}  P(fail) plug-in {plug:.3f}  predictive(t3) {pred:.3f}  plug-in over sigma CI [{rng_[0]:.3f}, {rng_[1]:.3f}]")
print(f"P(any V4 fail): plug-in {1-tot['plug']:.3f}, predictive {1-tot['pred']:.3f}")
# V2: (min, median, max) of 5 per-state ratios
v2 = {"P0": [(0.9080, 0.9539, 0.9841), (0.9224, 0.9822, 1.0075), (0.9356, 0.9499, 1.0074)],
      "P1": [(0.8383, 1.0107, 1.0783), (0.9432, 0.9756, 0.9847), (0.9156, 1.0191, 1.0510)]}
rows = [r for v in v2.values() for r in v]
med = np.array([r[1] for r in rows]); rngs = np.array([r[2] - r[0] for r in rows])
print(f"V2 medians mean {med.mean():.3f} SD {med.std(ddof=1):.3f}; per-state SD from mean range/2.326 = {rngs.mean()/2.326:.3f}")
print(f"V2 distance of nearest edge in median-SDs: {(med.mean()-0.8)/med.std(ddof=1):.1f}")
q95 = 1 - 0.05 ** (1 / 30)
print(f"V2 distribution-free: 30 per-state values inside band -> q <= {q95:.3f} (95%); P(median of 5 outside) <= 10 q^3 = {10*q95**3:.4f}")
