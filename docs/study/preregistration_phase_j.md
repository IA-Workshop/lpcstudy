# Phase J confirmatory round: pre-registration (DRAFT for owner approval)

**Status:** draft, 2026-10-27, main session (claude-opus-5-5). Binding only after the owner approves it in the ledger, before any of CONF-5 to CONF-9 is sealed. PENDING items are listed in §0 and must close before the seal.

**Authority:**
- ROADMAP §10.1;
- ledger seq 51 (owner: "Proceed with all as recommended");
- LPC.PC.1 scoped exception (seq 48);
- plan `docs/agent/notes/2026-10-27-phase-j-confirmatory-plan.md`.

**Machine-readable parts** (their sha256 are recorded at approval):
- `docs/study/preregistration_phase_j/claims.json`: the claims, rows and rule;
- `docs/study/preregistration_phase_j/lyapunov.json`: the pinned time unit, sha256 `852ce1f67cdcc55275f388c72817348b1b83e2146b4751c8c8aedc7a85453417`.

## 0. PENDING (all closed before any seal)

| Item | Closes with |
|---|---|
| P-1 Analysis and evaluator code (`tools/lpc_contrib.py`, `tools/lpc_contrib_ce.py`, `tools/lpc_confirm.py`) and the sealed-dump change | **closed:** WU-0054 merged into develop (54975c7); its acceptance criteria met (rehearsal on DEV-5 to DEV-9: 45 of 45 Tier 1 and 2 verdicts equal the replication class; v3 description 42 rows, 0 missing) |
| P-2 Rehearsal on development seeds through the whole chain, including a GPU regeneration with the pinned cache | **closed:** WU-0055 (`docs/agent/notes/2026-10-27-phase-j-rehearsal.md`). The chain ran end to end. DEV-6 regenerated bitwise; DEV-5 did not (DEF-0033: 420 leaves, 16 non-claimed Chua readings, 0 of the 48 claim rows). The owner dropped the bitwise expectation (ledger seq 54, §5) |
| P-3 Freeze commit and tag `freeze-j` on `main`, with the sha256 of this file and its two companions | WU-0056; owner |
| P-4 O-J1: who runs the regeneration (§5) | **closed:** the owner waived the other-actor requirement (ledger seq 52) |
| P-5 Tier 3 | **closed:** J-I1 and J-C2 included; J-C1 and J-E1 out (ledger seq 53) |
| P-6 O-J2: who runs the sealed analysis (§7). The analysis tools draw their bootstrap and learner randomness from the run's master seed, which a sealed `results.json` does not store. As built (WU-0054), `--sealed` reads `LPC_CONF_SEED` and `LPC_CONF_SALT`, checks them against the ledger commitment as the CLI does, and never writes the value. The sealed analysis is then an owner act. The alternative, a fixed analysis seed in this pre-registration, would break the tools' check that they reproduce the run's own rows | owner |
| P-7 Owner review of the seed-handling code in `--sealed` (LPC.PC.11), or a waiver as for CONF-1 (seq 33) | owner |

## 1. Question and scope

**Question.** Do the readings about the four local predictability conditions found on development seeds hold on fresh, sealed seeds? The conditions are R (recurrence), O (separation), I (instability) and N (noise). The readings come from phase J (report `docs/agent/notes/2026-10-26-phase-j-report.md`).

**Scope.**
- **Systems.** Lorenz-63, Rössler and Chua, at the v3 parameters.
- **Analysis.** The phase J analysis as frozen at `phasej-freeze` (0929a9a). Only the changes of WU-0054 are added: sealed-run mode, the evaluator and a docstring.
- **Out of scope:**
  - the extension systems;
  - any v3 hypothesis test (the v3 words are described only, §7a);
  - pooling across seeds;
  - any comparison with CONF-1.

**The v3 words these runs compute are a secondary description, not a test** (§7a; ledger seq 53, LPC.PC.1 as amended). CONF-1 stays the v3 result, and nothing here changes, confirms or replaces it.

## 2. What was seen before this was written

The claims were chosen after seeing two sets of development seeds:
- **Exploration seeds:** DEV-1, DEV-3 and DEV-4.
- **Held-out replication seeds:** DEV-5 to DEV-9. Every pre-registered row replicated there under the M-6 rule.

