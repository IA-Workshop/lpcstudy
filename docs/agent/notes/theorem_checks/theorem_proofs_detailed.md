# LPC Study: Theorem Program, Proofs in Full Detail, and Proposed New Theorems

**Version:** 2026-10-21 (v1). **Status:** working document for the coding and mathematics agents.
**Handling:** statements about results are PRELIMINARY: internal to the owner and the student until promotion.
They quote CONF-1 verdict words (UNPROMOTED) or DEV-0 reference numbers labelled DEVELOPMENT (not a hypothesis test).

**Scope note for the agent.**

- This file proves every theorem-grade item of the theorem program (`theorem_program_lpc_v1.md`, as amended by the
  v3 proposal), one elementary step at a time (Part A). It then states and proves eight proposed new results
  that tighten the study's conclusions (Part B), and ends with tasks (Part C).
- It does **not** change any pre-registered hypothesis, band, level or decision rule. Everything in Part B is
  post-freeze and exploratory. Any use of it in the study goes through an owner decision and is reported as
  exploratory, on development seeds only.
- The student's own hand proofs of P1 and P2 are the science-fair entry's. This document is a reference for
  agents and the mentor, not a substitute.
- Every claim here has an executable check: `theorem_checks.py` (37 checks, Part A) and `proposed_checks.py`
  (14 checks: Part B and the A4.4 lemma). All 51 pass. A passing check is evidence, not a proof; the proofs are the text.

---

## 0. How to read this document

### 0.1 Conventions

- A **state** is one point $s$ of the attractor at which a forecast is issued. Everything in Parts A and B is
  "at one state" unless it says "over states".
- **Expectation** $\mathbb{E}[\cdot]$ means the average over the random quantity named in that section. In the study,
  the oracle moments are averages over $M = 200$ *query-noise* draws at a fixed state, **with the library fixed**.
  This matters in Section A1.6 and in N1 and N2.
- **Raw moments.** The study uses raw (uncentered) second moments: $E_C = \mathbb{E}[e_C^2]$, not the variance.
- "**Iff**" means "if and only if".
- $\blacksquare$ ends a proof.
- Each result is labelled with its study name (P1, P2, P3) and its theorem-program name (L1 to L11).

### 0.2 Notation (every symbol used)

| Symbol | Meaning |
| --- | --- |
| $s$ | true latent state, in whitened coordinates (mean 0, covariance identity over the attractor) |
| $m$ | latent dimension (3 for all three systems) |
| $D$ | embedding dimension (7) |
| $\rho$ | observation-noise standard deviation, as a fraction of $\sigma_x$ |
| $\eta$ | the query's observation-noise vector in delay space, $\eta \in \mathbb{R}^D$, $\mathbb{E}\lVert\eta\rVert^2 = D\rho^2$ |
| $X_1, \dots, X_n$ | library delay vectors (noisy) |
| $x$ | the clean query delay vector $G(s)$; the observed query is $x + \eta$ |
| $r_1, r_2$ | distances from $x$ to its nearest and second-nearest library vectors |
| $\Delta$ | nearest-neighbour margin, $r_2 - r_1$ |
| $a$ | latent state of the analog CP retrieves |
| $\hat s$ | PLP's estimate of $s$ |
| $e_C, e_P$ | CP and PLP forecast errors at horizon $H$ (scalars, in units of $\sigma_x$) |
| $E_C, E_P, C$ | $\mathbb{E}[e_C^2]$, $\mathbb{E}[e_P^2]$, $\mathbb{E}[e_C e_P]$ |
| $c$ | curvature, $E_C + E_P - 2C = \mathbb{E}[(e_C - e_P)^2]$ |
| $u$ | unclipped optimum, $(E_P - C)/c$ |
| $w, w^*$ | weight on CP; optimal weight $\operatorname{clip}_{[0,1]}(u)$ |
| $V(w)$ | hybrid mean squared error at weight $w$ |
| $\Gamma_H$ | amplifier: the row vector $\nabla \tilde h(\Phi^H s)\, D\Phi^H(s)$, sensitivity of the normalized observable after $H$ steps to the initial state |
| $g_H$ | $\lVert\Gamma_H\rVert$ |
| $\Lambda$, $\bar\Lambda$ | a growth rate per step; the study's $\bar\Lambda$ is the slope of $\ln g_H$ over the first Lyapunov time (LT) |
| $J$ | Jacobian of the delay map $G$ ($D \times m$), assumed full column rank |
| $J^+$ | pseudoinverse $(J^\top J)^{-1}J^\top$ |
| $\nu$ | observability factor, $\nu^2 = \operatorname{tr}[(J^\top J)^{-1}]$ in whitened coordinates |
| $\theta$, $\theta'$ | error tolerance (fraction of $\sigma_x$); $\theta' = \sqrt{\theta^2 - \rho^2}$ when verification noise is included |
| $T(\theta)$ | first-passage (characteristic) horizon: first step at which the r.m.s. error exceeds $\theta$ |
| $F$ | the four-condition profile (oracle or deployable) |
| $k$ | number of analogs averaged (1 in the study) |
| $\xi$ | the copied future noise in CP's forecast |

### 0.3 Toolbox: facts used repeatedly (with proofs)

**F1. Linearity of expectation.** $\mathbb{E}[\alpha X + \beta Y] = \alpha\mathbb{E}[X] + \beta\mathbb{E}[Y]$ for constants
$\alpha, \beta$. (Definition of the average; holds for sample averages exactly.)

**F2. A square has nonnegative mean.** $\mathbb{E}[Z^2] \ge 0$, with equality iff $Z = 0$ (almost surely; for a sample
average, iff every sample is 0). *Proof:* $Z^2 \ge 0$ pointwise, and the average of nonnegative numbers is
nonnegative; it is 0 only if every term is 0. $\blacksquare$

**F3. Variance identity.** $\mathbb{E}[Z^2] = \operatorname{Var}(Z) + (\mathbb{E}Z)^2$, so $\mathbb{E}[Z^2] \ge \operatorname{Var}(Z)$.
*Proof:* write $Z = \mu + (Z - \mu)$ with $\mu = \mathbb{E}Z$. Square: $Z^2 = \mu^2 + 2\mu(Z-\mu) + (Z-\mu)^2$. Take
expectations (F1): the middle term has mean $2\mu(\mathbb{E}Z - \mu) = 0$. So $\mathbb{E}Z^2 = \mu^2 + \operatorname{Var}(Z)$. $\blacksquare$

**F4. Mean minimizes the squared spread.** For any vector $b$, $\mathbb{E}\lVert Y - b\rVert^2 = \mathbb{E}\lVert Y - \bar Y\rVert^2 + \lVert\bar Y - b\rVert^2 \ge \mathbb{E}\lVert Y - \bar Y\rVert^2$
, where $\bar Y = \mathbb{E}Y$. *Proof:* F3 applied coordinate by coordinate
to $Y - b$, whose mean is $\bar Y - b$, then summed over coordinates. $\blacksquare$

**F5. Cauchy–Schwarz.** $|\mathbb{E}[XY]| \le \sqrt{\mathbb{E}[X^2]\,\mathbb{E}[Y^2]}$. *Proof:* for every real $t$,
$0 \le \mathbb{E}[(X - tY)^2] = \mathbb{E}X^2 - 2t\,\mathbb{E}XY + t^2\mathbb{E}Y^2$ (F2, F1). A quadratic in $t$ that is never negative has
discriminant $\le 0$: $4(\mathbb{E}XY)^2 - 4\,\mathbb{E}X^2\,\mathbb{E}Y^2 \le 0$. (If $\mathbb{E}Y^2 = 0$ then $Y = 0$ and both sides are 0.) $\blacksquare$

**F6. Triangle inequalities.** For vectors, $\lVert p + q\rVert \le \lVert p\rVert + \lVert q\rVert$ and
$\bigl|\lVert p\rVert - \lVert q\rVert\bigr| \le \lVert p - q\rVert$. (Standard; the second follows from the first applied to
$p = (p - q) + q$ and to $q = (q - p) + p$.)

**F7. Markov's inequality.** If $Y \ge 0$ and $t > 0$, then $\Pr(Y \ge t) \le \mathbb{E}[Y]/t$. *Proof:*
$Y \ge t\,\mathbf{1}\{Y \ge t\}$ pointwise; take expectations: $\mathbb{E}Y \ge t\Pr(Y \ge t)$. $\blacksquare$

**F8. Taylor's theorem along a segment.** If $\varphi: [0,1] \to \mathbb{R}$ is twice differentiable, then
$\varphi(1) = \varphi(0) + \varphi'(0) + \tfrac12\varphi''(\tau)$ for some $\tau \in (0,1)$ (Lagrange remainder).

**F9. Jensen for the logarithm.** For positive numbers $y_1, \dots, y_M$,
$\frac1M\sum_i \ln y_i \le \ln\bigl(\frac1M\sum_i y_i\bigr)$, with equality iff all $y_i$ are equal (strict concavity of $\ln$).

**F10. Matrix facts.** $(AB)^\top = B^\top A^\top$; $(AB)^{-1} = B^{-1}A^{-1}$ for invertible square $A, B$;
$\operatorname{tr}(AB) = \operatorname{tr}(BA)$ whenever both products are defined; a symmetric matrix $S$ is positive
semidefinite ($S \succeq 0$) iff $v^\top S v \ge 0$ for all $v$; $ZZ^\top \succeq 0$ for every $Z$, because
$v^\top ZZ^\top v = \lVert Z^\top v\rVert^2 \ge 0$.

**F11. Rayleigh quotient.** For symmetric $A$ and symmetric positive definite $B$, the ratio
$R(v) = v^\top A v / v^\top B v$ ($v \ne 0$) takes values exactly in $[\lambda_{\min}, \lambda_{\max}]$, the extreme
eigenvalues of $B^{-1/2} A B^{-1/2}$, and attains both. *Proof:* substitute $v = B^{-1/2} z$; then
$R = z^\top (B^{-1/2}AB^{-1/2}) z / z^\top z$, the ordinary Rayleigh quotient of a symmetric matrix, whose range is
$[\lambda_{\min}, \lambda_{\max}]$ (expand $z$ in the orthonormal eigenbasis). $\blacksquare$

**F12. Conditional expectation (tower rule).** For a random profile $F$ and any function $g$,
$\mathbb{E}[g(F)\,X] = \mathbb{E}[g(F)\,\mathbb{E}[X \mid F]]$. With a finite profile this is regrouping a sum by the value of $F$.

**F13. Gaussian projections.** If $\eta \sim N(0, \rho^2 I_D)$ and $v \in \mathbb{R}^D$, then
$\langle\eta, v\rangle \sim N(0, \rho^2\lVert v\rVert^2)$. In particular $\operatorname{Var}(a^\top\eta) = \rho^2\lVert a\rVert^2$ and
$\operatorname{Cov}(L\eta) = \rho^2 LL^\top$ for any matrix $L$.

**F14. Implicit differentiation.** If $\Psi(T, \ell) = 0$ defines $T(\ell)$ and $\partial_T\Psi \ne 0$, then
$dT/d\ell = -\partial_\ell\Psi / \partial_T\Psi$.

---

# Part A. The theorem program, proved step by step

## A1. Theorem P1 (= L5 + L7): the optimal weight and the limit on blending

### A1.1 Setting

At one state and one horizon $H$, CP makes error $e_C$ and PLP makes error $e_P$. Both are random because the
query noise is random. The hybrid forecast with weight $w$ on CP has error

$$e(w) = w\,e_C + (1 - w)\,e_P .$$

(Why: the hybrid forecast is $w\hat x_{CP} + (1-w)\hat x_{PLP}$; subtract the truth $x = wx + (1-w)x$.)

Its mean squared error is $V(w) = \mathbb{E}[e(w)^2]$.

### A1.2 P1(a): $V$ is a parabola, and its minimizer

