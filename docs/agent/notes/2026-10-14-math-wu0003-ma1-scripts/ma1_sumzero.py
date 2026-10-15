"""MA-1 check 4: sum_j A_j = 0 (the fitted exponent is invariant to a common factor of the medians:
g(x; a + t, b, c + t) = g(x; a, b, c) + t exactly). DEVELOPMENT (DEV-0 pilot medians, read-only)."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ma1_core as mc
worst = 0.0
for path in sys.argv[1:]:
    A_ = json.load(open(path))
    for system, blk in A_["systems"].items():
        for rho, b in blk["H1a"]["by_noise"].items():
            sizes = np.array(sorted(int(k) for k in b["median_seed_by_n_lib"]), float)
            med = np.array([b["median_seed_by_n_lib"][str(int(n))] for n in sizes]) ** 2
            th = mc.fit_tight(sizes, med, x0=mc.fit_prod(sizes, med))
            D, cond, _ = mc.dtheta_dy(sizes, med, th)
            A = 0.5 * D[1]
            r = abs(A.sum()) / np.abs(A).max()
            # fit invariance itself: medians x 7.3 -> same exponent
            th7 = mc.fit_tight(sizes, 7.3 * med, x0=th + np.array([np.log(7.3), 0, np.log(7.3)]))
            worst = max(worst, r)
            print(f"{Path(path).parts[-3][:2]} {system:8s} {rho}  |sum A|/max|A| {r:.2e}  "
                  f"cond(H) {cond:.1e}  |b(7.3 m) - b(m)| {abs(th7[1] - th[1]):.1e}")
print(f"max |sum A|/max|A| = {worst:.2e}")
