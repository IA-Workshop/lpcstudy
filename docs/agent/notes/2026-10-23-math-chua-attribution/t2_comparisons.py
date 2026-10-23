"""T2: the B2 comparisons and the step-refinement table, from the E1/E2/E4 outputs."""
import json, math
import numpy as np
e1 = json.load(open("e1_reference.json")); e2 = json.load(open("e2_benettin_settings.json")); e4 = json.load(open("e4_dysts_spectrum_replica.json"))
code = 0.43113260161336364  # DEV-0 reference leaf systems/chua/context/lambda_max
dmax, dspec0 = 1.2301163591725595, 0.4605474829443073
o = e1["ours"]
se_code = o["batch_se_start07"]
ok = ~np.array(o["diverged"])
vals = np.array(o["lam1_all"])[ok]
print("SE_code (batch SE, independent run from (0.7,0,0), T=1e4):", round(se_code, 5))
print("spread check: sd over", ok.sum(), "distinct starts", round(vals.std(ddof=1), 5), "(should match SE_code)")
print("batch SE per start:", np.round(np.array(o["batch_se_all"])[ok], 4))
ens, ens_se = o["ens_mean"], o["ens_se"]
d = code - ens; c = math.hypot(se_code, ens_se)
print(f"code {code:.5f} vs independent ensemble {ens:.5f}+-{ens_se:.5f}: diff {d:+.5f}, combined SE {c:.5f}, |diff|/c {abs(d)/c:.2f}")
d = code - o["lam_start07"][0]; c = math.hypot(se_code, se_code)
print(f"code vs independent same-start run {o['lam_start07'][0]:.5f}: diff {d:+.5f}, |diff|/combined SE {abs(d)/c:.2f}")
for k in ["dysts", "exact"]:
    dd = e1[k]["ens_mean"] - ens; cc = math.hypot(e1[k]["ens_se"], ens_se)
    print(f"params {k}: ensemble {e1[k]['ens_mean']:.5f}+-{e1[k]['ens_se']:.5f}, minus ours {dd:+.5f} (combined SE {cc:.5f})")
print(f"Dysts max - code = {dmax - code:+.5f} = {(dmax-code)/se_code:.0f} SE_code; ratio {dmax/code:.3f}")
print(f"Dysts spec0 - code = {dspec0 - code:+.5f} = {(dspec0-code)/se_code:.1f} SE_code; ratio {dspec0/code:.4f}")
for k in ["rk4_tangent", "backward_euler"]:
    m, s = e4[k]["weighted_rep_lam1_mean"], e4[k]["weighted_rep_lam1_sd"]
    print(f"E4 replica ({k}): {m:.4f} sd {s:.4f}; (Dysts spec0 - replica mean)/sd = {(dspec0-m)/s:+.2f}; (Dysts max - replica mean)/sd = {(dmax-m)/s:+.1f}")
print("Spectrum: ours", np.round(o["spectrum_mean"], 4), "sum", round(o["sum_spectrum_mean"], 4), "; KY ours",
      round(2 + (o["spectrum_mean"][0] + o["spectrum_mean"][1]) / abs(o["spectrum_mean"][2]), 4))
inner, outer = -15.6 * (1 - 1.143) - 1, -15.6 * (1 - 0.714) - 1
for nm, s in [("ours", o["sum_spectrum_mean"]), ("Dysts spectrum", 0.4605474829443073 + 0.0022048281168492866 - 4.319076735248446)]:
    print(f"  implied time fraction in |x|<1 from sum {s:.4f} ({nm}): {(s - outer) / (inner - outer):.4f}")
print("Step refinement (E2a):")
lv = [0.01, 0.005, 0.0025, 0.00125]
q = [(e2[f"a_h={h}"]["mean"], e2[f"a_h={h}"]["se"]) for h in lv]
for i, h in enumerate(lv):
    s = f"  h={h:<8} {q[i][0]:.5f} +- {q[i][1]:.5f}"
    if i: s += f"  diff to previous {q[i][0]-q[i-1][0]:+.5f} +- {math.hypot(q[i][1], q[i-1][1]):.5f}"
    print(s)
d = q[1][0] - q[3][0]; c = math.hypot(q[1][1], q[3][1])
print(f"  h=0.005 minus h=0.00125: {d:+.5f} +- {c:.5f}; 2-sigma bound on |error at h=0.005|: {abs(d)+2*c:.4f}")
