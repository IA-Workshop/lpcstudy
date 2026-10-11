"""M7: half-width shortfall from measured two-sided coverage (WU-0006 run 2, R = 1000)."""
from statistics import NormalDist
from math import sqrt
N = NormalDist(); R = 1000
def shortfall(count, level):
    p = count / R
    z_nom = N.inv_cdf((1 + level) / 2); z_obs = N.inv_cdf((1 + p) / 2)
    se_p = sqrt(p * (1 - p) / R)
    se_z = se_p / (2 * N.pdf(z_obs))
    f = z_nom / z_obs - 1
    se_f = z_nom / z_obs**2 * se_z
    return p, se_p, z_obs, f, se_f
L = 1 - 0.05 / 3
cases = {"C3 (H2a(i))": (984, 973), "C7 (H2a(ii) interior)": (972, 977), "C1 (n=500 mean)": (983, 969),
         "C8 (H2b(ii); H2b(i) proposed)": (987, 972), "C4 (H3c)": (971, 961)}
for name, (c0, c3) in cases.items():
    for phi, c in (("0", c0), ("0.3", c3)):
        p, sp, z, f, sf = shortfall(c, L)
        print(f"{name:32s} phi {phi:3s}: p {p:.3f} +- {sp:.4f}; z_obs {z:.3f} (nom {N.inv_cdf((1+L)/2):.3f}); shortfall {f:+.3f} +- {sf:.3f}")
for name, c in (("C4h sigma 1.5, phi 0", 965), ("C4h sigma 2, phi 0", 984)):
    p, sp, z, f, sf = shortfall(c, L)
    print(f"{name:32s}: p {p:.3f} +- {sp:.4f}; shortfall {f:+.3f} +- {sf:.3f}")
# sanity: 10% shortfall corresponds to coverage
for frac in (0.05, 0.10):
    z = N.inv_cdf((1+L)/2)/(1+frac); print(f"shortfall {frac:.2f} <=> coverage {2*N.cdf(z)-1:.4f}")
