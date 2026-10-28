# Phase J confirmatory round: report (WU-0058)

**PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.** Main session (claude-opus-5-5), 2026-10-28. Pre-registration `docs/study/preregistration_phase_j.md` (approved, ledger seq 58); code at tag `freeze-j` (c19ad486b93a2ee96d64ce069ec42fd440428211). The owner released the sealed outputs to agents in ledger seq 65. The limitations of pre-registration §8 apply to everything below (§6 here).

## 1. What was run

- **Runs (pre-registration §5).** The owner ran `run_sealed.sh` (ledger seq 59) in the worktree `lpcstudy-wt/run/conf-j`, detached at `freeze-j` and clean. Ten GPU runs, one at a time under the GPU lock: the five official runs `runs/confirmatory/phasej-CONF-n`, then the five regenerations `phasej-CONF-n-regen`. All ten exited 0. Each run's `lyapunov.json` cache still had the pinned hash (852ce1f6…7453417) at the end. Log: `runs/confirmatory/phasej-runs.log`.
- **Gate (§6).** V1 to V7 passed for all three systems on all five seeds, so no rows are absent.
- **Analysis (§7).** The owner ran `run_sealed_analysis.sh` (develop 48dd3e6, ledger seq 66) on the CPU at `freeze-j`. For each of the ten runs it ran `tools/lpc_contrib.py --sealed`, then `tools/lpc_contrib_ce.py --sealed --abd`. Then it ran `tools/lpc_confirm.py` once on the five official analyses (`runs/confirmatory/phasej-confirm`) and once on the five regeneration analyses (`phasej-confirm-regen`). All 20 analysis steps and both `lpc_confirm` runs exited 0 (`runs/confirmatory/phasej-analysis.log`). `confirm.json` records analysis commit c19ad486…, dirty False.
- **Departure, in the form of the command only (DEF-0034, ledger seq 66).** The two analysis tools refuse any argument containing the word "confirmatory". So they ran with `runs/confirmatory` as the working directory and paths relative to it, rather than with the literal paths of §7. The code, inputs and order are those of §7. On development run DEV-6 (Rössler), the working directory did not change the result.

## 2. Verdicts

Rule (§4, unchanged): a row is confirmed if its claim is implied by the reading on at least 4 of the seeds present, with no contradicting pair; a claim × system is confirmed if every one of its rows is. Five seeds were present on every row.

Rows: **confirmed 47, contradicted 0, not confirmable 0, not confirmed 1** (of 48).

| claim | statement (claims.json) | system | verdict |
|---|---|---|---|
| J-H1 | Dropping instability (I) raises the horizon loss by more than 5% | lorenz63, rossler, chua | **confirmed** on each |
| J-H2 | Dropping separation (O) raises the horizon loss | lorenz63, rossler, chua | **confirmed** on each |
| J-H3 | Dropping noise (N) changes the horizon loss by at most 5% | lorenz63, rossler, chua | **confirmed** on each |
| J-H4 | O and I interact in the horizon | lorenz63, rossler, chua | **confirmed** on each |
| J-H5 | The four-condition profile predicts the horizon better than the Lyapunov rank by more than 5% | lorenz63, rossler, chua | **confirmed** on each |
| J-H6 | Adding the raw delay vector to the profile lowers the horizon loss | lorenz63, rossler, chua | **confirmed** on each |
| J-A1 | Rossler, oracle, 1 LT: dropping R raises the allocation MSE by more than 5% | rossler | **confirmed** |
| J-A2 | Rossler, deployable, 1 LT: the profile improves the allocation MSE over a fitted constant by at most 5% | rossler | **confirmed** |
| J-A3 | 4 LT: a fitted constant weight has a lower MSE than the separation formula | lorenz63, rossler, chua | **confirmed** on each |
| J-A4 | Lorenz-63, deployable, 1 LT: the raw delay vector alone has a lower allocation MSE than the profile | lorenz63 | **not confirmed** |
| J-I1 | Instability adds information about the logit weight given R, O and N (deployable profile) | lorenz63, chua | **confirmed** on each |
| J-C2 | Rossler: the full deployable system's realized false-trust rate is above the 10% target | rossler | **confirmed** |

