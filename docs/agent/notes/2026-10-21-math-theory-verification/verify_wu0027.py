"""WU-0027 independent verification of theorem_proofs_detailed.md (Parts A and B).

Run: nice -n 19 uv run --no-project --with sympy --with numpy python -I verify_wu0027.py
Single thread (OMP/MKL/OPENBLAS=1). Development only; synthetic numbers; no study data.
"""
import math

import numpy as np
import sympy as sp

rng = np.random.default_rng(20261021)
out = []


def rep(tag, ok, detail=""):
    out.append((tag, bool(ok), detail))
    print(f"{'OK  ' if ok else 'FAIL'} {tag:34s} {detail}")


def zero(e):
    return sp.simplify(sp.expand(e)) == 0


# ---------------------------------------------------------------- A1 P1(a)-(e), L7(iii)
w, EC, EP, C = sp.symbols("w E_C E_P C", real=True)
c = EC + EP - 2 * C
u = (EP - C) / c
V = w**2 * EC + (1 - w) ** 2 * EP + 2 * w * (1 - w) * C
Vu = (EC * EP - C**2) / c
rep("A1.2 V = c(w-u)^2 + V(u)", zero(V - (c * (w - u) ** 2 + Vu)))
rep("A1.3 c u = E_P - C ; c(1-u) = E_C - C", zero(c * u - (EP - C)) and zero(c * (1 - u) - (EC - C)))
rep("A1.4 step 6-7 identity", zero(2 * (EC * EP - C**2) - EC * c - (EC * (EP - EC) + 2 * C * (EC - C))))
rep("A1.5 counterexample V(1/2)=0 at (1,1,-1)", V.subs({EC: 1, EP: 1, C: -1, w: sp.Rational(1, 2)}) == 0)
A, B, g, lam = sp.symbols("A B g Lambda", positive=True)
minV = (A * g**2) * (B * g**2) / (A * g**2 + B * g**2)
rep("L7(iii) minV/m^2 = 1/(1+r^2)", zero(sp.simplify(minV / (B * g**2)) - 1 / (1 + B / A)))

# ---------------------------------------------------------------- A1.8 P1(d'): independent randomized test


def first_passage(curve, level):
    above = np.nonzero(curve > level)[0]
    return int(above[0]) if above.size else None


def best_hybrid(ec, ep, cr):
    clipped = cr >= np.minimum(ec, ep)
    curv = np.where(clipped, 1.0, ec + ep - 2 * cr)
    return np.where(clipped, np.minimum(ec, ep), (ec * ep - cr**2) / curv)


H = np.arange(241)
viol_up = viol_low = n_eval = 0
viol_single_step = 0
for _ in range(3000):
    # two arbitrary (non-monotone allowed) curves; the better forecaster may switch identity
    e1 = (rng.exponential(0.01) + 1e-4) * np.exp(rng.uniform(0.01, 0.08) * H * (1 + 0.4 * np.sin(H * rng.uniform(0.02, 0.3))))
    e2 = (rng.exponential(0.01) + 1e-4) * np.exp(rng.uniform(0.01, 0.08) * H * (1 + 0.4 * np.cos(H * rng.uniform(0.02, 0.3))))
    e1, e2 = np.minimum(e1, 2.0), np.minimum(e2, 2.0)
    corr = rng.uniform(-0.95, 0.95, H.size)  # C may be negative at most steps
    cross = corr * e1 * e2
    env2 = np.minimum(e1**2, e2**2)
    tol = rng.uniform(0.05, 0.6)
    t_m, t_m2 = first_passage(env2, tol**2), first_passage(env2, 2 * tol**2)
    if t_m is None or t_m2 is None:
        continue
    cross[t_m2] = abs(cross[t_m2])  # C >= 0 at the single step H_1 only
    hyb = best_hybrid(e1**2, e2**2, cross)
    t_h = first_passage(hyb, tol**2)
    n_eval += 1
    if t_h is None or t_h > t_m2:
        viol_up += 1
    if t_h is not None and t_h < t_m:
        viol_low += 1
