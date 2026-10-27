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
| P-1 Analysis and evaluator code (`tools/lpc_contrib.py`, `tools/lpc_contrib_ce.py`, `tools/lpc_confirm.py`) and the sealed-dump change | WU-0054 merged; acceptance criteria met |
| P-2 Rehearsal on development seeds through the whole chain, including a bitwise GPU regeneration with the pinned cache | WU-0055 |
| P-3 Freeze commit and tag `freeze-j` on `main`, with the sha256 of this file and its two companions | WU-0056; owner |
| P-4 O-J1: who runs the regeneration (§5) | **closed:** the owner waived the other-actor requirement (ledger seq 52) |
| P-5 Tier 3: included only if the student asks before approval (§3) | owner and student |

## 1. Question and scope

**Question.** Do the readings about the four local predictability conditions found on development seeds hold on fresh, sealed seeds? The conditions are R (recurrence), O (separation), I (instability) and N (noise). The readings come from phase J (report `docs/agent/notes/2026-10-26-phase-j-report.md`).

**Scope.**
- **Systems.** Lorenz-63, Rössler and Chua, at the v3 parameters.
- **Analysis.** The phase J analysis as frozen at `phasej-freeze` (0929a9a). Only the changes of WU-0054 are added: sealed-run mode, the evaluator and a docstring.
- **Out of scope:**
  - the extension systems;
  - any v3 hypothesis;
  - pooling across seeds;
  - any comparison with CONF-1.

**The v3 verdicts these runs compute are not part of this study.** The pipeline computes v3's hypothesis words for every run. For CONF-5 to CONF-9 they are neither reported nor used. CONF-1 stays the v3 result, and nothing here changes it.

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

That is 45 rows in 10 claims.

**Tier 3 is not included** unless the student asks before approval (P-5). It would cover:
- C2 forward one weight;
- C3 Rössler false trust;
- E-H3c;
- drop-I on the logit weight.

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
- for 45 rows, that is about 0.07 expected false confirmations.

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
  - It is compared at tier T0, bitwise on every compared leaf (`tools/compare_runs.py`), and the dump arrays are compared bitwise too.
  - A difference is reported. No verdict depends on the regeneration.
  - **Actor.** v3 §9 item 4 asks for another actor. The owner waived that requirement for this round (ledger seq 52, "Not feasible; waive as with CONF-1"), as seq 31 did for CONF-1, so the owner may run both the official and the regeneration runs.
- **CPU.** A CPU run happens only if a regeneration is not bitwise. It informs only: GPU and CPU build different orbits (diagnosis note, finding 4).
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

All of the analysis takes place after the owner releases the sealed outputs to agents with a ledger entry.
1. For each seed, at `freeze-j`, on the CPU:
   - `tools/lpc_contrib.py <run>/phasej --sealed --jobs 4 --out <run>/contrib-j`
   - then `tools/lpc_contrib_ce.py <run>/phasej --sealed --jobs 4 --abd <run>/contrib-j/contrib.json --out <run>/contrib-j`
2. Once: `tools/lpc_confirm.py --claims docs/study/preregistration_phase_j/claims.json --pinned docs/study/preregistration_phase_j/lyapunov.json <run CONF-5..9>/contrib-j --out runs/confirmatory/phasej-confirm`.
3. Report.

A tool that refuses or fails is reported as it stands. Any fix is a new commit and is labeled post-freeze.

## 8. Known limitations, stated before the run

1. **The claims were chosen on development seeds** whose results were seen (§2). The sealed seeds are fresh.
2. **Five realizations.** Each seed is one realization per system. Seeds are not pooled, and no between-seed variance is estimated.
3. **Allocation below 2 LT on Lorenz-63 and Chua is mostly unreadable** (the n_eff guard). No claim is made there.
4. **Chua gate risk** (§6). Two of the nine development GPU runs failed V1 on Chua, and both are diagnosed as artifacts of the check.
5. **Determinism, not independent reproduction.** The regeneration uses the same host and device, and the same actor (waiver, seq 52).
6. **The pinned time unit** is the value of 8 of 9 development GPU runs. The ninth differed by one ulp in Chua's λ_max.
7. **The analysis instruments** (HGB allocation fits, quantile boosting, the reading table) are analysis instruments, not rules of the v3 design (LPC.PC.1 exception).
8. **The phase J code was not reviewed by the owner.** Agents built and tested it.

## 9. What the result may and may not be called

**May be said**, with §8 attached: for each claim and system, the pre-registered analysis of sealed seeds CONF-5 to CONF-9 returned confirmed, not confirmed, contradicted or not confirmable.

**May not be said:**
- an overall verdict, or a count of claims presented as a finding;
- any pooling across seeds;
- that a condition causes predictability;
- that "not confirmed" means no effect;
- anything about the v3 hypotheses from these runs;
- any comparison with CONF-1's numbers, or any change to the CONF-1 result.

Development numbers (DEV seeds) stay labeled development.
