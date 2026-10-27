# Phase J confirmatory round: preparation plan (draft for the owner)

Main session (claude-opus-5-5), 2026-10-27. This is a plan. Nothing in it is approved until the owner rules on section 2.

- **Basis:** ROADMAP §10, decision 3 ("the intention of promoting it after a pre-registered confirmatory round … needs its own pre-registration, freeze and sealed seeds"), and the LPC.PC.1 scoped exception of 2026-10-26.
- **Starting point:** the phase J report (`2026-10-26-phase-j-report.md`, WU-0052).
- **CONF-1:** not changed or re-run. No development number is placed beside it.

## 1. What a confirmatory round adds

The held-out replication (DEV-5 to DEV-9) tested about 3,300 rows under a rule fixed in advance. The rows were not chosen in advance, though, and the seeds are development seeds.

The confirmatory round has four parts:
1. **Claims.** It names a short list of claims before any sealed seed exists.
2. **Rule.** It fixes how sealed seeds combine into a verdict for each claim.
3. **Freeze.** It freezes the code and the analysis on `main`.
4. **Run.** The owner seals the seeds and runs.

Promotion stays with the owner.

## 2. Decisions for the owner

| # | Decision | Recommendation |
|---|---|---|
| DC-1 | **Claims to confirm** (section 3) | Tiers 1 and 2. Tier 3 only if the student wants the joint and mechanism claims in the entry |
| DC-2 | **Seeds and combination rule** | Five sealed seeds, CONF-5 to CONF-9. CONF-2 to CONF-4 stay with phase I. A claim is confirmed on a system if it holds on at least 4 of 5 seeds with no contradiction: the M-6 rule the held-out set used, applied only to the pre-registered rows. Otherwise it reads "not confirmed", or "contradicted". No pooling |
| DC-3 | **O6: may a sealed run write the state dump?** The CLI refuses `--states-dump` with the confirmatory flag "until the owner decides" (`lpcstudy/__main__.py`, `choose_states_dump`). Every phase J analysis reads the dump | Allow it. The dump is flag-gated and bitwise neutral for `results.json`, apart from one provenance leaf (WU-0003.7b, WU-0046) |
| DC-4 | **Official device and regeneration** | GPU (RTX 4090), as in phase I decision 4, **with a pinned Lyapunov cache.** Each sealed run's cache starts from one `lyapunov.json` (Chua λ_max 0.4408520035546002, the value of 8 of 9 phase J runs), and its hash goes in the pre-registration. Regeneration is a second GPU run, expected bitwise. Without the pin, a GPU rerun changed Chua's whole orbit in 1 of 9 runs (DEF-0032). The rehearsal (WU-0055) tests the pin. A CPU run informs only. The alternative is a CPU official device, as for CONF-1, whose CPU regeneration was bitwise. It is several times slower at n_test 4000 |
| DC-5 | **Validation-gate failure on a sealed seed** | That system's rows for that seed count as "absent". A claim then needs 4 agreeing seeds among those present, so one gate failure is tolerated and two make the claim "not confirmable" on that system. No redraw and no retuning. This differs from CONF-1 (a hard stop, DEC-0027). For Chua, the per-seed gate-failure risk is roughly 10 to 15% (V1 about 5%, DEF-0031; V6 about 4.6%, DEF-0026; plus V4), so two or more failures in five seeds, which make Chua "not confirmable", has a probability of roughly 8 to 17%. Under a hard stop, the chance of the round stopping is roughly 40 to 55% |
| DC-6 | **Merge and freeze** | Phase J code (dump /3, `phasej` preset, analysis tools, the evaluator) merges to `main` after a green freeze gate, with tag `freeze-j`. The hook fix (seq 50) goes in the same merge |
| DC-7 | **DEF-0030** (`pooled_floor_count` docstring) | Fix the docstring in the same code change. `lpcstudy/` already differs from `freeze-1` (correction line in DEF-0030) |
| DC-8 | **Phase I** | Stays paused. The phase J round uses the GPU first |

## 3. Proposed claims