**Statement.** $V(w) = c\,(w - u)^2 + V(u)$, with $c = E_C + E_P - 2C$, $u = (E_P - C)/c$ (when $c > 0$),
and $V(u) = (E_C E_P - C^2)/c$. If $c > 0$, the minimizer of $V$ over $[0,1]$ is $w^* = \operatorname{clip}_{[0,1]}(u)$,
meaning $0$ if $u < 0$, $u$ if $0 \le u \le 1$, and $1$ if $u > 1$.

**Proof.**

1. Square the hybrid error: $e(w)^2 = w^2 e_C^2 + 2w(1-w)\,e_C e_P + (1-w)^2 e_P^2$.
2. Take expectations (F1); $w$ is a constant:
   $V(w) = w^2 E_C + 2w(1-w)\,C + (1-w)^2 E_P$.
3. Expand $2w(1-w) = 2w - 2w^2$ and $(1-w)^2 = 1 - 2w + w^2$:
   $V(w) = w^2E_C + 2wC - 2w^2C + E_P - 2wE_P + w^2E_P$.
4. Collect powers of $w$:
   $V(w) = w^2(E_C + E_P - 2C) - 2w(E_P - C) + E_P = c\,w^2 - 2(E_P - C)\,w + E_P$.
5. **$c$ is a mean square.** $\mathbb{E}[(e_C - e_P)^2] = E_C - 2C + E_P = c$ (expand and use F1). So $c \ge 0$ (F2).
6. Assume $c > 0$ (Section A1.6 says when this holds). Write $E_P - C = c\,u$ by the definition of $u$. Then
   $V(w) = c\,w^2 - 2c\,u\,w + E_P$.
7. Complete the square: $c\,w^2 - 2cuw = c(w - u)^2 - cu^2$. So $V(w) = c(w-u)^2 + (E_P - cu^2)$.
8. Simplify the constant. $cu^2 = (E_P - C)^2/c$, so
   $E_P - cu^2 = \dfrac{E_P c - (E_P - C)^2}{c}$.
   Numerator: $E_P(E_C + E_P - 2C) - (E_P^2 - 2E_PC + C^2) = E_PE_C + E_P^2 - 2E_PC - E_P^2 + 2E_PC - C^2 = E_CE_P - C^2$.
   So the constant is $(E_CE_P - C^2)/c$, and putting $w = u$ in step 7 shows it equals $V(u)$.
9. **Minimizer.** With $c > 0$, $c(w-u)^2 \ge 0$, with equality only at $w = u$, so $u$ is the unique minimizer over
   all real $w$. On $[0,1]$:
   - if $0 \le u \le 1$, $u$ is admissible, so $w^* = u$;
   - if $u < 0$, then for $w \in [0,1]$, $w - u > 0$ and $(w - u)^2$ increases with $w$; the smallest value is at
     $w = 0$;
   - if $u > 1$, then $w - u < 0$ on $[0,1]$ and $(w-u)^2$ decreases as $w$ grows; the smallest value is at $w = 1$.

   This is exactly $\operatorname{clip}_{[0,1]}(u)$. $\blacksquare$

*Check:* `theorem_checks.py`, items "P1(a) / L5" (symbolic identity; 5,000 random moment sets against a
20,001-point grid).

### A1.3 P1(b): when is the optimum inside $[0,1]$?

**Statement.** $0 \le u \le 1$ iff $C \le \min(E_C, E_P)$.

**Proof.** Take $c > 0$.

1. $u \ge 0 \iff E_P - C \ge 0 \iff C \le E_P$ (multiply by $c > 0$; the direction of the inequality is kept).
2. $1 - u = (c - E_P + C)/c = (E_C + E_P - 2C - E_P + C)/c = (E_C - C)/c$. So $u \le 1 \iff C \le E_C$.
3. Both hold iff $C \le E_P$ and $C \le E_C$, i.e. $C \le \min(E_C, E_P)$. $\blacksquare$

**Useful restatement (used in N2).** $w^* = 0 \iff u \le 0 \iff C \ge E_P$, and $w^* = 1 \iff C \ge E_C$.
In words: CP gets no weight exactly when the cross-moment is at least PLP's own mean square, i.e. when the
regression coefficient of $e_C$ on $e_P$, $C/E_P$, is at least 1.

### A1.4 P1(c): blending at best halves the MSE when $C \ge 0$

**Statement.** If $C \ge 0$ (and $c > 0$), then $\min_{w \in [0,1]} V(w) \ge \tfrac12\min(E_C, E_P)$.
Equality holds when $E_C = E_P$ and $C = 0$.

**Proof.**

1. The problem is symmetric: swapping the names CP and PLP and replacing $w$ by $1 - w$ leaves $V$ unchanged. So
   assume without loss of generality $E_C \le E_P$. Then $\min(E_C, E_P) = E_C$ and we must show $\min V \ge E_C/2$.
2. **Case 1: $C \ge E_C$.** By A1.3 step 2, $u \ge 1$, so $w^* = 1$ and $\min V = V(1) = E_C \ge E_C/2$. Done.
3. **Case 2: $C < E_C$.** Then also $C < E_P$ (because $E_C \le E_P$), so $0 \le u \le 1$ by A1.3, $w^* = u$, and
   $\min V = V(u) = (E_CE_P - C^2)/c$.
4. We need $V(u) \ge E_C/2$, i.e. $2(E_CE_P - C^2) \ge E_C\,c$ (multiply both sides by $2c > 0$).
5. Expand the right side: $E_C c = E_C^2 + E_CE_P - 2E_CC$.
6. Subtract: $2E_CE_P - 2C^2 - E_C^2 - E_CE_P + 2E_CC = E_CE_P - E_C^2 + 2E_CC - 2C^2$.
7. Factor in pairs: $E_C(E_P - E_C) + 2C(E_C - C)$.
8. Each factor is nonnegative: $E_C \ge 0$ (a mean square), $E_P - E_C \ge 0$ (step 1), $C \ge 0$ (hypothesis),
   $E_C - C > 0$ (Case 2). So the sum is $\ge 0$, which is step 4. $\blacksquare$

**Tightness.** With $E_C = E_P = 1$ and $C = 0$: $c = 2$, $u = \tfrac12$, $V(u) = (1 - 0)/2 = \tfrac12 = \tfrac12\min(E_C,E_P)$.
So the constant $\tfrac12$ cannot be improved.

*Check:* "P1(c) proof step" (the identity of step 7, symbolically), "P1(c) / L7(i)" (9,940 random cases),
"P1(c) tightness".

### A1.5 P1(e): the floor fails without $C \ge 0$

**Statement.** There are moments with $C < 0$ and $\min V = 0 < \tfrac12\min(E_C, E_P)$.

**Proof.** Let $e_C = Z$ and $e_P = -Z$ with $\mathbb{E}Z^2 = 1$. Then $E_C = E_P = 1$, $C = -1$, $c = 4$, $u = (1 + 1)/4 = \tfrac12$,
and $e(\tfrac12) = \tfrac12 Z - \tfrac12 Z = 0$, so $V(\tfrac12) = 0$. $\blacksquare$

Interpretation: when the two forecasters err in *opposite* directions, averaging cancels the errors, and the
gain from blending is unlimited. This is why $C < 0$ states matter (Part B, N4).

### A1.6 When is $c > 0$? (A conditioning caveat)

The v3 text justifies $c > 0$ by the copied noise: CP's forecast copies a noisy future value, so
$e_C$ contains a term $\xi$ with $\mathbb{E}\xi^2 = \rho^2/k$ that is orthogonal to $e_P$ and to $e_C - \xi$. Then
$c = \mathbb{E}[(e_C - \xi - e_P)^2] + 2\mathbb{E}[\xi(e_C - \xi - e_P)] + \mathbb{E}\xi^2 = \mathbb{E}[(e_C-\xi-e_P)^2] + \mathbb{E}\xi^2 \ge \rho^2/k > 0$.

**Caveat.** That argument averages over the *library's* noise. The study's oracle moments average over
*query* noise with the library fixed. Under that conditioning:

- when retrieval does not change across the draws, $\xi$ is one fixed number, not a random term;
- $\mathbb{E}[\xi e_P] = \xi\,\mathbb{E}[e_P]$, which is zero only if PLP is unbiased at that state.

So the orthogonality hypothesis is not guaranteed by the design. The conclusion $c > 0$ still holds in practice,
for a different reason, proved in N1 (Part B): $c \ge \operatorname{Var}(e_C - e_P)$, which is positive unless the two errors
move in lockstep across draws. **Action for the agent:** cite N1, not the copied-noise argument, when the code or
a report justifies strict convexity; and keep the code's handling of the degenerate case $c = 0$ (any $w$ is
optimal) counted, as it is now.

### A1.7 P1(d): the horizon gain under exponential growth

**Definitions.** For a nonnegative error curve $E(H)$ (an r.m.s. error as a function of the horizon), its
first-passage horizon at tolerance $\theta$ is $T(\theta) = \min\{H : E(H) > \theta\}$ in discrete steps (the infimum in
continuous time, where a continuous $E$ then satisfies $E(T) = \theta$). With verification noise the
study crosses when $\sqrt{E(H)^2 + \rho^2} > \theta$, i.e. when $E(H) > \theta' = \sqrt{\theta^2 - \rho^2}$; everything below
holds with $\theta'$ in place of $\theta$.

Let $m(H) = \sqrt{\min(E_C(H), E_P(H))}$, the **better-forecaster envelope**. Let $h(H) = \sqrt{\min_w V_H(w)}$, the
r.m.s. error of the optimal hybrid at each horizon. The **gain** is $T_h(\theta) - T_m(\theta)$.

**Statement (v3).** If $C(H) \ge 0$ at every horizon and $m(H) = r_0 e^{\Lambda H}$ with $\Lambda > 0$, then the
gain is at most $\ln 2/(2\Lambda)$ (continuous time).

**Proof.**

1. By P1(c) at every $H$: $h(H)^2 \ge \tfrac12 m(H)^2$, so $h(H) \ge m(H)/\sqrt2 = r_0e^{\Lambda H}/\sqrt2$.
2. The envelope crosses $\theta$ at $T_m$ with $r_0e^{\Lambda T_m} = \theta$, i.e. $T_m = \Lambda^{-1}\ln(\theta/r_0)$.
3. The lower curve $r_0e^{\Lambda H}/\sqrt2$ crosses $\theta$ at $H_1$ with $e^{\Lambda H_1} = \sqrt2\,\theta/r_0$, i.e.
   $H_1 = \Lambda^{-1}\ln(\theta/r_0) + \Lambda^{-1}\ln\sqrt2 = T_m + \ln 2/(2\Lambda)$.
4. For $H > H_1$, $h(H) \ge r_0e^{\Lambda H}/\sqrt2 > \theta$, so the hybrid has crossed: $T_h \le H_1$.
5. Gain $= T_h - T_m \le \ln 2/(2\Lambda)$. $\blacksquare$

**Fine print.** "The better forecaster" must be the envelope $m$. If one forecaster is better at every horizon,
$m$ is that forecaster's error. If the better one switches, the gain over the forecaster with the longer
horizon can exceed the bound by the envelope's own lead over it.

**L7(iii), the exact gain for uncorrelated proportional seeds.** Suppose $C = 0$, $E_C = A g^2$, $E_P = B g^2$
with the same growth factor $g = e^{\Lambda H}$, and $B \le A$. Let $r = \sqrt{B/A} \in (0,1]$ (smaller seed over larger).

1. By A1.2, $\min V = V(u) = E_CE_P/(E_C + E_P) = ABg^4/((A+B)g^2) = g^2\,AB/(A+B)$.
2. Divide by $m^2 = Bg^2$: $\min V / m^2 = A/(A+B) = 1/(1 + B/A) = 1/(1 + r^2)$.
3. So $h = m/\sqrt{1 + r^2}$, and as in steps 2 to 5 above the gain is $\Lambda^{-1}\ln\sqrt{1 + r^2} = \ln(1 + r^2)/(2\Lambda)$.
4. It increases with $r$ and is largest, $\ln 2/(2\Lambda)$, at $r = 1$ (equal seeds). $\blacksquare$

*Check:* "L7(iii)" (symbolic), "P1(d) / L7(ii)" (2,000 random exponential cases).

