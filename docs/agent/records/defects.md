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