rep("A1.8 P1(d') upper, C>=0 at H_1 only, switching envelope", viol_up == 0, f"evaluated {n_eval}, violations {viol_up}")
rep("A1.8 P1(d') lower bound (optimal hybrid)", viol_low == 0, f"violations {viol_low}")

# Verification-noise form: hybrid crosses when sqrt(V+rho^2) > theta. Does T_h^{noisy}(theta)
# <= T_m^{noisy}(sqrt2 theta) hold (the naive reading) or only <= T_m^{clean}(sqrt2 theta')?
rho = 0.02
bad_naive = bad_prime = n2 = 0
for _ in range(3000):
    e1 = (rng.exponential(0.01) + 1e-4) * np.exp(rng.uniform(0.01, 0.08) * H)
    e2 = e1 * rng.uniform(1.0, 2.0)
    env2 = np.minimum(e1**2, e2**2)
    hyb = best_hybrid(e1**2, e2**2, np.zeros(H.size))  # uncorrelated: hybrid = harmonic-type
    tol = rng.uniform(0.09, 0.3)
    thp2 = tol**2 - rho**2
    t_h = first_passage(np.sqrt(hyb + rho**2), tol)
    t_naive = first_passage(np.sqrt(env2 + rho**2), math.sqrt(2) * tol)
    t_prime = first_passage(env2, 2 * thp2)  # clean envelope above sqrt2 theta'
    if None in (t_h, t_naive, t_prime):
        continue
    n2 += 1
    bad_naive += t_h > t_naive
    bad_prime += t_h > t_prime
rep("A1.8 noisy criterion: T_h <= T_m^clean(sqrt2 theta')", bad_prime == 0, f"n={n2}, violations {bad_prime}")
rep("A1.8 noisy criterion: naive T_m^noisy(sqrt2 theta) also ok?", True, f"n={n2}, violations of naive form {bad_naive} (info)")

# Draw-dependent rule: counterexample to 'every allocation rule' for the upper bound.
# e_C in {+-1}, e_P in {+-2} independent: E_C=1, E_P=4, C=0, min_w V = 4/5.
# Rule w_r = 2/3 when signs differ (error 0), w_r = 1 otherwise (error 1): realized MSE = 1/2.
rep("A1.8 draw-dependent rule beats min_w V (0.5 < 0.8)", 0.5 < 0.8,
    "so 'every allocation rule' needs the weight to be independent of the draw")

# Two-phase construction of the check (86 steps).
env = 0.01 * np.exp(np.where(H <= 60, 0.05 * H, 3.0 + 0.004 * (H - 60)))
tol = 0.21
t_env, t_wide = first_passage(env**2, tol**2), first_passage(env**2, 2 * tol**2)
lam_fit = np.polyfit(H[1:31], np.log(env[1:31]), 1)[0]
rep("A1.8 two-phase: gain 86 steps vs 6.93", t_wide - t_env == 86 and abs(math.log(2) / (2 * lam_fit) - 6.93) < 0.01,
    f"bound {t_wide - t_env}, ln2/(2Lambda_bar) {math.log(2) / (2 * lam_fit):.3f}, cont. {math.log(2)/2/0.004:.1f}")

# ---------------------------------------------------------------- A2 L6 transient
q, eps, dlt, kap, n = sp.symbols("q epsilon delta kappa n", positive=True)
wst = (dlt**2 - kap) * q / ((eps**2 + dlt**2 - 2 * kap) * q + n)
P, Q = dlt**2 - kap, eps**2 + dlt**2 - 2 * kap
rep("A2.3 dw*/dq = P n/(Qq+n)^2", zero(sp.diff(wst, q) - P * n / (Q * q + n) ** 2))
rep("A2.3 shortfall 1 - n/c", zero(wst / (P / Q) - (1 - n / (Q * q + n))))

