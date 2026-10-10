# Defects

Append-only (PRIME.5). To change an entry's status, add a dated status line under it; never edit the original text (LPC.PC.14).

**Blocking** means the defect blocks the freeze and any reporting of the results it affects. **Tracked** means it is resolved on the stated schedule or reported as a known limitation (INTPR.10).

---

**DEF-0001: Silent handling of bad values is not counted or reported** (PRIME.4, LPC.PC.21d)

- **Blocking:** yes, before the freeze.
- **Affects:** every run.
- **Description.** These cases are documented in Methods v2 but not counted per run in `results.json`:
  - non-finite state estimates replaced by the invariant mean;
  - forecast errors clipped at 10 σ_x;
  - the regime-count fallback.
- **Resolution:** WU-0002, item 11.
- 2026-10-10: opened (Claude).
- 2026-10-10 (claude-sonnet-5-5, main session, on the WU-0013.2 reviewer's finding R3; both sites checked): two further silent cases that WU-0002.11 must count and report: `lpcstudy/statistics.py:61` (`kaplan_meier` sets the hazard to 0 where no subject is at risk) and `lpcstudy/statistics.py:95-96` (`logrank_test` returns p = 1.0 when the variance is not positive). Both feed H3a. Any fix is statistics code and needs owner review before the freeze.

**DEF-0002: Excess MSE uses c(w − w\*)² with clipped w\*** (VV.1)

- **Blocking:** yes.
- **Affects:** regret ratios, the K choice, the H3 statistics.
- **Description.** The formula understates the excess error for states where w\* is clipped (Methods v2 §M13, item 7).
- **Resolution:** WU-0002, item 2.
- 2026-10-10: opened (Claude).

**DEF-0003: Regime weight is the curvature-weighted mean of clipped w\*, not the optimum** (Theorem P3a)

- **Blocking:** yes.
- **Affects:** A5 and H3c.
- **Resolution:** WU-0002, item 2.
- 2026-10-10: opened (Claude).

**DEF-0004: Missing intervals for some tested statistics** (VV.3, v3 §7)

- **Blocking:** yes.
- **Affects:** H1d proxy correlations (v2 H1e) and H3c MSE ratio (v2 H3d), which have no bootstrap interval.
- **Resolution:** WU-0002, items 3 and 6.
- 2026-10-10: opened (Claude).

**DEF-0005: Hypothesis identifiers and criteria in code follow v1/v2, not v3** (INTPR.3)

- **Blocking:** yes.
- **Affects:** the report, figures and verdicts.
- **Resolution:** WU-0002, items 3–10.
- 2026-10-10: opened (Claude).

**DEF-0006: Outputs carry no provenance block** (REPRO.4)

- **Blocking:** yes.
- **Affects:** every output. Missing: seed id, commit, environment, device.
- **Resolution:** WU-0001.
- 2026-10-10: opened (Claude).

**DEF-0007: Tests not yet audited for regression guards versus reference tests** (VV.7, LPC.PC.21a)

- **Blocking:** yes, before the freeze.
- **Affects:** correctness evidence.
- **Description.** Some of the 14 v1 tests may compare against the code's own output. Each test must be labeled with its reference, or as a regression guard.
- **Resolution:** a unit before the freeze.
- 2026-10-10: opened (Claude).
- 2026-10-10 **resolved** (claude-sonnet-5-5, main session): WU-0013 audited all 14 tests (`docs/agent/records/audits/2026-10-10-def-0007-tests.md`: 13 reference, 1 defective) and fixed them (merged; merge gate 78 passed; independent review approved). Every test now names its reference and justifies its tolerances; the defective test is now a regression guard with three independent tests beside it. Open follow-up, not a reopening: the AMI delay band is uncited (needs the researcher).

**DEF-0008: N̂ does not estimate N without bias** (INTPR.10)

- **Blocking:** no (tracked).
- **Affects:** H1d's N̂ row and the deployable Q-N.
- **Description.** N̂ perturbs the noisy query, not the clean one.
- **Schedule:** reported as a known limitation in v3 §8. A fix is future work.
- 2026-10-10: opened (Claude).

**DEF-0009: Bootstrap-interval stability under doubled thinning not checked** (Methods v2 §M16)

- **Blocking:** no (tracked).
- **Schedule:** future work, reported as a limitation.
- 2026-10-10: opened (Claude).

**DEF-0010: Registered seeds of 2³² or more crash scikit-learn calls that take `config.seed` as `random_state`** (PRIME.4, LPC.PC.7)

- **Blocking:** yes. Blocks WU-0003 (the DEV-1 rehearsal) and the confirmatory run.
- **Affects:** runs on DEV-1 to DEV-4 (their registered values are all at least 2³²) and on any 62-bit confirmatory seed. DEV-0 (20261005) is unaffected, which is why the pilot and the baseline smoke run did not show it.
- **Description.** scikit-learn accepts `random_state` only in [0, 2³² − 1]. `check_random_state(2844678021587022684)` raises `ValueError: Seed must be between 0 and 2**32 - 1` (verified in the project venv by the main session, 2026-10-10). The code passes `config.seed` directly at `lpcstudy/analysis.py:295`, `:678`, `:680` and `lpcstudy/allocation.py:358`. Found by the WU-0001 planner while planning WU-0001.1; no test catches it, because every test and the smoke preset use DEV-0.
- **Resolution:** a fix in WU-0002 (a plan item to be added by amendment). It changes the random streams of every scikit-learn call, so it changes numbers for every seed unless the derivation keeps `config.seed` unchanged below 2³². The choice between "derive a 32-bit value with `make_rng(seed, label)` for all seeds" and "leave seeds below 2³² untouched" affects the WU-0002.12 regression against the pilot and is the owner's to rule on. Until then, only DEV-0 can be run.
- 2026-10-10: opened (claude-sonnet-5-5, main session).

**DEF-0011: Reference pool for the 1/d estimate is drawn with a fixed literal seed, outside `make_rng`** (LPC.PC.21, CLAUDE.md "Randomness only via `lpcstudy.data.make_rng`")

- **Blocking:** no (tracked). To be ruled on by the owner before the freeze, because fixing it changes numbers.
- **Affects:** every run: the pool of up to 2×10⁴ library states used for the 1/d reference is the same for every seed id.
- **Description.** `lpcstudy/oracle.py:101` has `rng = np.random.default_rng(0)` and draws the pool with `rng.choice`. Found by the WU-0014 reviewer (who cited line 99; checked by the main session at line 101). A grep also shows other `np.random.default_rng(...)` calls that take a seed directly instead of `make_rng(seed, *labels)`: `dynamics.py:147`, `validation.py:107` and `:147`, `statistics.py:151`, `networks.py:145`, `experiments.py:88`. Whether those derive correctly from the study seed has not been audited here.
- **Resolution:** to be planned in WU-0002 (the owner decides whether the pool should depend on the seed id; the pilot used the fixed pool, so a change affects the WU-0002.12 regression).
- 2026-10-10: opened (claude-sonnet-5-5, main session, on the WU-0014 reviewer's finding).
