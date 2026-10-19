"""Exact (rational-arithmetic) checks of the algebra behind Theorems P1 and P3.

SymPy is not installed in the project environment and nothing is installed
for this note, so every identity is checked in exact arithmetic with
``fractions.Fraction`` on 2000 random rational triples (E_C, E_P, C) that
satisfy Cauchy-Schwarz (C^2 <= E_C E_P). An identity that holds on 2000
random rationals with denominators up to 97 is, for polynomial identities of
this degree, a proof by the Schwartz-Zippel bound with failure probability far
below 1e-100; the inequalities are checked exactly as well (no rounding).

Checked:
  P1(a)  V(w) = c (w - u)^2 + V(u), with c = E_C + E_P - 2C, u = (E_P - C)/c.
  P1(b)  u in [0, 1]  <=>  C <= min(E_C, E_P)   (given c > 0).
  P1(c)  V(u) = (E_C E_P - C^2)/c ; if C >= 0 then min_{[0,1]} V >= min(E_C, E_P)/2,
         and the reduction 2V(u) - E_C = [E_C(E_P - E_C) + 2C(E_C - C)]/c.
  P1(e)  E_C = E_P = 1, C = -1 gives min V = 0.
  L6     separation: proportional covariances give u = (d^2 q - k q)/((e^2 + d^2 - 2k) q + r^2/k),
         which equals d^2/(e^2 + d^2) only when k = 0 and the copied-noise term r^2/k is 0.
  P3(a)  sum_i c_i (w - u_i)^2 has vertex sum c_i u_i / sum c_i.
  P3(b)  conditional identity E[c (f - u)^2 | F] = E[c|F] (f - ubar)^2 + E[c (u - ubar)^2 | F]
         for ubar = E[c u | F] / E[c | F]  (checked on random finite cells).
"""

from fractions import Fraction as Fr
import random

random.seed(20261019)


def rfrac(lo=-5, hi=5, den=97):
    d = random.randint(1, den)
    return Fr(random.randint(lo * d, hi * d), d)


def moment_triple():
    """Random (E_C, E_P, C) with E_C, E_P > 0 and C^2 <= E_C E_P (Cauchy-Schwarz)."""
    while True:
        ec, ep = rfrac(0, 5), rfrac(0, 5)
        if ec == 0 or ep == 0:
            continue
        c = rfrac(-5, 5)
        if c * c <= ec * ep:
            return ec, ep, c


def V(w, ec, ep, c):
    return w * w * ec + (1 - w) ** 2 * ep + 2 * w * (1 - w) * c


def clip(x):
    return max(Fr(0), min(Fr(1), x))