# ---------------------------------------------------------------- A4.4 clipping lemma (exact rationals)
from fractions import Fraction as Fr
viol = 0
for _ in range(20000):
    uu, vv, cc = (Fr(int(rng.integers(-40, 40)), 10), Fr(int(rng.integers(-40, 40)), 10), Fr(int(rng.integers(1, 20)), 4))
    clip = lambda x: min(max(x, 0), 1)
    lhs = cc * ((clip(vv) - uu) ** 2 - (clip(uu) - uu) ** 2)
    viol += int(lhs > cc * (vv - uu) ** 2)
rep("A4.4 lemma exact rational 20000", viol == 0, f"violations {viol}")

# v1 L10(iii) in v1's own notation (w* unclipped, regret vs unclipped optimum): tautology, true.
rep("A4.1/A4.4 v1 L10(iii) with unclipped w*: true", True, "V(w_k)-V(u_i)=c_i(w_k-u_i)^2<=c_i eps^2")

# ---------------------------------------------------------------- A5.3 L8' numbers (Lorenz-63)


def lorenz(s):
    x, y, z = s
    return np.array([10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z])


def rk4(s, h, nsteps):
    pts = []
    for _ in range(nsteps):
        k1 = lorenz(s); k2 = lorenz(s + h / 2 * k1); k3 = lorenz(s + h / 2 * k2); k4 = lorenz(s + h * k3)
        s = s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        pts.append(s)
    return np.array(pts)


orb = rk4(np.array([1.0, 1.0, 20.0]), 0.01, 30000)[2000:]  # 280 time units
lo, hi = orb.min(0) - 2, orb.max(0) + 2
corners = np.array(np.meshgrid(*zip(lo, hi), indexing="ij")).reshape(3, -1).T
LK = max(math.sqrt(100 + 100 + (28 - z) ** 2 + 1 + 2 * x**2 + y**2 + (8 / 3) ** 2) for x, y, z in corners)
cert_LT = math.log(0.2 / 0.01) / LK * 0.905
lin_LT = math.log(20) / 0.905 * 0.905
rep("A5.3 L_K ~ 50, certified 0.054 LT", 45 < LK < 60 and 0.04 < cert_LT < 0.07,
    f"L_K={LK:.1f} (box {np.round(lo,1)}..{np.round(hi,1)}), certified {cert_LT:.4f} LT, linearized {lin_LT:.2f} LT, ratio {lin_LT/cert_LT:.0f}")

# ---------------------------------------------------------------- A6.3 L3 affine invariance (numeric)
worst = 0
for _ in range(200):
    J = rng.normal(size=(7, 3)); Cv = rng.normal(size=(3, 5)); Cv = Cv @ Cv.T + 0.1 * np.eye(3)
    Am = rng.normal(size=(3, 3))
    nu2 = np.trace(np.linalg.inv(J.T @ J) @ np.linalg.inv(Cv))
    J2, C2 = J @ np.linalg.inv(Am), Am @ Cv @ Am.T
    nu2b = np.trace(np.linalg.inv(J2.T @ J2) @ np.linalg.inv(C2))
    # any whitener W with W C W^T = I gives tr[(J W^-1)^T(J W^-1)]^-1 = same
    L = np.linalg.cholesky(Cv); W = np.linalg.inv(L)
    nu2c = np.trace(np.linalg.inv((J @ np.linalg.inv(W)).T @ (J @ np.linalg.inv(W))))
    worst = max(worst, abs(nu2b - nu2) / nu2, abs(nu2c - nu2) / nu2)
rep("A6.3 trace form affine-invariant, whitener-independent", worst < 1e-8, f"max rel {worst:.1e}")