### A1.8 P1(d′): the gain without assuming exponential growth (new)

**Statement.** For any error curves (no growth model), if $C \ge 0$ at the single step
$H_1 = T_m(\sqrt2\,\theta)$, then for every allocation rule

$$0 \;\le\; T_h(\theta) - T_m(\theta) \;\le\; T_m(\sqrt2\,\theta) - T_m(\theta).$$

The lower bound needs no hypothesis and applies to the *optimal* hybrid; the upper bound applies to *every*
weight, because every $V(w) \ge \min V$.

**Proof.**

1. **Upper bound.** At $H_1 = T_m(\sqrt2\theta)$, by definition of first passage, $m(H_1) > \sqrt2\,\theta$, so
   $m(H_1)^2 > 2\theta^2$.
2. By P1(c) at that one step (it needs $C(H_1) \ge 0$ only there): $h(H_1)^2 \ge \tfrac12 m(H_1)^2 > \theta^2$.
3. So the hybrid's error exceeds $\theta$ at $H_1$, and its first passage is no later: $T_h(\theta) \le H_1$.
4. Subtract $T_m(\theta)$: gain $\le T_m(\sqrt2\theta) - T_m(\theta)$.
5. **Lower bound.** For every $H$, $\min_w V_H(w) \le \min(V_H(0), V_H(1)) = \min(E_P, E_C) = m(H)^2$, so
   $h(H) \le m(H)$. For $H < T_m(\theta)$, $m(H) \le \theta$, so $h(H) \le \theta$: the optimal hybrid has not crossed.
   Hence $T_h(\theta) \ge T_m(\theta)$. $\blacksquare$

**In words.** Blending buys at most what loosening the tolerance by a factor $\sqrt2$ would buy.

**Why it is stronger than P1(d).**

- No growth law: the right side is read straight off the envelope curve, state by state.
- $C \ge 0$ is needed at one step, not at every horizon.
- Under exponential growth, $T_m(\sqrt2\theta) - T_m(\theta) = \ln\sqrt2/\Lambda = \ln 2/(2\Lambda)$, so P1(d) is a special case.
- In discrete steps the bound is exact as stated (no "+1 step" allowance).

**Why it matters for the data.** The study's gain screen uses $\bar\Lambda$ fitted over the first LT. If the
growth rate changes between 1 LT and the crossing (2 to 3 LT), that screen can be exceeded while P1(d′) holds.
DEV-0 (DEVELOPMENT): 4.5%, 9.7% and 7.7% of eligible states exceed the screen (Lorenz-63, Rössler, Chua), with
largest gains of 1.7, 3.8 and 2.1 LT. A constructed two-phase curve (fast growth for 2 LT, then slow) gives a
gain of 86 steps: exactly the P1(d′) bound, against 6.9 steps allowed by $\ln 2/(2\bar\Lambda)$.

*Check:* "P1(d′) new" (4,000 random non-exponential curves, 0 exceedances), "P1(d) vs P1(d′)".

## A2. L6: separation (the remark after P1)

### A2.1 First-order errors

To first order (L1, Section A6), each error is the amplifier applied to a seed:
$e_C \approx \Gamma_H(a - s) + \xi$ and $e_P \approx \Gamma_H(\hat s - s)$. Write the seeds' raw second-moment matrices
$\Sigma_a = \mathbb{E}[(a-s)(a-s)^\top]$, $\Sigma_s = \mathbb{E}[(\hat s - s)(\hat s - s)^\top]$ and the cross matrix
$K = \mathbb{E}[(a - s)(\hat s - s)^\top]$. Ignoring $\xi$ for now, by F1:

- $E_C = \mathbb{E}[(\Gamma_H(a-s))^2] = \Gamma_H\Sigma_a\Gamma_H^\top =: V_a$ (a scalar: row vector times matrix times column);
- $E_P = \Gamma_H\Sigma_s\Gamma_H^\top =: V_s$;
- $C = \Gamma_H K\Gamma_H^\top =: V_K$.

### A2.2 Statement and proof

**Statement (L6).** If $\Sigma_a = \varepsilon^2 S$, $\Sigma_s = \delta^2 S$ and $K = \kappa S$ for one matrix $S$ and
numbers $\varepsilon, \delta, \kappa$ (proportional seed covariances), then

$$w^* = \frac{\delta^2 - \kappa}{\varepsilon^2 + \delta^2 - 2\kappa}$$

at every horizon and for every amplifier $\Gamma_H$ (when this lies in $[0,1]$). With uncorrelated seeds
($\kappa = 0$) it is $\delta^2/(\varepsilon^2 + \delta^2)$, the rule A4 approximates.

**Proof.**

1. Let $q_H = \Gamma_H S\Gamma_H^\top$, a number that depends on $H$.
2. Then $V_a = \varepsilon^2 q_H$, $V_s = \delta^2 q_H$, $V_K = \kappa q_H$ (substitute and pull the scalars out).
3. $u = (V_s - V_K)/(V_a + V_s - 2V_K) = q_H(\delta^2 - \kappa)/(q_H(\varepsilon^2 + \delta^2 - 2\kappa))$.
4. Cancel $q_H \ne 0$: $u = (\delta^2 - \kappa)/(\varepsilon^2 + \delta^2 - 2\kappa)$, which does not involve $H$ or $\Gamma_H$. $\blacksquare$

### A2.3 The copied-noise transient

**Statement.** Keep the copied noise as a term of size $n = \rho^2/k$ in $E_C$ that is uncorrelated with everything
else (the v3 modelling assumption; see A1.6 for its limits). Then

$$w^*(H) = \frac{(\delta^2 - \kappa)\,q_H}{(\varepsilon^2 + \delta^2 - 2\kappa)\,q_H + n},$$

which increases with $q_H$ when $\delta^2 > \kappa$ and tends to the separated value as $q_H \to \infty$.

**Proof.**

1. Now $E_C = \varepsilon^2 q_H + n$, $E_P = \delta^2 q_H$, $C = \kappa q_H$. So $E_P - C = (\delta^2-\kappa)q_H$ and
   $c = (\varepsilon^2 + \delta^2 - 2\kappa)q_H + n$. Divide to get the formula.
2. Write $P = \delta^2 - \kappa$ and $Q = \varepsilon^2 + \delta^2 - 2\kappa$. Differentiate $Pq/(Qq + n)$ in $q$ by the
   quotient rule: $\dfrac{P(Qq + n) - PqQ}{(Qq+n)^2} = \dfrac{Pn}{(Qq + n)^2}$, which is positive when $P > 0$ and $n > 0$.
3. Divide numerator and denominator by $q$: $P/(Q + n/q) \to P/Q$ as $q \to \infty$. $\blacksquare$

The relative shortfall from the separated value is exactly $n/c$ (from step 1: $w^*/(P/Q) = Qq/(Qq + n) = 1 - n/c$).

### A2.4 What the hypothesis means, and why H2a can fail

If the seed covariances are not proportional, $u$ depends on the *direction* of $\Gamma_H$, which turns as $H$
grows and differs between states of different instability. N3 (Part B) makes this exact. CONF-1 (PRELIMINARY):
H2a is not supported (part (i) fail on Rössler and Chua; part (ii) interior fail on Lorenz-63 and Chua). The
theorem is intact; its hypothesis does not hold on these attractors.

*Check:* "L6", "L6 transient" (symbolic), "L6 (hypothesis)" (500 random geometries).

## A3. Theorem P2 (= L11(b)): stability of analog retrieval

### A3.1 Setting

Library vectors $X_1, \dots, X_n \in \mathbb{R}^D$; clean query $x$; label the library so that $X_1$ is nearest,
$r_1 = \lVert x - X_1\rVert < r_2 \le \lVert x - X_j\rVert$ for every $j \ne 1$. Margin $\Delta = r_2 - r_1 > 0$. The noisy
query is $x + \eta$. CP retrieves the library vector nearest to $x + \eta$; call it $Y(\eta)$.

### A3.2 P2(a): stability

**Statement.** If $\lVert\eta\rVert < \Delta/2$, then $Y(\eta) = X_1$.

**Proof.**

1. Distance from the noisy query to $X_1$: by F6, $\lVert x + \eta - X_1\rVert \le \lVert x - X_1\rVert + \lVert\eta\rVert = r_1 + \lVert\eta\rVert$.
2. Distance to any other $X_j$: by F6 (reverse form), $\lVert x + \eta - X_j\rVert \ge \lVert x - X_j\rVert - \lVert\eta\rVert \ge r_2 - \lVert\eta\rVert$.
3. Compare: $r_2 - \lVert\eta\rVert - (r_1 + \lVert\eta\rVert) = \Delta - 2\lVert\eta\rVert > 0$ by hypothesis.
4. So every other library vector is strictly farther from the noisy query than $X_1$; the nearest is still $X_1$. $\blacksquare$

**Tightness.** Put $x = 0$, $X_1 = (1, 0, \dots, 0)$, $X_2 = (-1.3, 0, \dots, 0)$, so $r_1 = 1$, $r_2 = 1.3$,
$\Delta = 0.3$. Take $\eta = (-t, 0, \dots, 0)$. The distances become $1 + t$ and $1.3 - t$; retrieval switches as soon as
$1.3 - t < 1 + t$, i.e. $t > 0.15 = \Delta/2$. So $\Delta/2$ cannot be replaced by anything larger.

### A3.3 P2(b): the switching probability

**Statement.** $\Pr(Y(\eta) \ne X_1) \le \Pr(\lVert\eta\rVert \ge \Delta/2) \le 4D\rho^2/\Delta^2$.

**Proof.**

1. By P2(a), a switch can happen only if $\lVert\eta\rVert \ge \Delta/2$. The event "switch" is contained in the event
   "$\lVert\eta\rVert \ge \Delta/2$", so its probability is no larger.
2. $\lVert\eta\rVert \ge \Delta/2 \iff \lVert\eta\rVert^2 \ge \Delta^2/4$ (both sides nonnegative).
3. Markov (F7) with $Y = \lVert\eta\rVert^2$, $t = \Delta^2/4$: $\Pr(\lVert\eta\rVert^2 \ge \Delta^2/4) \le \mathbb{E}\lVert\eta\rVert^2/(\Delta^2/4) = 4D\rho^2/\Delta^2$. $\blacksquare$

N7 (Part B) gives exact per-competitor Gaussian probabilities, each free of the factor $D$; their sum is often, not always, smaller.

### A3.4 P2(c): the spread bound on $N$

**Definition.** $N = (\rho\sqrt D)^{-1}\bigl(\mathbb{E}\lVert Y - \bar Y\rVert^2\bigr)^{1/2}$ with $\bar Y = \mathbb{E}Y$: the r.m.s. displacement of the
retrieved vector, per coordinate, in noise units.

**Statement.** $N^2 \le \dfrac{4}{\rho^2 D}\,\mathbb{E}\bigl[(r_1 + \lVert\eta\rVert)^2\,\mathbf{1}\{\lVert\eta\rVert \ge \Delta/2\}\bigr]$.

**Proof.**

1. By F4 with $b = X_1$: $\mathbb{E}\lVert Y - \bar Y\rVert^2 \le \mathbb{E}\lVert Y - X_1\rVert^2$.
2. Split by whether a switch happens. Without a switch, $Y = X_1$ and the term is 0. So
   $\mathbb{E}\lVert Y - X_1\rVert^2 = \mathbb{E}[\lVert Y - X_1\rVert^2\,\mathbf{1}\{\text{switch}\}]$.
3. **Size of a switch.** Suppose $Y = X_j$. Then $X_j$ is at least as close to $x + \eta$ as $X_1$ is:
   $\lVert X_j - (x+\eta)\rVert \le \lVert X_1 - (x + \eta)\rVert$. By F6,
   $\lVert X_j - X_1\rVert \le \lVert X_j - (x+\eta)\rVert + \lVert(x+\eta) - X_1\rVert \le 2\lVert(x+\eta) - X_1\rVert \le 2(r_1 + \lVert\eta\rVert)$,
   the last step by A3.2 step 1.
