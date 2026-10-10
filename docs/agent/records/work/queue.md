# Work queue

Units in priority order. Each unit's plan, log, review and audit live in its own file, `WU-nnnn-<slug>.md`, copied from `WU-template.md` (LPC.PC.9).

| Unit | Title | Depends on | Owner checkpoint | Status |
| --- | --- | --- | --- | --- |
| WU-0001 | Seed registry, confirmatory-seed guard, run provenance | — | review of seed code before freeze | planned |
| WU-0002 | Code changes for Methods v2 §M15 and v3 identifiers | WU-0001 | review of verdict code before freeze | planned |
| WU-0003 | Development rehearsal on DEV-1 (pilot preset) and precision report | WU-0002 | sample-size decision; sets reproducibility tolerance | planned |
| WU-0004 | Freeze package (owner act) | WU-0003 | freeze transaction | planned |

The plans for WU-0001 to WU-0003 are in their unit files. WU-0004 is the owner's act; an agent prepares the checklist when WU-0003 closes.

## Added 2026-10-10: NVVUQ gaps (`docs/agent/governance/NVVUQ-instantiation-LPC.md`)

| Unit | Title | Depends on | Owner checkpoint | Status |
| --- | --- | --- | --- | --- |
| WU-0005 | Code-verification gaps: RK4 observed order, k-d tree against brute force, Levina–Bickel on sets of known dimension, Levenberg–Marquardt residual reporting, N against the Theorem P2 bound | — | none | planned |
| WU-0006 | Statistical-procedure verification: coverage and size simulations for the bootstrap intervals, log-rank with Holm, null ΔR², and the verdict rules, at pilot sample sizes | WU-0002 | review before the freeze | planned |
| WU-0007 | Reference-value validation: published λ_max and parameters for Lorenz-63, Rössler and Chua, retrieved and confirmed by the researcher agent (VV.2) | — | none | planned |
| WU-0008 | Uncertainty budget, numerical-error estimates and interval labels in the report | WU-0002, WU-0005 | review before the freeze | planned |

Before the freeze, WU-0005 to WU-0008 close or are recorded as known limitations. WU-0005 and WU-0007 can run in parallel with WU-0001.
