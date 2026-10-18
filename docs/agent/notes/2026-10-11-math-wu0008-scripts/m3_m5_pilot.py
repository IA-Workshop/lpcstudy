"""WU-0008 M3/M5/M9: the budget formulas evaluated on the DEV-0 pilot results (DEVELOPMENT (DEV-0); B = 500).

Usage: python m3_m5_pilot.py <results.json> <dev_regression_dev0.md>. Prints per system: the sampling half-widths
(hi - lo)/2 of the five primaries, F1 (H2a(i) indicative finite-M bias bound), F2 (H2b(ii) draw-noise share), the
expected endpoint-SE/half-width ratio for a near-normal bootstrap distribution, and the platform (round-off)
perturbation maxima of the pilot regression report.
"""
import json, re, sys
from math import pi, sqrt
from statistics import NormalDist
N = NormalDist()
results, report = sys.argv[1], sys.argv[2]
r = json.load(open(results))
L = 1 - 0.05 / 3
zL, z95 = N.inv_cdf(1 - (1 - L) / 2), N.inv_cdf(0.975)
D_K = {2: 2 / sqrt(pi), 3: 3 / sqrt(pi)}  # E[range] of k iid N(0, 1)
hw = lambda ci: (ci[1] - ci[0]) / 2
B = r["config"]["bootstrap_resamples"]
for level in (0.95, L):
    a = (1 - level) / 2; z = N.inv_cdf(1 - a)
    print(f"expected endpoint SE / half-width at level {level:.4f}: B={B}: {sqrt(a*(1-a)/B)/N.pdf(z)/z:.4f}; B=2000: {sqrt(a*(1-a)/2000)/N.pdf(z)/z:.4f}")
for name, s in r["systems"].items():
    v4 = s["validation"]["convergence"]; M = v4["used_M"]; m_max = max(int(k) for k in v4 if k.isdigit())
    h, a = v4[str(M)]["median_half_width"], v4[str(M)]["mean_abs_dev_from_max"]
    s_med, s_mean = h / z95, a / (sqrt(2 / pi) * sqrt(1 - M / m_max))
    h2a, h2b, h3c = s["H2a"], s["H2b"], s["H3c"]
    f1 = D_K[3] * s_med
    lc = h2b["library_change"]; f2 = zL * sqrt(2) * s_mean / sqrt(lc["n_states"])
    print(f"== {name}: V4 h={h:.4f} a={a:.4f} s_med={s_med:.4f} s_mean={s_mean:.4f}; V6={s['validation']['integrator_max_dev_sigma']:.2e}")
    print(f"  H2a(i) est {h2a['median_range']:.4f} ci {[round(x,4) for x in h2a['range_ci']]} hw {hw(h2a['range_ci']):.4f}; F1 {f1:.4f} = {f1/hw(h2a['range_ci']):.2f} hw; lower - F1 = {h2a['range_ci'][0]-f1:.4f}")
    for part, p in h2a["part_ii"].items():
        print(f"  H2a(ii) {part}: est {p['partial_corr']:.4f} ci {[round(x,4) for x in p['ci']]} hw {hw(p['ci']):.4f} n {p['n_states']}")
    nb = h2b["noise"]; print(f"  H2b(i) est {nb['mean_state_spearman']:.4f} hw {hw(nb['ci']):.4f}")
    print(f"  H2b(ii) est {lc['mean_change']:.4f} hw {hw(lc['ci']):.4f}; F2 {f2:.4f} = {f2/hw(lc['ci']):.2f} hw; hw at M=inf >= {sqrt(max(hw(lc['ci'])**2-f2**2,0)):.4f}")
    print(f"  H3c est {h3c['A5_over_A4_mse']:.4f} ci {[round(x,4) for x in h3c['ci']]} hw {hw(h3c['ci']):.4f}")
    o = s["oracle_recovery"]; d = s["H1d"]["rows"]
    print(f"  proxy (H3c): A4_vs_A4o {o['A4_vs_A4o']:.3f}, A5_vs_Astar {o['A5_vs_Astar']:.3f}; H1d " +
          ", ".join(f"{k} {d[k]['spearman']:.3f}" for k in ("analog_seed", "estimation_seed", "growth", "nhat")))
# Platform (round-off-level) perturbation: DEV-0 against the v1 pilot (branch N tables N2 and N3).
lines = open(report).read().split("\n")
def table_after(prefix, stop):
    i = next(k for k, l in enumerate(lines) if l.startswith(prefix)); out = []
    for l in lines[i + 1:]:
        if l.startswith(stop): break
        p = [x.strip() for x in l.split("|")][1:-1]
        try: out.append((float(p[3]), p[0]))
        except (ValueError, IndexError): pass
    return out
n2 = table_after("N2 (", "N3 ("); n3 = table_after("N3 (", "Chain-head")
cont = [x for x in n2 + n3 if "gain_bound" not in x[1] and "/fitted/" not in x[1]]  # fitted coefficients at a ~0 floor are chain-head events, not QoIs
wp4 = [x for x in cont if re.search(r"weight_profile/\w+/\[(\d+)\]", x[1]) and int(re.search(r"\[(\d+)\]", x[1]).group(1)) <= 120]
notwp = [x for x in cont if "weight_profile" not in x[1]]
print(f"platform: {len(n2)} N2 + {len(n3)} N3 leaves; max relative, continuous non-weight-profile leaves (fitted coefficients excluded): {sorted(notwp, reverse=True)[:3]}")
print(f"  weight_profile up to 4 LT (120 steps): {max(wp4)}; all weight_profile: {max(x for x in cont if 'weight_profile' in x[1])}")
print(f"  discrete-event leaves (gain_bound): {sorted([x for x in n2 + n3 if 'gain_bound' in x[1]], reverse=True)[:3]}")
