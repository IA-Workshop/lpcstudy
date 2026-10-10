# NVVUQ Instantiation for the LPC Study

| Field | Value |
| --- | --- |
| Level | LVL3 project instrument: how the project meets LVL1 profile NVVUQ (GOV.20, GOV.25) |
| Applies at | CSQ2 for the confirmatory pipeline; CSQ3 for development work (LPC.PC.5, NVVUQ.23) |
| Status | **Draft.** Adopted by the human owner after the custodians adopt NVVUQ (LPC.PC.4). |

**How to read this file.** Each row cites the profile provision it meets, gives the project's means, and gives the current status. The statuses are:

- **met:** evidence exists in the code or the pilot;
- **gap → WU-nnnn:** to be closed by the named unit of work before the freeze;
- **declared:** stated as a limitation or axiom.

## Modeling convention that bounds the numerical-error question

**LPC.NV.1 The system is the discrete map** (NVVUQ.4, NVVUQ.9). Every QoI is defined for the fixed-step RK4 flow map at the configured observation interval, not for the continuous ODE. Truth and the physics model use the same map (exact-model design, decision D2). Discretization error therefore does not enter forecast-error comparisons.

Discretization error does enter one place: how the discrete map relates to the published continuous systems. That is checked through λ_max (LPC.NV.13) and the step-halving check V6.

## Mapping

| Profile | Project means | Status |
| --- | --- | --- |
| NVVUQ.3 QoIs | Declared in proposal and methods v3: w*, ε_s, δ, ν, Λ̄, N, horizons, MSE and its ratios, ΔR², the statistics behind each hypothesis. Acceptance criteria: v3 §2 and §7. | met (design); restate in the report → WU-0008 |
| NVVUQ.4 Domain of validity | Small-error regime (assumption A6); θ ≥ 3√2ρ; delay window ≤ 1 LT; float64 | met |
| NVVUQ.5 Code verification | RK4: V6 step halving checks magnitude, not order | **gap → WU-0005**: observed-order test on a linear ODE with an exact solution |
| | Analog search | **gap → WU-0005**: k-d tree against brute-force nearest neighbor |
| | Levina–Bickel dimension | **gap → WU-0005**: test on sets of known dimension |
| | Kaplan–Meier against exact censored geometric survival (V5) | met |
| | Gauss–Newton attains ρ²ν² (V2) | met |
| | Noise sensitivity N against the Theorem P2 bound, state by state | **gap → WU-0005** |
| NVVUQ.6 Derivatives | Delay-map Jacobian and amplifier against central differences (V1, relative error < 10⁻⁴) | met |
| NVVUQ.7 Statistical procedures | Coverage of the moving-block bootstrap intervals (mean, median, Spearman, partial correlation, paired change, MSE ratio); size of Holm-adjusted log-rank tests; ΔR² interval under a null; verdict-rule branches | **gap → WU-0006** (at pilot sample sizes, with the simulation's own Monte Carlo error) |
| NVVUQ.8 Random streams | `make_rng(seed, *labels)` derives an independent stream per purpose; seed registry and confirmatory commitment | met; provenance → WU-0001 |
| NVVUQ.9 Numerical error | Discretization bounded by LPC.NV.1 and V6; round-off: float64 throughout, and the observability formula avoids inverting ill-conditioned Q (cond ≈ 10⁷) | met. The size of each error per QoI is to be stated in the report's budget → WU-0008 |
| | Levenberg–Marquardt iterative error: about 2% of draws land in a wrong basin and are kept by design; the residual is not reported per estimate | **gap → WU-0005**: report the achieved residual and the iteration count |
| NVVUQ.10 Convergence | Oracle draws: V4 half-width ≤ 0.05 at M = 200. Bootstrap: 2000 resamples. | met; Monte Carlo error of the interval endpoints → WU-0008 |
| NVVUQ.11 Special values | Replacement by the invariant mean; clipping at 10 σ_x; regime-count fallback | **gap → DEF-0001 / WU-0002** |
| NVVUQ.12 Precision, determinism | float64 declared; GPU run-to-run tolerance | **gap → WU-0003** |
| NVVUQ.13 Validation | No real-world referent: the systems are mathematical models. Validation that applies: (a) λ_max of each discrete map against published values, confirmed under VV.2 → **WU-0007** (researcher); (b) theorem hypotheses (NVVUQ.14) | gap → WU-0007; (b) met by design |
| NVVUQ.14 Theorem hypotheses | P1(c)–(d) need C ≥ 0: report the fraction of states where it holds (H2e subset). Separation needs proportional covariances (tested by H2a). P2 is checked numerically (WU-0005). A6 is enforced by the small-error restriction. | met (design); P2 → WU-0005 |
| NVVUQ.15 Uncertainty budget | Per primary QoI: oracle Monte Carlo error (M draws), bootstrap interval, numerical error, proxy error (deployable vs oracle), and epistemic items (exact-model assumption, three systems only) | **gap → WU-0008** |
| NVVUQ.16 Intervals | v3 §7: moving-block bootstrap, blocks of 5, 95% (98.3% for primaries), intersection–union overall verdict | met (design); figure labels → WU-0008 |
| NVVUQ.17 Sensitivity | Robustness experiment E6 (D, k, model perturbation, finite-amplitude growth) and V4 (M). The embedding delay and θ are fixed with their reasons stated in v3. | met (design) |
| NVVUQ.18 Confirmatory separation | Seed registry, salted SHA-256 commitment, per-action confirmatory authorization (LPC.PC.7, LPC.AUTH.6) | met (design); code → WU-0001 |
| NVVUQ.19 Decision rules | v3 §7 three-way verdicts and the Q-N reading table | met (design); code → WU-0002 |
| NVVUQ.20 Precision planning | Pilot projection (Methods v2 §M12); development rehearsal | met; update → WU-0003 |
| NVVUQ.21 Multiplicity | Three primaries at 1 − 0.05/3; intersection–union across systems; secondaries labeled | met (design) |
| NVVUQ.22 Reporting | `RESULTS.md` header labels and provenance; per-QoI budget table | **gap → WU-0001, WU-0008** |

## Axioms and declared limitations (VV.9, INTPR.10)

**LPC.NV.2** Proposed axioms, for the human owner to declare or reject:

- the moving-block bootstrap with blocks of 5 states is adequate for the residual dependence of thinned states;
- Theorem P2's Gaussian-concentration form is not relied upon; only the Markov form is.

Stability of the intervals under doubled thinning is not checked (DEF-0009).

## Revision history

| Revision | Date | Change |
| --- | --- | --- |
| 0.1 (draft) | 2026-10-10 | Proposed by Claude for adoption by the human owner. |