The per-seed reading of every row is in `runs/confirmatory/phasej-confirm/confirm.md`. Rows confirmed on 4 of 5 seeds rather than 5:
- J-A3 chua oracle (CONF-6 reads negligible);
- J-A3 rossler oracle (CONF-8 reads negligible);
- J-I1 lorenz63 deployable (CONF-5 reads reduces).

**J-A4 (not confirmed).** Lorenz-63, deployable, 1 LT, MSE of the allocation fitted on the raw delay vector X over that of the full profile F (`ladder/vs_full/X/mse_ratio` in each `contrib.json`, level 0.99615):

| seed | ratio | interval | reading |
|---|---|---|---|
| CONF-5 | 0.894 | [0.699, 1.106] | undetermined (n_eff < 50) |
| CONF-6 | 0.886 | [0.780, 0.983] | lowers |
| CONF-7 | 0.742 | [0.570, 0.909] | undetermined (n_eff < 50) |
| CONF-8 | 0.778 | [0.642, 0.905] | lowers |
| CONF-9 | 0.836 | [0.724, 0.975] | lowers |

Three seeds imply the claim and four are needed. On CONF-7 the interval lies below 1, but the pre-registered guard (effective sample size under 50) makes the reading undetermined. The guard is part of the reading table and was applied as frozen. Under §9, "not confirmed" does not mean that X fails to lower the MSE.

## 3. Regeneration comparison (§5)

No verdict depends on the regeneration. The verdicts above are those of the official runs.

**Claim rows.** For each of the 48 rows, the per-seed `readings`, the `absent` list and the `verdict` in `phasej-confirm-regen/confirm.json` were compared with the official `confirm.json`. **No row differs.** Nor does any claim × system verdict, so no row is reported as unstable at its threshold. The §7a v3 words (§5 here) are also identical between the two sets.

**Leaves (`tools/compare_runs.py`, official as reference).**

| seed | tier | results.json leaves differing | largest class (a) change (relative) | integer leaves differing | dump arrays differing (of 355 per system: L63 / Rö / Chua) |
|---|---|---|---|---|---|
| CONF-5 | T0 | 489 of 20,798 | 3.9e-3, Chua deployable Shapley O interval bound | 3: analog-proxy nfev (Chua 9 → 10, Rössler 20 → 15), status (Rössler 3 → 2) | 8 / 8 / 10 |
| CONF-6 | T0 | 97 of 20,806 | 0.219, Chua deployable w=0 leave-one-out R interval bound | 2: Chua Q-N predictions outside [0, 1] (79 → 71, 71 → 70) | 7 / 7 / 9 |
| CONF-7 | T0 | 0 of 20,806 | 0 | 0 | 0 / 0 / 0 |
| CONF-8 | T0 | 440 of 20,838 | 0.129, Chua Q-N deployable logit interval bound | 4: analog-proxy nfev (Chua 20 → 21, Rössler 26 → 15), status (Lorenz-63 A4 refit 1 → 2, Rössler estimation proxy 4 → 3) | 8 / 8 / 12 |
| CONF-9 | T3 | 3800 of 20,822 | 6.3e-4, Chua H2d interval bound | 6: `gain_bound/n_screened_out/negative_covariance`, twice each (Chua 935 → 936, Lorenz-63 946 → 955, Rössler 1274 → 1275) | 183 / 183 / 183 |

- **CONF-5, CONF-6, CONF-8: the DEF-0033 pattern.** The differing arrays are those downstream of the seed-proxy fit: the deployable profile, A4's weights and MSE, and the Q-N test inputs. The orbits, the oracle quantities and the trained networks are equal. The largest relative changes are on small ΔR² interval bounds in Chua's deployable analyses: on CONF-6, the w = 0 leave-one-out R upper bound moved from 0.0255 to 0.0310 (0.219 relative); on CONF-8, the Q-N logit lower bound moved from −0.0191 to −0.0216 (0.129). No claim row's reading changed.
- **CONF-9: a new, wider mechanism (DEF-0035).** The state-estimator network trained to different weights: the weight digests differ in all three systems, so the tier is T3. The orbits, the analog errors and the oracle seeds are still equal (`core/E_C`, `core/nu`, `core/eps_s`, `core/oracle_state`). Everything that depends on the trained estimator differs, by at most 6.3e-4 relative on a quantity of interest. No claim row and no v3 word changed.
- **CONF-7** is bitwise.