4. So on a switch, $\lVert Y - X_1\rVert^2 \le 4(r_1 + \lVert\eta\rVert)^2$.
5. A switch implies $\lVert\eta\rVert \ge \Delta/2$ (P2(a)), so $\mathbf{1}\{\text{switch}\} \le \mathbf{1}\{\lVert\eta\rVert \ge \Delta/2\}$.
6. Combine 1, 2, 4, 5: $\mathbb{E}\lVert Y - \bar Y\rVert^2 \le 4\,\mathbb{E}[(r_1 + \lVert\eta\rVert)^2\mathbf{1}\{\lVert\eta\rVert \ge \Delta/2\}]$.
7. Divide by $\rho^2 D$ (definition of $N$). $\blacksquare$

**Remark.** Every step holds for the empirical average over any finite set of draws, so the inequality holds
exactly for the study's $M = 200$ draws. DEV-0 (DEVELOPMENT): 0 violations in 1,400 states per system; the bound
is loose by a factor of about 5 in $N$ (median $N/\sqrt{\text{bound}}$ 0.18 to 0.23).

### A3.5 L11(a): no fourth condition on the PLP side

**Statement.** To first order, PLP's response to the query noise is $\Gamma_H J^+\eta$, with r.m.s. size
$\rho\lVert\Gamma_HJ^+\rVert \le \rho\,g_H\,\nu$.

**Proof.**

1. First-order estimation error: $\hat s - s \approx J^+\eta$ (linearized least squares; L2).
2. Forecast error: $e_P \approx \Gamma_H(\hat s - s) = (\Gamma_HJ^+)\eta$, a linear function $a^\top\eta$ with
   $a^\top = \Gamma_H J^+$.
3. By F13, its variance is $\rho^2\lVert\Gamma_HJ^+\rVert^2$.
4. Operator-norm inequality: $\lVert\Gamma_H J^+\rVert \le \lVert\Gamma_H\rVert\,\lVert J^+\rVert_2 \le g_H\lVert J^+\rVert_F$, because the spectral
   norm never exceeds the Frobenius norm.
5. $\lVert J^+\rVert_F^2 = \operatorname{tr}(J^+J^{+\top}) = \operatorname{tr}((J^\top J)^{-1}) = \nu^2$ (L2(b), Section A6).
6. So the r.m.s. size is at most $\rho g_H\nu$: a function of observability, amplification and $\rho$ only. $\blacksquare$

*Check:* "P2(a) / L11(b)(i)", "P2(a) tightness", "P2(b) / L11(b)(ii)", "P2(c) / L11(b)(iii)", "L11(a)".

## A4. Theorem P3 (= L10): regimes and the measurability floor

### A4.1 The regret identity (corrected L10(i))

**Statement.** For each state $i$, $V_i(w) - V_i(u_i) = c_i(w - u_i)^2$, with the **unclipped** $u_i$.

**Proof.** This is A1.2 step 7 rewritten: $V_i(w) = c_i(w-u_i)^2 + V_i(u_i)$. $\blacksquare$

**The v1 form is false.** The program's v1 wrote $V_i(w) - V_i(w_i^*) = c_i(w - w_i^*)^2$ with the clipped $w^*_i$.
Counterexample: $c = 1$, $u = 1.4$ (so $w^* = 1$), $w = 0$. True excess:
$V(0) - V(1) = (0 - 1.4)^2 - (1 - 1.4)^2 = 1.96 - 0.16 = 1.80$. The v1 form gives $(0 - 1)^2 = 1.00$, understating the
excess. Methods v2 §M13 item 7 corrected the code; the program text should be amended too.

### A4.2 P3(a): the best regime weight

**Statement.** For a regime $S$ (a set of states sharing one weight), $\sum_{i \in S}V_i(w)$ over $w \in [0,1]$ is
minimized by $w_S = \operatorname{clip}_{[0,1]}\bigl(\sum_{i\in S}c_iu_i / \sum_{i\in S}c_i\bigr)$.

**Proof.**

1. By A4.1, $\sum_i V_i(w) = \sum_i c_i(w - u_i)^2 + \text{const}$.
2. Expand: $\sum_i c_i(w^2 - 2u_iw + u_i^2) = (\sum c_i)w^2 - 2(\sum c_iu_i)w + \sum c_iu_i^2$.
3. This is a parabola in $w$ with positive leading coefficient $\sum c_i$. Complete the square as in A1.2:
   its unconstrained minimizer is $\bar u_S = \sum c_iu_i/\sum c_i$, the curvature-weighted mean of the $u_i$.
4. On $[0,1]$ the minimizer is $\operatorname{clip}(\bar u_S)$, by the argument of A1.2 step 9. $\blacksquare$

**Common mistake.** Averaging the *clipped* $w^*_i$ is not optimal (v1 did this).

### A4.3 P3(b): the measurability floor

**Statement.** Let $F$ be a profile (any random quantity) and $f$ any rule whose weight depends on the state only
through $F$, with values in $[0,1]$. Let $\bar u(F) = \mathbb{E}[cu \mid F]/\mathbb{E}[c \mid F]$. Then

$$\mathbb{E}\bigl[V(f(F))\bigr] \;\ge\; \mathbb{E}\bigl[V(\operatorname{clip}\bar u(F))\bigr].$$

**Proof.**

1. For each state, $V(w) = c\,w^2 - 2cu\,w + cu^2 + V(u)$ (A4.2 step 2 for one state).
2. Fix a value $\phi$ of the profile. Every state with $F = \phi$ receives the same weight $f(\phi)$. Average over
   those states (conditional expectation):
   $\mathbb{E}[V(f(\phi)) \mid F = \phi] = \mathbb{E}[c\mid\phi]\,f(\phi)^2 - 2\mathbb{E}[cu \mid \phi]\,f(\phi) + \text{terms without } f$.
3. This is a parabola in the single number $f(\phi)$ with positive leading coefficient. On $[0,1]$ it is smallest
   at $\operatorname{clip}(\mathbb{E}[cu\mid\phi]/\mathbb{E}[c\mid\phi]) = \operatorname{clip}\bar u(\phi)$ (A1.2 step 9).
4. So for every $\phi$, the conditional average for $f$ is at least that for $\operatorname{clip}\bar u$. Averaging over $\phi$
   (F12) keeps the inequality. $\blacksquare$

**Meaning.** $\mathbb{E}V(\operatorname{clip}\bar u(F)) - \mathbb{E}V(w^*)$ is a floor on the excess of *every* regime map, for *every*
number of regimes $K$. It vanishes when $u$ is a function of $F$. N6 (Part B) computes it.

### A4.4 L10(iii) and L10(iv)

**Lemma (clipping never hurts the comparison).** For one state with curvature $c$, unclipped optimum $u$ and
$w^* = \operatorname{clip}(u)$, and any real $v$: $V(\operatorname{clip} v) - V(w^*) \le c\,(v - u)^2$.

*Proof.* By A4.1, $V(\operatorname{clip}v) - V(w^*) = c[(\operatorname{clip}v - u)^2 - (w^* - u)^2]$. Three cases.

1. $u \in [0,1]$: $w^* = u$, and the left side is $c(\operatorname{clip}v - u)^2 \le c(v - u)^2$, because clipping to $[0,1]$ moves $v$
   toward every point of $[0,1]$, including $u$.
2. $u > 1$: $w^* = 1$. If $v \ge 1$, then $\operatorname{clip}v = 1$ and the left side is 0. If $0 \le v < 1$, the left side is
   $c[(u - v)^2 - (u - 1)^2] \le c(u - v)^2$. If $v < 0$, then $\operatorname{clip}v = 0$ and the left side is
   $c[u^2 - (u - 1)^2] = c(2u - 1) \le c\,u^2 \le c(u - v)^2$, using $(u - 1)^2 \ge 0$ and $u - v > u > 0$.
3. $u < 0$: the mirror image of case 2 ($w \mapsto 1 - w$). $\blacksquare$

**L10(iii), corrected.** If the unclipped regime mean satisfies $|\bar u_S - u_i| \le \varepsilon_w$ for all $i$ in the regime,
then the mean excess over the state-optimal weights is
$\frac1{|S|}\sum_i[V_i(\operatorname{clip}\bar u_S) - V_i(w_i^*)] \le \varepsilon_w^2\max_i c_i$.
*Proof:* by the lemma with $v = \bar u_S$, each term is at most $c_i\varepsilon_w^2 \le (\max c)\,\varepsilon_w^2$. $\blacksquare$

(The program's v1 form, with the clipped $w_S$ in the hypothesis and regret measured against the unclipped $u_i$,
fails when the $u_i$ lie outside $[0,1]$: for $u = \{1.4, 1.2\}$ with equal $c$, $\bar u_S = 1.3$ is within 0.1 of both, but
$w_S = 1$ is up to 0.4 from them.)

**L10(iv).** If $u$ is an $L$-Lipschitz function of a profile in $[0,1]^p$ and the regimes are the $K = n^p$ cells
of a regular grid, then the mean excess over $w^*$ of the regime weights $\operatorname{clip}\bar u_S$ is $\le c_{\max}L^2p\,K^{-2/p}$.

*Proof.*

1. A grid cell has side $1/n$ and diameter $\sqrt p/n$.
2. Inside a cell, any two values of $u$ differ by at most $L\sqrt p/n$ (Lipschitz).
3. The regime weight $\bar u_S$ is a weighted mean of the cell's $u_i$, so it lies between their minimum and maximum;
   hence $|\bar u_S - u_i| \le L\sqrt p/n$ for every $i$ in the cell.
4. Apply the corrected L10(iii) with $\varepsilon_w = L\sqrt p/n$: excess $\le c_{\max}L^2p/n^2 = c_{\max}L^2pK^{-2/p}$. $\blacksquare$

**Why the data do not show this rate.** Its hypothesis is that $u$ is a function of the profile. The flat regret
curves and Q-N's "reduces" reading for logit $w^*$ (CONF-1, PRELIMINARY) say it is not; the floor of A4.3 then
dominates.

*Check:* "L10(i) corrected", "L10(i) as in v1", "P3(a) / L10(ii)", "L10(iii)", "L10(iv)", "P3(b)".

## A5. Horizons: L8 (law and bracket), L8′ (certified horizon), L9 (growth exponents)

### A5.1 L8, the horizon law

**Statement.** If the r.m.s. error is $E(H) = e_0 g_H$ with $g_H = e^{\Lambda H}$, then the (continuous)
first-passage horizon is $T = \Lambda^{-1}\ln(\theta'/e_0)$. Hence $dT/d\ln\theta' = 1/\Lambda$; $T$ increases with $\theta'$ and
decreases with $e_0$.

**Proof.**

1. Crossing condition: $e_0e^{\Lambda T} = \theta'$.
2. Take logarithms: $\ln e_0 + \Lambda T = \ln\theta'$, so $T = (\ln\theta' - \ln e_0)/\Lambda$.
3. Differentiate in $\ln\theta'$: $dT/d\ln\theta' = 1/\Lambda > 0$. Differentiate in $\ln e_0$: $-1/\Lambda < 0$. $\blacksquare$

In the study, $\theta' = \sqrt{\theta^2 - \rho^2}$ and the regression is on $\ln\theta$; the factor relating them is
$d\ln\theta'/d\ln\theta = \theta^2/(\theta^2 - \rho^2)$ (at most 1.06 under the rule $\theta \ge 3\sqrt2\rho$). See N5.

### A5.2 L8, the robust bracket

**Statement.** Suppose $(\Lambda - \epsilon)H \le \ln g_H \le (\Lambda + \epsilon)H$ for all $H$ in the window, with
$0 < \epsilon < \Lambda$, and $e_0 < \theta'$. Then

$$\frac{\ln(\theta'/e_0)}{\Lambda + \epsilon} \;\le\; T \;\le\; \frac{\ln(\theta'/e_0)}{\Lambda - \epsilon}\quad(+1\text{ step in discrete time}).$$

**Proof.**

