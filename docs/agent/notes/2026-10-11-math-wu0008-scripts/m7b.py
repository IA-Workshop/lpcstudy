"""M7 with the WU-0006 reference rates (math note 2026-10-11-math-wu0006.md, R_ref 1e4-4e4) at 1 - 0.05/3."""
from statistics import NormalDist
N = NormalDist(); L = 1 - 0.05/3; z_nom = N.inv_cdf((1+L)/2)
def sf(p, se):
    z = N.inv_cdf((1+p)/2); se_z = se/(2*N.pdf(z)); return z_nom/z - 1, z_nom/z**2*se_z
ref = {"C3 phi0": (0.9807, 0.0010), "C3 phi0.3": (0.9732, 0.0011),
       "C7 phi0": (0.9794, 0.0010), "C7 phi0.3": (0.9762, 0.0011),
       "C1 phi0": (0.9800, 0.0007), "C1 phi0.3": (0.9695, 0.0009),
       "C8 phi0": (0.9806, 0.0007), "C8 phi0.3": (0.9682, 0.0009),
       "C4 phi0": (0.9772, 0.0007), "C4 phi0.3": (0.9715, 0.0008),
       "C4h s1.5 phi0": (0.9744, 0.0011), "C4h s2 phi0": (0.9669, 0.0013)}
for k, (p, se) in ref.items():
    f, sef = sf(p, se); print(f"{k:14s} p_ref {p:.4f} ({se}) shortfall {f:+.4f} +- {sef:.4f}")