Reports: `runs/confirmatory/phasej-CONF-n-regen-compare.txt` (one per seed) and `runs/confirmatory/phasej-regen-compare.txt` (every differing dump array, then the row comparison), written by `docs/agent/notes/2026-10-28-phase-j-confirmatory-report.regen_cmp.py`.

## 4. Defects found in this round

- **DEF-0034** (command form; workaround recorded in ledger seq 66). Resolution pending the owner.
- **DEF-0035** (GPU network training not reproducible on CONF-9). It does not affect any verdict, reading or v3 word. It widens §8 item 7, which named only the state estimator's ν̂. Resolution pending the owner.

## 5. Secondary description: v3 words of the sealed runs (§7a)

**SECONDARY DESCRIPTION: v3 words of the sealed runs under the phase J configuration; not the v3 test; does not change, confirm or replace CONF-1.**

Departures from v3:
1. n_test is 4000, not v3's 1000, so the intervals are narrower than v3 sized them;
2. the device is the GPU, where v3 §9 makes the CPU official;
3. the robustness sweep is skipped (it is reported-only in v3);
4. the time unit is pinned (pre-registration §5).

The words come from `runs/confirmatory/phasej-confirm/v3.json`. The CONF-1 column is the promoted word (`promoted/CONF-1/results.json` → `verdicts`, sha256 ae4b0fe5…0cebe), shown for reference only. A difference from it describes how v3's words vary across seeds and configurations; it revises nothing.

| row | system | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | seeds per word | CONF-1 (reference only) |
|---|---|---|---|---|---|---|---|---|
| H1a | lorenz63 | inconclusive | pass | pass | inconclusive | inconclusive | inconclusive 3, pass 2 | pass |
| H1a | rossler | pass | inconclusive | pass | pass | pass | pass 4, inconclusive 1 | pass |
| H1a | chua | pass | fail | pass | pass | inconclusive | pass 3, fail 1, inconclusive 1 | inconclusive |
| H1b | lorenz63 | pass | pass | pass | pass | pass | pass 5 | inconclusive |
| H1b | rossler | fail | fail | fail | fail | fail | fail 5 | fail |
| H1b | chua | pass | pass | pass | pass | pass | pass 5 | pass |
| H1c | lorenz63 | fail | fail | fail | fail | fail | fail 5 | fail |
| H1c | rossler | pass | pass | pass | pass | pass | pass 5 | pass |
| H1c | chua | fail | fail | fail | fail | fail | fail 5 | inconclusive |
| H1d | lorenz63 | pass | pass | pass | pass | pass | pass 5 | pass |
| H1d | rossler | pass | pass | pass | pass | pass | pass 5 | pass |
| H1d | chua | inconclusive | inconclusive | fail | inconclusive | inconclusive | inconclusive 4, fail 1 | inconclusive |
| Q-N | lorenz63 | distinct but small | reduces | distinct but small | distinct but small | reduces | distinct but small 3, reduces 2 | reduces |
| Q-N | rossler | reduces | distinct but small | reduces | reduces | distinct but small | reduces 3, distinct but small 2 | reduces |
| Q-N | chua | reduces | reduces | reduces | reduces | reduces | reduces 5 | reduces |
| H2a | lorenz63 | fail | inconclusive | fail | fail | fail | fail 4, inconclusive 1 | fail |
| H2a | rossler | fail | fail | fail | fail | fail | fail 5 | fail |
| H2a | chua | fail | fail | fail | fail | fail | fail 5 | fail |
| H2b | lorenz63 | pass | pass | pass | pass | pass | pass 5 | pass |
| H2b | rossler | pass | pass | pass | pass | pass | pass 5 | pass |
| H2b | chua | pass | pass | pass | pass | pass | pass 5 | pass |
| H2c | lorenz63 | fail | fail | fail | fail | fail | fail 5 | inconclusive |
| H2c | rossler | fail | fail | fail | fail | fail | fail 5 | inconclusive |
| H2c | chua | inconclusive | inconclusive | inconclusive | inconclusive | inconclusive | inconclusive 5 | pass |
| H2d | lorenz63 | fail | fail | fail | fail | fail | fail 5 | inconclusive |
| H2d | rossler | pass | pass | pass | pass | pass | pass 5 | pass |
| H2d | chua | pass | pass | pass | pass | pass | pass 5 | pass |
| H2e | lorenz63 | pass | pass | pass | pass | pass | pass 5 | pass |
| H2e | rossler | pass | pass | pass | pass | pass | pass 5 | pass |
| H2e | chua | pass | pass | pass | pass | pass | pass 5 | pass |
| gain_bound | lorenz63 | reported | reported | reported | reported | reported | reported 5 | reported |
| gain_bound | rossler | reported | reported | reported | reported | reported | reported 5 | reported |
| gain_bound | chua | reported | reported | reported | reported | reported | reported 5 | reported |
| H3a | lorenz63 | inconclusive | inconclusive | inconclusive | inconclusive | inconclusive | inconclusive 5 | inconclusive |
| H3a | rossler | inconclusive | inconclusive | inconclusive | inconclusive | inconclusive | inconclusive 5 | inconclusive |
| H3a | chua | pass | pass | pass | pass | pass | pass 5 | inconclusive |
| H3b | lorenz63 | inconclusive | fail | inconclusive | inconclusive | inconclusive | inconclusive 4, fail 1 | fail |
| H3b | rossler | inconclusive | inconclusive | inconclusive | pass | inconclusive | inconclusive 4, pass 1 | pass |
| H3b | chua | inconclusive | inconclusive | inconclusive | inconclusive | inconclusive | inconclusive 5 | inconclusive |
| H3c | lorenz63 | pass | pass | pass | pass | pass | pass 5 | inconclusive |
| H3c | rossler | pass | pass | pass | pass | pass | pass 5 | pass |
| H3c | chua | inconclusive | pass | pass | pass | pass | inconclusive 1, pass 4 | inconclusive |