1. **Lower.** If $H < \ln(\theta'/e_0)/(\Lambda + \epsilon)$, then $\ln g_H \le (\Lambda+\epsilon)H < \ln(\theta'/e_0)$, so
   $e_0g_H < \theta'$: not crossed yet. Hence $T \ge \ln(\theta'/e_0)/(\Lambda + \epsilon)$.
2. **Upper.** If $H > \ln(\theta'/e_0)/(\Lambda - \epsilon)$, then $\ln g_H \ge (\Lambda - \epsilon)H > \ln(\theta'/e_0)$, so crossed.
   The first integer above that value is at most that value plus 1. $\blacksquare$

**Use.** H1c's band $[0.8, 1.25]$ for $\bar\Lambda \cdot dT/d\ln\theta$ is a statement about how close to linear $\ln g_H$ stays
out to the crossing. N5 makes the exact version.

### A5.3 L8′, a certified horizon (Grönwall)

**Statement.** Let the vector field $f$ be $L_K$-Lipschitz on a convex set $\mathcal K$ that contains both the true and
the perturbed trajectory up to time $t$, and let the observable be $L_h$-Lipschitz. If the initial error is $\xi$,
then the observable's error is at most $L_h\lVert\xi\rVert e^{L_Kt}$, so the forecast stays within $\theta$ for all
$t < L_K^{-1}\ln(\theta/(L_h\lVert\xi\rVert))$.

**Proof.**

1. Let $y_1(t), y_2(t)$ solve $\dot y = f(y)$ with $y_2(0) - y_1(0) = \xi$. Let $\phi(t) = \lVert y_2(t) - y_1(t)\rVert$.
2. Integral form: $y_2(t) - y_1(t) = \xi + \int_0^t (f(y_2) - f(y_1))\,d\tau$. Take norms, use F6 and the Lipschitz bound:
   $\phi(t) \le \lVert\xi\rVert + L_K\int_0^t\phi(\tau)\,d\tau$.
3. **Grönwall.** Let $\Psi(t) = \int_0^t\phi$. Step 2 says $\Psi'(t) \le \lVert\xi\rVert + L_K\Psi(t)$. Multiply by $e^{-L_Kt}$:
   $(e^{-L_Kt}\Psi)' \le \lVert\xi\rVert e^{-L_Kt}$. Integrate from 0: $e^{-L_Kt}\Psi(t) \le \lVert\xi\rVert(1 - e^{-L_Kt})/L_K$.
   So $L_K\Psi(t) \le \lVert\xi\rVert(e^{L_Kt} - 1)$ and, back in step 2, $\phi(t) \le \lVert\xi\rVert e^{L_Kt}$.
4. Observable error $\le L_h\phi(t) \le L_h\lVert\xi\rVert e^{L_Kt}$; solve $L_h\lVert\xi\rVert e^{L_Kt} = \theta$ for $t$. $\blacksquare$

**Size on Lorenz-63.** A bound on the Jacobian's Frobenius norm over the attractor's bounding box gives
$L_K \approx 50$, against $\lambda_{\max} = 0.905$. For a 1% seed and $\theta = 0.2$ (both in units of $\sigma_x$) the
certified horizon is 0.054 LT, against 3.0 LT from the linearized law: about 55 times shorter. It is rigorous but
useless for allocation; this is why the study relies on the linearized law and tests it (H1c).

### A5.4 L9, growth exponents

**Statement.** For growth factors $g_1, \dots, g_M > 0$ over a horizon $H$:
$\frac{1}{2H}\cdot\frac1M\sum_i\ln g_i^2 \le \frac1{2H}\ln\bigl(\frac1M\sum_i g_i^2\bigr)$, with equality iff all $g_i$ are equal.

**Proof.** Apply F9 to $y_i = g_i^2$ and divide by $2H > 0$. $\blacksquare$

**Meaning.** The finite-time exponent that averages logarithms never exceeds the mean-square exponent that the
horizon law uses. Not computed in the study.

*Check:* "L8", "L8 bracket", "L8′", "L9".

## A6. Seeds and observability: L1 to L4

### A6.1 L1, seed × amplifier with an explicit remainder

**Statement.** Let $F = \tilde h\circ\Phi^H$ be twice differentiable on the segment from $s$ to $s + \xi$, with
$\lVert D^2F\rVert \le M_2$ there. Then $|F(s + \xi) - F(s) - \Gamma_H\xi| \le \tfrac{M_2}{2}\lVert\xi\rVert^2$.

**Proof.**

1. Define $\varphi(t) = F(s + t\xi)$ for $t \in [0,1]$.
2. Chain rule: $\varphi'(t) = DF(s + t\xi)\,\xi$, so $\varphi'(0) = \Gamma_H\xi$; and $\varphi''(t) = \xi^\top D^2F(s+t\xi)\,\xi$.
3. F8: $\varphi(1) = \varphi(0) + \varphi'(0) + \tfrac12\varphi''(\tau)$, i.e. $F(s+\xi) - F(s) - \Gamma_H\xi = \tfrac12\xi^\top D^2F\,\xi$.
4. $|\xi^\top D^2F\,\xi| \le \lVert D^2F\rVert\,\lVert\xi\rVert^2 \le M_2\lVert\xi\rVert^2$. $\blacksquare$

**Consequence.** $e_C = \Gamma_H(a - s) + \xi_{\text{copied}} + r_a$ and $e_P = \Gamma_H(\hat s - s) + r_{\hat s}$ with
$|r| \le \tfrac{M_2}{2}\lVert\text{seed}\rVert^2$: each error is seed times amplifier plus a quadratic remainder.

**Data.** CONF-1 (PRELIMINARY), H1b (PLP slope): pass on Chua, inconclusive on Lorenz-63, fail on Rössler.

### A6.2 L2, Gauss–Markov

**Statement.** Let $J \in \mathbb{R}^{D\times m}$ have full column rank and $J^+ = (J^\top J)^{-1}J^\top$.

- (a) $J^+J = I$.
- (b) $J^+J^{+\top} = (J^\top J)^{-1}$, and $\operatorname{tr}(J^+J^{+\top}) = \sum_j\sigma_j^{-2}$ (singular values $\sigma_j$ of $J$).
- (c) Every left inverse $L$ ($LJ = I$) has $LL^\top \succeq (J^\top J)^{-1}$, with equality iff $L = J^+$.
- (d) If $\eta$ has mean 0 and covariance $\rho^2I$, then $\operatorname{Cov}(L\eta) = \rho^2LL^\top$; the least-squares estimator has the
  smallest error covariance among linear unbiased estimators.

**Proof.**

1. (a) $J^+J = (J^\top J)^{-1}J^\top J = I$.
2. (b) $J^+J^{+\top} = (J^\top J)^{-1}J^\top\,J(J^\top J)^{-1} = (J^\top J)^{-1}$ (F10: $(J^\top J)^{-1}$ is symmetric). Write the SVD
   $J = U\Sigma W^\top$; then $J^\top J = W\Sigma^2W^\top$, $(J^\top J)^{-1} = W\Sigma^{-2}W^\top$, whose trace is $\sum\sigma_j^{-2}$.
3. (c) Let $Z = L - J^+$. Then $ZJ = LJ - J^+J = I - I = 0$. Hence $ZJ^{+\top} = ZJ(J^\top J)^{-1} = 0$ and likewise
   $J^+Z^\top = 0$. Expand $LL^\top = (J^+ + Z)(J^+ + Z)^\top = J^+J^{+\top} + J^+Z^\top + ZJ^{+\top} + ZZ^\top = (J^\top J)^{-1} + ZZ^\top$.
   $ZZ^\top \succeq 0$ (F10), and it is 0 iff $Z = 0$.
4. (d) F13 gives $\operatorname{Cov}(L\eta) = \rho^2LL^\top$; combine with (c). A linear estimator $L(Js + \eta)$ is unbiased iff $LJ = I$. $\blacksquare$

**Data.** The estimator-efficiency check V7 and the validation gate pass on all three systems.

### A6.3 L3, the forward observability formula and its invariance

**Statement.**

- (a) If $J = AQ^{-1}$ with $Q$ invertible and $A^\top A$ invertible, then $(J^\top J)^{-1} = Q(A^\top A)^{-1}Q^\top$.
- (b) **(Strengthened.)** In whitened coordinates $\nu^2 = \operatorname{tr}[(J^\top J)^{-1}C^{-1}]$, where $C$ is the attractor
  covariance in the original coordinates. This number is unchanged by every invertible affine change of
  coordinates $s \mapsto As + b$.

**Proof.**

1. (a) $J^\top J = Q^{-\top}A^\top AQ^{-1}$. Invert with F10: $(J^\top J)^{-1} = Q(A^\top A)^{-1}Q^\top$.
2. (b), the formula. Whitened coordinates are $\bar s = C^{-1/2}(s - \mu)$, so $s = \mu + C^{1/2}\bar s$, and the Jacobian
   with respect to $\bar s$ is $\bar J = JC^{1/2}$. Then $(\bar J^\top\bar J)^{-1} = C^{-1/2}(J^\top J)^{-1}C^{-1/2}$ and, by trace
   cyclicity, $\nu^2 = \operatorname{tr}[(J^\top J)^{-1}C^{-1/2}C^{-1/2}] = \operatorname{tr}[(J^\top J)^{-1}C^{-1}]$.
3. (b), the invariance. New coordinates $s' = As + b$: the Jacobian becomes $J' = JA^{-1}$ and the covariance
   $C' = ACA^\top$. Then $(J'^\top J')^{-1} = A(J^\top J)^{-1}A^\top$ and $C'^{-1} = A^{-\top}C^{-1}A^{-1}$. Multiply:
   $(J'^\top J')^{-1}C'^{-1} = A(J^\top J)^{-1}C^{-1}A^{-1}$. Trace cyclicity removes $A$ and $A^{-1}$. $\blacksquare$

**Note on the v1 erratum.** The erratum restricted L3 to orthogonal maps. That restriction applies to the
program's literal form $\operatorname{tr}[W(J^\top J)^{-1}W^\top]$ with $W \mapsto UW$, which a shear changes (2.22 to 4.17 in the
check). The quantity the study computes is the trace form of (b), which is affine-invariant.

### A6.4 L4, delay distance bounds the latent mismatch

**Statement.** Let $G$ be the delay map. Suppose $\lVert J(s)v\rVert \ge \sigma_m\lVert v\rVert$ for all $v$ (smallest singular value
$\sigma_m$ at $s$), $\lVert D^2G\rVert \le L_2$ on the segment from $s$ to $a$, and $d := \lVert a - s\rVert \le \sigma_m/L_2$. With noisy
delay vectors $X_t = G(s) + \eta_t$, $X_a = G(a) + \eta_a$ and recurrence distance $R = \lVert X_t - X_a\rVert$:

$$\lVert a - s\rVert \le \frac{2\,(R + \lVert\eta_t - \eta_a\rVert)}{\sigma_m}.$$

**Proof.**

1. Taylor with integral remainder (vector form): $G(a) - G(s) = J(s)(a - s) + r$, where
   $r = \int_0^1(1 - t)\,D^2G(s + t(a - s))[a - s, a - s]\,dt$. Here $\lVert D^2G\rVert$ is the norm of the second derivative as a
   bilinear map, $\lVert D^2G[v, v]\rVert \le \lVert D^2G\rVert\lVert v\rVert^2$. So $\lVert r\rVert \le L_2d^2\int_0^1(1-t)\,dt = \tfrac{L_2}{2}d^2$. (Applying the scalar form A6.1
   coordinate by coordinate would cost an extra factor $\sqrt D$.)
2. Reverse triangle (F6): $\lVert G(a) - G(s)\rVert \ge \lVert J(s)(a-s)\rVert - \lVert r\rVert \ge \sigma_md - \tfrac{L_2}{2}d^2$.
3. Since $d \le \sigma_m/L_2$, $\tfrac{L_2}{2}d^2 \le \tfrac{\sigma_m}{2}d$, so $\lVert G(a) - G(s)\rVert \ge \tfrac{\sigma_m}{2}d$.
4. The clean distance relates to the noisy one: $G(s) - G(a) = (X_t - X_a) - (\eta_t - \eta_a)$, so by F6
   $\lVert G(a) - G(s)\rVert \le R + \lVert\eta_t - \eta_a\rVert$.
