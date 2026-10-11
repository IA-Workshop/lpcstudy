"""M1: bounds, count thresholds and exact binomial false-alarm probabilities at nominal p."""
import math
from scipy import stats
rows = [  # name, nominal p, R, side ('ge' coverage-type lower bound, 'le' rate upper bound), roadmap rounded
    ("A1 cov95", 0.95, 1000, "ge", 0.929),
    ("A2 cov98.3", 1 - 0.05/3, 1000, "ge", 0.971),
    ("A3 edge 95", 0.025, 1000, "le", None),
    ("A3 edge 98.3", 0.05/6, 1000, "le", None),
    ("L1/L2 FWER", 0.01, 2000, "le", 0.0167),
    ("N1 N3 cov95", 0.95, 500, "ge", 0.921),
    ("N2 lower>0", 0.025, 500, "le", None),
]
for name, p, R, side, rnd in rows:
    se = math.sqrt(p*(1-p)/R)
    f = p - 3*se if side == "ge" else p + 3*se
    if side == "ge":
        b = max(f, rnd) if rnd else f
        kmin = math.ceil(b*R - 1e-12)  # pass iff count >= kmin
        alarm = stats.binom.cdf(kmin-1, R, p)
        kf = math.ceil(f*R-1e-12); kr = math.ceil(rnd*R-1e-12) if rnd else None
        print(f"{name:14s} p={p:.6f} R={R} SE={se:.6f} formula={f:.6f} rounded={rnd} bound={b:.6f} "
              f"pass iff count>={kmin} (formula {kf}, rounded {kr}) P(spurious fail at nominal)={alarm:.5f}")
    else:
        b = min(f, rnd) if rnd else f
        kmax = math.floor(b*R + 1e-12)
        alarm = stats.binom.sf(kmax, R, p)
        kf = math.floor(f*R+1e-12); kr = math.floor(rnd*R+1e-12) if rnd else None
        print(f"{name:14s} p={p:.6f} R={R} SE={se:.6f} formula={f:.6f} rounded={rnd} bound={b:.6f} "
              f"pass iff count<={kmax} (formula {kf}, rounded {kr}) P(spurious fail at nominal)={alarm:.5f}")
