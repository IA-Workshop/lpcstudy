# Merge gate, develop, 2026-10-18 (d): after the owner's code review (WU-0004h)

Main session (claude-sonnet-5-5). Tree: develop at `e326c87` (all eleven style branches merged), run with the script `/tmp/claude-1000/final_gate.sh`; the review fix `f07a154` renames one test back and changes no code. `LPC_GATE=merge`, `LPC_PYTHON` set to the project venv.

- `tools/run_tests.sh unit tests/unit`: `1870 passed in 141.55s (0:02:21)`.
- `tools/run_tests.sh integration tests/integration`: `19 passed in 451.49s (0:07:31)`.
- Three-system smoke (DEV-0, CPU, 4 threads) against `runs/refactor-base3/smoke`: tier T0, 13,914 leaves, 13,908 equal, 6 different, 0 one-sided; the 6 are the American-spelling string leaves (`H1a/reference_estimator`, `H2a/controls`, three systems), RESULT FAIL by the tool's text-leaf rule, as expected (amendments note section 46, R2). New baseline: `runs/refactor-base4/smoke`.
- `tools/run_tests.sh gpu tests/gpu`: `1 passed in 456.20s (0:07:36)`; run 1 236 s, run 2 219 s, 4732 leaves (3166 floats), 0 different, 0 one-sided, max abs and max rel difference 0.0, `compare_runs` tier T0, exit 0 (after the `LPC_THREADS` fix of `70a696d`; the owner's freeze run at `2fa4259` had failed only at the tier assertion).
- Slow tier: not rerun. Owner's freeze run at `2fa4259`: `158 passed, 14 warnings in 1183.69s`; changes since are style, docstrings, spelling and the GPU test environment.
- After the gate: `f07a154` (test renamed back, R1), `54d627d` (review record merged). Radius for `f07a154`: `tests/unit/test_data.py`, `tests/unit/test_report.py`, `61 passed in 15.66s`.
