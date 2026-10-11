# WU-0007: Reference-value validation of lambda_max (Lorenz-63, Rossler, Chua)

| Field | Value |
| --- | --- |
| Status | in progress (WU-0007.1 done with Chua not found; .2 and .3 to plan) |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (main session) under governance ledger entry 5 (authorizations 4, 6); DEC-0009, DEC-0010 |
| Estimate | ROADMAP WU-0007.2 (S), .3 (S) |

## Plan (written before execution)

Planner: claude-opus-5-5, 2026-10-11. Sources: ROADMAP WU-0007.2/.3, v3 §4 (systems table, "Integration and time scale"), Methods v2 §M2, NVVUQ-instantiation-LPC (LPC.NV.1, row NVVUQ.13, NVVUQ.22), `docs/agent/notes/2026-10-10-research-lyapunov.md` incl. "Chua follow-up (2026-10-11)", DEC-0010 (proposed).

**Roadmap rows (verbatim).**
- WU-0007.2 | Test: the code's Benettin estimate against the confirmed published value per system | applied-mathematician (tolerance), developer | WU-0007.1 | CSQ3 | NVVUQ.13 | `test_systems` (slow if over 5 s) | S
  - Acceptance: "Test passes or a DEF records the discrepancy | The code's `estimate_lyapunov` at the configured interval agrees with the confirmed value within 3% relative (Benettin estimates over 2×10⁵ steps carry a standard error near 1%; the applied-mathematician confirms or tightens before execution). A larger discrepancy is reported with the step size as the suspected cause (LPC.NV.1) and is not tuned away. The Methods v2 §M2 values (0.905, 0.0719, 0.431) are compared with the confirmed values in the note."
- WU-0007.3 | Validation section of the report states the comparison and the LPC.NV.1 convention | developer | WU-0007.2 | CSQ3 | NVVUQ.13, NVVUQ.22 | `test_report` | S
  - Acceptance: "`RESULTS.md` validation section has the three comparisons and the sentence that validation against a real-world referent does not apply (NVVUQ.13) | `test_report` asserts both on a fake results dict."

**Facts read from the code (bear on the criteria).**
- "Configured interval" = `lyapunov_cached` (`lpcstudy/data.py:214`): tangent step `20*max_dt` (Lorenz 0.2, Rössler 0.8, Chua 0.1 time units, 20 RK4 substeps each), `n_steps=100_000`, `burn_in=5_000`, start `spec.initial_state`. Averaging time T: Lorenz 2×10⁴, Rössler 8×10⁴, Chua 10⁴ time units. **The roadmap's "2×10⁵ steps" does not match the code (10⁵ Benettin steps; 2×10⁵ is the statistics trajectory).** The SE must be re-derived for 10⁵ (question M1).
- `estimate_lyapunov` returns per natural time unit, so the comparison is in natural time units directly; no step conversion (per-step λ is 1/30 by construction and carries no information).
- The estimate is deterministic and seed-independent (fixed initial state, no RNG). It is already in `results.json` as `systems.<s>.context.lambda_max` (`build_context` meta, `experiments.py:137`). **No schema change.**
- The pilot already shows the code's values (`docs/study/pilot_results_v1.json`): Lorenz 0.905494, Rössler 0.0719398, Chua 0.431133. Methods v2/v3's 0.905, 0.0719, 0.431 are these rounded: code output, not literature. **VV.3 caveat:** the values are visible, so the 3% stays as the roadmap fixed it, and any tightening must rest on the SE alone, not on the observed gaps.
- Chua field form: `f(x) = m1 x + (m0-m1)(|x+1|-|x-1|)/2` has slope m0 for |x|<1 and m1 outside, with x' = α(y - x - f(x)), y' = x - y + z, z' = -βy. This is the same form and slope naming as the researcher's mapping of the memo (inner -0.8/0.7 = -8/7 = m0, outer -0.5/0.7 = -5/7 = m1). It is verified against `systems.py:74-101`.