Each claim is a set of rows of the frozen analysis, with the reading it needs. "Rows" means three systems × two profiles unless stated. In the held-out set, every Tier 1 and Tier 2 row replicated, and the column says on how many seeds.

### Tier 1: horizon (the strongest result)

| Id | Claim | Rows (family, item) | Needed reading | Held-out seeds |
|---|---|---|---|---|
| J-H1 | Instability matters most: dropping I raises the horizon loss by more than 5% | A drop-one, `drop I: pinball ratio` | substantial (ratio > 1.05) | 5 of 5 on all 6 |
| J-H2 | Separation matters: dropping O raises the loss | A drop-one, `drop O: pinball ratio` | ratio > 1 | at least 4 of 5 on all 6 |
| J-H3 | Noise level does not matter for the horizon | A drop-one, `drop N: pinball ratio` | negligible (ratio ≤ 1.05) | at least 4 of 5 on all 6 |
| J-H4 | O and I interact in the horizon | B pair, `log T OI: Delta` | interaction gain detected | at least 4 of 5 on all 6 |
| J-H5 | The profile beats the zero-parameter Lyapunov rank | D vs full, `lyapunov: pinball ratio vs F` | substantial | 5 of 5 on all 6 |
| J-H6 | The raw delay vector adds information beyond the profile | D vs full, `X+F: pinball ratio vs F` | lowers (ratio < 1) | 5 of 5 on all 6 |

### Tier 2: allocation

| Id | Claim | Rows | Needed reading | Held-out seeds |
|---|---|---|---|---|
| J-A1 | On Rössler, the oracle R decides the weight at 1 LT | A drop-one, Rössler, oracle, H=30, `drop R: MSE ratio` | substantial | 5 of 5 |
| J-A2 | On Rössler, the estimated profile gives no gain over a constant at 1 LT | D vs full, Rössler, deployable, H=30, `none: mse ratio vs F` | negligible | 5 of 5 |
| J-A3 | At 4 LT, a fitted constant beats the separation formula | A vs separation, H=120, `none: MSE(F)/MSE(sep)` (6 rows) | lowers | at least 4 of 5 on all 6 |
| J-A4 | On Lorenz-63 at 1 LT, the raw delay vector beats the estimated profile | D vs full, Lorenz-63, deployable, H=30, `X: mse ratio vs F` | lowers | 5 of 5 |

### Tier 3: joint system and mechanism (optional)

| Id | Claim | Rows | Needed reading | Held-out seeds |
|---|---|---|---|---|
| J-C1 | One weight cannot carry the horizon: forward one-weight C2 loses most | C2 retained, `forward one weight retained`, H = 0.27 to 2 LT | loses most | at least 4 of 5 on all 24 |
| J-C2 | The full deployable system over-trusts on Rössler | C3, Rössler, `g(F-hat) + h(F-hat)`, realized false trust | interval above 0.10 | 5 of 5 (13.2 to 14.0%). **Not a row of the replication tool; it needs a new evaluator row** |
| J-E1 | Lorenz-63's heavy tail does not sit in high-I states | E-H3c `lorenz63_part` | not consistent (point reading) | 5 of 5 |
| J-I1 | Instability adds information about the logit weight given R, O and N (Lorenz-63 and Chua, deployable) | the pipeline's own ablation, `profile_conditions/deployable/logit_w_interior/leave_one_out/I` | substantial | 5 of 5. **Not a row of the replication tool; it needs a new evaluator row.** This is the student's H2a question |

**Expected false confirmations.** The Tier 1 and Tier 2 rows number 45. At r ≈ 1.0 to 1.5 (r-measurement note), the per-row false-replication rate is at most 1.5·10⁻³, so at most about 0.07 rows are expected to be confirmed falsely. Tier 3 adds 28 rows, with r up to about 2 for C2.

## 4. Work units

