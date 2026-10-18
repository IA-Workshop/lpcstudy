"""M1 (TD statistic): P0 against P1 (two independent DEV-0 realizations: redrawn states and streams).

For each primary part: delta, se = hw / z_level (A6 form) and the 'arms facing away' form (DEC-0027),
z_TD = |delta| / sqrt(se0^2 + se1^2); also hw ratios P1/P0 (for M3: realization spread of hw).
DEVELOPMENT (DEV-0): not a hypothesis test. Reads results.json only.
Usage: python -I m1_td_p0p1.py P0.json P1.json
"""
import json, math, sys
from statistics import NormalDist
N = NormalDist()
LEVEL = 1 - 0.05 / 3
z_lvl = N.inv_cdf(1 - (1 - LEVEL) / 2)
parts = {
    "H2a(i)": ("H2a", "median_range", "range_ci"),
    "H2a(ii)zero": ("H2a/part_ii/zero", "partial_corr", "ci"),
    "H2a(ii)int": ("H2a/part_ii/interior", "partial_corr", "ci"),
    "H2b(i)": ("H2b/noise", "mean_state_spearman", "ci"),
    "H2b(ii)": ("H2b/library_change", "mean_change", "ci"),
    "H3c": ("H3c", "A5_over_A4_mse", "ci"),
}
def get(d, p):
    for k in p.split("/"):
        d = d[k]
    return d
r0 = json.load(open(sys.argv[1]))["systems"]; r1 = json.load(open(sys.argv[2]))["systems"]
zs, zs_away, lhw = [], [], []
print(f"z_level = {z_lvl:.4f}; Bonferroni over 15: {N.inv_cdf(1-0.005/15):.3f}; over 18: {N.inv_cdf(1-0.005/18):.3f}")
print(f"{'system':9s} {'part':12s} {'est0':>9s} {'est1':>9s} {'hw0':>8s} {'hw1':>8s} {'hw1/hw0':>7s} {'z_TD':>6s} {'z_away':>6s} n0 n1")
for s in r0:
    for name, (blk, pt, ci) in parts.items():
        b0, b1 = get(r0[s], blk), get(r1[s], blk)
        e0, e1 = b0[pt], b1[pt]; c0, c1 = b0[ci], b1[ci]
        hw0, hw1 = (c0[1]-c0[0])/2, (c1[1]-c1[0])/2
        d = e1 - e0
        z = abs(d) / math.hypot(hw0/z_lvl, hw1/z_lvl)
        # arms facing away from the other estimate (DEC-0027): run 1 above run 0 (d > 0) -> run 0's
        # lower arm and run 1's upper arm
        a0 = (e0-c0[0]) if d > 0 else (c0[1]-e0); a1 = (c1[1]-e1) if d > 0 else (e1-c1[0])
        za = abs(d) / math.hypot(a0/z_lvl, a1/z_lvl)
        n0 = b0.get("n_states", b0.get("n_eligible_states")); n1 = b1.get("n_states", b1.get("n_eligible_states"))
        if name == "H2b(i)":
            n0 = n1 = 300  # n_test_sweep (no n_states stored, WU-0005.6 D6)
        if name == "H2a(i)":
            n0, n1 = b0["n_eligible_states"], b1["n_eligible_states"]
        zs.append(z); zs_away.append(za); lhw.append((name, s, math.log(hw1/hw0), n0, n1))
        print(f"{s:9s} {name:12s} {e0:9.4f} {e1:9.4f} {hw0:8.4f} {hw1:8.4f} {hw1/hw0:7.3f} {z:6.2f} {za:6.2f} {n0} {n1}")
k = len(zs)
print(f"\nsum z^2 = {sum(z*z for z in zs):.2f} on {k} (E = {k}); max z = {max(zs):.2f}; "
      f"away: sum {sum(z*z for z in zs_away):.2f}, max {max(zs_away):.2f}")
# log hw ratio spread, corrected for n change: expected log ratio = 0.5*log(n0/n1)
dev = [l - 0.5*math.log(n0/n1) for _, _, l, n0, n1 in lhw]
sd = math.sqrt(sum(x*x for x in dev)/len(dev))
print(f"log(hw1/hw0) after the sqrt(n) correction: RMS {sd:.3f} over {len(dev)} parts -> per-run SD(log hw) ~ {sd/math.sqrt(2):.3f}")
for (name, s, l, n0, n1), x in zip(lhw, dev):
    print(f"   {s:9s} {name:12s} log ratio {l:+.3f} corrected {x:+.3f}")
