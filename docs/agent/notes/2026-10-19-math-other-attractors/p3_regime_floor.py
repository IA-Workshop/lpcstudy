"""Numerical check of Theorem P3 (a) and (b), and of the sharpened floor.

(a) The regime weight clip(sum c_i u_i / sum c_i) is compared with a brute
    force minimiser of sum_i V_i(w) over a 1e-6 grid on [0, 1], on random
    regimes, including regimes where every u_i is above 1 or below 0 (where
    the clipped-mean rule of DEF-0003 was wrong) with float64 moments.
(b) The measurability floor: for a finite profile F with cells, the best
    F-measurable rule is found by brute force per cell and compared with
    clip(ubar(F)); the inequality E[V(f(F))] >= E[V(clip ubar)] is checked for
    1000 random F-measurable rules; the floor E[V(clip ubar)] - E[V(w*)] is
    computed and shown to be exactly 0 on cells where w* (not u) is constant.
(c) What the code's `regime_regret` ignores: for a rule whose weight depends
    on the SAME draw as the errors (deployable A3/A4/A5), the plug-in
    V_i(w_d) averaged over draws differs from the true E[(w_d e_C,d + (1-w_d)
    e_P,d)^2] by the dependence term h_i (the kappa_E note R2). A synthetic
    example quantifies the size; the P3(b) floor itself is unaffected (it is a
    statement about sigma-algebras), but the K-selection rule and the reported
    excess MSE use the plug-in.

DEVELOPMENT, scratch seed 20261019, numpy only.
"""

import numpy as np

rng = np.random.default_rng(20261019)


def moments(n, mode):
    ec = rng.lognormal(-4, 1, n)
    ep = rng.lognormal(-4, 1, n)
    corr = rng.uniform(-0.3, 0.95, n)
    c = corr * np.sqrt(ec * ep)
    if mode == "above":  # all u > 1: need E_C < C <= sqrt(E_C E_P), so E_P >= (C/E_C)^2 E_C
        ep = ec * 4.0
        c = ec * rng.uniform(1.05, 1.5, n)
    if mode == "below":  # all u < 0: need E_P < C <= sqrt(E_C E_P)
        ec = ep * 4.0
        c = ep * rng.uniform(1.05, 1.5, n)
    assert (c**2 <= ec * ep * (1 + 1e-12)).all()
    return ec, ep, c


def V(w, ec, ep, c):
    return w**2 * ec + (1 - w) ** 2 * ep + 2 * w * (1 - w) * c


grid = np.linspace(0, 1, 1_000_001)
worst = 0.0
for mode in ("free", "above", "below", "mixed"):
    for _ in range(50):
        ec, ep, c = moments(12, mode if mode != "mixed" else "free")
        if mode == "mixed":
            ec2, ep2, c2 = moments(6, "above")
            ec, ep, c = np.concatenate([ec[:6], ec2]), np.concatenate([ep[:6], ep2]), np.concatenate([c[:6], c2])
        curv = ec + ep - 2 * c
        b = ep - c
        u = b / curv
        rule = np.clip(b.sum() / curv.sum(), 0, 1)
        total = sum(V(grid, ec[i], ep[i], c[i]) for i in range(len(ec)))
        brute = grid[np.argmin(total)]
        worst = max(worst, abs(rule - brute))
        if mode in ("above", "below"):
            assert (u > 1).all() if mode == "above" else (u < 0).all(), mode
print(f"(a) P3(a) regime weight vs brute force (grid 1e-6): worst |difference| = {worst:.2e}  (tolerance 1e-6)")

# (b) measurability floor
n = 4000
F = rng.integers(0, 8, n)  # 8 cells
ec, ep, c = moments(n, "free")
# make cells 0 and 1 'all above 1' (w* = 1 constant, u varies) to show a zero floor
above = (F <= 1)
ec_a, ep_a, c_a = moments(above.sum(), "above")
ec[above], ep[above], c[above] = ec_a, ep_a, c_a
curv = ec + ep - 2 * c
b = ep - c
u = b / curv
wstar = np.clip(u, 0, 1)
v_star = V(wstar, ec, ep, c).mean()
ubar = np.array([b[F == k].sum() / curv[F == k].sum() for k in range(8)])
f_bar = np.clip(ubar, 0, 1)[F]
v_bar = V(f_bar, ec, ep, c).mean()
# brute force best F-measurable rule, cell by cell
best = np.zeros(8)
for k in range(8):
    tot = sum(V(grid, ec[i], ep[i], c[i]) for i in np.nonzero(F == k)[0][:400])  # subset for speed
    best[k] = grid[np.argmin(tot)]
print(f"(b) P3(b): clip(ubar) per cell vs brute-force best F-measurable rule (first 400 states per cell):")
print("    cell  clip(ubar)  brute   |diff|")
for k in range(8):
    # recompute ubar on the same subset
    idx = np.nonzero(F == k)[0][:400]
    ub = np.clip(b[idx].sum() / curv[idx].sum(), 0, 1)
    print(f"    {k:3d}   {ub:.6f}  {best[k]:.6f}  {abs(ub-best[k]):.1e}")
viol = 0
for _ in range(1000):
    f = rng.random(8)[F]
    if V(f, ec, ep, c).mean() < v_bar - 1e-15:
        viol += 1
print(f"    random F-measurable rules beating clip(ubar): {viol} of 1000 (expected 0)")
floor_cell = np.array([
    (V(f_bar, ec, ep, c) - V(wstar, ec, ep, c))[F == k].mean() for k in range(8)
])
print("    floor per cell (E[V(clip ubar)] - E[V(w*)]):", np.array2string(floor_cell, precision=3))
print(f"    cells 0,1 have u in ({u[above].min():.2f}, {u[above].max():.2f}) not F-measurable, "
      f"yet w* = 1 there and the floor is exactly {floor_cell[:2].max():.1e}: the floor is zero iff w* "
      f"(the clipped optimum) is F-measurable, not u")
print(f"    overall floor E[V(clip ubar)] - E[V(w*)] = {v_bar - v_star:.4e}, relative to E[V(w*)] = {(v_bar - v_star)/v_star:.3f}")

# (c) the plug-in V_i(w_d) versus the true draw-dependent MSE
Md = 2000
n2 = 300
ec, ep, c = moments(n2, "free")
L = np.linalg.cholesky(np.array([[1.0, 0.0], [0.0, 1.0]]))
errs_c = np.sqrt(ec)[:, None] * rng.standard_normal((n2, Md))
rho_cp = c / np.sqrt(ec * ep)
errs_p = np.sqrt(ep)[:, None] * (rho_cp[:, None] * errs_c / np.sqrt(ec)[:, None] + np.sqrt(1 - rho_cp**2)[:, None] * rng.standard_normal((n2, Md)))
# a 'deployable' rule that sees the draw's own |e_C| (like R in A4: larger analog error -> less CP)
w_d = 1 / (1 + (errs_c**2) / ep[:, None])
true_mse = ((w_d * errs_c + (1 - w_d) * errs_p) ** 2).mean(axis=1)
plug = V(w_d, ec[:, None], ep[:, None], c[:, None]).mean(axis=1)
print(f"(c) draw-dependent rule: mean true MSE {true_mse.mean():.4e}, mean plug-in V_i(w_d) {plug.mean():.4e}, "
      f"relative gap {(plug.mean()-true_mse.mean())/true_mse.mean():+.3f} (the h_i term; zero for draw-constant rules)")
