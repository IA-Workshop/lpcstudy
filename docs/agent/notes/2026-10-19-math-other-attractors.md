# Other attractors for the LPC study, and the soundness of Theorems P1 to P3

**DEVELOPMENT: not a hypothesis test.** Synthetic scratch seed 20261019 for every script; DEV-0 pilot leaves (`docs/study/pilot_results_v3_dev0_reference.json`) read only. No preset, no test tier, no GPU, no network. The confirmatory seed, flag, tool and run directory were not read, drawn or run. Every computation ran single-threaded at `nice -n 19` (`run.sh`) while the sealed run was in progress.

- **Date:** 2026-10-19. **Agent:** applied-mathematician (claude-fable-5-1). **Owner's instruction:** "research other attractors with different properties that could be used to explore the hypothesis further and if gaps exist, why the original theorem was unsound."
- **Read in full:** proposal and methods v3 §1–§9; Methods v2 (M1–M16 and the amendment table); `theorem_program_lpc_v1.md`; the notes of 2026-10-14 (WU-0003, .9 Q1, .3a κ) and 2026-10-17 (block length); the research note on Lyapunov exponents (2026-10-10/11); `lpcstudy/systems.py`, `oracle.py`, `allocation.py`, `dynamics.py`, `ensemble.py`, `validation.py`, `data.py` (`estimation.py` signatures only); `docs/agent/records/defects.md` DEF-0003, 0008, 0015, 0017, 0022, 0025.
- **Branch:** `wu/math-other-attractors` from develop 044dae2. Scripts and logs: `docs/agent/notes/2026-10-19-math-other-attractors/` (§E).
- **Not changed:** no file under `lpcstudy/`, `tools/`, `docs/study/`, `seeds/`, `.claude/`, `ROADMAP.md`, the ledger or any record.

## 0. Summary and verdicts

**The owner's wording presupposes a gap ("why the original theorem was unsound"). I did not find an unsound theorem.** Every algebraic step of P1, P2 and P3 was re-derived and verified symbolically (SymPy, ephemeral) and in exact rational arithmetic (2000 random triples, zero failures), and every inequality was checked numerically on adversarial cases. What I found instead are three places where the stated hypotheses or wording are narrower or looser than the text suggests. None changes a pre-registered verdict; all are post-freeze findings to report, not to apply (PRIME.2, QA.12).