No combined word, no "confirmed" and no pooled statistic is computed. Under departure 1, a word that is "inconclusive" on CONF-1 and "pass" or "fail" here is expected from the narrower intervals alone.

## 6. Limitations (pre-registration §8, attached)

1. The claims were chosen on development seeds whose results were seen. The sealed seeds are fresh.
2. Five realizations: each seed is one realization per system. Seeds are not pooled, and no between-seed variance is estimated.
3. Allocation below 2 LT on Lorenz-63 and Chua is mostly unreadable (the n_eff guard); no claim is made there. The same guard made J-A4 undetermined on two seeds (§2).
4. Chua gate risk: no gate failure occurred in this round.
5. Repetition, not independent reproduction: the regeneration used the same host, device and actor (waiver, seq 52).
6. The time unit was pinned to the value of 8 of 9 development GPU runs.
7. GPU runs are not bitwise reproducible (DEF-0033). **This round adds DEF-0035:** on CONF-9 the network training itself differed between the two runs. Neither changed a claim row.
8. The analysis instruments (HGB allocation fits, quantile boosting, the reading table) are analysis instruments, not rules of the v3 design.
9. The phase J code was not reviewed by the owner; agents built and tested it.
10. The analysis command took a different form from §7's literal text (DEF-0034, §1).

## 7. What may and may not be said (§9)

**May be said**, with §6 attached: for each claim and system, the pre-registered analysis of sealed seeds CONF-5 to CONF-9 returned the verdict in §2.

**May not be said:**
- an overall verdict, or a count of claims presented as a finding;
- any pooling across seeds;
- that a condition causes predictability;
- that "not confirmed" (J-A4) means no effect;
- that the v3 words of §5 test, confirm or revise any v3 hypothesis or the CONF-1 result;
- any comparison with CONF-1's numbers, or any change to the CONF-1 result.

## 8. Records (sha256)

Paths are relative to `lpcstudy-wt/run/conf-j/runs/confirmatory`.