5. Combine 3 and 4: $\tfrac{\sigma_m}{2}d \le R + \lVert\eta_t - \eta_a\rVert$. Rearrange. $\blacksquare$

**Use.** This is why the analog proxy is built from $R\hat\nu$ rather than $R$ alone. DEV-0 (DEVELOPMENT) fits the
same proxy constant, about 0.27, on all three systems.

*Check:* "L1" (two), "L2(a)–(c)", "L2(d)", "L3", "L3 (strengthened)", "L3 (literal form)", "L4".

---

# Part B. Proposed new theorems that tighten the results

Each item gives: the statement, a complete proof, what it tightens or explains, and an exploratory test on
development seeds. All eight are checked in `proposed_checks.py` (14 checks with the A4.4 lemma, all pass). They are post-freeze
and exploratory; none changes a pre-registered criterion.

| # | Result | What it tightens | Grade |
| --- | --- | --- | --- |
| N1 | Curvature under the study's conditioning | Replaces the copied-noise justification of P1(a) | Theorem |
| N2 | Exact weight under stable retrieval; when $w^* = 0$ is possible; noise matching needs switching | Explains Q-N's "w* = 0" result and H2e | Theorem |
| N3 | Weight range from the seed-covariance pencil; the analog seed is rank one | Quantifies the H2a failure | Theorem |
| N4 | Correlation-adjusted horizon gain | Links noise matching (H2e) to the horizon; sharpens P1(d′) | Theorem |
| N5 | Local horizon law | Reinterprets the H1c failure on Lorenz-63 | Theorem |
| N6 | The regime floor is a weighted unexplained variance | Predicts the flat regret from an $R^2$ | Theorem |
| N7 | Exact per-competitor switching probabilities | Usually sharper than Markov in P2(b); a cheaper $\hat N$ | Theorem |
| N8 | The weight rises with noise (comparative statics) | Gives H2b(i), the strongest result, a theorem | Theorem, under stated conditions |

## N1. Curvature under conditioning on the library

**Statement.** With expectations over query-noise draws at a fixed library,
$c = \mathbb{E}[(e_C - e_P)^2] \ge \operatorname{Var}(e_C - e_P)$. In particular, if retrieval does not change across the draws
(so $e_C$ is one fixed number), then $c \ge \operatorname{Var}(e_P)$, which is positive whenever PLP's forecast responds to the
query noise at all.

**Proof.**

1. A1.2 step 5: $c = \mathbb{E}[(e_C - e_P)^2]$.
2. F3 with $Z = e_C - e_P$: $\mathbb{E}[Z^2] = \operatorname{Var}(Z) + (\mathbb{E}Z)^2 \ge \operatorname{Var}(Z)$.
3. If $e_C$ is constant across draws, adding a constant does not change a variance:
   $\operatorname{Var}(e_C - e_P) = \operatorname{Var}(-e_P) = \operatorname{Var}(e_P)$. $\blacksquare$

**What it tightens.** P1(a)'s strict convexity no longer rests on an orthogonality hypothesis the design does not
guarantee (A1.6). To first order $\operatorname{Var}(e_P) = \rho^2\lVert\Gamma_HJ^+\rVert^2$ (A3.5), so $c$ is bounded below by PLP's noise
sensitivity. **Test:** report the fraction of states with $c < 10^{-12}$ (it should be 0) next to the existing
`handling` counters.

## N2. Stable retrieval: the exact weight, and when $w^* = 0$ can happen

