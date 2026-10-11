"""Fast exact re-formulations of the WU-0006 statistics on moving-block resamples (scratch, AM)."""
import numpy as np

BLOCK = 5


def ar1(rng, n, phi, k=1, c=0.0):
    """Stationary (bi)variate AR(1), unit variance, common phi, lag-0 cross-corr c (k=2)."""
    if k == 1:
        e = rng.standard_normal(n)
    else:
        z = rng.standard_normal((n, 2))
        e = np.column_stack([z[:, 0], c * z[:, 0] + np.sqrt(1 - c * c) * z[:, 1]])
    x = np.empty_like(e)
    x[0] = e[0]
    s = np.sqrt(1 - phi * phi)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + s * e[t]
    return x


def starts(rng, B, n):
    return rng.integers(0, n - BLOCK + 1, (B, int(np.ceil(n / BLOCK))))


def idx_from(st, n):
    return (st[:, :, None] + np.arange(BLOCK)).reshape(st.shape[0], -1)[:, :n]


def block_sums(x):
    c = np.concatenate([[0.0], np.cumsum(x)])
    return c[BLOCK:] - c[:-BLOCK]


def mult(idx, n):
    B = idx.shape[0]
    return np.bincount((idx + n * np.arange(B)[:, None]).ravel(), minlength=B * n).reshape(B, n)


def avg_ranks(m, x):
    o = np.argsort(x)
    mo = m[:, o].astype(float)
    r = np.cumsum(mo, axis=1) - mo + (mo + 1) / 2
    out = np.empty_like(r)
    out[:, o] = r
    return out


def spearman_w(m, a, b):
    ra, rb = avg_ranks(m, a), avg_ranks(m, b)
    n = m.sum(1, keepdims=True)
    mu_a = (m * ra).sum(1, keepdims=True) / n
    mu_b = (m * rb).sum(1, keepdims=True) / n
    da, db = ra - mu_a, rb - mu_b
    return (m * da * db).sum(1) / np.sqrt((m * da * da).sum(1) * (m * db * db).sum(1))


def partial_w(m, t, v, Q):
    n = len(t)
    Z = np.column_stack([np.ones(n), Q, t, v])
    p = Z.shape[1]
    G = (m @ (Z[:, :, None] * Z[:, None, :]).reshape(n, p * p)).reshape(-1, p, p)
    Gxx, Gxy, Gyy = G[:, :-2, :-2], G[:, :-2, -2:], G[:, -2:, -2:]
    S = Gyy - np.einsum('bki,bkj->bij', Gxy, np.linalg.solve(Gxx, Gxy))
    return S[:, 0, 1] / np.sqrt(S[:, 0, 0] * S[:, 1, 1])


def quad(s):
    s = s - s.mean(0)
    return np.column_stack([s[:, 0], s[:, 1], s[:, 0] ** 2, s[:, 1] ** 2, s[:, 0] * s[:, 1]])