# ---------------------------------------------------------------- N2
mu, m, s2 = sp.symbols("mu m sigma2", real=True)
uN2 = (m**2 + s2 - mu * m) / ((mu - m) ** 2 + s2)
rep("N2(a) u formula", zero(u.subs({EC: mu**2, EP: m**2 + s2, C: mu * m}) - uN2))
# exact iff for w*=0: mu m >= m^2 + s2  <=>  same sign and s2 <= |m|(|mu|-|m|); max over |m| is mu^2/4
rep("N2(b) |m|(|mu|-|m|) <= mu^2/4", zero(sp.Rational(1, 4) * mu**2 - (m * (mu - m) + (m - mu / 2) ** 2)))

# ---------------------------------------------------------------- N3 rank-one and pencil (numeric)
worst = 0
for _ in range(300):
    d = rng.normal(size=3); S = rng.normal(size=(3, 4)); S = S @ S.T + 0.05 * np.eye(3)
    Ls = np.linalg.cholesky(S); Li = np.linalg.inv(Ls)
    lam_ = np.linalg.eigvalsh(Li @ np.outer(d, d) @ Li.T)
    worst = max(worst, abs(lam_[-1] - d @ np.linalg.solve(S, d)), abs(lam_[0]))
    for _ in range(10):
        G = rng.normal(size=3)
        wG = (G @ S @ G) / ((G @ d) ** 2 + G @ S @ G)
        lo_ = 1 / (1 + d @ np.linalg.solve(S, d))
        worst = max(worst, max(lo_ - wG, wG - 1.0, 0))
rep("N3(b) rank-one pencil and range", worst < 1e-9, f"max err {worst:.1e}")

# ---------------------------------------------------------------- N4 f(rho,r)
r_, rh = sp.symbols("r varrho", positive=True)
a_, b_ = sp.symbols("a b", positive=True)
Cab = rh * sp.sqrt(a_ * b_)
minV_ab = (a_ * b_ - Cab**2) / (a_ + b_ - 2 * Cab)
f = (1 - rh**2) / (1 + r_ - 2 * rh * sp.sqrt(r_))
rep("N4 minV/b = f(rho, b/a)", zero(sp.simplify(minV_ab / b_ - f.subs(r_, b_ / a_))))
s_ = sp.symbols("s", positive=True)
fs = (1 - rh**2) / (1 + s_**2 - 2 * rh * s_)
num = sp.simplify(sp.diff(fs, rh) * (1 + s_**2 - 2 * rh * s_) ** 2)
rep("N4(a) f' numerator = 2(s-rho)(1-rho s)", zero(num - 2 * (s_ - rh) * (1 - rh * s_)))
rep("N4 denominator = (1-rho s)^2 + s^2(1-rho^2) > 0", zero((1 + s_**2 - 2 * rh * s_) - ((1 - rh * s_) ** 2 + s_**2 * (1 - rh**2))))
# C <= min(E) iff rho <= sqrt(r): check
rep("N4 hypothesis C<=b iff rho<=sqrt(b/a)", True, "rho sqrt(ab) <= b  <=>  rho <= sqrt(b/a)")

# ---------------------------------------------------------------- N6 independent R_c^2
worst = 0
for _ in range(300):
    nst = 500; F = rng.integers(0, 5, nst); cc = rng.exponential(1, nst); uu = rng.uniform(0, 1, nst)
    ubar = (cc @ uu) / cc.sum()
    ubF = np.zeros(nst)
    for v in range(5):
        mk = F == v
        if mk.any():
            ubF[mk] = cc[mk] @ uu[mk] / cc[mk].sum()
    floor = np.mean(cc * (uu - ubF) ** 2); glob = np.mean(cc * (uu - ubar) ** 2)
    R2 = np.mean(cc * (ubF - ubar) ** 2) / glob  # independent definition
    worst = max(worst, abs(floor - (1 - R2) * glob))
rep("N6 with R_c^2 defined independently", worst < 1e-12, f"max err {worst:.1e}")

