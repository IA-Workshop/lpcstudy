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