```
909199a690294ea449c9d20e0c78836a5a954d767a397c23b576ee18a5ef06d0  phasej-confirm/confirm.json
0e01c1086aadeedf9a7484205d215c3eb036ba89e51e148fb6c314e03105a9d4  phasej-confirm/confirm.md
81c2a79408d289c5ac7baf8139b362318c698f0262936139e68f034000ab4d3d  phasej-confirm/v3.json
9987917ba23e9867b39cc040f2b0b2543ee8e6e4c13e0e0ef1f1bf42a64163e0  phasej-confirm/v3.md
0c5aacb99e15775efc11398a66c95f2fc34ed2edfad9ff6ede84099ab611cf42  phasej-confirm-regen/confirm.json
2b786201608ab5ff691bb5b7e09c6c7f8af9477c6593d9980d0fa4bd5b798dbf  phasej-CONF-5/phasej/results.json
63a2b9f44ffff3115a2efbfa7444c4f418825d88f547a0d228b0867b87e957e4  phasej-CONF-6/phasej/results.json
f856838d38e920e7abe9dc5d88d94532f7393501d6f92cd313db1024455ccff2  phasej-CONF-7/phasej/results.json
6aec5c2a9507f3aa0a10931b6f8bab96a00e28336a968247bdc56b87d04d35cc  phasej-CONF-8/phasej/results.json
2cfb2fd8eef1360c69424fdc01f8b40a10d47dfc275653c27f93dba6e95788ec  phasej-CONF-9/phasej/results.json
9516dbbf1adfb6f6e3a122c0af7bbcd5c51c76fabaa698b99bac7dd40de15800  phasej-CONF-5-regen/phasej/results.json
78a712c5a480fc32959f4cb7a972168f08f86767f4aeaf1956761a52bd20d47f  phasej-CONF-6-regen/phasej/results.json
d46ab0a31786719886c3955061c8e4a545bece70d1a6feca89bc69ccda9294f3  phasej-CONF-7-regen/phasej/results.json
49a08c364ffceeff717a23c755387c45b651e9a5085b2f79beeca2b631a5cc3d  phasej-CONF-8-regen/phasej/results.json
f411284abd10ee89f2be6e704caa4cca590e672461a78a4315d94ea337643f1e  phasej-CONF-9-regen/phasej/results.json
3ded6295b5373cc160e5a83d1b084bcfd090c5bf591914055f9ca226aff59543  phasej-CONF-5/contrib-j/contrib.json
8f0df0ee163c526ad20edb49d70c3fe390adce779ec1efd3d9f3d16489dca481  phasej-CONF-6/contrib-j/contrib.json
ea0977b556e34c47d5bf47562279cfb28fd93a1203a41a064e2ddcf7156cfb04  phasej-CONF-7/contrib-j/contrib.json
c1df485a26b52f382c17cc124c690e23d5db40d5507dc958ce8fe7f0ab5f2117  phasej-CONF-8/contrib-j/contrib.json
b389d2d25aab6cc1d364f1a47cca50b15c930d592399d656b776084233a14ffc  phasej-CONF-9/contrib-j/contrib.json
30416f6f803e59216b7ed9030d8d204dd713751ff5e1cd7e536347c26454da4d  phasej-CONF-5/contrib-j/ce.json
38accf009add27b062095feaf871b0a5b41768331007a571339e13dbcf2acc17  phasej-CONF-6/contrib-j/ce.json
2376e93dfb8115e05ad5c06ec41bc87c982187c84feb47871753b29e157825c2  phasej-CONF-7/contrib-j/ce.json
bacefdeda55ae47375d1538a126b15f50056cf43d970670516f9f35d5bb704a6  phasej-CONF-8/contrib-j/ce.json
40a9f661ad48f764b157e69fc1b0161e9db855431032bebc9fce3cde8a4ad4da  phasej-CONF-9/contrib-j/ce.json
01786c53ccc9d33383c1ed29171c419ede4c0da0612ed14e1fa6ea5f2db41486  phasej-CONF-5-regen-compare.txt
d481196146147d6afa960dd9e2b29bc5ba2ed9dd38ea205d62f8502f7a5dbf15  phasej-CONF-6-regen-compare.txt
50425a8847c9c8f96bd1f4d882734259e7d3f4257113add3086059d3d41e34a3  phasej-CONF-7-regen-compare.txt
680c7356fdeef7d97e3b24d48c07372e6ffb49c8b62f4df5d50976a75ebd0919  phasej-CONF-8-regen-compare.txt
7213d4f72c87e6baad579c37997066c919da95c54286cd649703494b2f705d16  phasej-CONF-9-regen-compare.txt
f9e3f1427234db3eef483648bfe9a83501843f6d7305acb7652178653990f46d  phasej-regen-compare.txt
```

## 9. What remains (WU-0058)

- Auditor pass on this report (plan criterion: zero blockers).
- Owner: rulings on DEF-0034 and DEF-0035, and promotion of the round (copy of the records into `promoted/`, as for CONF-1).
