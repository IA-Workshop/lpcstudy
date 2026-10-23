# WU-0022.2: attribution of the Chua exponent difference (Dysts against the study)

Date: 2026-10-23. Agent: applied-mathematician (claude-opus-5-5). Branch `wu/chua-math` from `develop` at `beb6254`. ROADMAP phase H, WU-0022.2 (the unit plan named this note `2026-10-21-dysts-chua-attribution.md`; the dispatch named the present file). CSQ3 development, documentation and scratch computation only: nothing in `lpcstudy/` or `tests/` was touched, the ledger and sealed run files were not read or written, and no study seed was used (the scratch computations draw no random numbers; their starts are listed below).

Scripts, logs and JSON outputs: `docs/agent/notes/2026-10-23-math-chua-attribution/`. Regenerate with `run_all.sh` there (one thread, `nice -n 19`, `JAX_PLATFORMS=cpu`, about 20 CPU minutes).

## 0. The question and the numbers compared

| Quantity | Value | Source |
| --- | --- | --- |
| Study's lambda_max, Chua, **DEVELOPMENT (DEV-0)** | 0.43113260161336364 per time unit | `docs/study/pilot_results_v3_dev0_reference.json`, `systems/chua/context/lambda_max` |
| How the study computes it | RK4 step 0.005, tangent of the RK4 flow map by `jax.jacfwd`, QR every 0.1 time units, burn-in 5000 intervals (500 time units), 100 000 intervals (T = 10^4), start (0.7, 0, 0) | `lpcstudy/data.py` `lyapunov_record`, `lpcstudy/systems.py` `lyapunov_guarded` (read) |
| Dysts `maximum_lyapunov_estimated`, Chua | 1.2301163591725595 (2.853 times ours) | researcher note `2026-10-20-researcher-dysts-extension.md` A.2 (fetch extract, `master`, commit unknown) |
| Dysts `lyapunov_spectrum_estimated`, Chua | 0.46055, 0.00220, -4.31908 | same |
| Dysts statement of an uncertainty for either field | none found | same, A.2 and A.5 |

The equations and parameters in Dysts are, by the relayed text, the study's own (A.1): x' = alpha(y - x - f(x)), y' = x - y + z, z' = -beta y, f(x) = m1 x + (m0 - m1)(|x+1| - |x-1|)/2, alpha 15.6, beta 28, m0 -1.142857 (ours -1.143), m1 -0.71429 (ours -0.714). The researcher's equations note (`2026-10-20-researcher-dysts-equations.md`) covers four other systems and adds nothing on Chua.

## 1. The independent implementation and its checks

`chua_np.py` is written from the equations above in NumPy and imports nothing from `lpcstudy`. It differs from the study's code in three ways: NumPy instead of JAX/XLA; the tangent comes from RK4 applied to the variational equation dV/dt = J(x) V with the analytic piecewise Jacobian (J11 = -alpha(1 + f'(x)), f' = m0 for |x| < 1, m1 otherwise), not from automatic differentiation of the map; and a second estimator, the two-trajectory Benettin method, uses no Jacobian at all.

Checks (`t0_checks.log`, `e1_reference.log`, `e2_benettin_settings.log`):

