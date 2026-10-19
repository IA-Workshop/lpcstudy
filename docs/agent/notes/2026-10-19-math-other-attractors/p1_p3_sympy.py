"""Symbolic verification of the algebra of Theorems P1 and P3 with SymPy.

SymPy is NOT a project dependency: this script is run in an ephemeral
environment (``uv run --no-project --with sympy python -I p1_p3_sympy.py``)
that leaves the project venv untouched (main-session instruction, LPC.PC.17).
The exact-rational script ``p1_p3_identities.py`` is the independent second
check in the project environment. Versions are printed first.
"""

import mpmath
import sympy as sp

print(f"sympy {sp.__version__}, mpmath {mpmath.__version__} (ephemeral tool, not a project dependency)")

w, EC, EP, C = sp.symbols("w E_C E_P C", real=True)
c = EC + EP - 2 * C
u = (EP - C) / c
V = w**2 * EC + (1 - w) ** 2 * EP + 2 * w * (1 - w) * C
Vu = V.subs(w, u)

# P1(a): completing the square
print("P1(a)  V(w) - [c (w-u)^2 + V(u)] =", sp.simplify(V - (c * (w - u) ** 2 + Vu)))
# P1(c): closed form of V(u)
print("P1(c)  V(u) - (E_C E_P - C^2)/c =", sp.simplify(Vu - (EC * EP - C**2) / c))
# P1(c): the reduction used in the proof sketch
print("P1(c)  2V(u) - E_C - [E_C(E_P - E_C) + 2C(E_C - C)]/c =",
      sp.simplify(2 * Vu - EC - (EC * (EP - EC) + 2 * C * (EC - C)) / c))
# P1(b): u >= 0 iff C <= E_P and u <= 1 iff C <= E_C (for c > 0)
print("P1(b)  c*u - (E_P - C) =", sp.simplify(c * u - (EP - C)), ";  c*(1-u) - (E_C - C) =", sp.simplify(c * (1 - u) - (EC - C)))
# P1(e)
print("P1(e)  V(u) at E_C=E_P=1, C=-1:", Vu.subs({EC: 1, EP: 1, C: -1}))
# P1(d): the horizon shift: r0 e^{Lambda H}/sqrt2 = r0 e^{Lambda H'} gives H' - H = ln2/(2 Lambda)
H, Hp, Lam, r0 = sp.symbols("H H' Lambda r0", positive=True)
sol = sp.solve(sp.Eq(r0 * sp.exp(Lam * H) / sp.sqrt(2), r0 * sp.exp(Lam * Hp)), Hp)[0]
print("P1(d)  H' - H =", sp.simplify(sol - H))
# P1(d) with verification noise in quadrature: sqrt(E/2 + rho^2) >= sqrt((E + rho^2)/2)
E, rho = sp.symbols("E rho", positive=True)
print("P1(d)  (E/2 + rho^2) - (E + rho^2)/2 =", sp.simplify((E / 2 + rho**2) - (E + rho**2) / 2), ">= 0")
# Separation remark with the copied-noise term (L6)
e2, d2, kap, q, r2k = sp.symbols("eps2 delta2 kappa q r2k", real=True)
u_sep = sp.simplify(u.subs({EC: e2 * q + r2k, EP: d2 * q, C: kap * q}))
print("L6     u under proportional covariances + copied noise =", u_sep)
print("L6     limit q -> oo:", sp.limit(u_sep, q, sp.oo), "; equals delta2/(eps2+delta2) only if kappa = 0")
print("L6     at finite q with kappa = 0, u - delta2/(eps2+delta2) =",
      sp.simplify(u_sep.subs(kap, 0) - d2 / (e2 + d2)), "(nonzero whenever r2k > 0: an H-dependence through q_H)")
# P3(a): vertex of sum c_i (w - u_i)^2
n = 4
cs = sp.symbols(f"c1:{n+1}", positive=True)
us = sp.symbols(f"u1:{n+1}", real=True)
S = sum(ci * (w - ui) ** 2 for ci, ui in zip(cs, us))
vertex = sp.solve(sp.diff(S, w), w)[0]
print("P3(a)  vertex - sum c u / sum c =", sp.simplify(vertex - sum(ci * ui for ci, ui in zip(cs, us)) / sum(cs)))
# P3(b): conditional decomposition on a finite cell (weights p_i)
ps = sp.symbols(f"p1:{n+1}", positive=True)
f = sp.symbols("f", real=True)
Ec = sum(p * ci for p, ci in zip(ps, cs))
ubar = sum(p * ci * ui for p, ci, ui in zip(ps, cs, us)) / Ec
lhs = sum(p * ci * (f - ui) ** 2 for p, ci, ui in zip(ps, cs, us))
rhs = Ec * (f - ubar) ** 2 + sum(p * ci * (ui - ubar) ** 2 for p, ci, ui in zip(ps, cs, us))
print("P3(b)  E[c(f-u)^2|F] - {E[c|F](f-ubar)^2 + E[c(u-ubar)^2|F]} =", sp.simplify(lhs - rhs))
# P2(a): the chain of inequalities, as a symbolic check that the constants are right
r1, Delta, eta = sp.symbols("r1 Delta eta", positive=True)
lower_other = (r1 + Delta) - eta  # ||x+eta - X_j|| >= r2 - ||eta||
upper_nearest = r1 + eta  # ||x+eta - X_1|| <= r1 + ||eta||
print("P2(a)  (r2 - eta) - (r1 + eta) =", sp.simplify(lower_other - upper_nearest), "> 0 iff eta < Delta/2")
