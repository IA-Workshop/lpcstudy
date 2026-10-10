# Results manifest

Every result that is reported or cited, with its inputs (LPC.PC.15, REPRO.1). Append-only. Status values:

- `exploratory`: development or pilot, never a hypothesis test;
- `unpromoted`: a confirmatory result not yet promoted;
- `promoted`: promoted, with the ledger entry number;
- `withdrawn`: with the reason.

| Result | File | Seed | Code | Environment | Status |
| --- | --- | --- | --- | --- | --- |
| Pilot v1 (2026-10-06) | `docs/study/pilot_results_v1.json` | DEV-0 (20261005) | v1 code in the Cowork sandbox; **not under version control**; this package's `lpcstudy/` is that code | Python 3.13.16, jax 0.11.2, CPU (2 cores) | exploratory; **provenance reconstructed** (REPRO.4): not reproducible under REPRO.1 until regenerated on DEV-0 with a committed revision (WU-0002 regression) |
| Library-sweep recheck (2026-10-10) | `docs/study/pilot_library_recheck.json` | DEV-0 | as above, plus a sandbox script (not included) | as above | exploratory; provenance reconstructed |
| Baseline smoke reference (2026-10-10) | `runs/baseline/smoke/results.json` (sha256 `0da48771ee967525f71518d4bb6e7aec675349ff175a2d4544234d4f8f084b79`) | DEV-0 (20261005) | commit `f01360d` (tag `v1-baseline`); `lpcstudy/` and `tests/` unmodified | Python 3.13.16, jax 0.11.2, numpy 2.5.3, CPU (`JAX_PLATFORMS=cpu`, 4 threads) | exploratory; smoke preset, plumbing reference only, not a hypothesis test; cited by WU-0001.5 |

- 2026-10-10, claude-sonnet-5-5: "Pilot v1" row: the code in this package was committed unchanged as the baseline commit `f01360d606b161206bae13a59cc8f476f5ddacbd` (tag `v1-baseline`). The row's provenance stays `reconstructed` until the WU-0002 regression regenerates it on DEV-0 (WU-0009.1).