- **Tangent.** One RK4 step against a central difference of the RK4 map (step 1e-6, no breakpoint crossed): max difference 7.3e-11. The expected size is the difference rounding, about 1e-16 / 1e-6 times |J| ≈ 1e-10, so the check passes.
- **Liouville identity.** The sum of the three exponents must equal the time mean of div F = -alpha(1 + f') - 1. The run gives -3.81406 against -3.81402, a difference of 4e-5. That is of order 1/T, the size of the boundary terms of the QR product.
- **Re-orthonormalisation.** The interval (0.01, 0.1, 1.0) leaves lambda_1 unchanged to 5 decimals on identical orbits. This is expected, because the tangent map is linear.
- **Two estimators.** The two-trajectory method minus QR on identical orbits is +0.00051 ± 0.00012 (paired, 16 orbits, T = 2000). The size matches the O(1/T) alignment transient of a different initial vector.

**Escaping orbits (PRIME.4).** With the three-segment diode, some starts leave to infinity: 2 of the 9 distinct starts in E1 (grid points (-1.5, ±0.2, -1)), 4 of 4 at alpha ≥ 18.5 or beta = 20 in E3, and none elsewhere. They are counted in the logs and excluded. A first E1 version flagged them wrongly. After the state becomes NaN, the tangent follows the constant outer-region Jacobian, which gives a finite "exponent" of 0.3055, the real part of the outer complex pair. The flag was fixed and E1 was rerun. The first E2 version used time-shifted points of one orbit, whose windows overlapped at h = 0.005 and understated the SE. It was replaced, and its output was overwritten.

## 2. SE of the study's estimate, and the B2 comparisons

**Starts in E1.**

- (0.7, 0, 0), the study's start.
- The 8 grid points with x < 0: x in {-1.5, -0.5}, y in {±0.2}, z in {±1}. The field is odd, so the mirror points give identical exponents and are not used.

**Settings.** The code's: h = 0.005, QR every 0.1, burn-in 5000 intervals, T = 10^4.

**SE_code.** Batch means over 20 batches of 500 time units, about 215 Lyapunov times each:

- from the start (0.7, 0, 0), SE_code = **0.0046**;
- each of the 7 bounded starts gives a batch SE between 0.0046 and 0.0062;
- the standard deviation of lambda_1 across the 7 starts is 0.00465, so batch SE and between-start spread agree;
- batch independence is assumed, and this spread check supports it.

| Comparison | Difference | Combined SE | Verdict (B2: \|Δ\| ≤ 3 × combined SE) |
| --- | --- | --- | --- |
| Study 0.43113 against the independent ensemble mean of 7 starts, 0.43470 ± 0.00176 | -0.00357 | 0.00491 | agree (0.73 combined SE) |
| Study against the independent run from the same start, 0.44085 ± 0.0046 (the orbits separate after about 90 time units, so the two are effectively independent) | -0.00972 | 0.0065 | agree (1.5 combined SE) |
| Dysts maximum 1.23012 against the study | +0.79898 (174 SE_code) | no Dysts SE | reported without a verdict word |
| Dysts spectrum[0] 0.46055 against the study | +0.02941 (6.4 SE_code) | no Dysts SE | reported without a verdict word |

The independent implementation reproduces the study's exponent. The gap to the Dysts maximum field is 174 times the study's SE.

## 3. Candidate causes

| # | Candidate cause | Tested? | Result | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Different time units or rescaling (unit plan ii) | Tested, by arithmetic on stored values (no simulation is needed: a unit change multiplies the exponent by a factor fixed by a rule) | No single rule fits. The ratio Dysts-maximum/ours is 0.985 (Lorenz), 2.093 (Rössler), 2.853 (Chua). Ratio/period gives 0.66, 0.35, 2.00 and ratio·period gives 1.48, 12.4, 4.06, so neither is constant. The log-base factors (1.443, 2.303) and grid-spacing ratios (5, 10, 50, 100, 500, 5000) match none of the three. The Dysts `_rhs` has no time factor (A.4). | `t1_units.log` |
| 2a | Different parameters: rounding of m0, m1 (unit plan i) | Tested | Ensemble means: ours 0.43470 ± 0.00176, Dysts digits 0.43455 ± 0.00178, exact -8/7, -5/7 0.43374 ± 0.00237. The differences are -0.00014 and -0.00096 (combined SE 0.0025 and 0.0030), so no effect is resolved, against the 0.80 needed. | `e1_reference.log`, `t2_comparisons.log` |
| 2b | Different parameters: a nearby or classical set, or swapped diode slopes | Tested (4 starts each, T = 1000) | alpha from 8 to 18 at beta = 28: lambda_1 from -0.15 to 0.77; alpha from 18.5 to 20 escape. beta from 24 to 35 at alpha = 15.6: at most 0.62. Slopes swapped (m0 outer, m1 inner): 0.49 to 0.52. Classical double scroll (alpha 9, beta 100/7): 0.32 to 0.33. No scanned set reaches 1.23. | `e3_parameters_attractor.log` |
| 3 | Different attractor (single scroll against double scroll) | Tested | At the nominal parameters, every bounded orbit is the double scroll: 7 distinct starts in E1 and 4 in E3, including starts near the origin and near the outer equilibrium P+ = (1.5, 0, -1.5). On these orbits x > 0 for 49-51% of the time, there are about 160 scroll switches per 1000 time units, and max\|x\| is 2.2631, equal to the study's orbit maximum `lyapunov_orbit_max_abs` 2.26305. Single-scroll chaos appears only at other parameters (alpha 14, beta 32), with lambda_1 from 0.27 to 0.41. The Dysts spectrum is consistent with the double scroll: sum -3.856 against our -3.814, KY 2.107 against our 2.102, and an implied time fraction in \|x\| < 1 of 0.240 against our 0.246. | `e1_reference.log`, `e3_parameters_attractor.log`, `t2_comparisons.log` |
| 4a | Benettin RK4 step (unit plan iv) | Tested (32 independent orbits per level, T = 2000) | Levels: h 0.01: 0.43833 ± 0.00224; h 0.005: 0.43467 ± 0.00201; h 0.0025: 0.42976 ± 0.00190; h 0.00125: 0.43245 ± 0.00269. The differences are not monotone and lie within 1.8 SE of a difference, so no observed order can be computed (the piecewise-linear field is not smooth at \|x\| = 1, and the order is in any case below the noise). h 0.005 minus h 0.00125 = +0.0022 ± 0.0034, which bounds the error at the study's step below 0.009 at two sigma. | `e2_benettin_settings.log`, `t2_comparisons.log` |
| 4b | Re-orthonormalisation interval | Tested (paired) | 0.01, 0.1 and 1.0 give identical values to 5 decimals. | `e2_benettin_settings.log` |
| 4c | Transient (burn-in) | Tested | At T = 100: burn-in 0 gives 0.416, 5000 intervals give 0.454. The burn-in-0 members are correlated during their first 20 time units, so that SE is not valid. The study uses a 500-time-unit burn-in with T = 10^4, and the direction-alignment transient is O(1/T), about 1e-4. | `e2_benettin_settings.log` |
| 4d | Run length (unit plan iv, and the Dysts recipe, plan iii) | Tested | The finite-time exponent spreads with a standard deviation of 0.066 at T = 100, 0.0126 at T = 2000 and 0.0047 at T = 10^4, roughly as T^(-1/2). No finite-time value reaches 1.23. The largest over all runs with T ≥ 100 is 0.63. At the Dysts length T = 42.7 (E4), 400 single runs have mean 0.43 and sd 0.08, so 1.23 would be 10 sd above the mean. | `e2_benettin_settings.log`, `e1_reference.log`, `e4_dysts_spectrum_replica.log` |
| 4e | Dysts' spectrum recipe, as relayed (plan iii; this explains the spectrum field, not the maximum field) | Tested by replica. Unknowns, assumed: how the starts are drawn, the transient, and the integrator (RK4 at Δ/5 instead of Radau) | The replica uses 500 points per period, 15 000 samples (T = 42.7), backward-Euler tangents, 20 starts weighted by exp(-1000 min\|λ_i\|), and 20 replications. lambda_1 = 0.450 (sd 0.054) with the RK4 tangent and 0.380 (sd 0.051) with backward Euler. The weighting gives about three-quarters of the weight to a single run (median top share 0.74 to 0.76). Dysts' 0.4605 lies 0.2 and 1.6 replica sd from these two means. Dysts' 1.2301 lies 14.5 and 16.7 sd away. | `e4_dysts_spectrum_replica.log`, `t2_comparisons.log` |
| 5 | Jacobian form | Tested | The analytic variational Jacobian, the Jacobian-free two-trajectory method and the study's `jacfwd` give the same exponent (sections 1 and 2). Two deliberate Jacobian errors on the true orbit, with the inner and outer slopes swapped or the 1/2 dropped in f', give 2.097 ± 0.007 and 2.090 ± 0.009, not 1.23. Dysts' own Jacobian-based spectrum field is 0.46, so a Jacobian error of that kind is not visible in Dysts' spectrum field. | `e2_benettin_settings.log` |
| 6 | The stored maximum is unreliable, or comes from a different estimator | Partly tested. The code that wrote the field was **not read** (A.5), so its method and settings are untested. | (a) The field is not consistent with Dysts' own spectrum (2.67 times spectrum[0]), while the stored KY dimension 2.107 follows from the spectrum, not from the maximum. (b) A short-window nearest-neighbour divergence estimate (Rosenstein, full state, 100 samples per period, fit windows K = 5 to 100 samples fixed in advance) gives 0.60 to 2.77 for Chua, depending on K. K = 40 gives 1.197. But no single K reproduces all three stored maxima: at K = 40 Lorenz gives 1.91 (stored 0.89) and Rössler 0.095 (stored 0.151). So a divergence-type estimator can produce values of this size for Chua, but this replica does not reproduce the stored field. (c) Two numerical coincidences, found after about 15 expressions were tried (look-elsewhere), are recorded and not used as attribution: 2 × period = 2.847 against the ratio 2.853, a rule that fails for Lorenz and Rössler; and the inner-region divergence -alpha(1 + m0) - 1 = 1.2286 (Dysts m0) against the stored 1.2301, a rule that fails for Lorenz (divergence -13.67, stored 0.89). | `t1_units.log`, `e5_divergence_estimators.log` |

## 4. Uncertainty budget for the study's lambda_max (Chua, DEVELOPMENT DEV-0)

| Source | Type | How estimated | Size | Included in the reported interval? |
| --- | --- | --- | --- | --- |
| Finite averaging time (T = 10^4, one orbit) | sampling (deterministic chaos treated as a stationary process) | batch means, 20 × 500 time units; checked against the spread over 7 starts | SE 0.0046 | yes, as the SE in B2 |
| RK4 step h = 0.005 | numerical | step refinement, 4 levels (4a) | not resolved; \|e\| < 0.009 (2σ) | no. **Not shown to be 10 times below the SE (NVVUQ.9)**: resolving it needs about 100 times the run length per level. |
| Re-orthonormalisation interval | numerical | paired change of interval (4b) | < 1e-5 | no |
| Transient and initial alignment | numerical | 500-time-unit burn-in; O(1/T) bound; two-trajectory minus QR | about 5e-4 | no |
| Round-off | numerical | float64; the identical-orbit comparisons agree to 1e-5 | < 1e-5 (not estimated separately) | no |
| Parameter rounding (-1.143, -0.714 against -8/7, -5/7) | model input | ensemble comparison (2a) | not resolved; \|Δ\| < 0.009 (3 combined SE) | no; the study defines its own parameters |
| Model form (dimensionless three-segment diode) | epistemic | not estimated | — | no |

Interval level: 1 SE. Dependence: the batches are assumed independent, and the spread over the 7 starts supports this. The numbers come from scratch runs on deterministic starts. They are not study data and carry no seed.

## 5. Conclusion: what the data support, and no more

The study's exponent is reproduced by an independent implementation within one combined SE. Each tested candidate cause changes the exponent by at most about 0.01, or reaches at most 0.77. The difference to be explained is 0.80.

- Time units: no single conversion rule fits the three systems.
- Parameters and diode slopes: rounding, nearby values, swapped slopes and the classical set all fall short.
- The attractor: every bounded orbit is the double scroll that the study uses.
- Benettin settings: step, re-orthonormalisation interval, transient and length.
- The Jacobian.

Dysts' own spectrum entry, 0.46, lies within the spread of a replica of Dysts' short-run recipe (sd about 0.05). Its sum and Kaplan-Yorke dimension are consistent with the study's attractor.

The stored maximum field, 1.23, is not consistent with Dysts' own spectrum for the same system. Short-window divergence estimators can give values of that size for Chua, but the replica tried here does not reproduce the three stored maxima with one setting. The script that wrote the field was not read. **The cause of the difference is not determined.** The data support no more than this: the field was not produced by a different system, parameter set, time unit, attractor or Benettin setting. Whether it comes from a different estimator, or is an error, is open.

**Sentence for the research statement:** "The Dysts database's stored maximum Lyapunov exponent for Chua's circuit differs from ours, and the cause is not determined. We tested and excluded differences of equations, parameters, time unit, attractor and integration settings, and Dysts' own Lyapunov spectrum for the same system lies within the sampling spread of its short-run method around our value."

Number-free variant for WU-0025.3: "The Dysts database's stored maximum Lyapunov exponent for Chua's circuit differs from ours for a reason we could not determine; the same equations, parameters, time unit and attractor were confirmed, and Dysts' own spectrum entry for the system is near our value."

**Proposed DEC-0010 limitation wording, for the owner:** "No published largest Lyapunov exponent exists for Chua at the study's parameters. The study's value is reproduced by an independent implementation. Of the two Dysts estimates, the spectrum entry is near it and the stored maximum is about three times larger for an undetermined reason, so neither Dysts number validates the study's value."

## 6. Open item (needs the researcher, which this role cannot dispatch)

Read the Dysts script and version that wrote `maximum_lyapunov_estimated`: the `analysis.py` `max_lyapunov_exponent` settings and the git history of `chaotic_attractors.json`. Then rerun `e5_divergence_estimators.py` with those settings. That is the only test left for candidate 6.