**Setting.** At a state, let $S$ be the event "retrieval differs from the no-noise analog". Off $S$, CP's error is
one fixed number $\mu$ (the analog's amplified mismatch plus its copied noise, both fixed when the analog is
fixed). Let $m = \mathbb{E}[e_P]$ (PLP's bias at that state) and $\sigma^2 = \operatorname{Var}(e_P)$.

**Statement.**

- (a) If $\Pr(S) = 0$ (stable retrieval), then
  $u = \dfrac{m^2 + \sigma^2 - \mu m}{(\mu - m)^2 + \sigma^2}$. If moreover PLP is unbiased ($m = 0$), then
  $u = \sigma^2/(\mu^2 + \sigma^2)$, which lies strictly between 0 and 1 (when $\mu \ne 0$ and $\sigma > 0$).
- (b) Under stable retrieval, with $\sigma > 0$ (PLP's forecast responds to the query noise; then $c > 0$ by N1),
  $w^* = 0$ implies $\mu m > 0$ and $\sigma \le |\mu|/2$. So with stable retrieval, CP can be given zero weight only if PLP is biased in the same direction as CP's error and PLP's spread is at most half
  of CP's error.
- (c) In general (switching allowed), $C = \mu m + \mathbb{E}[(e_C - \mu)\,e_P\,\mathbf{1}_S]$, and
  $|C - \mu m| \le \sqrt{\mathbb{E}[(e_C - \mu)^2\mathbf{1}_S]}\;\sqrt{\mathbb{E}[e_P^2\mathbf{1}_S]}$.
  Without switching, the cross-moment is exactly $\mu m$; it is zero for an unbiased PLP. **Noise matching
  ($C > 0$ beyond $\mu m$) can only come from switching.**

**Proof.**

1. (a) With $e_C = \mu$ on every draw: $E_C = \mu^2$, $C = \mathbb{E}[\mu e_P] = \mu m$, and $E_P = m^2 + \sigma^2$ (F3).
2. $E_P - C = m^2 + \sigma^2 - \mu m$ and $c = \mu^2 + m^2 + \sigma^2 - 2\mu m = (\mu - m)^2 + \sigma^2$. Divide.
3. With $m = 0$: $u = \sigma^2/(\mu^2 + \sigma^2)$. Numerator and denominator are positive and the denominator is
   larger, so $0 < u < 1$.
4. (b) By A1.3, $w^* = 0 \iff C \ge E_P \iff \mu m \ge m^2 + \sigma^2$.
5. The right side is $> 0$ (as $\sigma > 0$), so $\mu m > 0$: $\mu$ and $m$ have the same sign.
6. Write $|\mu m| = |\mu||m|$. The condition is $\sigma^2 \le |\mu||m| - m^2 = |m|(|\mu| - |m|)$.
7. For fixed $|\mu|$, the product $|m|(|\mu| - |m|)$ is largest at $|m| = |\mu|/2$, with value $\mu^2/4$. So
   $\sigma^2 \le \mu^2/4$, i.e. $\sigma \le |\mu|/2$.
8. (c) Write $e_C = \mu + (e_C - \mu)\mathbf{1}_S$ (off $S$ the second term is 0). Multiply by $e_P$ and take
   expectations: $C = \mu m + \mathbb{E}[(e_C - \mu)\,e_P\,\mathbf{1}_S]$.
9. Since $\mathbf{1}_S = \mathbf{1}_S^2$, the last term is $\mathbb{E}[((e_C - \mu)\mathbf{1}_S)(e_P\mathbf{1}_S)]$; apply Cauchy–Schwarz (F5). $\blacksquare$

**What it explains.**

- **The "w* = 0" result.** Q-N found that noise sensitivity $N$ adds substantial information about *whether*
  $w^* = 0$ (CONF-1, PRELIMINARY: "substantial" on all three systems). N2(b) says why: with stable retrieval
  ($N = 0$), an unbiased PLP and $\sigma > 0$, $w^* = 0$ is impossible. Zero weight needs switching (large $N$) or a biased PLP.
- **The chain for noise matching (H2e).** Margin $\Delta$ small relative to $\rho$ ⟶ switching (P2, N7) ⟶ cross-moment
  beyond $\mu m$ (N2(c)) ⟶ lower weight (P1(a)). Each arrow is now a theorem.
- **A4's form.** Under stable retrieval with unbiased PLP, $w^* = \sigma^2/(\mu^2 + \sigma^2)$ exactly: the closed form, but with
  amplified quantities $\mu = \Gamma_H(a - s) + \xi$ and $\sigma^2 = \Gamma_H\Sigma_s\Gamma_H^\top$, not the latent seed norms. N3 shows what
  that difference costs.

**Tests (DEV seeds).**

- Among states with no switching across the 200 draws (DEV-0 has 75–90% of states with at least one switch, so
  the rest), count those with $w^* = 0$ and check N2(b)'s two conditions on each.
- For all states, compute both sides of N2(c) and report the share of $C - \mu m$ explained by switching draws.

## N3. The weight's range is set by the seed-covariance pencil

**Setting.** First order (A2.1) with uncorrelated seeds ($K = 0$), and $\Sigma_s$ positive definite. Then for an
amplifier direction $\Gamma$,
$w^*(\Gamma) = \dfrac{\Gamma\Sigma_s\Gamma^\top}{\Gamma\Sigma_a\Gamma^\top + \Gamma\Sigma_s\Gamma^\top}$.

**Statement.**

- (a) Let $\lambda_{\min} \le \lambda_{\max}$ be the extreme eigenvalues of $\Sigma_s^{-1/2}\Sigma_a\Sigma_s^{-1/2}$. Then
  $\dfrac{1}{1 + \lambda_{\max}} \le w^*(\Gamma) \le \dfrac1{1 + \lambda_{\min}}$ for every $\Gamma$, and both ends are attained. So the range of
  $w^*$ over horizons (and over instabilities) can be as large as $\frac1{1+\lambda_{\min}} - \frac1{1+\lambda_{\max}}$, and is 0 iff
  $\lambda_{\min} = \lambda_{\max}$, i.e. iff $\Sigma_a \propto \Sigma_s$ (separation, L6).
- (b) If the analog's mismatch is one fixed nonzero vector $d = a - s$ (stable retrieval), then $\Sigma_a = dd^\top$ has rank one,
  $\lambda_{\max} = d^\top\Sigma_s^{-1}d$ and $\lambda_{\min} = 0$ (for $m \ge 2$). So
  $w^*(\Gamma) = \dfrac{1}{1 + (\Gamma d)^2/(\Gamma\Sigma_s\Gamma^\top)}$, ranging over $\bigl[\frac1{1 + d^\top\Sigma_s^{-1}d},\,1\bigr]$.

**Proof.**

1. Divide numerator and denominator of $w^*(\Gamma)$ by $\Gamma\Sigma_s\Gamma^\top > 0$:
   $w^* = 1/(1 + R(\Gamma^\top))$ with $R(v) = v^\top\Sigma_av/v^\top\Sigma_sv$.
2. By F11 (with $A = \Sigma_a$, $B = \Sigma_s$), $R$ takes exactly the values in $[\lambda_{\min}, \lambda_{\max}]$, attaining both.
3. $1/(1 + R)$ decreases in $R$, so $w^*$ ranges over $[1/(1+\lambda_{\max}), 1/(1+\lambda_{\min})]$, attaining both ends.
4. The range is 0 iff $\lambda_{\min} = \lambda_{\max} =: \lambda$, iff $\Sigma_s^{-1/2}\Sigma_a\Sigma_s^{-1/2} = \lambda I$, iff $\Sigma_a = \lambda\Sigma_s$.
5. (b) $\Sigma_s^{-1/2}dd^\top\Sigma_s^{-1/2} = zz^\top$ with $z = \Sigma_s^{-1/2}d$. A rank-one matrix $zz^\top$ has one eigenvalue
   $\lVert z\rVert^2 = d^\top\Sigma_s^{-1}d$ (eigenvector $z$) and $m - 1$ zero eigenvalues (any vector orthogonal to $z$).
6. $\Gamma\Sigma_a\Gamma^\top = \Gamma dd^\top\Gamma^\top = (\Gamma d)^2$. Substitute in step 1. $\blacksquare$

**What it tightens.** L6 says only "proportional ⟹ constant". N3 says *how much* $w^*$ can move, from two numbers
per state. Under stable retrieval the analog seed is a single vector, never proportional to the estimation
cloud, so **separation cannot hold exactly** for CP. $w^*(H)$ follows the angle between the amplifier and the
fixed mismatch $d$: it is near 1 when $\Gamma_H$ is nearly orthogonal to $d$, and smallest when $\Gamma_H$ lines up with
$\Sigma_s^{-1}d$. As $\Gamma_H$ aligns with the leading (Oseledets) direction $v$, $w^*(H) \to 1/(1 + (vd)^2/(v\Sigma_sv^\top))$.

**Test (DEV seeds).** Per state, store $d$ (or $\Sigma_a$), $\Sigma_s$ and $\Gamma_H$ at 1, 2, 4 LT. Report: the predicted
$w^*$ from step 6 against the measured $w^*$; and the H2a(i) range regressed on the pencil spread
$\frac1{1+\lambda_{\min}} - \frac1{1+\lambda_{\max}}$ (or on the angle between $\Gamma_H$ and $d$).

## N4. Correlation-adjusted horizon gain

**Statement.** At one horizon, suppose $c > 0$ and $C \le \min(E_C, E_P)$. Let $r = \min(E_C,E_P)/\max(E_C,E_P) \in (0,1]$ and
$\varrho = C/\sqrt{E_CE_P}$ (the error correlation, using raw moments). Then

$$\frac{\min_w V}{\min(E_C, E_P)} \;=\; f(\varrho, r) \;:=\; \frac{1 - \varrho^2}{1 + r - 2\varrho\sqrt r}.$$

- (a) $f$ increases in $\varrho$ on $[-1, \sqrt r]$, with $f(-1) = 0$, $f(0) = 1/(1 + r) \ge \tfrac12$ and $f(\sqrt r) = 1$.
- (b) If $f \ge f_0$ at the step $T_m(\theta/\sqrt{f_0})$, then $0 \le T_h(\theta) - T_m(\theta) \le T_m(\theta/\sqrt{f_0}) - T_m(\theta)$.
  Under exponential growth the gain is at most $\ln(1/f_0)/(2\Lambda)$.

**Proof.**

1. Let $b = \min(E_C,E_P)$ and $a = \max(E_C, E_P)$ (the problem is symmetric, A1.4 step 1). Then $C = \varrho\sqrt{ab}$.
2. $C \le b$ puts the optimum inside $[0,1]$ (A1.3), so $\min V = V(u) = (ab - C^2)/(a + b - 2C) = ab(1 - \varrho^2)/(a + b - 2\varrho\sqrt{ab})$.
3. Divide by $b$ and then numerator and denominator by $a$: $\min V/b = (1 - \varrho^2)/(1 + b/a - 2\varrho\sqrt{b/a}) = f(\varrho, r)$.
4. (a) Let $s = \sqrt r$ and $D(\varrho) = 1 + s^2 - 2\varrho s$. Quotient rule:
   $f' = [-2\varrho D + 2s(1 - \varrho^2)]/D^2$. Expand the bracket:
   $-2\varrho - 2\varrho s^2 + 4\varrho^2s + 2s - 2\varrho^2s = 2(s - \varrho) - 2\varrho s(s - \varrho) = 2(s - \varrho)(1 - \varrho s)$.
   On $[-1, s]$ both factors are $\ge 0$ (since $\varrho s \le s^2 \le 1$), so $f' \ge 0$. The three values follow by substitution
   (at $\varrho = s$: numerator $1 - s^2$, denominator $1 + s^2 - 2s^2 = 1 - s^2$).
5. (b) Same as A1.8 with $\tfrac12$ replaced by $f_0$: at $H_1 = T_m(\theta/\sqrt{f_0})$, $m(H_1)^2 > \theta^2/f_0$, so
   $h(H_1)^2 = f\,m(H_1)^2 > f_0\,\theta^2/f_0 = \theta^2$; the lower bound is A1.8 step 5. Under exponential growth
   $T_m(\theta/\sqrt{f_0}) - T_m(\theta) = \ln(1/\sqrt{f_0})/\Lambda$. $\blacksquare$

**What it tightens.**

- P1(c) and P1(d′) are the case $\varrho \ge 0$, where $f \ge 1/(1 + r) \ge \tfrac12$. N4 is exact, not a bound.
- **Noise matching erodes the horizon gain.** As the library grows, $\varrho$ rises (H2e passes on all three systems,
  CONF-1, PRELIMINARY), $f$ rises toward 1 and the gain shrinks toward 0. The hybrid horizon gain is therefore
  predicted to *fall* with library size: a sharp, testable consequence linking RQ2's mechanism to horizons.
- **Negative correlation is where blending pays.** For $\varrho < 0$, $f < 1/(1+r)$ and the gain can exceed
  $\ln 2/(2\Lambda)$ without limit (P1(e)). DEV-0 (DEVELOPMENT): 22–32% of states have $C < 0$ at some horizon.

**Tests (DEV seeds).** Per state at the crossing, compute $f$ and compare $T_m(\theta/\sqrt f) - T_m(\theta)$ with the realized
characteristic gain. Plot the median gain against $N_{lib}$; N4 predicts a decrease. Describe the $C < 0$ states by
the four conditions.

## N5. The local horizon law

**Statement.** Let the r.m.s. error $E(H)$ be differentiable and increasing near its crossing, with local growth
rate $\Lambda_{\text{loc}}(H) = d\ln E/dH$. Then the characteristic horizon satisfies

$$\frac{dT}{d\ln\theta'} = \frac{1}{\Lambda_{\text{loc}}(T)}, \qquad \frac{dT}{d\ln\theta} = \frac{\theta^2}{\theta^2 - \rho^2}\cdot\frac{1}{\Lambda_{\text{loc}}(T)}.$$

So H1c's statistic $\bar\Lambda\cdot dT/d\ln\theta$ estimates $\dfrac{\theta^2}{\theta^2-\rho^2}\cdot\dfrac{\bar\Lambda}{\Lambda_{\text{loc}}(T)}$: the ratio of the growth rate
over the first LT to the growth rate of the error at the crossing.

**Proof.**

1. $T$ is defined by $\Psi(T, \ell) := \ln E(T) - \ell = 0$ with $\ell = \ln\theta'$.
2. F14: $dT/d\ell = -\partial_\ell\Psi/\partial_T\Psi = -(-1)/\Lambda_{\text{loc}}(T) = 1/\Lambda_{\text{loc}}(T)$.
3. Chain rule with $\ln\theta' = \tfrac12\ln(\theta^2 - \rho^2)$: $d\ln\theta'/d\ln\theta = \theta\cdot\tfrac12\cdot 2\theta/(\theta^2 - \rho^2) = \theta^2/(\theta^2-\rho^2)$. $\blacksquare$

**What it explains.** The horizon law of L8 is the special case $\Lambda_{\text{loc}} \equiv \Lambda$. H1c's fail on Lorenz-63
(CONF-1, PRELIMINARY; DEV-0 value 0.60) then reads: the error grows about $1/0.60 \approx 1.7$ times faster near the
crossing (2 to 3 LT) than the amplifier does over the first LT. Two sources can cause it, and N5 separates
neither from the other on its own:

- the growth rate changes with time (non-uniform stretching on the attractor);
- the error's growth differs from the amplifier's because the seeds are anisotropic (N3): $E(H)^2 = \Gamma_H\Sigma\Gamma_H^\top$
  grows at the rate of $\Gamma_H$ *in the seed's direction*, not at the rate of $\lVert\Gamma_H\rVert$.

**Test (DEV seeds).** Per state, estimate $\Lambda_{\text{loc}}(T)$ from the stored error curve by a local slope around $T$,
and check that $\bar\Lambda\cdot\widehat{dT/d\ln\theta}$ matches $\bar\Lambda/\Lambda_{\text{loc}}(T)$ times the noise factor. Then split
$\Lambda_{\text{loc}}$ into the amplifier's local rate and the seed-direction effect.

## N6. The regime floor is a weighted unexplained variance

**Setting.** Over states, let $\bar u(F) = \mathbb{E}[cu\mid F]/\mathbb{E}[c\mid F]$ (best profile-based weight, A4.3) and
$\bar u = \mathbb{E}[cu]/\mathbb{E}[c]$ (best single global weight). Assume no clipping: $u$, $\bar u(F)$ and $\bar u$ all lie in $[0,1]$.

**Statement.**

$$\underbrace{\mathbb{E}[c\,(u - \bar u(F))^2]}_{\text{floor}} \;=\; (1 - R_c^2)\;\underbrace{\mathbb{E}[c\,(u - \bar u)^2]}_{\text{excess of the best global weight}},$$

where $R_c^2$ is the curvature-weighted $R^2$ of $u$ on $F$: the share of the global weight's excess that the profile can
remove. Equivalently (a Pythagoras identity), $\mathbb{E}[c(u - \bar u)^2] = \mathbb{E}[c(\bar u(F) - \bar u)^2] + \mathbb{E}[c(u - \bar u(F))^2]$.

**Proof.**

1. By A4.1, a rule $w$ has excess $\mathbb{E}[c(w - u)^2]$ over $w^* = u$ (no clipping). For $w = \bar u(F)$ that is the floor of
   A4.3; for $w = \bar u$ it is the global weight's excess.
2. Expand $u - \bar u = (u - \bar u(F)) + (\bar u(F) - \bar u)$ and square:
   $\mathbb{E}[c(u - \bar u)^2] = \mathbb{E}[c(u - \bar u(F))^2] + 2\mathbb{E}[c(u - \bar u(F))(\bar u(F) - \bar u)] + \mathbb{E}[c(\bar u(F) - \bar u)^2]$.
3. The middle term is 0: by F12 with $g(F) = \bar u(F) - \bar u$,
   $\mathbb{E}[c(u - \bar u(F))g(F)] = \mathbb{E}[g(F)\,(\mathbb{E}[cu\mid F] - \bar u(F)\mathbb{E}[c\mid F])] = 0$, by the definition of $\bar u(F)$.
4. Define $R_c^2 = \mathbb{E}[c(\bar u(F) - \bar u)^2]/\mathbb{E}[c(u - \bar u)^2]$. Then step 2 gives
   floor $= (1 - R_c^2)\,\mathbb{E}[c(u - \bar u)^2]$. $\blacksquare$

**What it tightens.** The flat regret-versus-$K$ curves become a *prediction*: no regime map, with any number of
regimes, can remove more than $R_c^2$ of the global weight's excess, where $R_c^2$ is the best achievable weighted fit
of $u$ on the profile. Q-N's regressors already estimate a closely related $R^2$ (on logit $w^*$, interior states).
With clipping (22–36% of states have $w^* = 0$) the identity becomes the inequality of A4.3; N2 says the clipped
states are the switching or biased ones, which suggests treating them as a separate regime.

**Test (DEV seeds).** Fit $\bar u(F)$ by curvature-weighted regression of $u$ on $F$ (oracle and deployable). Compare the
predicted floor $(1 - \hat R_c^2)\times$ (A2's excess) with the observed regret plateau at large $K$.

## N7. Exact per-competitor switching probabilities

**Statement.** Let $\eta \sim N(0, \rho^2I_D)$. For each competitor $j \ne 1$ let
$p_j = \bar\Phi\!\left(\dfrac{r_j^2 - r_1^2}{2\rho\,\lVert X_j - X_1\rVert}\right)$, where $r_j = \lVert x - X_j\rVert$ and $\bar\Phi$ is the standard
normal upper tail. Then

$$\max_j p_j \;\le\; \Pr(\text{switch}) \;\le\; \min\Bigl(1, \sum_{j\ne1}p_j\Bigr), \qquad\text{and}\qquad p_j \le \bar\Phi\!\left(\frac{\Delta}{2\rho}\right)\ \text{for every } j.$$

Also, exactly, $\Pr(\lVert\eta\rVert \ge \Delta/2) = \Pr(\chi^2_D \ge \Delta^2/(4\rho^2))$.

**Proof.**

1. The noisy query is closer to $X_j$ than to $X_1$ iff $\lVert x + \eta - X_j\rVert^2 < \lVert x + \eta - X_1\rVert^2$.
2. Expand both squares: $\lVert x - X_j\rVert^2 + 2\langle\eta, x - X_j\rangle + \lVert\eta\rVert^2 < \lVert x - X_1\rVert^2 + 2\langle\eta, x - X_1\rangle + \lVert\eta\rVert^2$.
3. Cancel $\lVert\eta\rVert^2$ and rearrange: $2\langle\eta, X_j - X_1\rangle > r_j^2 - r_1^2$.
4. By F13, $\langle\eta, X_j - X_1\rangle \sim N(0, \rho^2\lVert X_j - X_1\rVert^2)$. So the probability of the event in step 3 is
   $\bar\Phi\bigl((r_j^2 - r_1^2)/(2\rho\lVert X_j - X_1\rVert)\bigr) = p_j$, exactly.
5. "Switch" is the union over $j$ of the events "closer to $X_j$ than to $X_1$": if the retrieved vector is $X_j \ne X_1$,
   that event holds for this $j$; conversely, if any such event holds, $X_1$ is not the nearest. The probability
   of a union is at most the sum (union bound) and at least the largest member.
6. **Dimension-free bound on each $p_j$.** $r_j^2 - r_1^2 = (r_j - r_1)(r_j + r_1)$, and $\lVert X_j - X_1\rVert \le r_j + r_1$ (F6
   through $x$). So the argument of $\bar\Phi$ is at least $(r_j - r_1)/(2\rho) \ge \Delta/(2\rho)$; $\bar\Phi$ decreases, giving the bound.
7. The last identity: $\lVert\eta\rVert^2/\rho^2$ is a sum of $D$ squared independent standard normals, i.e. $\chi^2_D$. $\blacksquare$

**What it tightens.**

- P2(b) charged a factor $D$ ($4D\rho^2/\Delta^2$). Each half-space term costs at most $\bar\Phi(\Delta/(2\rho))$, exponentially small
  in $(\Delta/\rho)^2$ and free of $D$. The *sum* has one term per competitor, so it is not uniformly better than Markov:
  in the check it was smaller in 293 of 300 random states, and with many near-tied competitors it can exceed 1.
  The lower bound $\max_j p_j$ is new: P2 had none.
- **A better deployable $\hat N$.** The $p_j$ need only the library and the query: no Monte Carlo, and no bias from
  the 16 synthetic perturbations. This addresses the future-work item "a deployable $\hat N$ that estimates $N$
  without bias" (v3 §8). Only the few nearest competitors matter, so the sum is cheap.

**Test (DEV seeds).** Compute $\sum_j p_j$ (over, say, the 20 nearest competitors) from the clean query (oracle) and from
the observed query (deployable). Compare with the empirical switching rate over the 200 draws, and use
$\ln(\sum_j p_j)$ as a candidate fourth coordinate in Q-N (exploratory).

## N8. The weight rises with the noise level (comparative statics)

**Setting.** Stable retrieval, unbiased PLP to first order, and the study's common random numbers: all noise is a
fixed standard-normal draw scaled by $\rho$. Then, at one state and horizon:

- CP's error is $\mu(\rho) = A + \rho z$, where $A = \Gamma_H d$ is the amplified latent mismatch (independent of $\rho$
  while the analog index is fixed) and $\rho z$ is the copied noise;
- PLP's error variance is $\sigma^2 = \rho^2q$ with $q = \lVert\Gamma_HJ^+\rVert^2$ (A3.5).

**Statement.** $w^*(\rho) = \dfrac{q}{(A/\rho + z)^2 + q}$, and

$$\frac{dw^*}{d\rho} = \frac{2qA(A + \rho z)}{\rho^3\bigl((A/\rho + z)^2 + q\bigr)^2},$$

which is positive iff $A(A + \rho z) > 0$, i.e. unless the copied noise $\rho z$ overturns the amplified mismatch
(opposite sign and larger size). In particular $w^*$ increases with $\rho$ whenever $\rho|z| < |A|$.

**Proof.**

1. N2(a) with $m = 0$: $w^* = \sigma^2/(\mu^2 + \sigma^2) = \rho^2q/((A + \rho z)^2 + \rho^2q)$. Divide by $\rho^2$:
   $w^* = q/((A/\rho + z)^2 + q)$.
2. Let $X(\rho) = (A/\rho + z)^2$. Then $X'(\rho) = 2(A/\rho + z)\cdot(-A/\rho^2)$.
3. $dw^*/d\rho = -qX'/(X + q)^2 = 2q(A/\rho + z)A/(\rho^2(X+q)^2) = 2qA(A + \rho z)/(\rho^3(X+q)^2)$.
4. All factors except $A(A + \rho z)$ are positive. $\blacksquare$

**What it tightens.** H2b(i), "w* rises with noise", is supported (preliminary, unpromoted; pass on all three
systems). N8 turns it into a consequence of the first-order theory: in the stable-retrieval regime, the weight
rises with $\rho$ because PLP's error scales with $\rho$ while CP's amplified mismatch does not. At $H_{ref} = 1$ LT the
mismatch is amplified while the copied noise is not, so $|A| > \rho|z|$ is the typical case. The exceptions are
switching states, where the analog index itself changes with $\rho$.

**Library size (heuristic only).** With nested libraries the nearest delay distance $R$ cannot increase as $N_{lib}$
grows. L4 gives $\lVert d\rVert \le 2(R + \lVert\eta_t - \eta_a\rVert)/\sigma_m$ (inside its radius $\lVert d\rVert \le \sigma_m/L_2$), but the noise term changes
with the analog, so this bound is not guaranteed to fall; at best it falls in expectation. This is consistent with
the rising branch tested by H2b(ii), not a proof of it, and it does not predict the later fall, which N2(c) and N4
attribute to switching and noise matching.

**Test (DEV seeds).** In E1 (noise sweep), split states by whether the analog index is the same at all four noise
levels. N8 predicts a per-state rank correlation of $w^*$ with $\rho$ near +1 in the stable group and weaker in the
switching group.

---

# Part C. Tasks for the agent

All tasks run on development seeds (DEV-1 to DEV-8), carry the label `DEVELOPMENT (DEV-n): not a hypothesis test`,
and never touch the confirmatory seed, the sealed results or any pre-registered criterion. Each becomes a work
unit with acceptance criteria written in advance (`/work-unit`), reviewed independently (`/independent-review`).

## C1. Housekeeping (no new runs)

1. Copy `theorem_checks.py`, `proposed_checks.py` and this file to `docs/agent/notes/theorem_checks/`. They are
   verification records, not part of the `lpcstudy` package or its test suite. Run both once; record the summary
   lines (expected: 37/37 and 14/14).
2. Draft (do not apply) amendments to `theorem_program_lpc_v1.md` for the owner:
   - L3: the trace form is affine-invariant (A6.3); narrow the v1 erratum to the literal $W$ form.
   - L10(i): use the unclipped $u_i$ (A4.1).
   - P1(a): cite N1 for $c > 0$ instead of the copied-noise orthogonality (A1.6).
   - P1(d): "better forecaster" means the envelope (A1.7, fine print).
3. Draft a decision proposal (`docs/agent/notes/`) on whether the reported-only gain screen (WU-0002.15,
   DEC-0033) should use P1(d′), which needs no growth fit and $C \ge 0$ at one step only. Owner decides.

## C2. Store what the new results need (code change, DEV only)

Add an opt-in diagnostic output (off by default, so the frozen pipeline is unchanged) that writes, per test state
at the core cell:

- the per-horizon raw moments $E_C(H)$, $E_P(H)$, $C(H)$ for $H = 1, \dots, 240$;
- whether retrieval switched on each of the $M$ draws, the base analog's $\mu$ at $H_{ref}$, PLP's mean $m$ and variance $\sigma^2$;
- the mismatch vector $d = a - s$ (base analog), $\Sigma_s$, and $\Gamma_H$ at 1, 2 and 4 LT;
- the 20 nearest competitors' distances and pairwise gaps (for N7).

Acceptance: identical results with the option off (bitwise on the smoke preset); a unit test per new field against
an independent computation.

## C3. Exploratory measurements, in priority order

| Priority | Result | Measurement | What would count as support |
| --- | --- | --- | --- |
| 1 | N2 | Among no-switch states, the share with $w^* = 0$, and N2(b)'s two conditions on each; decompose $C - \mu m$ into switching draws | Every no-switch $w^* = 0$ state meets both conditions; switching explains most of $C - \mu m$ |
| 2 | N3 | Predicted $w^*(\Gamma_H)$ from $d$, $\Sigma_s$ against measured $w^*$ at 1, 2, 4 LT; H2a(i) range against the pencil spread | High rank correlation; the spread predicts the range |
| 3 | N4 | Gain predicted from $f$ at the crossing against realized gain; median gain against $N_{lib}$ | Close agreement; gain falls as $N_{lib}$ grows |
| 4 | P1(d′) | Per state, realized gain against $T_m(\sqrt2\theta) - T_m(\theta)$ where $C \ge 0$ at that step | 0 violations |
| 5 | N7 | $\sum_j p_j$ against the empirical switching rate; $\ln\sum_jp_j$ as an alternative fourth coordinate in Q-N | Calibrated switching probabilities; Q-N gain at least as large as with $\hat N$ |
| 6 | N5 | $\Lambda_{\text{loc}}(T)$ from the stored curves; check $\bar\Lambda\,dT/d\ln\theta \approx \bar\Lambda/\Lambda_{\text{loc}}(T)$ × noise factor | Agreement within the bootstrap interval |
| 7 | N6 | Weighted $R_c^2$ of $u$ on $F$; predicted floor against the regret plateau | Predicted floor matches the plateau |
| 8 | N8 | E1 states split by stable vs switching analog index; per-state rank correlation of $w^*$ with $\rho$ | Near +1 in the stable group |

Report each in one development note with the provenance of every number. No overall verdicts.

## C4. For the student (owner and mentor decide)

- **N2(a)** and **N4** are short, elegant and provable by hand with the tools of A1: good candidates for an
  extension slide.
- **P1(d′)** is a two-line strengthening of P1(d).
- Lean formalization stays deferred (D4). When it starts, the shortest targets are P1(a)–(c), P1(d′), P2(a), N2(a),
  N4(a) and N7 steps 1–5.

## C5. Do not

- Do not change any pre-registered hypothesis, band, level, block length or decision rule, or re-describe a
  sealed verdict. Results from Part B are exploratory and are never placed beside the sealed result.
- Do not run anything on the confirmatory seed. Do not rerun tests without a code change; use `/test-impact`.
- Do not claim a proposed theorem is "confirmed" by the data. Write "consistent with" or "not consistent with".

---

## Appendix: index of checks

| Section | Check names (`theorem_checks.py`) |
| --- | --- |
| A1 (P1) | P1(a) / L5 (×2), P1(b), P1(c) proof step, P1(c) / L7(i), P1(c) tightness, P1(e) / L7(iv), L7(iii), P1(d) / L7(ii), P1(d′) new, P1(d) vs P1(d′) |
| A2 (L6) | L6, L6 transient, L6 (hypothesis) |
| A3 (P2) | P2(a) / L11(b)(i), P2(a) tightness, P2(b) / L11(b)(ii), P2(c) / L11(b)(iii), L11(a) |
| A4 (P3) | L10(i) corrected, L10(i) as in v1, P3(a) / L10(ii), L10(iii), L10(iv), P3(b) |
| A5 (horizons) | L8, L8 bracket, L8′, L9 |
| A6 (seeds) | L1 (×2), L2(a)–(c), L2(d), L3, L3 (strengthened), L3 (literal form), L4 |

| Section | Check names (`proposed_checks.py`) |
| --- | --- |
| A4.4 | A4.4 lemma |
| N1 | N1 |
| N2 | N2(a), N2(b), N2(c) |
| N3 | N3(a), N3(b) |
| N4 | N4(a), N4(b) |
| N5 | N5, N5 noise factor |
| N6 | N6 |
| N7 | N7 |
| N8 | N8 |

Both scripts use fixed seeds (20261020 and 20261021) and run in under a minute each on two CPU cores.