The sealed seeds have not been drawn, so they are fresh. This round is therefore a test of the replicated readings, and they are expected to confirm. A reading that does not confirm is reported as such.

## 3. Claims

The full definition, including the exact row identifiers, is `claims.json`. Each row is one (system, profile) or one (system, profile, horizon) case of the frozen analysis. A row's reading comes from the tool's 1.05 reading table, or for B from the Holm-adjusted interaction test, as frozen.

| Id | Tier | Claim | Rows | Needed |
|---|---|---|---|---|
| J-H1 | 1 | Dropping instability (I) raises the horizon loss by more than 5% | 3 systems × 2 profiles | pinball ratio > 1.05 |
| J-H2 | 1 | Dropping separation (O) raises the horizon loss | 6 | ratio > 1 |
| J-H3 | 1 | Dropping noise (N) changes the horizon loss by at most 5% | 6 | ratio ≤ 1.05 |
| J-H4 | 1 | O and I interact in the horizon | 6 | interaction gain Δ > 0 |
| J-H5 | 1 | The profile predicts the horizon better than the Lyapunov rank by more than 5% | 6 | ratio > 1.05 |
| J-H6 | 1 | Adding the raw delay vector to the profile lowers the horizon loss | 6 | ratio < 1 |
| J-A1 | 2 | Rössler, oracle profile, 1 LT: dropping R raises the allocation MSE by more than 5% | 1 | ratio > 1.05 |
| J-A2 | 2 | Rössler, deployable profile, 1 LT: the profile improves the allocation MSE over a fitted constant by at most 5% | 1 | ratio ≤ 1.05 |
| J-A3 | 2 | 4 LT: a fitted constant weight has a lower MSE than the separation formula | 3 systems × 2 profiles | ratio < 1 |
| J-A4 | 2 | Lorenz-63, deployable profile, 1 LT: the raw delay vector alone has a lower allocation MSE than the profile | 1 | ratio < 1 |