**Scope.**
- In:
  - (.2) a new slow test of `lyapunov_cached` (hence `estimate_lyapunov`) at the configured settings, against published values;
  - (.2) the memo check (only if DEC-0010's proposal is approved);
  - (.2) a dated addendum to the research note: the Methods v2 comparison plus the finding that those values are the code's pilot output;
  - (.3) a new subsection "Lyapunov exponent against published values" under `## Validation gate` in `write_markdown`, a reference table constant in `report.py`, and the `test_report` test.
- Out:
  - any change to `systems.py`, `data.py` or `pipeline.py`;
  - changes to the estimator's step, length or burn-in (that would be tuning: LPC.NV.1, PRIME.2);
  - putting the λ comparison into `gate_pass`, `VALIDATION_CRITERIA` or `verdicts()` (verdict code: owner decision, Q-O3);
  - running the memo case in the pipeline;
  - Chua validation at the study's own parameters (a known limitation, DEC-0010).

**WU-0007.2 test.** File `tests/slow/test_systems_lyapunov.py`. It is new and the first in `tests/slow/`. The name follows the `test_<m>_*` convention so `/test-impact --include-slow` reaches it on `systems.py` changes, and it avoids a basename clash with `tests/unit/test_systems.py`. Each case calls `lyapunov_cached(spec, tmp_path/"lyapunov.json")` and asserts the value is finite and within tolerance. Each docstring names its reference and gives the tolerance's derivation.

| Case | Reference (per natural time unit) | Status | Conversion | Tolerance (proposed, mathematician confirms/tightens) |
|---|---|---|---|---|
| `lorenz63` (registry spec) | 0.90563, Sprott lespec.htm. Cross-check: Hartl 0.905±0.003 | confirmed; integrator and step not stated | none | \|λ/0.90563 − 1\| ≤ 0.03. This is ≈3 SE if SE ≈ 1% (M1). The source spread 0.897–0.9056 (Kuznetsov, B&B, Hartl) is ≤ 1%. RK4 at dt 0.01 bias is O(dt⁴), negligible. QR interval does not bias λ₁. |
| `rossler` (registry spec) | 0.0714, Sprott as cited by Bogdanov & Bogdanova arXiv:1412.2242. Also 0.07062±0.00066 (B&B own) | 0.0714 confirmed, secondary. 0.07062 confirmed, primary. | none | \|λ/0.0714 − 1\| ≤ 0.03, **and** \|λ/0.07062 − 1\| ≤ 0.03. The second is a tightening; the two references differ by 1.1%. |
| `chua_memo`, built in the test as `SystemSpec(name="chua_memo", field_fn=chua_field, params={alpha: 9, beta: 100/7, m0: -8/7, m1: -5/7}, dim=3, observed_index=0, initial_state=(0.7,0,0), max_dt=0.005)` | μ₁ ≈ 0.23 per memo circuit time (UCB/ERL M84/73 (3.23), RK step 0.005, T = 3000, "convergence ... very slow") | confirmed for the memo's set. Conversion DERIVED (researcher, not in the memo). | τ = 0.7 t, so λ_τ = 0.23/0.7 = 0.3286 | Proposed \|λ/0.3286 − 1\| ≤ 0.10. Rounding of "0.23" gives ±2.2%. The memo's finite-time error at λT ≈ 0.33 × 2100 ≈ 700 LT is ≈ 5% (1 SE, scaled from Lorenz), and it is biased low ("still increasing"). M3 fixes this before execution. |
| `chua` (registry) | none | **not found**: known limitation (DEC-0010) | n/a | no assertion. The value is recorded in the Log and in RESULTS.md as "no published reference". |

- **Tier and cost: slow.**
  - Per case: 5×10³ + 10⁵ Benettin steps. Each step is `jacfwd` through 20 RK4 substeps plus a 3×3 QR inside `lax.scan`. Estimate: 3–10 s per case on CPU at 4 threads, plus 1–3 s JIT, so ≈ 15–50 s for the four cases.
  - That exceeds the 5 s unit budget, and the length cannot be cut: a shorter run tests a different estimator from the one the study uses, and its SE (∝ 1/√T: ≈ 3% at 10⁴ steps) would reach the tolerance.
  - The developer records `--durations` once (§4.6) to confirm.
  - Run once, through `tools/run_tests.sh`, in the background, after checking `pgrep -fa "lpcstudy --preset"`.
- **On failure:**
  - record a DEF with the value, the step (`20*max_dt`, `max_dt`) as the suspected cause (LPC.NV.1), and the reference conditions (unknown integrator);
  - change no step, length, seed or tolerance (PRIME.2).
  - For the memo case, the derived conversion and the memo's convergence are suspects before the code.
- **Note addendum** (append-only, dated): a table of Methods v2 values against the references with relative differences, and the finding that they are the code's rounded pilot values.

**WU-0007.3 report section.**
- Add a constant `LYAPUNOV_REFERENCES` in `report.py`: system → (value or None, source text, status), with the three rows above and the 3% bound.
- `write_markdown` adds, after the V7 rows, the subsection `### Largest Lyapunov exponent against published values`.
- The subsection holds one row per system present: system | code λ_max (from `systems.<s>.context.lambda_max`) | reference(s) | status and source | relative difference | "within 3%", or "outside 3%: step size suspected (LPC.NV.1), reported not tuned", or "no published reference (known limitation, DEC-0010)". A missing `context` prints "n/a", not a silent skip (PRIME.4).
- Fixed sentences:
  - (a) "Every quantity is defined for the fixed-step RK4 flow map at the configured observation interval, not for the continuous ODE (LPC.NV.1). λ_max is estimated on that map by Benettin's method and compared in natural time units with published values for the continuous systems."
  - (b) "Validation against a real-world referent does not apply: the three systems are mathematical models (NVVUQ.13)."
  - (c) A memo-case sentence citing `tests/slow/test_systems_lyapunov.py`, only if Q-O1 is approved.
- Test `test_markdown_lyapunov_section_has_comparisons_convention_and_referent` in `tests/unit/test_report.py`:
  - add `"context": {"lambda_max": ...}` to `fake_system`;
  - use fake values lorenz63 0.9 (−0.62%, within), rossler 0.08 (+12.0% vs 0.0714, outside, with the LPC.NV.1 phrase), chua 0.43 (limitation text);
  - expected strings are computed by hand in the test;
  - assert sentences (a) and (b) verbatim;
  - add one case without `context`, which gives "n/a".
- **DEV-0 smoke consequence:**
  - no computation path changes, so `results.json` is numerically and structurally identical to the baseline;
  - `RESULTS.md` gains the subsection, with one row (smoke runs lorenz63 only); this is an expected diff, to be recorded.

**Definition of done.**
- (.2) The slow test is committed and run once, and its summary line and the four values are in the Log.
- (.2) Each of Lorenz and Rössler passes, or has a DEF.
- (.2) The memo case passes, has a DEF, or is dropped by Q-O1.
- (.2) The Chua limitation is restated in the Log.
- (.2) The note addendum is appended.
- (.3) The section is rendered, `test_report` passes, and the integration radius has passed once.
- Review per the cycle.

**Acceptance criteria.** The tolerances in the table above, fixed now (VV.3). The mathematician may tighten them, never loosen them.

**Affected checks (§4.2; confirm with `/test-impact`).**
- (.2): new single file, so that file only: `tests/slow/test_systems_lyapunov.py` (slow). The docs addendum needs no tests.
- (.3): `report.py` is touched, so `tests/unit/test_report.py` and `tests/unit/test___main__.py` (direct dependent), unit tier, plus `tests/integration/` (the pipeline is touched): `test_smoke_pipeline.py`, `test_cli_seeds.py`, `test_preset_wrapper.py`. Run the smoke test or the smoke preset by hand, not both.

**Owner checkpoints (LPC.PC.11).**
- Verdict or statistics code: no. `verdicts()`, `VALIDATION_CRITERIA` and the gate are untouched; if the developer finds otherwise, stop and `/refer`.
- Seed or provenance: no.
- Dependencies: no.
- DEC-0010 (memo case) is proposed and awaits the owner (Q-O1).

**Split.** Two coherent changes, done in order: .2 (test plus note, no `lpcstudy/` change) and then .3 (report). Separate commits and separate radii, on the same branch.

**Risks.**
- Pilot values were already seen (VV.3; see above).
- The memo initial state may lie outside the double-scroll basin. The 3-segment piecewise-linear model can diverge from far states, so the test asserts a finite, positive λ and a bounded `|x|`.
- The derived memo conversion may be wrong (the m0/m1 labels are swapped in the memo).
- `report.py` merge conflicts with the WU-0002 lanes (the main session resolves them).
- The `fake_system` change feeds every `test_report` test.

**For the applied-mathematician (before execution).**
- M1: the SE of `estimate_lyapunov` at 10⁵ steps × `20*max_dt` per system (T = 2×10⁴, 8×10⁴, 10⁴ time units). If no a-priori bound is possible, say whether the slow test must estimate it from K = 4 extra runs from distinct attractor states (cost ×5).
- M2: do the Lorenz and Rössler references, with unknown integrators and run lengths, justify 3%, or a tighter bound (≥ 3 SE plus the reference spread)? Is the dual Rössler assertion sound?
- M3: confirm the memo conversion (τ = tG/C₂ = 0.7t; α = 9, β = 100/7, m0 = −8/7, m1 = −5/7 in the code's naming) and fix the memo tolerance (10% proposed).
- M4: is a finite-T start-up bias from the burn-in and basis alignment negligible at these lengths?

**Questions for the owner.**
- Q-O1: approve DEC-0010's memo case (otherwise drop it and keep the limitation only).
- Q-O2: v3 §4's λ_max column is the code's own rounded output; should the design text say so? (This is a documentation decision, not code.)
- Q-O3: should an "outside 3%" result ever affect `gate_pass`? (Currently report-only; changing it is verdict code.)

**Open questions for the researcher.** None blocking. Optional: the primary source for Sprott's Rössler 0.0714 (book, 2003).

### Plan amendment (2026-10-11, planner claude-opus-5-5)

This follows the applied-mathematician's entry in `## Log` dated 2026-10-11 (commit 8e1dc9e). It supersedes the plan text above where they differ; the text above is kept unedited. No criterion is loosened.

**A1. Standard errors at the code's length** (10⁵ Benettin steps at 20·max_dt, burn-in 5000). Lorenz 0.0012 (0.13%), Rössler 0.00055 (0.75%), registry Chua 0.0048 (1.1%), memo case 0.0050 (1.5%). These are DEVELOPMENT measurements, to be cited as such in the docstrings.
- The roadmap's "SE near 1%" is 8× too pessimistic for Lorenz and refers to 2×10⁵ steps, which the code does not use.
- No extra runs in the test. M1's K = 4 option is withdrawn: the SD it would give is uncertain by ±40%.
- Start-up bias is negligible (at most 0.06% of λ) and the 5000-step burn-in is adequate (M4).

**A2. Tolerances** (they replace the table's tolerance column).

| Case | Assertion | Derivation |
|---|---|---|
| `lorenz63` | \|λ/0.90563 − 1\| ≤ **0.01** (tightened from 3%) | 3·√(0.13² + 0.33²) = 1.06%. The 0.13% is the code's SE; the 0.33% is Hartl's ±0.003, standing in for Sprott's unstated uncertainty. RK4 bias is below 1e-4 relative. No observed gap was used. |
| `rossler` | \|λ/0.0714 − 1\| ≤ 0.03 **and** \|λ/0.07062 − 1\| ≤ 0.03 | Against 0.07062 the combined σ is √(0.75² + 0.93²) = 1.19%, so 3% ≈ 2.5σ. It cannot be tightened on SE grounds. The two references agree within about 1.2 of B&B's σ, and the family-wise false-alarm probability is at most about 2%. RK4 bias is -0.1%. |
| `chua` (study parameters) | no λ assertion | Known limitation, not validated (NVVUQ.13; DEC-0010). λ is reported only. The orbit guard (A4) still applies. |
| `chua_memo` | **on hold** (A3) | — |

The roadmap's three-way comparison is met by Lorenz and Rössler. Chua is recorded as **not validated**, a known limitation under NVVUQ.13, unless A3's condition is met.

**A3. Memo case on hold.** The memo as read gives μ₃ ≈ -0.28 and Σμ ≈ -0.05. The mathematician showed both are impossible for the assumed standard double-scroll equations: Σμ must equal the mean divergence, about -1.54 per circuit time. The memo case therefore enters the plan only if the researcher's re-read (memo pp. 22-25 and eq. (1.1)) confirms all three of:
- (i) a verbatim (1.1) in the assumed form;
- (ii) a time variable that gives τ = tG/C₂ = 0.7t;
- (iii) μ₁ ≈ 0.23 as a value per that time, with the μ₃/Σμ discrepancy explained (for example, a misread scan).

If all three hold, `chua_memo` is tested as `SystemSpec(alpha=9, beta=100/7, m0=-8/7, m1=-5/7, initial_state=(0.7,0,0), max_dt=0.005)`:
- assertion: |λ/0.3286 − 1| ≤ 0.10;
- the 10% is the mathematician's combined σ ≈ 3.9% (code SE 1.5%, memo finite-T SE 3.3%, rounding of "0.23" with SD 1.3%, discretization below 1.5%), so 10% ≈ 2.6σ;
- the memo value is not biased low, so no one-sided allowance;
- plus the A4 guard with max|x| ≤ 3.

The code's memo value (0.3235) has already been seen in development. The 10% comes from the error budget only.

If any of (i)-(iii) fails, the memo case is dropped. The unit then records the memo as an unusable reference and Chua as not validated. Q-O1 becomes moot unless the re-read confirms.

**A4. Divergence guard (F1, DEF-0015).**
- The problem: `estimate_lyapunov` returns a finite, positive, plausible value for diverging orbits (3 of 12 perturbed Chua starts), so "finite and positive" detects nothing.
- What each case adds: build the same map, `make_flow_step(spec, spec.params, 20*spec.max_dt)`, from the same `spec.initial_state`. Run `simulate_trajectory` for 5000 + 10⁵ steps (≈ 0.2 s), and assert every value finite and max|x| ≤ B:
  - **Chua, both sets: B = 3.** The attractor has |x| ≤ 2.26, measured by the mathematician. The registry start (0.7,0,0) is in the basin for both sets.
  - **Lorenz: B = 40.** This is rigorous for the ODE. V = x² + y² + (z − σ − ρ)² satisfies V̇ = −2(σx² + y² + βz² − β(σ+ρ)z), which is negative outside an ellipsoid contained in the ball V ≤ (σ+ρ)²β²/(4(β−1)) = 38²·16/15, radius 39.25. So the ball is forward-invariant. The start (1,1,1) has V = 1371 < 1540, so |x| ≤ 39.25 for all t. The margin 0.75 absorbs RK4 error at h = 0.01. Any value above 40 means the map has departed from the flow.
  - **Rössler: B = 25.** No simple global trapping region exists, so the guard rests on the escape mechanism. An escaping orbit has x > c = 5.7 persistently, and z' = b + z(x − c) then grows z exponentially into overflow within 10⁵ steps. Any bound well above the attractor separates the two cases. The developer records the observed max|x| in the Log. If it exceeds 2/3 of B (16.7), stop and `/refer`; do not raise B.
- The guard duplicates `lyapunov_cached`'s constants (20·max_dt, 10⁵, 5000). The test names them in one place and comments that they mirror `data.py:231-233`.
- A guard inside `estimate_lyapunov` stays out of scope (DEF-0015, main session).

**A5. Tier and file: unit, in `tests/unit/test_data.py`.**
- The slow tier is withdrawn. The only reason for it was my runtime estimate, which was about 10× too high; the measured cost is 0.4-0.6 s per case including JIT, plus 0.2 s for the guard. There is no other reason for slow.
- Placement:
  - The module under test is not `dynamics.py`: `estimate_lyapunov` is in `lpcstudy/systems.py` and `lyapunov_cached` in `lpcstudy/data.py`.
  - `tools/test_impact.py` maps a module's unit tests only to `tests/unit/test_<module>.py`. A new `test_lyapunov.py` would never be selected.
  - `test_data.py` is reached by a change to `data.py` (own test) and by a change to `systems.py` (core-module rule: `data` is a direct dependent of `systems`). The roadmap's `test_systems.py` would miss changes to `lyapunov_cached`.
  - Form: one parametrized test, `test_lyapunov_cached_matches_published_reference[case]`, one item per case, each under 5 s.
  - The developer records `--durations` once (§4.6) as evidence of the budget.
- The note addendum (Methods v2 comparison) is unchanged.

**A6. Affected checks and smoke** (replaces the .2 bullet above).
- (.2): single test file changed, so `tests/unit/test_data.py` only (unit tier), run once. No `lpcstudy/` change, so no integration and no smoke.
- (.3): unchanged.
- Smoke consequence: unchanged (`results.json` identical; `RESULTS.md` gains the subsection).
- (.3) text changes:
  - The Lorenz row says "within 1%".
  - The Rössler row lists both references, each "within 3%".
  - The Chua row says "not validated: no published reference at these parameters (known limitation, NVVUQ.13, DEC-0010)".
  - The memo sentence appears only if A3 is confirmed.
  - The test's expected strings follow these changes: fake lorenz63 0.9 gives -0.62%, "within 1%".
  - The bounds come from `LYAPUNOV_REFERENCES` per system, not from a single 3% constant.

**A7. Definition of done** (replaces the .2 part):
- The parametrized unit test is committed and run once in the radius.
- The values, max|x| per case, durations and summary line are in the Log.
- Each of Lorenz and Rössler passes, or has a DEF reporting the step size as the suspected cause (LPC.NV.1), with nothing tuned.
- Chua is recorded as not validated.
- The memo case is resolved per A3.

**A8. Owner questions.**
- Q-O2 (should the design text say Methods v2/v3's λ values are code output?) and Q-O3 (should an out-of-tolerance λ ever affect `gate_pass`?) remain open. The default is report-only, with no change to verdict code.
- Q-O1 waits on A3.

## Log

<dated entries: what was done, commands, results, commits>

### 2026-10-11 Mathematics review of the WU-0007.2 plan (applied-mathematician, claude-opus-5-5)

Scope: M1 to M4 before any code is written. No library or test file was touched, and nothing was committed. The scratch scripts are in the session scratchpad (`lyap_se.py`, `refine.py`, `more.py`, `ics.py`, `memo2.py`), not in the repository. They run a verbatim copy of the body of `estimate_lyapunov` that also returns the per-step log growth; on the registry Lorenz case it reproduces 0.905494 exactly. Runs: CPU, `taskset -c 0,1`, 2 threads, about 130 runs of 0.4 to 2 s each. No seed is involved: the estimator is deterministic, and the initial conditions (ICs) are the only variable. Labelled DEVELOPMENT: these are not study outputs.

**M1. Standard error at the code's settings** (10^5 Benettin steps at 20*max_dt, burn-in 5000, RK4). The SE was estimated in two ways: batch means on one run (20, 50 and 100 batches agree within 15%), and the spread across ICs.

| System | T (time units) | lambda (registry IC) | SE per run: batch means | SD across ICs (n) | SE adopted (relative) |
|---|---|---|---|---|---|
| lorenz63 | 2e4 | 0.905494 | 1.0-1.3e-3 | 7.0e-4 (4) | 0.0012 (0.13%) |
| rossler | 8e4 | 0.071940 | 5.0-6.2e-4 | 4.2e-4 (4), 4.5e-4 (8) | 0.00055 (0.75%) |
| chua (registry) | 1e4 | 0.431133 | 4.2-5.2e-3 | 4.8e-3 (13 in-basin) | 0.0048 (1.1%) |
| chua_memo (alpha 9, beta 100/7, m0 -8/7, m1 -5/7) | 1e4 | 0.323544 at (0.7,0,0) | 3.6-4.7e-3 | 4.5e-3 (13), 5.4e-3 (8) | 0.0050 (1.5%) |

- The roadmap's "SE near 1%" is 8 times too pessimistic for Lorenz, about right for Rössler and Chua, and refers to the wrong run length: the code uses 10^5 Benettin steps, not 2×10^5, as the plan already notes.
- The SE can be bounded in advance (table). The test does not need K = 4 extra runs: they would be cheap (about 2 s), but an SD from 3 degrees of freedom is uncertain by about ±40%, which is worse than the a-priori values above. The docstrings should cite these values as DEVELOPMENT measurements.

**Discretization (numerical row, LPC.NV.1).** The interval was held fixed and the RK4 substep varied, with the same ICs at every level.
- Lorenz, h = 0.01 / 0.02 / 0.04: 0.90619 / 0.90511 / 0.90549 (SE of each mean about 4e-4). No trend, even at 4h, so the bias at h = 0.01 is below 1e-4 relative.
- Rössler (8 ICs), h = 0.01 / 0.02 / 0.04 / 0.08: 0.071569 / 0.071566 / 0.071488 / 0.070664 (SE of each mean about 1.2-2.6e-4). The map's lambda is low at large h. The observed order from 0.08→0.04→0.02 is about 3.4 (noisy; formal order 4). The bias at the code's h = 0.04 is about -8e-5 (-0.1%), below 1/7 of the SE.
- Memo case, h = 0.0025 / 0.005 / 0.01 / 0.02: 0.32811 / 0.32744 / 0.3313 / 0.3267. There is no resolvable trend. Order 2 or lower is expected because of the diode kinks. The bias at h = 0.005 is below 1.5% (2σ bound).
- Registry Chua, h = 0.005 / 0.01 / 0.02: 0.4323 / 0.4355 / 0.4396 (SE of each mean about 0.4%). There may be an upward trend at coarse h. The bias at 0.005 is not resolved: below about 0.7%.

**M2. Lorenz and Rössler tolerances.**
- Lorenz: the code SE is 0.13% and the discretization bias is negligible.
  - The reference uncertainty of Sprott's 0.90563 is unknown. Hartl's stated ±0.003 (0.33%) is the largest stated uncertainty among the confirmed sources, and I use it as a stand-in.
  - 3·sqrt(0.13² + 0.33²) = 1.06%.
  - **Recommend tightening to |λ/0.90563 − 1| ≤ 1%** (≈2.8σ; about 7.5 code SEs). The derivation uses no observed gap.
  - The fixed 3% is about 23 code SEs and would not detect a 1-2% defect such as a wrong time unit or a wrong parameter at the third digit.
- Rössler: σ_code = 0.75%; B&B 0.07062 ± 0.00066 (0.93%).
  - σ_diff = 1.19%, so 3% is 2.5σ (two-sided false-alarm probability 1.2% if all assumptions hold). For Sprott's 0.0714, of unknown uncertainty, 3% is about 2.4-4σ.
  - **Keep 3% for both; it cannot be tightened on SE grounds.** The dual assertion is sound as two separate checks: the references differ by 1.1%, about 1.2 of B&B's σ, so they are mutually consistent. The family-wise false-alarm probability is at most about 2%.
- Reading of the visible values, after the tolerances were fixed above:
  - Lorenz 0.905494 is -0.015% from Sprott (0.1 SE).
  - Rössler 0.0719398 is +0.76% from 0.0714 (≈1.0 σ_code). It is +1.87% from 0.07062 (≈1.6 σ_diff).
  - Both gaps are within sampling error. The integrator does not explain them: the RK4 bias is -0.1%, in the opposite direction.
  - The 8-IC mean at h = 0.04 is 0.07149, so the registry-IC run sits +0.6% (≈0.8 SE) above it by chance.

**M3. Memo case.**
- *Conversion.* Assume the standard double-scroll circuit equations: C1 v1' = G(v2 − v1) − g(v1), C2 v2' = G(v1 − v2) + iL, L iL' = −v2. Put x = v1/Bp, y = v2/Bp, z = iL/(G Bp), τ = tG/C2. Then:
  - α = C2/C1 = 9, and the y and z equations take the code's form;
  - β = C2/(L G²) = 7/0.49 = 100/7;
  - the diode slopes divided by G give inner -0.8/0.7 = -8/7 (code m0) and outer -0.5/0.7 = -5/7 (code m1), with breakpoints at x = ±1 because Bp = 1;
  - λ_τ = λ_t · C2/G = 0.23/0.7 = 0.3286.

  Each step is correct, but the research note does **not** quote the memo's equations (1.1). Only (1.2) and (1.3) are quoted, so the form above is an assumption. Missing: a verbatim quote of (1.1), the definition of the memo's time variable, and confirmation that x0 is (v_C1, v_C2, i_L). If x0 is in those variables, it maps to z = 1.74606/0.7 = 2.494; this is irrelevant to the test, which uses (0.7,0,0) with burn-in.

  The code's `chua_field` has the same form and naming (systems.py:94-101).
- *Independent check of the field and time scaling: sum of exponents equals the mean divergence.* This identity is exact and needs no reference.
  - Full spectrum of the memo case per τ: (0.3235, 0.0008, -2.5259), sum -2.2016. The sampled mean divergence is -2.2023: inner fraction 0.355 × (+2/7) + outer fraction × (-25/7).
  - Per circuit time the spectrum is (0.2265, 0.0006, -1.768), sum -1.541.
  - **Discrepancy.** The memo as read gives μ3 ≈ -0.28, a sum of -0.05 (3.22) and d_L = 2.82. These cannot hold for these equations: the sum must equal the mean divergence, about -1.54 per circuit time. The computed Kaplan-Yorke dimension is 2.13.
  - So the memo's μ3 and sum are wrong in the memo, misread from the scan, or the equations differ from the assumed form. This weakens the memo as a "confirmed" reference.
  - Recommend that the researcher re-read memo pp. 22-25 and (1.1) before the memo case is relied on. This is a status question for Q-O1, not a blocker for coding.
- *Tolerance.*
  - σ_code = 1.5%.
  - Memo sampling SE at T = 3000 circuit time, which is 2100 τ: 1.5%·sqrt(10^4/2100) = 3.3%. The plan's "≈5%, scaled from Lorenz" overstates it.
  - Rounding of "0.23": ±2.2% bounded, SD 1.3%.
  - Start-up bias of the memo's vector alignment: O(1 nat)/(0.23·3000 ≈ 690 nats), below 0.5%.
  - Discretization: below 1.5%.
  - Combined σ ≈ 3.9%, so 10% ≈ 2.6σ (false-alarm probability about 1%). **Keep 10%; it cannot be tightened.**
  - "Biased low (still increasing)" is not supported as an estimator bias: the finite-T Benettin bias is O(1/T), about 0.3% here. A running average that is still drifting at T is consistent with a fluctuation of about ±3%.

**M4. Start-up bias.** Burn-in is 5000 steps: 1000, 4000 and 500 time units for Lorenz, Rössler and Chua.
- This is ample for the state. Every IC I tried that stays bounded reaches the attractor within O(10) time units; burn-in cannot rescue an IC outside the basin.
- The basis alignment decays as exp(-(λ1-λ2)t). The excess of the first 100 Benettin steps over the stationary rate is at most 3.4 nats in every run, which is at most 0.06% of λ (at most 1/10 SE in every case).
- **Negligible**, and the burn-in is adequate.

**Finding F1 (flag, PRIME.4): `estimate_lyapunov` returns a finite, positive, plausible value for a divergent orbit.**
- Of 12 ICs drawn as (0.7,0,0) + N(0, 0.5²), 3 leave the double-scroll basin for both Chua parameter sets, and the state overflows.
- The estimator then returns the real part of the outer linear region's unstable complex pair: 0.1854 for the memo case and 0.3055 for the registry Chua. The eigenvalues of the outer matrix agree to 4 digits.
- The plan's "finite, positive λ" assertion therefore does not detect divergence. The boundedness check must be on the actual orbit: `simulate_trajectory` from the same IC and map for 5000 + 10^5 steps, asserting all finite and max|x| ≤ 3 (the attractor has |x| ≤ 2.26), at about 0.2 s.
- The registry IC (0.7,0,0) is in the basin for both sets: x ∈ [-2.26, 2.26], with both scrolls visited.
- A guard inside `estimate_lyapunov` is a library change and is out of scope here. It is recommended to the main session as a DEF candidate.

**Runtime and tier.** Each case takes 0.4-0.6 s including JIT compilation, measured at 2 threads with the machine at load average about 4.5. The four cases plus the import take about 3-5 s. The plan's 3-10 s per case is about 10 times high, so "exceeds the 5 s unit budget" is not true per test. The tier is the planner's decision; if `slow` is kept, it needs another reason.

**Plan corrections.**
- (a) The SE is 0.13% / 0.75% / 1.1% / 1.5%, not "near 1%".
- (b) The memo's finite-T SE is 3.3%, not 5%, and it is not biased low.
- (c) The boundedness check needs a trajectory (F1).
- (d) The runtime estimate is 10 times high.
- (e) The memo's equations (1.1) are not quoted, and its μ3 and sum contradict the divergence identity.

Tightened: Lorenz 3% → 1%. Unchanged: Rössler 3% (both references) and memo 10%.

### 2026-10-11 WU-0007.2 and .3 implementation (developer, claude-sonnet-5-5)

**Base smoke (taken before any report change).** `tools/run_preset.sh smoke DEV-0 runs/dev/base-0007`, CPU, 48 s wall, exit 0. This is the comparison base for WU-0007.3.

**Interpretation of "max|x|" in the orbit guard (A4).** Measured once (scratch script, not a test; CPU, 4 threads, 5000 + 10^5 steps of the study's map from the registry start): max over the orbit of each coordinate (x, y, z).
- Lorenz: (19.27, 26.73, 47.45). Rössler: (11.43, 10.79, 22.85). Chua: (2.263, 0.389, 3.638).
- "max|x|" in A4 can only mean the FIRST coordinate (the observed variable, `spec.observed_index` = 0): the plan's Chua attractor figure 2.26 is the x coordinate (z reaches 3.64 > B = 3), and the Lorenz ball of radius 39.25 is centred at z = sigma + rho = 38, so z = 47.45 is inside it and |z| ≤ 40 would be wrong. The test therefore asserts max|x| over the first state coordinate, as the plan's numbers require. Observed x: Lorenz 19.27 ≤ 40, Rössler 11.43 ≤ 25 (and ≤ 16.7, so no referral), Chua 2.263 ≤ 3.

**§4.9 checklist before the WU-0007.2 invocation.**
1. Change set: `git status --porcelain` shows only ` M tests/unit/test_data.py`; the branch's committed diff against develop is the unit file only.
2. Radius: a test file changed and no `lpcstudy/` file: "test file: that file only" (`tools/test_impact.py --explain`, rule for `tests/unit/test_data.py`), so `tests/unit/test_data.py`, unit tier, smaller than the suite; no integration, no smoke (A6).
3. Already run? No; the file is new in this form.
4. Device: `tools/run_tests.sh` sets `JAX_PLATFORMS=cpu`, `XLA_PYTHON_CLIENT_PREALLOCATE=false`.
5. Threads: `LPC_THREADS` default 4 (budget 4); unit timeout 300 s.
6. Contention: CPU only, no lock; no preset of mine running.
7. Output: the wrapper's `-q --tb=short -rfE`; `--durations=10` added for the §4.6 evidence.
8. Command: `tools/run_tests.sh unit --durations=10 tests/unit/test_data.py`.

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>
