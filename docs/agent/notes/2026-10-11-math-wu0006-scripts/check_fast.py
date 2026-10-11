import sys, numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[4]))  # repo root
from lpcstudy.statistics import block_resample_indices, spearman, partial_correlation
from lpcstudy.analysis import quadratic_controls
from simcore import *
rng = np.random.default_rng(1)
n = 500
x = ar1(rng, n, 0.3, 2, 0.716736)
idx = np.stack(list(block_resample_indices(n, 50, 5, 123)))
st = np.random.default_rng(123).integers(0, n - 4, (50, 100))
print("index semantics equal:", np.array_equal(idx, idx_from(st, n)))
m = mult(idx, n)
sp_fast = spearman_w(m, x[:, 0], x[:, 1])
sp_prod = np.array([spearman(x[i, 0], x[i, 1]) for i in idx])
print("spearman max diff", np.abs(sp_fast - sp_prod).max())
s = ar1(rng, n, 0.3, 2, 0.0); e = ar1(rng, n, 0.3, 2, 0.1)
t = 0.5 * s[:, 0] - 0.3 * s[:, 1] ** 2 + e[:, 0]; v = 0.4 * s[:, 1] + 0.2 * s[:, 0] * s[:, 1] + e[:, 1]
Q = quadratic_controls(s)
pc_fast = partial_w(m, t, v, Q)
pc_prod = np.array([partial_correlation(t[i], v[i], Q[i]) for i in idx])
print("partial max diff", np.abs(pc_fast - pc_prod).max(), np.allclose(Q, quad(s)))
bs = block_sums(x[:, 0])
print("mean via block sums diff", np.abs(bs[st].sum(1) / n - x[idx, 0].mean(1)).max())