| J-I1 | 3 | Instability adds information about the logit weight given R, O and N (the student's H2a question) | Lorenz-63 and Chua, deployable profile: 2 rows | ΔR² > 0 |
| J-C2 | 3 | Rössler: the full deployable system's realized false-trust rate is above the 10% target | 1 | false trust > 0.10 |

That is 48 rows in 12 claims. Tier 3 entered by ledger seq 53. J-C1 (C2 forward one weight) and J-E1 (E-H3c) are not included.

**How the two Tier 3 rows are read.** `claims.json` → `reading_tables` gives the rules.
- **J-I1.**
  - Its rows come from each run's own Q-N ablation (`results.json`), with their stored 95% interval and the frozen Q-N reading.
  - Q-N's "substantial" means the interval lies above 0 and reaches 0.05. It does not bound the size from below, so the claim is stated as ΔR² > 0. That is a refinement of the plan's wording ("substantial"), made before any sealed seed exists.
  - A seed reading "reduces" claims only ΔR² < 0.05, which is compatible with the claim. So J-I1 can be not confirmed but never contradicted.
- **J-C2.**
  - Its row comes from `ce.json`, using the realized false-trust rate's 95% interval.
  - "Above target" if the lower bound exceeds 0.10, "below target" if the upper bound is under 0.10, otherwise not determined.
- **Held-out seeds.** J-I1's lower bounds were 0.010 to 0.055 on all five seeds and both systems. J-C2's lower bounds were 12.6% to 13.4% on all five.

## 4. Seeds and the rule

- **Seeds.** Five sealed seeds, CONF-5 to CONF-9. Each is drawn by the owner with `tools/seal_confirmatory_seed.py`, and each commitment goes into the ledger before any run. CONF-2 to CONF-4 stay reserved for phase I.
- **Per row:**
  - **Confirmed:** the needed claim is implied by the reading on at least 4 of the seeds present, and no two present seeds have jointly unsatisfiable interval claims. Point claims never contradict.
  - **Contradicted:** such a pair exists.
  - **Not confirmable:** fewer than 4 seeds are present.
  - **Not confirmed:** otherwise.
- **Per claim and system:**
  - **Confirmed:** every row on that system is confirmed.
  - **Contradicted:** any row is contradicted.
  - **Not confirmable:** any row is not confirmable and none is contradicted.
  - **Not confirmed:** otherwise.
- **The rule is applied mechanically** by `tools/lpc_confirm.py` at `freeze-j`. No row outside `claims.json` gets a verdict.
- **No pooling.** No statistic is computed across seeds.

**Error rates.** These use the r measurement of the development seeds (`docs/agent/notes/2026-10-26-phase-j-r-measurement.md`):
- if a row's claim were false at its boundary, the chance that it still reads confirmed is at most about 1.5·10⁻³ per row;
- for the 45 Tier 1 and 2 rows, that is about 0.07 expected false confirmations. r was not measured for the three Tier 3 rows, so they add an unquantified, small risk.

The rule's power for an effect near its reading boundary is limited. M-6 put it at 0.74 for a borderline effect. Most rows sit far from their boundary on the development seeds; for example, drop-I ratios are 1.20 to 1.29 against 1.05.

## 5. Runs: device, time unit, regeneration

- **Code.** Tag `freeze-j` on `main` (P-3), in a clean detached worktree.
- **Device.** The RTX 4090 (`jax[cuda12]==0.11.2`), one job at a time, under the GPU lock.
- **Time unit.** Before each run, the pinned `lyapunov.json` is copied to `<out>/phasej/cache/lyapunov.json`. This fixes λ_max and the step interval for every system: DEF-0032 showed a one-ulp GPU difference in Chua's λ_max that changed a whole orbit. The analysis tools refuse a sealed run whose cache file differs from the pinned file.
- **Command.** One per seed, run by the owner. It runs all three systems:

  ```bash
  OUT=runs/confirmatory/phasej-CONF-n
  mkdir -p $OUT/phasej/cache && cp docs/study/preregistration_phase_j/lyapunov.json $OUT/phasej/cache/
  flock -n /tmp/lpcstudy-gpu.lock env JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_PREALLOCATE=false \
    python -m lpcstudy --preset phasej --confirmatory --seed-id CONF-n \
    --skip-robustness --states-dump --out $OUT
  ```

- **Regeneration.**
  - Each seed is run a second time on the same host and device from the same commit and inputs, into `runs/confirmatory/phasej-CONF-n-regen`.
  - **It is not expected to be bitwise** (ledger seq 54). On the GPU, the state estimator's ν̂ can differ between runs on a few entries even with the pinned time unit. That moves both seed-proxy fits by about 1e-9 and can flip a reading that sits at its threshold (DEF-0033; on the DEV-5 rehearsal, 420 leaves and 16 non-claimed Chua readings, none of the 48 claim rows).
  - **Leaves.** It is compared with the official run at tier T0 (`tools/compare_runs.py`), and the dump arrays bitwise. Every differing leaf and array is reported, with its size.
  - **Claim rows.** The regeneration is analyzed as in §7 step 1, into `<regen run>/contrib-j`, and `tools/lpc_confirm.py` is run once on the five regeneration analyses, into `runs/confirmatory/phasej-confirm-regen`. For each of the 48 rows, the per-seed `readings` and `absent` lists and the `verdict` are compared with the official `confirm.json`. Every row where any of them differs is reported by name.
  - **No verdict depends on the regeneration.** The verdicts are those of the official runs. A row whose reading differs between the two runs is reported as unstable at its threshold beside its verdict, which is not changed.
  - **Actor.** v3 §9 item 4 asks for another actor. The owner waived that requirement for this round (ledger seq 52, "Not feasible; waive as with CONF-1"), as seq 31 did for CONF-1, so the owner may run both the official and the regeneration runs.
- **CPU.** No CPU run. GPU and CPU build different orbits (diagnosis note, finding 4), so a CPU run could not explain a difference between two GPU runs.
- **Refusals.** A refused or crashed run is reported and not redrawn. If a run stops after some systems, the systems it did not reach are absent for that seed.

## 6. Validation gate

- **The gate.** V1 to V7 at their v3 criteria, per system and seed.
- **A failure makes that system's rows absent for that seed** (DC-5, seq 51). It does not stop the round, and nothing is retuned or redrawn.
- **Expected risk on Chua.** About 10 to 15% per seed:
  - V1 about 5% (DEF-0031, a finite-difference artifact at the diode breakpoint);
  - V6 about 4.6% (DEF-0026);
  - plus V4.

  So two or more failures in five seeds, which make every Chua claim "not confirmable", has a probability of roughly 8 to 17%. Lorenz-63 and Rössler have much lower rates.

## 7. Analysis, once

All of the analysis takes place after the owner releases the sealed outputs to agents with a ledger entry. If P-6 stands as built, the owner runs steps 1 and 2 in the sealed environment, because the tools need the sealed seed. Agents then read only the records and write the report.
1. For each seed, at `freeze-j`, on the CPU:
   - `tools/lpc_contrib.py <run>/phasej --sealed --jobs 4 --out <run>/contrib-j`
   - then `tools/lpc_contrib_ce.py <run>/phasej --sealed --jobs 4 --abd <run>/contrib-j/contrib.json --out <run>/contrib-j`
2. Once: `tools/lpc_confirm.py --claims docs/study/preregistration_phase_j/claims.json --pinned docs/study/preregistration_phase_j/lyapunov.json <run CONF-5..9>/contrib-j --out runs/confirmatory/phasej-confirm`.
3. Report.

A tool that refuses or fails is reported as it stands. Any fix is a new commit and is labeled post-freeze.

## 7a. Secondary description: the v3 words of the sealed runs

Every sealed run computes v3's hypothesis words for Lorenz-63, Rössler and Chua. They are reported as a description (LPC.PC.1 as amended, ledger seq 53):
- **What is listed.** For each v3 row and system, the word on each of CONF-5 to CONF-9 is listed, read from `results.json` → `verdicts`. Beside it goes the count of seeds that give each word, and CONF-1's promoted word, shown for reference only.
- **What is not computed.** No combined word, no "confirmed" and no pooled statistic.
- **Departures from v3, stated with the table:**
  1. n_test is 4000, not v3's 1000, so the intervals are narrower than v3 sized them;
  2. the device is the GPU, where v3 §9 makes the CPU official;
  3. the robustness sweep is skipped (it is reported-only in v3);
  4. the time unit is pinned (§5).
- **What it may not be used for.** It is not the v3 test. It cannot change, confirm or replace CONF-1. A disagreement with CONF-1 is reported as information about how v3's words vary across seeds and configurations, not as a revision.
- **Gate.** A system that fails the gate on a seed is listed as "gate failed" for that seed.

## 8. Known limitations, stated before the run

1. **The claims were chosen on development seeds** whose results were seen (§2). The sealed seeds are fresh.
2. **Five realizations.** Each seed is one realization per system. Seeds are not pooled, and no between-seed variance is estimated.
3. **Allocation below 2 LT on Lorenz-63 and Chua is mostly unreadable** (the n_eff guard). No claim is made there.
4. **Chua gate risk** (§6). Two of the nine development GPU runs failed V1 on Chua, and both are diagnosed as artifacts of the check.
5. **Repetition, not independent reproduction.** The regeneration uses the same host and device, and the same actor (waiver, seq 52). It is not expected to be bitwise (item 7).
6. **The pinned time unit** is the value of 8 of 9 development GPU runs. The ninth differed by one ulp in Chua's λ_max.
7. **GPU runs are not bitwise reproducible** (DEF-0033). A rerun of the same seed can move the deployable profile by about 1e-9. On the DEV-5 rehearsal that flipped 16 non-claimed Chua deployable readings. A claim row whose reading sits at its threshold on a sealed seed could read differently on a rerun; the regeneration comparison (§5) reports any such row.
7. **The analysis instruments** (HGB allocation fits, quantile boosting, the reading table) are analysis instruments, not rules of the v3 design (LPC.PC.1 exception).
8. **The phase J code was not reviewed by the owner.** Agents built and tested it.

## 9. What the result may and may not be called

**May be said**, with §8 attached: for each claim and system, the pre-registered analysis of sealed seeds CONF-5 to CONF-9 returned confirmed, not confirmed, contradicted or not confirmable.

**May not be said:**
- an overall verdict, or a count of claims presented as a finding;
- any pooling across seeds;
- that a condition causes predictability;
- that "not confirmed" means no effect;
- that the v3 words of these runs test, confirm or revise any v3 hypothesis or the CONF-1 result (§7a);
- any comparison with CONF-1's numbers, or any change to the CONF-1 result.

Development numbers (DEV seeds) stay labeled development.