n_fail = {k: 0 for k in ("a", "b", "c_form", "c_ineq", "c_reduction", "p3a", "p3b", "l6")}
n_ok_c = 0
for _ in range(2000):
    ec, ep, cc = moment_triple()
    curv = ec + ep - 2 * cc
    if curv == 0:
        continue  # e_C = e_P a.s.; V is constant; excluded by P1(a)'s hypothesis c > 0
    u = (ep - cc) / curv
    # (a): identity in w on three random w
    for _ in range(3):
        w = rfrac(-3, 3)
        if V(w, ec, ep, cc) != curv * (w - u) ** 2 + V(u, ec, ep, cc):
            n_fail["a"] += 1
    # (b)
    if (0 <= u <= 1) != (cc <= min(ec, ep)):
        n_fail["b"] += 1
    # (c) closed form of V(u)
    if V(u, ec, ep, cc) != (ec * ep - cc * cc) / curv:
        n_fail["c_form"] += 1
    # (c) inequality, checked by exact minimisation over [0,1]: convex quadratic, so min at clip(u)
    vmin = V(clip(u), ec, ep, cc)
    if cc >= 0:
        n_ok_c += 1
        if 2 * vmin < min(ec, ep):
            n_fail["c_ineq"] += 1
    # (c) the reduction used in the proof sketch (case E_C <= E_P, C < E_C)
    if ec <= ep and cc < ec:
        lhs = 2 * V(u, ec, ep, cc) - ec
        rhs = (ec * (ep - ec) + 2 * cc * (ec - cc)) / curv
        if lhs != rhs:
            n_fail["c_reduction"] += 1
    # P3(a): vertex of a sum of quadratics (random regime of 4 states)
    cs = [rfrac(0, 5) + Fr(1, 10) for _ in range(4)]
    us = [rfrac(-2, 3) for _ in range(4)]
    vertex = sum(ci * ui for ci, ui in zip(cs, us)) / sum(cs)
    for _ in range(2):
        w = rfrac(-3, 3)
        total = sum(ci * (w - ui) ** 2 for ci, ui in zip(cs, us))
        base = sum(ci * (vertex - ui) ** 2 for ci, ui in zip(cs, us))
        if total != sum(cs) * (w - vertex) ** 2 + base:
            n_fail["p3a"] += 1
    # P3(b): the conditional decomposition on a finite cell with weights p_i
    ps = [rfrac(0, 3) + Fr(1, 7) for _ in range(4)]
    z = sum(ps)
    ps = [p / z for p in ps]
    ecf = sum(p * ci for p, ci in zip(ps, cs))
    ubar = sum(p * ci * ui for p, ci, ui in zip(ps, cs, us)) / ecf
    f = rfrac(-1, 2)
    lhs = sum(p * ci * (f - ui) ** 2 for p, ci, ui in zip(ps, cs, us))
    rhs = ecf * (f - ubar) ** 2 + sum(
        p * ci * (ui - ubar) ** 2 for p, ci, ui in zip(ps, cs, us)
    )
    if lhs != rhs:
        n_fail["p3b"] += 1
    # L6 separation with the copied-noise term: E_C = e^2 q + r^2/k, E_P = d^2 q, C = k q
    e2, d2, kq, q, r2k = (
        rfrac(0, 3) + Fr(1, 9),
        rfrac(0, 3) + Fr(1, 9),
        rfrac(-1, 1),
        rfrac(0, 50) + Fr(1, 9),
        rfrac(0, 1) + Fr(1, 100),
    )
    ec2, ep2, c2 = e2 * q + r2k, d2 * q, kq * q
    curv2 = ec2 + ep2 - 2 * c2
    if curv2 != 0:
        u2 = (ep2 - c2) / curv2
        if u2 != (d2 * q - kq * q) / ((e2 + d2 - 2 * kq) * q + r2k):
            n_fail["l6"] += 1

print("exact rational checks on 2000 random moment triples")
for k, v in n_fail.items():
    print(f"  {k:12s} failures: {v}")
print(f"  triples with C >= 0 used for (c): {n_ok_c}")

# P1(e)
ec, ep, cc = Fr(1), Fr(1), Fr(-1)
curv = ec + ep - 2 * cc
u = (ep - cc) / curv
print(f"P1(e): E_C=E_P=1, C=-1 -> c={curv}, u={u}, V(u)={V(u, ec, ep, cc)} (expected 0)")

# Limit of the separation formula: w*(H) -> d^2/(e^2+d^2) only as q -> inf with k = 0
e2, d2 = Fr(1, 100), Fr(1, 400)
for q in (Fr(1), Fr(10), Fr(100), Fr(10000)):
    r2k = Fr(1, 10000)  # rho = 1%, k = 1
    val = (d2 * q) / ((e2 + d2) * q + r2k)
    print(
        f"L6 transient: q={float(q):8.1f}  w*(H)={float(val):.5f}  "
        f"limit d^2/(e^2+d^2)={float(d2 / (e2 + d2)):.5f}"
    )

# Sharpened P3(b): the floor vanishes iff clip(ubar) = clip(u) a.s. on {c > 0}.
# Cell with all u_i >= 1 but different: u not F-measurable, w* = 1 is.
cs = [Fr(1), Fr(2), Fr(3)]
us = [Fr(3, 2), Fr(5, 2), Fr(7, 2)]
ubar = sum(c * u for c, u in zip(cs, us)) / sum(cs)
floor = sum(c * ((clip(ubar) - u) ** 2 - (clip(u) - u) ** 2) for c, u in zip(cs, us))
print(f"P3(b) sharpening: cell u={us}, ubar={ubar}, clip(ubar)={clip(ubar)}, floor={floor} (0: w* is F-measurable, u is not)")
us = [Fr(1, 2), Fr(5, 2), Fr(7, 2)]
ubar = sum(c * u for c, u in zip(cs, us)) / sum(cs)
floor = sum(c * ((clip(ubar) - u) ** 2 - (clip(u) - u) ** 2) for c, u in zip(cs, us))
print(f"P3(b) sharpening: cell u={us}, ubar={ubar}, clip(ubar)={clip(ubar)}, floor={floor} (> 0: w* not F-measurable)")