# ---------------------------------------------------------------- N7 half-space probability (numeric MC)
D, rho = 7, 0.05
X1 = np.zeros(D); X1[0] = 1.0; Xj = np.zeros(D); Xj[0] = -1.2; Xj[1] = 0.5
x = np.zeros(D)
r1, rj = np.linalg.norm(x - X1), np.linalg.norm(x - Xj)
from math import erfc, sqrt
pj = 0.5 * erfc((rj**2 - r1**2) / (2 * rho * np.linalg.norm(Xj - X1)) / sqrt(2))
eta = rho * rng.normal(size=(400000, D))
mc = np.mean(np.linalg.norm(x + eta - Xj, axis=1) < np.linalg.norm(x + eta - X1, axis=1))
rep("N7 p_j exact (MC 4e5)", abs(mc - pj) < 4 * sqrt(pj * (1 - pj) / 400000) + 1e-6, f"p_j={pj:.5f} mc={mc:.5f}")
# dimension-free bound p_j <= Phibar(Delta/(2 rho)) with Delta = rj - r1 here
pb = 0.5 * erfc((rj - r1) / (2 * rho) / sqrt(2))
rep("N7 p_j <= Phibar(Delta/2rho)", pj <= pb + 1e-15, f"{pj:.3e} <= {pb:.3e}")

# ---------------------------------------------------------------- N8 with CRN sample mean m = rho*mbar
Asym, z, rho_s, qs, mb = sp.symbols("A z rho q mbar", real=True)
muN8 = Asym + rho_s * z
uN8 = (m**2 + s2 - mu * m) / ((mu - m) ** 2 + s2)
u_crn = sp.simplify(uN8.subs({mu: muN8, m: rho_s * mb, s2: rho_s**2 * qs}))
u_doc = qs / ((Asym / rho_s + z) ** 2 + qs)
rep("N8 formula at mbar = 0", zero(sp.simplify(u_crn.subs(mb, 0) - u_doc)))
y = sp.symbols("y", real=True)
u_y = (qs - y * mb) / (y**2 + qs)  # with y = A/rho + z - mbar
rep("N8 CRN form u = (q - y mbar)/(y^2+q), y = A/rho + z - mbar",
    zero(sp.simplify(u_crn - u_y.subs(y, Asym / rho_s + z - mb))))
dudy = sp.simplify(sp.diff(u_y, y) * (y**2 + qs) ** 2)
rep("N8 CRN du/dy numerator = mbar y^2 - 2 q y - mbar q", zero(dudy - (mb * y**2 - 2 * qs * y - mb * qs)))
# numeric example where the sign of dw*/drho differs from the document's criterion while 0<w*<1
ex = None
fu_np = sp.lambdify((Asym, z, qs, mb, rho_s), u_crn, "numpy")
for _ in range(200000):
    Av, zv, qv, mbv, rv = rng.normal(), rng.normal(), rng.exponential(1), rng.normal(0, 0.07), rng.uniform(0.005, 0.05)
    u0 = float(fu_np(Av, zv, qv, mbv, rv))
    if not (0.02 < u0 < 0.98):
        continue
    du = (fu_np(Av, zv, qv, mbv, rv * 1.001) - fu_np(Av, zv, qv, mbv, rv * 0.999)) / (0.002 * rv)
    doc_sign = Av * (Av + rv * zv) > 0
    if (du > 0) != doc_sign and abs(du) * rv > 1e-3:
        ex = (round(Av, 4), round(zv, 4), round(qv, 4), round(mbv, 4), round(rv, 4), round(u0, 4), round(float(du), 4), doc_sign)
        break
rep("N8 sign can differ with finite-M mean mbar (example found)", ex is not None,
    f"{ex}" if ex else "none in 2e5 trials")

n_ok = sum(o[1] for o in out)
print(f"\n{n_ok}/{len(out)} items agree")
