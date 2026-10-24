"""E5: candidate "stored value from a different estimator" (maximum field).

The Dysts code that wrote ``maximum_lyapunov_estimated`` was not read (note
A.5). This script does not reproduce it. It tests whether two standard
short-time quantities that are known to exceed lambda_1 reach the stored
values with one setting applied to all three systems:
(1) Rosenstein (1993) nearest-neighbour divergence on the full state,
    100 samples per Dysts period, 10 000 samples after a 500-period transient,
    Theiler window one period, slope of the mean log distance over the first
    K samples, K in {5, 10, 20, 40, 100} (grid fixed before running);
(2) orbit means of the largest eigenvalue of the symmetric part (J + J^T)/2
    and of the largest real part of the eigenvalues of J.
Stored Dysts values (note A.2): maximum 0.89171 / 0.150597 / 1.230116;
spectrum[0] 1.09109 / 0.076330 / 0.460547; periods 1.5008 / 5.9086 / 1.4235.
Benettin values (pilot_results_v3_dev0_reference.json): 0.905494 /
0.0719398 / 0.431133. Start states: Lorenz (1, 1, 1), Rossler (1, 1, 0),
Chua (0.7, 0, 0).
"""
import json, numpy as np
from scipy.spatial import cKDTree
from chua_np import DYSTS, field as chua_f, jac as chua_j

def lor_f(s, p=None):
    x, y, z = s[:, 0], s[:, 1], s[:, 2]
    return np.stack([10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z], axis=1)
def lor_j(s):
    x, y, z = s[:, 0], s[:, 1], s[:, 2]; n = len(x); J = np.zeros((n, 3, 3))
    J[:, 0, 0] = -10; J[:, 0, 1] = 10; J[:, 1, 0] = 28 - z; J[:, 1, 1] = -1; J[:, 1, 2] = -x
    J[:, 2, 0] = y; J[:, 2, 1] = x; J[:, 2, 2] = -8 / 3; return J
def ros_f(s, p=None):
    x, y, z = s[:, 0], s[:, 1], s[:, 2]
    return np.stack([-y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)], axis=1)
def ros_j(s):
    x, y, z = s[:, 0], s[:, 1], s[:, 2]; n = len(x); J = np.zeros((n, 3, 3))
    J[:, 0, 1] = -1; J[:, 0, 2] = -1; J[:, 1, 0] = 1; J[:, 1, 1] = 0.2; J[:, 2, 0] = z; J[:, 2, 2] = x - 5.7
    return J
systems = {
    "lorenz63": (lambda s: lor_f(s), lor_j, 1.5008, 0.002, (1.0, 1.0, 1.0), 0.89171, 1.09109, 0.905494),
    "rossler": (lambda s: ros_f(s), ros_j, 5.9086, 0.01, (1.0, 1.0, 0.0), 0.150597, 0.076330, 0.0719398),
    "chua": (lambda s: chua_f(s, DYSTS), lambda s: chua_j(s, DYSTS), 1.4235, 0.002, (0.7, 0.0, 0.0), 1.230116, 0.460547, 0.431133),
}
def rk4(f, s, h):
    k1 = f(s); k2 = f(s + 0.5 * h * k1); k3 = f(s + 0.5 * h * k2); k4 = f(s + h * k3)
    return s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
Ks = [5, 10, 20, 40, 100]
out = {}
for name, (f, jf, period, hmax, s0, dmax, dspec, ours) in systems.items():
    delta = period / 100
    sub = int(np.ceil(delta / hmax)); h = delta / sub
    s = np.array([s0], dtype=float)
    for _ in range(500 * 100 * sub):
        s = rk4(f, s, h)
    n = 10000 + 200
    traj = np.zeros((n, 3))
    for i in range(n):
        traj[i] = s[0]
        for _ in range(sub):
            s = rk4(f, s, h)
    # Rosenstein
    base = traj[:10000]
    tree = cKDTree(base)
    dist, idx = tree.query(base, k=60)
    theiler = 100
    nn = np.full(10000, -1)
    for i in range(10000):
        for d_, j in zip(dist[i, 1:], idx[i, 1:]):
            if abs(j - i) > theiler and d_ > 0:
                nn[i] = j; break
    good = np.where(nn >= 0)[0]
    kmax = 100
    curve = np.zeros(kmax + 1)
    for k in range(kmax + 1):
        dk = np.linalg.norm(traj[good + k] - traj[nn[good] + k], axis=1)
        curve[k] = np.mean(np.log(dk[dk > 0]))
    slopes = {K: float(np.polyfit(np.arange(K + 1), curve[: K + 1], 1)[0] / delta) for K in Ks}
    J = jf(base)
    sym_max = np.linalg.eigvalsh(0.5 * (J + np.transpose(J, (0, 2, 1))))[:, -1].mean()
    re_max = np.linalg.eigvals(J).real.max(axis=1).mean()
    div = np.trace(J, axis1=1, axis2=2).mean()
    out[name] = {"rosenstein_slopes": slopes, "n_pairs": int(good.size), "mean_sym_max": float(sym_max),
                 "mean_re_eig_max": float(re_max), "mean_div": float(div), "dysts_max": dmax, "dysts_spec0": dspec, "benettin": ours}
    print(name, "pairs", good.size, "| Rosenstein slope by K:", {K: round(v, 4) for K, v in slopes.items()},
          "| ratio to Benettin:", {K: round(v / ours, 3) for K, v in slopes.items()})
    print("   mean max eig sym(J)", round(float(sym_max), 4), " mean max Re eig(J)", round(float(re_max), 4), " mean div", round(float(div), 4),
          " | Dysts max", dmax, "ratio Dysts max / Benettin", round(dmax / ours, 3), flush=True)
json.dump(out, open("e5_divergence_estimators.json", "w"), indent=1)
