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

## Log

<dated entries: what was done, commands, results, commits>

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>