| Unit | Content | Acceptance criteria (fixed before work starts) |
|---|---|---|
| WU-0053 | **Pre-registration** `docs/study/preregistration_phase_j.md`: claims, rows, readings, combination rule, gate handling (DC-5), device, seed ids, analysis commit, limitations (n_eff, Chua V1, deployable-only claims, the logit row's R² scale), predictions | Every claim maps to a row identifier that exists in the frozen tools' output on DEV-5 to DEV-9. Owner approves before any seal |
| WU-0054 | **Code.** (a) Per DC-3: `--states-dump` accepted with the confirmatory flag. (b) The analysis tools accept a sealed run (seed kind confirmatory, `CONF-n`) and label it accordingly; development runs unchanged. (c) `tools/lpc_confirm.py`: reads the pre-registration's claim table (machine-readable block) and N seeds' records, applies the rule, writes one verdict per claim and system, and nothing for other rows. (d) DC-7 docstring | (a) The DEV-0 smoke differs from the pre-change smoke only by added leaves (0 changed, 0 removed). The confirmatory refusal tests pass unedited, except the one test that asserts the old refusal, which changes per the ruling. (b) Development outputs bitwise unchanged on DEV-1. (c) On DEV-5 to DEV-9 in rehearsal mode, every Tier 1 and 2 verdict equals the replication tool's class for that row. Synthetic seed sets cover confirmed, contradicted, absent seed and 3 of 5. (d) Docstring only |
| WU-0055 | **Dress rehearsal** of the whole chain on two development seeds through the confirmatory code path, with the analysis tools and `lpc_confirm.py` in rehearsal mode | Exit 0 everywhere; labels say DEVELOPMENT; one manifest line per run |
| WU-0056 | **Freeze**: gate on every tier (`LPC_GATE=freeze-j`), merge to `main` (owner), tag `freeze-j` | Gate green; tag on `main`; the analysis and evaluator hashes recorded |
| WU-0057 | **Owner acts**: seal CONF-5 to CONF-9 (ledger commitments), then one command per seed for the official GPU run and the regeneration | Commitments in the ledger; seed values in no output |
| WU-0058 | **Analysis and verdicts**: tools once per seed, `lpc_confirm.py` once; comparison of the regeneration; report; auditor pass; owner promotion | Regeneration compared at T0, every differing leaf reported, and every claim row whose per-seed reading or verdict differs between official and regeneration runs reported (seq 54; was "Regeneration bitwise (T0)"); every reported number traced to a record; auditor finds zero blockers |

Compute: about 33 min of GPU time per run. Five official runs plus five regeneration runs make about 5.5 h. The analysis takes about 29 min of CPU per seed.

## 5. Chua V1 and the gate rule

The diagnosis (`2026-10-27-chua-v1-diagnosis.md`) finds:
- **The failures are artifacts of the check.** The Chua V1 failures on DEV-7 and DEV-8 are finite-difference artifacts at the diode breakpoint, and the Jacobian is correct.
- **They recur.** They occur on about 5% of seeds (DEF-0031).
- **GPU reruns can drift on Chua.** Separately, a GPU rerun can change Chua's orbit through a one-ulp difference in λ_max (DEF-0032).

The plan therefore proposes:
- **DC-5:** a gate failure removes that system's rows for that seed. It does not stop the round.
- **DC-4:** the pinned Lyapunov cache.

V1's bar and recipe are not changed. That is the owner's alone (PRIME.2). If the owner wants V1 to stop failing on correct Jacobians, it would be a separate ruling, made before the seal: for example, accept a state when either one-sided difference agrees. It is not proposed here.

WU-0055 adds one acceptance criterion: with the pinned cache, a second GPU run of each rehearsal seed is bitwise equal to the first (tier T0).

**Ruling on DC-4 after the rehearsal** (owner, 2026-10-27, ledger seq 54, "choose recommendation A"):
- **The criterion was not met.** DEV-6 regenerated bitwise; DEV-5 did not (DEF-0033, `docs/agent/notes/2026-10-27-phase-j-rehearsal.md`).
- **The ruling.** The official device stays the GPU with the pinned cache, and the bitwise expectation is dropped.
- **What replaces it.** The regeneration is compared at T0 and every differing leaf is reported. It is also analyzed, and every claim row whose per-seed reading or verdict differs from the official runs is reported by name.
- **Verdicts.** Verdicts come from the official runs only. There is no CPU fallback run.
- **The pre-registration.** §5 and §8 item 7 carry the ruling.
