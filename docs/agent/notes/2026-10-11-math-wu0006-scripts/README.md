# Reference scripts for the WU-0006 mathematics review (2026-10-11)

These scripts regenerate every number in `../2026-10-11-math-wu0006.md` (REPRO.10). They are scratch reference code, not library code and not tests: synthetic data only, scratch seed literal 20261011 (no DEV or CONF seed), CPU only, 4 spawned single-thread workers (LPC_THREADS = 4).

Run from this directory with the project interpreter (`LPC_PYTHON`, or `.venv/bin/python`). The `.npy` outputs are written here and are not committed. The `.log` files are the committed outputs of the runs the note quotes.

| Script | What | Time (4 workers) |
| --- | --- | --- |
| `check_fast.py` | Fast statistic forms against production `block_resample_indices`, `spearman`, `partial_correlation`, `quadratic_controls` | seconds |
| `m1_bounds.py` | M1 bounds, integer rules, exact binomial false-alarm | seconds |
| `run_m2b.sh` → `m2_coverage.py` | Coverage reference C1–C9 (both phi), C1s, heavy-tail rows → `cov_*.npy`, `m2_coverage.log` | about 15 min |
| `make_tables.py` (uses `m2_pfail.py`, `m2_ranges.py`) | Coverage, A3, P(fail) and consistency-range tables from `cov_*.npy` | seconds |
| `m2_analytic.py` | Influence-series acf and first-order MBB coverage (exact E V* = tr(M Sigma)) | seconds |
| `m2_decomp.py` | Second-order decomposition (1 thread) | about 1 min |
| `m5_logrank.py <phi> <L1\|L2> 40000` | Log-rank size through production `h3a_logrank` → `m5_logrank.log` | about 1 min each |
| `m4_dr2.py <phi> 400`, `m4_dr2_full.py 0 200` | Null ΔR² through production `qn_profile_block` and conditional truth → `m4_dr2.log`, `other_outputs.log` | about 7 and 3 min |
| `o4_proxy.py` | O4 dynamics proxy, independent numpy RK4 (1 thread) | about 1 min |

**WU-0006.4 additions (2026-10-11, C7 correction, DEF-0022).** Run from a directory that holds `cov_C7_0.npy` and `cov_C7_0.3.npy` from `m2_coverage.py`.

| Script | What | Time (4 workers) |
| --- | --- | --- |
| `c7_extend.py <phi> 40000` | Independent extension of the C7 reference (scratch seed 20261012) → `cov_C7_<phi>_ext.npy`, `c7_extend.log` | about 2 min each |
| `c7_verdict_ranges.py` | C7 pass / fail / inconclusive counts by the production verdict rule, ranges by the `m2_ranges` rule (R_ref 60 000) → `c7_verdict_ranges.log` | seconds |
| `h2a_power.py` | H2a(ii-b) interval width against n (250 to 2000) and P(pass \| rho), phi 0 and 0.3 (scratch seed 20261013) → `h2a_power.log` | about 2 min |
| `dr2_full_ref.py <phi> 1000 8` | A9: null ΔR² reference at 3000/1000 (the study's sizes), `m4_dr2_full.work` with scratch seed 20261014 → `dr2ref_<phi>.npy`, `dr2ref.log` | about 12 min each (8 workers) |
| `dr2_full_ranges.py` | A9: N1–N3 rates, P(fail) of the R = 500 bounds and consistency ranges (same rule) → `dr2_full_ranges.log` | seconds |

`simcore.py` holds the shared generators and fast statistics. The scripts that import `lpcstudy` put the repository root on `sys.path` (`parents[4]` of the script).