| Theorem | Verdict | One-line reason |
| --- | --- | --- |
| **P1(a)** optimal weight, clipping | sound (algebra); **the curvature floor c ≥ ρ²/k is sound only with an unstated hypothesis** | The floor needs the expectation to include the library noise of the copied value, and retrieval not to depend on it. The study's estimand conditions on the realized library (`forecast_draws` varies the query noise only), so the copied noise ξ is a constant per analog, E[ξ e_P] = ξ E[e_P] ≠ 0, and c can be below ρ²/k (§B.1, scripts `p1_curvature_floor.py`). What the rest of the study needs, c > 0, holds whenever e_C ≠ e_P with positive draw probability. No test checks ρ²/k; a violation is silent (`curvature_floor` counts c < 1e-300 only). |
| **P1(b)** | sound as stated | Pure algebra given c > 0. |
| **P1(c)** | sound as stated | Needs C ≥ 0 only; proof's case split and inequality verified. |
| **P1(d)** | **sound only in a regime** | Needs (i) C ≥ 0 at every horizon, (ii) the per-horizon envelope min(E_C, E_P)^{1/2} to be exactly r₀e^{ΛH}, (iii) first passage read on that envelope; +1 step on integer horizons; the noisy-verification criterion preserves it. (ii) fails at short H (CP's noise floor ρ) and after saturation. The v3 Summary sentence drops (i) (§B.7). Pilot: 4–10% of states exceed the bound (`gain_bound.fraction_within_bound` 0.90–0.96), as expected where (i) or (ii) fail; reported without a bar, which is the right handling. |
| **P1(e)** | sound | E_C = E_P = 1, C = −1 gives V(u) = 0 (verified). |
| Separation remark | a remark with hypotheses known to fail; **v3's formula omits the copied-noise term** | Under proportional covariances and K = 0, u = δ²q_H/((ε²+δ²)q_H + ρ²/k), which equals δ²/(ε²+δ²) only as q_H → ∞ (Methods v2 and the theorem program L6 state it correctly; v3 §3 does not). H2a tests it; the pilot median ranges 0.10–0.25 say the hypothesis fails. |
| **P2(a)(b)(c)** | **sound as stated** | A statement about a finite point set in a normed space and a perturbed query; no dynamics, no Gaussianity (only E‖η‖² = Dρ²), k = 1. Verified on 2-flat, curve, two-point and Student-t cases: zero violations of (a), (b), (c). (b) is vacuous wherever Δ < 2ρ√D (nearly all states at N_lib = 10⁴: Lorenz-63 Δ/ρ ≈ 1.9); (c) is loose by 3–5× in N. The "why this matters" paragraph is a heuristic, correctly left to Q-N. |
| **P3(a)** | sound as stated | Needs Σc_i > 0; brute force agrees to 5e-7 on clipped and unclipped regimes. |
| **P3(b)** | sound; **the "vanishes when" clause is sharper than written** | The floor is zero iff w* = clip(u) (not u) is F-measurable on {c > 0}: a cell with every u_i > 1 has a zero floor although u varies (verified). Methods v2's "vanishes when u is a function of F" is sufficient, not necessary. Separately, the code applies V_i(w) to draw-dependent rules (A3–A5) in `regime_regret` and the K rule, which drops the dependence term h_i (the κ_E note R2); an implementation approximation, not a theorem issue; H3c's verdict uses realized MSE and is unaffected. |

**Implementation findings already on record are not theorem findings:** DEF-0003 (clipped-mean regime weight), DEF-0002 (excess formula), DEF-0008 (N̂ estimand), DEF-0015/0017 (orbit guard, seed-dependent starts), DEF-0022 (power of H2a(ii)), DEF-0025 (dof filter) are all code- or design-level; each theorem's statement was right and the code was brought to it.

**Catalog (§A):** twelve candidates ranked; recommended first three are the **hyperchaotic Rössler system** (two positive exponents, d_KY ≈ 3.0; the first system where "the" Lyapunov time and Λ̃ are not a single scale), **Rössler observed through z** (same equations; observability ν varies by orders of magnitude, which the three studied systems never give), and **Lorenz-63 at r = 166.1** (type-I intermittency; a bimodal local-instability distribution). A zero-cost null, **Rössler at c = 2.5 (limit cycle, λ_max = 0)**, should run alongside. §C gives the pre-specified criteria.

**Researcher requests:** 14 (§D). Every literature value in this note is marked unverified; the numbers in the tables are DEVELOPMENT estimates from `lyapunov_candidates.py` (an independent Benettin/QR implementation that reproduces the code's `estimate_lyapunov` bitwise on Lorenz-63).

## A. Catalog of candidate systems

### A.1 How the current three constrain the hypotheses

All three studied systems have one positive exponent, d_KY 2.01–2.10 (my spectra: Lorenz 2.06, Rössler 2.01, Chua 2.10), a single observable with modest observability variation (fitted δ̂² ≈ (ρν̂)², Methods v2 M13 item 1), an exact model, and a continuous (Chua: C¹ but not C²) flow. In that corner the pilot found: median w* 0.05–0.08 at 1 LT with the lower quartile at 0 (DEV-0 `weight_profile`), N adding ΔR² 0.21–0.27 to the w* = 0 indicator but nothing to logit w*, and 4–10% of states beyond the P1(d) bound. What the three cannot show: whether the conditions still decide the blend when (1) there are two growth rates, (2) observability rather than recurrence varies, (3) instability is intermittent, (4) λ_max = 0 (null), (5) the model is wrong, (6) the local dimension is far from 2.

### A.2 Ranked table

Time unit: the code sets Δ = 1/(30 λ_max); "substeps" is ⌈Δ/max_dt⌉ with the max_dt I used. Cost is relative to the 4.7 h CPU full preset for all three systems (about 1.6 h per 3-D system; the RK4 and Jacobian cost scales with the substeps and m², the LM and network cost with m and D). Spectra: DEVELOPMENT, `lyapunov_candidates.log` (60 000 tangent steps, 4-D and below; 40 000 above; block SE of λ₁ given); literature values: **unverified, request numbers in §D**.

| # | System (axis) | Equations, parameters | λ spectrum, d_KY (this note, DEVELOPMENT) | Literature (unverified; request) | Δ and substeps | Code changes | Cost | Risk of an uninformative outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **Hyperchaotic Rössler** (1: hyperchaos; 7: d_KY 3) | ẋ = −y − z, ẏ = x + ay + w, ż = b + xz, ẇ = −cz + dw; a = 0.25, b = 3, c = 0.5, d = 0.05 | (+0.112, +0.021, 0.000, −24.9); d_KY 3.01; LT 9.0 | Rössler 1979; λ₁ ≈ 0.11, λ₂ ≈ 0.02 (R1) | Δ = 0.30; max_dt 0.005 → 60 substeps (V6 must set max_dt; the w equation is slow, z spikes fast) | new `SystemSpec` (dim 4, bound on x ≈ 60), D = 7 keeps dof 3 (D > 2d_KY = 6.0 is borderline: R11), AMI delay recomputed | ×1.5–2.5 per system | low: both exponents are resolved by the 1-LT window (λ₂/λ₁ = 0.19, so the second direction grows e^{0.19} per LT; the amplifier's 1-LT slope is dominated by λ₁ at most states, which is itself the finding to make) |
| 2 | **Rössler observed through z** (8: exact model, poorly conditioned) | registry Rössler, `observed_index = 2` | same attractor (λ₁ 0.072, d_KY 2.01) | Letellier, Aguirre & Maquet 2005 rank z as Rössler's worst observable (R4) | unchanged | `observed_index = 2`; `checked_bound` requires index 0 (one guard line; keep the bound on x); σ_x becomes σ_z, so ρ is a fraction of the spike-dominated scale | ×1 | low: ν will span orders of magnitude between the flat phase (z ≈ 0) and the spikes; the risk is the opposite, that PLP is useless in the flat phase so w* ≈ 1 there and the interior-w* parts thin out (counts reported) |
| 3 | **Lorenz-63 at r = 166.1** (2: type-I intermittency) | registry field, r = 166.1 | (+0.61 ± 0.05, 0.00, −14.3); d_KY 2.04; at r = 166.2: λ₁ 0.90 | Manneville & Pomeau 1979: r_c ≈ 166.06 (R2) | Δ = 0.055; max_dt 0.002 → 28 substeps (|x| reaches 262: bound ≈ 300) | parameter and bound change only | ×1.5 | **medium**: λ_max converges slowly (SE 0.05 at 60 000 steps against 0.0014 for r = 28), so the time unit is uncertain at the percent level; the laminar phases make the ACF time long (thinning widens, fewer states per trajectory length) |
| 4 | **Rössler at c = 2.5, limit cycle** (6: null, λ_max = 0) | registry field, c = 2.5 | (0.000, −0.046, −2.12); period-1 cycle; d = 1 | period-1 window at c = 2.5 for a = b = 0.2 (R3) | Δ undefined by the code (1/(30·0)): needs an interval override (e.g. 30 steps per period) | `config`/`SystemSpec` field `interval_override`; the Λ̃ profile coordinate is ≈ 0 and constant; horizons mostly censored | ×1 | by design: RQ2/RQ3 are degenerate here (that is the null); the value is in H1a at d = 1 and H2a(i), the one case where separation can pass |
| 5 | **Hénon–Heiles, E = 1/6** (4: Hamiltonian, mixed) | ẋ = p_x, ẏ = p_y, ṗ_x = −x − 2xy, ṗ_y = −y − x² + y²; start (0, 0.1, p_x(E), 0.3) | (+0.136, 0, 0, −0.136); energy shell d = 3; KY formula degenerate (volume preserving); LT 7.4; at E = 1/8 the same start is regular (λ ≈ 3e-4) | Hénon & Heiles 1964; λ at E = 1/6 (R6) | Δ = 0.245; max_dt 0.02 → 13 substeps | new spec (dim 4, bound 1); `kaplan_yorke`-type code absent, fine; the Benettin orbit must start in the chaotic component (start registry) | ×1.3 | **medium**: sticky islands give long censored horizons and a non-ergodic library (one orbit samples one component; the test states come from the same orbit, so the estimands are well defined but component-specific) |
| 6 | **Chua, cubic diode truth vs PWL model** (8: misspecified model) | truth: f(x) = ax + bx³, α = 10, β = 14.87, a = −1.27, b = 0.0157; model: the registry PWL diode fitted to it (or the reverse pairing) | truth: (+0.277, 0, −5.75); d_KY 2.05 | Zhong 1994 cubic Chua (R7) | Δ = 0.12; max_dt 0.005 → 25 substeps | `ForecastSetup.model_step` already accepts a different model; a `misspec` field naming the model diode; new spec for the cubic truth | ×1 | **medium**: the magnitude of the model error is a free knob; it must be fixed in advance (the fitted PWL slopes) and the "model-error seed" has no proxy yet (v3 §8 future work) |
| 7 | **Lorenz-63 observed through z** (8: exact but non-identifiable) | registry Lorenz, `observed_index = 2` | same attractor | the (x, y, z) → (−x, −y, z) symmetry makes z-delay vectors two-to-one (R4) | unchanged | as #2 | ×1 | **high as a hypothesis test, high value as a limit case**: the mirror minimum has the same LM residual, so the χ² diagnostic is blind; V7 (δ/(ρν) ≫ 1) will fail the gate and mark the system provisional; CP's z-forecast is unaffected by the mirror ambiguity, so w* → 1 everywhere. It shows that a local ν cannot see global non-identifiability |
| 8 | **Lorenz-96, N = 8, F = 8** (1, 7: hyperchaos, d_KY 5.4) | ẋ_i = (x_{i+1} − x_{i−2})x_{i−1} − x_i + F | (+1.63, +0.39, 0, −0.47, −0.97, −1.52, −2.46, −4.61); d_KY 5.39; N = 6 has one positive exponent (0.95, d_KY 4.0), N = 5 one (0.47, d_KY 2.9) | Lorenz 1996; small-N spectra (R5) | Δ = 0.020; max_dt 0.005 → 5 substeps | D = 7 < m + 1: JᵀJ singular, PLP undefined (Methods v2 D3 dropped L96 for this). Needs D ≥ 11 (> 2d_KY) with τ = 2–3 to keep the window ≤ 1 LT; estimator width rule; `robustness_dims` filter d > m | ×3–4 | **high**: observability of an 8-D state from one coordinate over 1 LT is poor (ν large), and the network initial guess needs more training; a first smoke-size check of V2/V7 is mandatory |
| 9 | **Rössler funnel** (2: phase-incoherent, broader local exponents) | a = 0.3, b = 0.2, c = 5.7 (or a = 0.343, b = 1.82, c = 9.75) | (+0.119, 0, −4.92), d_KY 2.02; (+0.143, 0, −8.57), d_KY 2.02 | funnel parameter sets (R3) | Δ = 0.28 (0.23); max_dt 0.02 → 14 (12) substeps | parameters and bound (|x| ≤ 56, 67) | ×1 | low but incremental: it mostly removes the 50-LT ACF time of the spiral Rössler (block-length note §2.6) |
| 10 | **Hénon map** (3: discrete, d_KY 1.26, lacunar) | x' = 1 − 1.4x² + y, y' = 0.3x | not computed (ODE-only code) | Sprott: λ = 0.419217, −1.623190 (fetch extract in the research note of 2026-10-11, row 1); d_KY = 1 + 0.419/1.623 = 1.26 (R8) | 1 iterate = 1 step; LT = 2.4 iterates: the 30-steps-per-LT convention cannot hold | `make_flow_step` must return the map; `steps_per_lyapunov` per system; the delay-window cap (6τ ≥ 6 iterates = 2.5 LT) and H_ref = 1 LT = 2 iterates break the design | ×0.5 | **high**: horizons in iterates are too coarse (1–19) for KM medians and the 1-LT window has 2 points |
| 11 | **Lozi map** (3: piecewise-linear, discontinuous Jacobian) | x' = 1 − 1.7\|x\| + y, y' = 0.5x | not computed | Lozi 1978; λ (R8) | as #10 | as #10 | ×0.5 | as #10; what it adds over Chua: DΦ^H is discontinuous across the preimages of x = 0, so Λ̂(ŝ) and Λ̄(s) differ by O(1) for a tiny estimation error (H1d-Λ stress), and the first-order remainder has no M₂ |
| 12 | **Mackey–Glass, τ = 17** (5: delay, infinite-dimensional) | ẋ = βx(t−τ)/(1 + x(t−τ)^10) − γx; β = 0.2, γ = 0.1 | not computed | Farmer 1982: λ₁ ≈ 0.007, d_KY ≈ 2.1 for τ = 17 (R9) | LT ≈ 140 time units; Δ ≈ 4.7 | the state is a function segment: PLP needs a method-of-steps state of m = τ/h ≫ D, so JᵀJ is singular and ν undefined; a filtering PLP is a new estimator | ×5+ | **high**: the design's PLP does not exist for it; the embedding dimension question it probes is real but needs a different method |

Also considered, not ranked: Kuramoto–Sivashinsky (L = 22, m = 64 modes; the same PLP objection as #12, worse; R10); a quasi-periodic torus (two oscillators, λ = 0, verified; all four conditions constant, so every allocation rule collapses to A2: a calibration of the false-positive rate of the verdict machinery, nothing more); a forced Duffing oscillator (λ₁ = 0.10, d_KY 2.25, verified chaotic for δ = 0.3, α = −1, β = 1, γ = 0.5, ω = 1.2; its phase coordinate is unbounded, which breaks the whitening and the orbit guard); strange non-chaotic attractors (quasi-periodically forced maps: discrete, same objection as #10).

### A.3 Expected behaviour of the four conditions and the hypotheses, per candidate

Signs are predictions with reasons, not guesses; "same" means no change expected from the studied systems.

| # | Recurrence (ε_s, R) | Observability (ν, δ) | Instability (Λ̃) | Noise sensitivity (N) | H1a–H1d | H2a | H2b, H2e | H2c, H2d | H3a–H3c, Q-N |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 hyper-Rössler | ε_s² ∝ N_lib^{−2/3} (d ≈ 3): the seed shrinks more slowly with N_lib, so CP is worse at fixed N_lib | ν larger (4 states from 7 points over 1 LT) | the 1-LT slope mixes λ₁ and λ₂ by state; Λ̃ has a wider spread | N larger: smaller margins in a d = 3 library | H1a with 1/d_LB ≈ 0.33 (decidable; a 30% shortfall as on Rössler/Chua is the thing to look for); H1b holds (first order); H1c: the horizon law uses one Λ̄ per state, fine; H1d same | separation is less likely: two growth directions give anisotropic amplified seeds, so part (ii) should show a larger partial correlation (a pre-registered reading, v3 §7) | w* rises with ρ and N_lib as before; H2e (noise matching) should be stronger because margins are smaller | PLP still wins after 1 LT; A4 − A2 harder to decide | H3b: Λ̃ importance in the horizon tree may fall (two rates); Q-N: N adds more |
| 2 Rössler-z | R in z-delay space is tiny in the flat phase (many near-identical windows): recurrence looks excellent but the latent mismatch is large: ε̂ = a(Rν̂)² is where L4 earns its keep | ν spans orders of magnitude; δ ≈ ρν follows it (V7 should still pass if the LM converges) | same | N large in the flat phase (dense near-ties) | H1d-δ̂ should pass with a high Spearman (ν̂ is the signal); H1d-ε̂ is the test of L4 | same | same | **H2c becomes decidable**: a state-dependent rule gains where ν varies by 10× | regimes split on ν̂; H3b weight tree should load on observability, not Λ̃ |
| 3 Lorenz r = 166.1 | same | same | **bimodal Λ̃** (laminar ≈ 0, bursts high) | same | H1c: the horizon law per state covers two populations | H2a(ii): if separation holds it should hold with the largest dynamic range in Λ̃ available anywhere; a failure here is the most informative one | same | same | **H3b** is the target: the horizon tree should split on Λ̃ with a large D; the weight tree should not |
| 4 Rössler c = 2.5 | d = 1: ε_s² ∝ N_lib^{−2} (fast) | ν constant along the cycle up to phase | Λ̃ ≈ 0, constant | N: near-ties along the cycle | H1a at 1/d = 1 (new regime for the scaling law); H1c undefined (no growth) | **H2a(i) can pass**: w* independent of H exactly (no amplifier) | H2b(ii) large (ε_s falls as N_lib^{−1}) | A4 − A2: nothing to gain if the conditions are constant | H3a inconclusive by design; Q-N undefined (w* = 0 count) |
| 5 Hénon–Heiles | d = 3 on the shell (1/d_LB ≈ 0.33, not fractal) | ν varies with the orbit's position relative to islands | Λ̃ from ≈ 0 (sticky) to > 1 | same | H1a at d = 3 and a smooth measure (Levina–Bickel's uniform hypothesis holds exactly, unlike on a fractal) | as #3 | same | same | horizons censored for sticky states: KM medians infinite for a regime (H3a pairs "cannot be computed", p = 1) |
| 6 Chua cubic/PWL | same | δ gains a model-error term that grows with H (not ∝ ρ): V7 fails by design at small ρ (δ/(ρν) ≫ 1) | Λ̂ from the wrong model differs from Λ̄ | same | H1b fails (seed × amplifier needs the exact model); H1d-δ̂ falls | w* now depends on H (model error accumulates): H2a(i) fails by design | w* rises with N_lib more strongly (CP is right, PLP is biased) | **A4 cannot beat A2 unless the model-error seed is proxied**: H2c fails, "A4o beats A2" reading | regimes on H carry the model error |
| 7 Lorenz-z | same | ν finite but the map is two-to-one: δ ≈ lobe separation on half the draws | same | same | V7 fails (gate), H1d-δ̂ fails | w* ≈ 1 everywhere: interior part empty (< 50 states, inconclusive by rule) | monotone but saturated | A0 wins; A4 ≈ A0 | degenerate |
| 8 L96 N = 8 | d ≈ 5.4: ε_s² ∝ N_lib^{−0.37}: CP barely improves with N_lib | ν very large; PLP may not converge at ρ = 1% | two rates (λ₂/λ₁ = 0.24) | N large | H1a slope tiny against the floor: likely undetermined | as #1, stronger | H2b(ii) may be undetectable (flat ε_s) | CP competitive even at 1 LT | — |
| 9 funnel Rössler | same | same | broader | same | same | same | same | same | same |
| 10/11 maps | d = 1.26; lacunar: Levina–Bickel biased (R12) | ν from a 2-D state: fine | per-iterate | same | H1a stressed; H1c on 2 points per LT undefined | coarse H | same | same | horizons too coarse |
| 12 MG | d ≈ 2.1 in delay space | undefined under the design | small λ, long LT | same | — | — | — | — | — |

### A.4 Recommended first three, and what each adds that Lorenz-63, Rössler and Chua cannot

1. **Hyperchaotic Rössler (#1).** Adds a second positive exponent and d_KY ≈ 3. Every studied system has one growth direction, so "instability" is one number per state and the amplifier is a rank-one-dominated object; with two rates the seed × amplifier law, the horizon law and the separation remark are tested where the proportional-covariance hypothesis is least plausible. It also moves H1a's reference 1/d from ≈ 0.5 to ≈ 0.33 and tests the N_lib^{−2/d} law outside d ≈ 2. Cost ×1.5–2.5 for one system; the V6 step must be set first.
2. **Rössler observed through z (#2).** Adds observability as a varying condition. On the three studied systems δ̂² ≈ (ρν̂)² with modest spread, so A4 reduces to a recurrence-in-noise-units rule (Methods v2 M13 item 1) and the observability condition is never the deciding one. The z observable gives ν a range of orders of magnitude at zero cost and no new equations, so H2c can be decided and the H1d-ε̂ test of L4 (R·ν̂, not R) gets its dynamic range.
3. **Lorenz-63 at r = 166.1 (#3).** Adds intermittency: a bimodal distribution of the local growth exponent. The studied attractors have unimodal Λ̃; the H3b claim "instability sets the horizon, not the weight" is most sharply tested where instability switches between near-zero and large along one orbit. Cost ×1.5; the time unit needs a longer Benettin run (SE 0.05 → 0.01 needs ≈ 25× more steps, about 3 min single-threaded).

**Zero-cost null (#4, Rössler c = 2.5):** the one configuration where the conditions predict no benefit from allocation and where separation (H2a(i)) can pass; it needs an interval override because Δ = 1/(30λ_max) is undefined at λ_max = 0.

## B. Theorem audit

### B.1 Theorem P1 (v3 §3; Methods v2 M9)

**Restated.** Fix a state and a horizon. e_C, e_P are the CP and PLP errors over observation-noise draws with E_C = E[e_C²], E_P = E[e_P²], C = E[e_C e_P]. V(w) = E[(w e_C + (1−w) e_P)²] = c(w−u)² + V(u), c = E_C + E_P − 2C, u = (E_P − C)/c. (a) CP copies a noisy future value, so e_C contains ξ with E[ξ²] = ρ²/k orthogonal to e_P and to e_C − ξ; then c ≥ ρ²/k > 0, V is strictly convex, w* = clip(u). (b) u ∈ [0, 1] iff C ≤ min(E_C, E_P). (c) If C ≥ 0, min_{[0,1]} V ≥ ½ min(E_C, E_P). (d) If (c) holds at every horizon and the better forecaster's r.m.s. error is r₀e^{ΛH}, the hybrid's characteristic horizon exceeds it by at most ln 2/(2Λ). (e) (c) fails without C ≥ 0: E_C = E_P = 1, C = −1 gives min V = 0.

**Hypotheses used, explicit and implicit.**

| # | Hypothesis | Where it enters | Holds for L63 / Rössler / Chua? | Checked in the project? |
| --- | --- | --- | --- | --- |
| P1-1 | e_C, e_P square-integrable; the hybrid error is the linear blend of the two errors | the quadratic form | yes: errors are clipped at 10σ_x and the hybrid blends the clipped errors (the estimand, v3 §4) | the clip is counted (`error_clips_*`); the clip-sensitivity flag |
| P1-2 | c > 0 | existence and uniqueness of u; (b) | yes a.s.: e_P varies across draws (continuous function of the query noise) | `curvature_floor` counts c < 1e-300 only |
| P1-3 | **copied noise ξ with E[ξ²] = ρ²/k, E[ξ e_P] = E[ξ (e_C − ξ)] = 0** | the floor c ≥ ρ²/k | **not for the study's estimand** (below) | **no** (silent) |
| P1-4 | C ≥ 0 | (c), (d) | at most states; 4–10% of pilot states violate the gain bound | the gain-bound screen (reported, no bar) |
| P1-5 | exact exponential growth of the better forecaster's envelope, r₀e^{ΛH}, with the first passage read on it | (d) | only in the linear regime: fails for H ≲ a few steps (CP's floor ρ; PLP's ρν_H) and after saturation | H1c tests the law for PLP at 1 LT; the screen |
| P1-6 | verification noise added in quadrature; integer horizons | (d) as the code computes horizons | yes | `characteristic_horizon` |

**Derivation checked step by step** (`p1_p3_sympy.log`, `p1_p3_identities.log`).

- (a) V(w) − [c(w−u)² + V(u)] = 0 identically: **correct**. Clip: a convex quadratic's minimiser on an interval is the projection of the vertex: **correct** given c > 0.
- (a) floor: with e_C = ξ + e', orthogonality gives c = E[(e' − e_P)²] + E[ξ²] ≥ ρ²/k: **correct given P1-3**. P1-3 is where the text is loose. In `ensemble.forecast_draws` the library (with its noise `ctx.library_unit_noise`) is fixed and only the query noise `unit_noise` varies across the M draws. The copied value is x_{i*_r + H} = h(s_{i*_r+H}) + ρ z_{i*_r+H} with z a fixed array. When retrieval is stable (`cp_constant`, the common case at ρ = 1%, N_lib = 10⁴, H = 1 LT), ξ is a constant per state, so E_draws[ξ e_P] = ξ E[e_P] ≠ 0 and E[ξ²] = ξ² is one number, not ρ². Then c = (e_C − E e_P)² + Var(e_P), which is below ρ²/k whenever Var(e_P) < ρ²/k and e_C ≈ E e_P. Var(e_P) < ρ² is realistic at short horizons: to first order Var(e_P)/ρ² = ‖Γ_H J⁺‖² (L11(a)), the leverage of a 7-point window fit, which is below 1 at H = 1 step on Lorenz-63 (table below). The toy in `p1_curvature_floor.log` (A) gives c/(ρ²/k) = 0.4.
  - **Unconditionally** (library noise averaged in), orthogonality is an approximation: i* is chosen among candidates whose windows contain z_{i*+H} (candidate i*+H has it at lag 0), so z_{i*+H} is not independent of the selection event. The effect is a selection bias that vanishes when the H-shifted candidate is not a retrieval competitor (‖X_{i*+H} − q‖ ≫ r₁ + ρ√D), i.e. for H ≳ a few steps; part (C) of the script measures E[ξ_H] and E[ξ_H (e_C − ξ_H)] on a Lorenz-63 library (table below).
  - **The smallest correct statement:** "c = E[(e_C − e_P)²] ≥ 0, and c > 0 whenever Pr(e_C ≠ e_P) > 0 over the draws; if, in addition, the expectation includes the noise of the copied value and that noise is independent of the retrieval and of e_P, then c ≥ ρ²/k." The downstream code needs only c > 0.
  - **Detection:** silent. No test or counter compares c with ρ²/k. A cheap report-only diagnostic would be the fraction of (state, horizon) pairs with c < ρ²/k, from the existing moments; it changes no number.
- (b) c·u = E_P − C and c(1−u) = E_C − C (verified): u ∈ [0, 1] iff C ≤ E_P and C ≤ E_C: **correct**.
- (c) Case E_C ≤ E_P. If C ≥ E_C then u ≥ 1 and V(1) = E_C ≥ E_C/2. Otherwise u ∈ (0, 1] and V(u) = (E_C E_P − C²)/c (verified); 2V(u) − E_C = [E_C(E_P − E_C) + 2C(E_C − C)]/c (verified), both terms ≥ 0 for 0 ≤ C < E_C ≤ E_P: **correct**. Exact check on 982 random triples with C ≥ 0: zero failures.
- (d) r₀e^{ΛH}/√2 = r₀e^{ΛH'} gives H' − H = ln 2/(2Λ) (verified). With the code's criterion √(V + ρ²) > θ: V_hyb ≥ E_best/2 gives V_hyb + ρ² ≥ (E_best + ρ²)/2, so the bound survives verification noise (verified: the difference is ρ²/2 ≥ 0). On integer steps the gain is ≤ ln 2/(2Λ) + 1. Numerically: 1976 random cases with C ≥ 0 at every horizon, zero violations; with C = −0.9√(E_C E_P) the gain is 44 steps against a bound of 11.4 (`p1d_horizon_gain.log`). **Correct in the regime P1-4 + P1-5.** Two readings the text leaves implicit: "the better forecaster" must be the per-horizon envelope (its identity may switch with H; the proof uses min(E_C, E_P) at each H, so this is fine), and the exponential law must hold for the envelope, which is false near H = 0 for CP (floor ρ) and after saturation for both; the bound is then a bound on a comparison that the data do not satisfy, which is why the study reports the gain without a bar (v3 §2 last sentence; DEC-0016 O2 screen).
- (e) **correct** (verified).

**Verdict P1:** (a) algebra sound; floor sound with the unstated hypothesis above (and false for the conditional estimand); (b), (c), (e) sound as stated; (d) sound only in a regime.

### B.2 Theorem P2

**Restated.** Library delay vectors X₁…X_n, clean query x, nearest and second-nearest distances r₁ < r₂, margin Δ = r₂ − r₁; noise η with E‖η‖² = Dρ². (a) ‖η‖ < Δ/2 ⇒ the nearest analog of x + η is still X₁. (b) Pr(change) ≤ Pr(‖η‖ ≥ Δ/2) ≤ 4Dρ²/Δ². (c) N² ≤ (4/(ρ²D)) E[(r₁ + ‖η‖)² 1{‖η‖ ≥ Δ/2}], N the r.m.s. displacement of the retrieved analog's delay vector per coordinate in noise units.

**Hypotheses.** (P2-1) a norm (triangle inequality); (P2-2) a finite library with deterministic tie-breaking; (P2-3) E‖η‖² = Dρ² (no Gaussianity, no isotropy, no independence across coordinates); (P2-4) k = 1 analog; (P2-5) N defined with the population mean (the code's sample mean over M draws satisfies N_M² ≤ A_M by Huygens' identity, as `validation.p2_bound_terms` checks). Nothing about the dynamics, the embedding, the smoothness or the noise law of the system: **P2 holds for every candidate in the catalog, including maps and Hamiltonian systems.**

**Derivation.** (a) ‖x+η−X_j‖ ≥ r₂ − ‖η‖ > r₁ + ‖η‖ ≥ ‖x+η−X₁‖ iff ‖η‖ < Δ/2 (symbolic: (r₂−η) − (r₁+η) = Δ − 2η): **correct**. (b) {change} ⊆ {‖η‖ ≥ Δ/2} by (a); Markov on ‖η‖²: **correct**. (c) N² ≤ (ρ²D)⁻¹E‖Y − X₁‖² (variance about any point); on a switch, ‖Y − X₁‖ ≤ ‖Y − (x+η)‖ + ‖(x+η) − X₁‖ ≤ 2(r₁ + ‖η‖) because Y is nearest to x + η; and switch ⊆ {‖η‖ ≥ Δ/2}: **correct**.

**Numerical check** (`p2_bound_check.log`): 2-flat library in R⁷ at ρ = 0.3%, 1%, 3%; a d = 1 curve; a two-point adversarial library with Δ = ρ√D; Student-t(3) noise (unit variance, heavy tails). (a): 0 switches below Δ/2 in 1.1 million draws. (b): 0 states where P(switch) exceeds P(‖η‖ ≥ Δ/2); 0 states where the exact 99.9% lower confidence bound of P(‖η‖ ≥ Δ/2) exceeds the Markov bound. (c): 0 violations. Tightness: N/√B median 0.18–0.25, max 0.38: the bound overstates N by 3–5×. The Markov bound is ≥ 1 at 97–100% of states whenever Δ < 2ρ√D, which is the typical regime at N_lib = 10⁴ (the WU-0003 note gives Δ/ρ ≈ 1.9 on Lorenz-63).

**What is not a theorem in §3 of v3:** "N can carry state-level information the other three conditions do not" is a heuristic about order statistics (L11's "different order statistic" argument); it is correctly estimated (Q-N), not asserted. The pilot's Q-N (N adds ΔR² 0.21–0.27 to the w* = 0 indicator, and about 0 to logit w*) is consistent with it.

**Verdict P2:** sound as stated. The bound is loose and (b) is vacuous in the study's own regime, which is a matter of usefulness, not truth; the study's P2(c) verification (`verification.P2c`) already reports tightness.

### B.3 Theorem P3

**Restated.** (a) For a regime S, Σ_{i∈S} V_i(w) on [0, 1] is minimised by w_S = clip(Σc_iu_i/Σc_i). (b) For a profile F and any rule f(F) ∈ [0, 1], E[V(f(F))] ≥ E[V(clip ū(F))] with ū = E[cu|F]/E[c|F]; the gap to E[V(w*)] is a floor on the excess MSE of every F-measurable rule; it vanishes when the optimum is a function of F.

**Hypotheses.** (P3-1) each V_i is the quadratic of P1(a) with c_i ≥ 0 (always: c_i = E[(e_C − e_P)²]); (P3-2) Σc_i > 0 (a); (P3-3) integrability and E[c|F] > 0 (b); (P3-4) the rule's weight is a function of F alone, with V evaluated as the conditional MSE given the state. Note cu = b = E[e_P(e_P − e_C)], so E[cu|F] is defined even where c = 0.

**Derivation.** (a) Σc_i(w−u_i)² is convex with vertex Σc_iu_i/Σc_i (verified symbolically); projection onto [0, 1]: **correct**. Brute force on 200 random regimes, including all-above-1 and all-below-0 regimes (the DEF-0003 cases), agrees to 5e-7 (`p3_regime_floor.log`). (b) E[c(f−u)²|F] = E[c|F](f−ū)² + E[c(u−ū)²|F] (verified symbolically; the cross term vanishes by the definition of ū); minimising over f ∈ [0, 1] gives clip(ū): **correct**. 1000 random F-measurable rules never beat clip(ū); per-cell brute force agrees to 5e-7.

**Sharpening.** The floor equals E[c((clip ū − u)² − (clip u − u)²)] ≥ 0, which is zero iff clip ū(F) = clip u a.s. on {c > 0}. So "vanishes when the optimum is a function of F" is exactly right if "the optimum" means w* = clip(u), and Methods v2's "vanishes when u is a function of F" is sufficient but not necessary: a cell with u ∈ {3/2, 5/2, 7/2} has floor 0 (exact rational check), and the synthetic cells 0–1 with u ∈ (1.02, 1.25) have floor 0.0 while cells with interior u have floors 0.006–0.009. This matters for reading the flat regret-versus-K curve: the floor is driven by the states with 0 < w* < 1 only.

**Implementation remark (not a theorem issue).** `regime_regret` and the K rule plug per-draw weights w_{id} of A5 (whose profile F̂ depends on the same draw as the errors) into V_i(w), which assumes the weight is independent of the draw's errors. The true MSE is V_i(w) + E[h_i(w)], with h_i the dependence term of the κ_E note (R2). A synthetic rule that sees the draw's own analog error shows a plug-in error of +56% (`p3_regime_floor.log` (c)); the real A4/A5 dependence is weaker but not measured. The P3(b) inequality itself is unaffected (it is about σ-algebras), H3c's verdict uses realized evaluation MSE and is unaffected; the reported "excess MSE" of A3–A5 and the choice of K are the quantities that carry the approximation.

**Verdict P3:** (a) sound; (b) sound, with the "vanishes" clause to be read as an iff on w*.

### B.4 The separation remark and the cited results

- **Separation (v3 §3 remark; L6).** With Σ_a = ε²S, Σ_s = δ²S, K = κS and the copied-noise term: u = (δ² − κ)q_H/((ε² + δ² − 2κ)q_H + ρ²/k) (verified symbolically). v3 writes "the amplifier cancels from u, and w* = δ²/(ε_s² + δ²)": that needs κ = 0 **and** ρ²/k = 0 (or q_H → ∞). At 1 LT, q_H ≈ e²·(seed scale)² ≫ ρ², so the transient is negligible for H2a's horizons (the exact check: at q = 100 the relative error is 4e-5 for ε = 0.1, δ = 0.05, ρ = 1%); at H = 1–3 steps it is not. Methods v2 M9 and L6 state the transient correctly. The κ = 0 hypothesis is the one H2e (noise matching: C grows with N_lib) says fails as the library grows: separation and noise matching are in tension by the theorem's own algebra, which v3 §7's pre-registered reading of an H2a failure already names.
- **Seed × amplifier (L1).** Needs F = h̃∘Φ^H twice differentiable with ‖D²F‖ ≤ M₂ on the segment. Lorenz-63 and Rössler: C^∞. **Chua: the vector field is Lipschitz and continuous but not C¹ at |x| = 1, so the flow map is C¹ (the saltation matrix is the identity for a continuous field) but not C²:** the remainder is O(‖ξ‖·jump) across a breakpoint crossing, not O(‖ξ‖²). H1b's PLP slope (pilot 1.01 on Chua) is the visible side; the Jacobian-based ν and g_H are still exact a.e. V6's Chua margin (DEF-0026) is the integrator side of the same non-smoothness.
- **Cramér–Rao and the LM as MLE (L2).** Needs J full column rank (D ≥ m and local observability) and Gaussian noise. Holds for the three; fails by design for #12 (m ≫ D) and #8 at D = 7; is locally true but globally two-to-one for #7.
- **Nearest-neighbour scaling and Levina–Bickel (L12; H1a's reference).** The Poisson law of the k-nearest-neighbour distances on a locally uniform d-flat gives E[S/(k−1)] = 1/d exactly (`oracle.inverse_dimension`). On a fractal attractor the local measure is not uniform (lacunarity), and the pilot's fitted 1/d is 10–30% below the reference on Rössler and Chua (DEV-0: 0.44–0.48 against 0.49 on Lorenz; 0.56–0.58 against 0.51 on Rössler; 0.43–0.49 against 0.50 on Chua): H1a is the test, so this is detected, not silent. Hénon–Heiles (#5) is the control where the measure is smooth and the law should hold at d = 3; the Hénon map (#10) is the stress case.
- **Horizon law (L8).** Needs ln g_H linear in H over the window; the robust bracket turns H1c's band into a statement about that linearity. For #3 (intermittent) and #5 (sticky islands) the per-state window will straddle laminar and bursting phases at some states; H1c's median is robust to that, the per-state value is not.
- **Oseledets alignment (L6′).** Cited; for hyperchaos (#1, #8) the adjoint direction at 1 LT is not yet aligned (λ₂/λ₁ ≈ 0.2–0.24 means the second direction decays relative to the first by e^{−0.8} per LT), so the long-horizon limit is further away than on the three studied systems.

### B.5 Hypothesis-by-system table

Y = holds; ~ = holds approximately or in a regime; N = fails; "—" = not applicable. Columns: the three studied systems and the catalog numbers.

| Hypothesis | L63 | Rös | Chua | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10/11 | 12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Smooth (C²) flow (L1 remainder) | Y | Y | ~ (C¹) | Y | Y | Y | Y | Y | ~/Y | Y | Y | Y | N (Lozi: C⁰ map) / Y (Hénon) | Y |
| Local linearisation valid up to H (A6, small-error regime) | ~ (to 2–4 LT) | ~ | ~ | ~ (two rates) | ~ | N in bursts | Y (no growth) | ~ | N (model error grows) | — | ~ | ~ | ~ | ~ |
| Delay map injective, J full rank (ν defined; LM = MLE) | Y | Y | Y | Y (D = 7 ≥ 2d_KY + 1 borderline) | Y (ill-conditioned) | Y | Y | Y | Y | **N (two-to-one)** | **N at D = 7** | Y | Y | **N (m ≫ D)** |
| Gaussian, isotropic query noise | Y (by design) | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| P2's E‖η‖² = Dρ² (nothing else) | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| Whitening: C positive definite | Y | Y | Y | Y | Y | Y | ~ (a curve: C is rank-deficient in the normal direction only up to noise; fine) | Y (on the shell) | Y | Y | Y | Y | Y | — |
| Ergodic averaging; the statistics orbit samples the invariant measure | Y | Y | Y | Y | Y | ~ (long laminar phases; slow convergence of λ) | Y (a cycle) | **N (non-ergodic phase space; one component)** | Y | Y | Y | Y | Y | Y |
| c > 0 (existence, uniqueness of w*) | Y a.s. | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| c ≥ ρ²/k (P1(a) floor, conditional estimand) | **N at short H** | N | N | N | N | N | **N (no growth at any H)** | N | N | N | N | N | N | N |
| C ≥ 0 at every horizon (P1(c),(d)) | ~ (90–96% of states within the bound) | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | — | ~ | ~ | ~ | ~ |
| Exponential envelope r₀e^{ΛH} (P1(d), L8) | ~ (linear regime only) | ~ | ~ | ~ (which Λ?) | ~ | N (bimodal) | **N (Λ = 0)** | N (sticky states) | N | — | ~ | ~ | ~ | ~ |
| Proportional seed covariances, K = 0 (separation) | N (pilot range 0.10) | N (0.25) | N (0.17) | N (more so) | N | N | **Y (trivially)** | N | N | — | N | N | N | N |
| Copied-noise orthogonality (unconditional) | ~ (H ≥ a few steps) | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |
| Levina–Bickel Poisson/uniform law (H1a reference) | ~ | ~ (−10 to −30%) | ~ | ~ | ~ | ~ | Y (d = 1) | **Y (smooth measure)** | ~ | ~ | ~ | ~ | **N (lacunar)** | ~ |
| Σc_i > 0 per regime (P3(a)) | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| Rule weight independent of the draw's errors (plug-in excess MSE) | N for A3–A5 (implementation) | N | N | N | N | N | N | N | N | N | N | N | N | N |
| Finite library, Euclidean metric, k = 1 (P2) | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |

**Which failures the study's tests detect.** Detected: Levina–Bickel (H1a), separation (H2a), the exponential law for PLP (H1c), C ≥ 0 (the screen, reported), the integrator's non-smoothness (V6), global non-identifiability (V7 fails; the LM residual does not see it). Silent: the ρ²/k floor; the unconditional orthogonality of ξ; the draw-dependence term in the plug-in excess MSE (reported "excess" values and K); the C² remainder at Chua's breakpoints (only its integrator shadow is seen).

### B.6 Implementation findings versus theorem findings

| Record | Level | Theorem statement right? |
| --- | --- | --- |
| DEF-0003 regime weight was the curvature-weighted mean of clipped w* | implementation | yes: P3(a) says clip of the mean of unclipped u; fixed in WU-0002.3 and verified here by brute force |
| DEF-0002 excess MSE as c(w − w*)² | implementation | yes: P1(a) gives c[(w−u)² − (w*−u)²]; `excess_mse` implements it |
| DEC-0008 amendments (Q-N two parts, H2a parts, K rule) | analysis design | not theorem-level |
| DEF-0008 N̂ estimand | estimator | P2 defines N at the clean query; N̂ perturbs the noisy one; a bias of the proxy, reported not tested |
| DEF-0015, DEF-0017 | data generation | not theorem-level |
| DEF-0022 | power | not theorem-level |
| DEF-0025 | dof filter | the χ² reference needs dof > 0; not theorem-level |

### B.7 Sentences in the text that are broader than the proofs

- v3 Summary: "P1: the mean-squared-error-optimal weight is a closed-form function of the two forecasters' error moments, and blending can extend the forecast horizon by at most half an error-doubling time." The second clause holds only under C ≥ 0 at every horizon and an exponential envelope; P1(d)–(e) say so, the Summary does not.
- v3 §3 P1(a): "Its error therefore contains a term ξ with E[ξ²] = ρ²/k … orthogonal to e_P and to e_C − ξ. Then c ≥ ρ²/k > 0." True for the unconditional expectation up to the selection effect; not for the moments the code computes (library fixed). "V is strictly convex" is nevertheless true a.s.
- v3 §3 remark: "Then the amplifier cancels from u, and w* = δ²/(ε_s² + δ²)": the limit q_H → ∞ with κ = 0; the finite-H form has the ρ²/k term.
- Methods v2 M9 P3(b): "The floor vanishes when u is a function of F": sufficient, not necessary (iff for w*).
- v3 §3 P2 "Why this matters", "N can carry state-level information the other three conditions do not": a heuristic, correctly tested by Q-N, but placed under the theorem's heading.
- "chaotic attractors" in general: P1 and P3 are moment statements with no dynamical hypothesis; P2 is geometric. The dynamical content lies in the cited results (L1, L2, L8, L12) and in the separation remark, whose hypotheses the table above shows fail on every chaotic system in the catalog except the null.

## C. Synthesis

### C.1 Is there a gap, and what is the smallest corrected statement?

**No theorem is unsound.** One hypothesis is unstated (P1(a)'s floor), one hypothesis set is implicit (P1(d)'s regime), one remark drops a term (separation), one clause is weaker than the truth (P3(b)). Corrected statements, each a post-freeze finding for the report and for a later v3 erratum, never applied to the sealed run:

1. **P1(a′).** c ≥ 0 always; c > 0 iff Pr_draws(e_C ≠ e_P) > 0; and c ≥ ρ²/k when the expectation is taken over the copied value's noise, which is independent of retrieval and of e_P. The study's w*, V(w) and excess MSE need only c > 0. **Affected verdicts: none.** Affected text: v3 §3 P1(a), Methods v2 M9 P1(a); the `excess_mse` docstring cites "c ≥ ρ²/k" as the hypothesis and should cite c > 0.
2. **P1(d′).** Add "with C ≥ 0 at every horizon, and the per-horizon envelope min(E_C, E_P)^{1/2} = r₀e^{ΛH}; on integer horizons the gain is at most ln 2/(2Λ) + 1 step; the bound survives verification noise added in quadrature." **Affected verdicts: none** (reported only, DEC-0016 O2).
3. **Separation.** u = (δ² − κ)q_H/((ε² + δ² − 2κ)q_H + ρ²/k); the stated closed form is its q_H → ∞ limit at κ = 0. **Affected: the reading of H2a** at horizons below a few steps only; H2a's horizons (1, 2, 4 LT) are unaffected.
4. **P3(b′).** The floor is zero iff clip(ū(F)) = w* a.s. on {c > 0}. **Affected verdicts: none**; it sharpens the reading of the regret-versus-K curve (H3c's pre-registered reading "this is the P3 floor").

### C.2 Which candidates best test the corrected or original claims

- P1(a′) (c against ρ²/k at short H): the null #4 (no growth at any H, so Var(e_P) stays near its H = 0 value) and any system at H = 1–3 steps; a report-only counter of c < ρ²/k costs nothing on the existing dumps.
- P1(d′) and the horizon law with two rates: #1 (hyper-Rössler) and #8.
- P2: any system; the useful test is tightness, where #2 (Rössler-z, dense near-ties) will have the most switching states.
- Separation against noise matching (H2a versus H2e): #3 (bimodal Λ̃) and #5 (sticky islands) give Λ̃ its widest range; #4 gives the only case where H2a(i) can pass.
- P3(b′) and the regret floor: #2, where w* should become a function of ν̂ to a larger degree (the floor should fall).

### C.3 Proposed experiment design for the first three (pre-specified; DEVELOPMENT seeds only)

Common to all: preset `pilot` on one development seed not yet used for the system (DEV-3 or DEV-4 from `seeds/`; never the confirmatory seed, never `--confirmatory`), one system per run, CPU at the owner's thread cap, after a `smoke` plumbing run; V1–V7 gate first, and a gate failure marks the system provisional and is referred, never retuned (v3 §6 E0). Expected pilot cost per system: about 0.5 h at 8 threads for a 3-D system (the local v1 pilot re-run took 5 493 s for three systems), ×1.5–2.5 for #1. Criteria below are fixed now, before any run; the hypotheses' pre-registered bands and levels are reused unchanged.

**#1 Hyperchaotic Rössler.**

- Prerequisites: V6 sets max_dt (halving must change x by < 1e-3 σ_x over 1 LT); Benettin λ₁ with SE ≤ 1% (the 100 000-step registry run gives SE ≈ 0.003/0.112 = 3%: use 10⁶ steps); the bound on |x| from the statistics orbit maximum ×1.5; AMI delay τ ≤ 5 so that 6τ ≤ 30.
- Support for the framework: H1a ratio in [0.75, 1.25] at both ρ with 1/d_LB ≈ 0.33; H1b slope in [0.8, 1.2]; H1c ratio in [0.8, 1.25]; the gain-bound fraction ≥ 0.90 (the lowest pilot value).
- Counterexample (pre-specified): H1b slope interval entirely outside [0.8, 1.2] (the seed × amplifier law fails with two rates), or H1c interval entirely outside its band (the horizon is not set by the 1-LT exponent).
- Report only: the H2a(ii) partial correlation against the three studied systems (an increase is the predicted sign; it cannot pass at n = 500, DEF-0022); Q-N both parts; the distribution of Λ̃ (expected wider: report its interquartile range against Lorenz-63's).

**#2 Rössler observed through z.**

- Prerequisites: `observed_index = 2` with the orbit bound kept on x (a guard change, one line, with its test); V7 at every ρ in [0.9, 1.1] (if V7 fails, the LM does not converge in the flat phase: provisional, and the finding is that the Cramér–Rao floor is not reached, itself informative).
- Support: H1d Spearman(δ̂, δ) ≥ 0.7 and Spearman(ε̂, ε_s) ≥ 0.7 with ε̂ built from Rν̂ (L4); H2c both upper bounds < 0 (A4 beats A2 and the better single forecaster: the observability mechanism makes state-dependent allocation pay).
- Counterexample: H2c's A4 − A2 interval entirely above 0 while A4o − A2 is below 0 (the pre-registered reading "deployable seeds limit it") or, stronger, A4o − A2 also above 0 (the closed form does not gain even with exact seeds where ν varies: a counterexample to the mechanism, not to P1).
- Report only: the fitted proxy coefficients (whether b_δ ≠ 0 and ν̂ no longer cancels in A4); the fraction of states with w* = 0 and w* = 1 (if w* = 1 exceeds 5%, H2a's third part is added by the existing rule).

**#3 Lorenz-63 at r = 166.1.**

- Prerequisites: λ₁ from a 10⁶-step Benettin run with the block SE reported (target ≤ 1%); orbit bound 300; max_dt 0.002 with V6; the ACF time and spacing recorded (the laminar phases lengthen it, so the trajectory length per state grows: the pilot's 500 test states may need a longer main trajectory, which the config already derives from the spacing).
- Support: H3b horizon-tree D lower bound > 0 and weight-tree Λ̃ importance interval inside [0, 0.2) (instability sets the horizon, not the weight, in the most intermittent case available); H1c ratio in [0.8, 1.25].
- Counterexample: the weight-tree Λ̃ importance interval entirely above 0.2 (instability enters the weight; the pre-registered reading "seed anisotropy" with the burst/laminar split as its mechanism) or the H3b lower bound of D < 0.
- Report only: the bimodality of Λ̃ (the two-component fit's separation); H2a(i) median range; the fraction of test states in laminar phases (by a Λ̃ threshold fixed at the pilot's Lorenz-63 median).

**Null #4 (Rössler c = 2.5), alongside, same seed:** support = H1a ratio inside [0.75, 1.25] at 1/d_LB ≈ 1 and H2a(i) median range interval below 0.1; counterexample = H2a(i) interval above 0.1 (w* depends on H with no amplifier: that would contradict P1's algebra under its own hypotheses and point to the copied-noise transient or an estimator artefact); H3a is inconclusive by construction (all censored) and is recorded as such.

None of these runs tests the sealed study's hypotheses; they test whether the framework's domain extends, and each is labelled DEVELOPMENT with its seed id.

## D. Researcher requests (numbered; no web access here; nothing below is asserted as fact)

1. Rössler, O. E. (1979), "An equation for hyperchaos", Phys. Lett. A 71: the four equations and the parameter set a = 0.25, b = 3, c = 0.5, d = 0.05; a published Lyapunov spectrum and Kaplan–Yorke dimension for it (expected ≈ (0.11, 0.02, 0, −25), d_KY ≈ 3.0 from this note's DEVELOPMENT estimate).
2. Manneville & Pomeau (1979) / Pomeau & Manneville (1980): the Lorenz-63 type-I intermittency threshold r_c (≈ 166.06?) at σ = 10, b = 8/3, and any published λ_max at r = 166.1 (this note: 0.61 ± 0.05).
3. Rössler, a = b = 0.2: the periodic windows in c (period-1 at c = 2.5? period-2 at 3.5?), and the funnel/screw parameter sets (a = 0.3, b = 0.2, c = 5.7; a = 0.343, b = 1.82, c = 9.75) with λ_max (this note: 0.119, 0.143).
4. Letellier, Aguirre & Maquet (2005), Phys. Rev. E 71: the observability ranking of x, y, z for Rössler and Lorenz-63 (z worst for Rössler? z symmetric-blind for Lorenz?), with the observability indices.
5. Lorenz (1996) "Predictability: a problem partly solved"; any source with the Lyapunov spectrum of Lorenz-96 at small N (5, 6, 8) and F = 8 (this note: N = 8 has two positive exponents, d_KY 5.4; N = 6 one, d_KY 4.0; N = 5 one, d_KY 2.9).
6. Hénon & Heiles (1964): the fraction of chaotic phase space at E = 1/8 and 1/6, and a published largest exponent in the chaotic component at E = 1/6 (this note: 0.136).
7. Zhong (1994) or another source for Chua's circuit with a cubic diode: a published chaotic parameter set (is α = 10, β = 14.87, a = −1.27, b = 0.0157 one?) and its λ_max (this note: 0.277 for that set).
8. Hénon map: Sprott's λ = (0.419217, −1.623190) at a = 1.4, b = 0.3 (already a fetch extract in `2026-10-10-research-lyapunov.md`, Chua follow-up row 1: please confirm from the page); Lozi map a = 1.7, b = 0.5 and Ikeda map u = 0.9: published λ and d_KY.
9. Mackey & Glass (1977); Farmer (1982) Physica D 4: λ₁ and the Lyapunov dimension for τ = 17 and τ = 30 at β = 0.2, γ = 0.1, n = 10.
10. Kuramoto–Sivashinsky at L = 22: a published λ₁ and d_KY (e.g. Edson et al. 2019 or Cvitanović et al.).
11. Sauer, Yorke & Casdagli (1991) "Embedology": the statement that D > 2 d_box suffices for a delay embedding of the attractor (needed for D = 7 with d_KY ≈ 3 and for D ≥ 11 with d_KY ≈ 5.4).
12. Levina & Bickel (2005): the locally-uniform (Poisson) hypothesis of the MLE and any published bias of the estimator on fractal or lacunar sets (needed to read H1a on #10 and on the current Rössler/Chua shortfall).
13. Bates & Granger (1969): confirm that their combination weight covers correlated errors (the form (E_P − C)/(E_C + E_P − 2C)), for the attribution in v3 §3.
14. Any published statement that for a continuous piecewise-linear vector field the flow map is C¹ but not C² (saltation matrix equal to the identity; e.g. di Bernardo et al. 2008, Piecewise-smooth Dynamical Systems), to support §B.4's Chua remark.

## E. Scripts and their outputs

All in `docs/agent/notes/2026-10-19-math-other-attractors/`, run by `run.sh` (project venv, `python -s`, `PYTHONPATH` = the worktree, one thread, nice 19; the venv was not modified). Logs are committed beside the scripts.

| Script | What it checks | Key output |
| --- | --- | --- |
| `p1_p3_sympy.py` (run with `uv run --no-project --with sympy python -I`; **sympy 1.14.0, mpmath 1.3.0, an ephemeral tool, not a project dependency**) | symbolic identities of P1(a)–(e), L6, P3(a)(b), P2(a) | every residual simplifies to 0; H′ − H = ln 2/(2Λ); u under proportional covariances has the ρ²/k term |
| `p1_p3_identities.py` | the same identities and inequalities in exact rational arithmetic, 2000 random triples; the P3(b) sharpening | 0 failures in all 8 checks; floor 0 for u ∈ {3/2, 5/2, 7/2}, 1/4 for {1/2, 5/2, 7/2} |
| `p1_curvature_floor.py` | (A) toy counterexample to c ≥ ρ²/k for the conditional estimand; (B) Lorenz-63 leverage ‖Γ_H J⁺‖² at H = 1…30 steps; (C) the selection effect on the copied noise, unconditional | see §B.1 and the block below |
| `p2_bound_check.py` | P2(a)(b)(c) on four libraries and two noise laws, 1.1 million draws | 0 violations; N/√B median 0.18–0.25 |
| `p3_regime_floor.py` | P3(a) brute force; P3(b) brute force per cell, 1000 random rules; the plug-in gap for a draw-dependent rule | 5e-7 agreement; 0 of 1000 rules beat clip(ū); floor exactly 0 where w* is constant; plug-in gap +56% in the adversarial toy |
| `p1d_horizon_gain.py` | P1(d) with the code's noisy, integer first passage | 0 violations in 1976 cases with C ≥ 0; violated in 500 of 500 with C = −0.9√(E_C E_P) |
| `lyapunov_candidates.py` | independent Benettin/QR spectra of 17 configurations; cross-check against `estimate_lyapunov` | cross-check bitwise (0.9054940534657817); registry systems within 1–2 SE of the cached values; the table of §A.2 |

**`p1_curvature_floor.log` (DEVELOPMENT, Lorenz-63, seed 20261019):**

- (A) Toy, conditional estimand (retrieval stable, Var(e_P) = 0.4ρ², e_C ≈ E e_P): c = 4.06e-5 against ρ²/k = 1.00e-4, ratio 0.41: the floor is violated.
- (B) First-order Var(e_P)/ρ² = ‖Γ_H J⁺‖² at 40 attractor states (physical coordinates; the quantity is coordinate-invariant):

  | H (steps) | median | min | max | fraction < 1 |
  | --- | --- | --- | --- | --- |
  | 1 | 0.70 | 0.03 | 1.9 | 0.70 |
  | 2 | 0.87 | 0.08 | 3.7 | 0.53 |
  | 5 | 0.98 | 0.03 | 20 | 0.50 |
  | 10 | 0.93 | 0.03 | 716 | 0.53 |
  | 30 (1 LT) | 4.0 | 0.04 | 6 232 | 0.30 |

  So at short horizons the PLP error's draw variance is below ρ² at most states, and even at 1 LT at 30% of them (the states where the observable's sensitivity direction is nearly orthogonal to the estimation error). The floor c ≥ ρ²/k therefore cannot be relied on from Var(e_P); in practice c ≫ ρ² at H_ref because (e_C − E e_P)² ≈ E_C ≫ ρ² there, which is a different reason from the theorem's.
- (C) Unconditional orthogonality on a Lorenz-63 delay-vector library (N_lib = 10⁴, D = 7, τ = 5, ρ = 1%; 30 library-noise realizations × 300 queries × 4 draws, 36 000 retrievals per H):

  | H | E[ξ]/ρ (± se) | E[ξ(e_C − ξ)]/ρ² (± se) | E[ξ²]/ρ² |
  | --- | --- | --- | --- |
  | 1 | −0.004 (0.005) | −0.087 (0.025) | 0.991 |
  | 2 | +0.001 (0.005) | +0.081 (0.030) | 0.991 |
  | 3 | −0.002 (0.005) | +0.057 (0.033) | 0.993 |
  | 5 | −0.000 (0.005) | −0.091 (0.040) | 0.994 |
  | 10 | −0.015 (0.005) | +0.186 (0.093) | 0.996 |
  | 30 | +0.015 (0.005) | −0.196 (0.204) | 1.013 |

  E[ξ²] = ρ² to 1%; the cross term with the latent mismatch is at most about 0.1ρ² in size at H ≤ 5 (3.5 se at H = 1, the H-shifted-competitor effect) and within noise at 1 LT; E[ξ] is zero within 1–3 se. So the **unconditional** version of P1(a)'s floor holds to within about 10% at the shortest horizons and exactly in the limit of distant competitors; it is the conditioning on the realized library in the study's estimand, not the selection effect, that removes the guarantee.

## F. What I could not verify

- Every literature value in §A (equations from memory are marked UNVERIFIED; the researcher requests of §D cover them). The chaotic parameter sets I used for the cubic Chua, the funnel Rössler and the Duffing oscillator are shown chaotic by my spectra but their provenance is unverified.
- The curvature floor on the real pipeline (a context build with a trained estimator was out of scope under the compute constraint); the evidence is the toy, the first-order leverage on Lorenz-63 and the selection-effect measurement on a Lorenz-63 library.
- The size of the draw-dependence term h_i for the real A4/A5 rules (needs the per-draw evaluation errors in the dump; the κ_E note's recommendation).
- Whether D = 7 embeds the hyperchaotic Rössler attractor (d_KY 3.01; D > 2d is 7 > 6.02, borderline: request 11).
- Nothing in this note was run on a GPU or at any preset size; the costs in §A.2 are extrapolated from the local pilot timing in DEF-0024's status line.
