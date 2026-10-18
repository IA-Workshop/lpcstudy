# Merge gate on develop, 2026-10-18 (main session)

Gate: merge (DEVELOPMENT_WORKFLOW.md 4.3), `LPC_GATE=merge`, one call per tier, once. Reason: since the gated line tip 2d99ac4 (GATE-2026-10-17-wu0003-line) develop gained WU-0003.8 fix round 5 (the H1d tie rule), DEF-0028 (`tools/lm_doubling.py`), WU-0003.8d (`tools/rehearsal_diagnostics.py`), the golden refresh, and the independent review of 8d found the golden regression test red since 1ed9e2d (amendments note 32). This gate confirms the combined state.

Tip: develop `1e3d726` (merge of WU-0003.8d). Checklist (4.9), one line each:
1. Change set: all changes since 2d99ac4 (tools, tests, docs). 2. Radius: whole suite, unit and integration tiers (the gate; named role main session). 3. Slow tier not part of this gate. 4. Device: CPU (wrapper). 5. Not rerun without a code change: the unit tier ran last at 2d99ac4, a different code state. 6. No GPU. 7. Output: wrapper default. 8. Commands: `LPC_GATE=merge tools/run_tests.sh unit tests/unit`, then `LPC_GATE=merge tools/run_tests.sh integration tests/integration`.

## Results
- `LPC_GATE=merge tools/run_tests.sh unit tests/unit`: `1735 passed in 131.87s (0:02:11)`, exit 0.
- `LPC_GATE=merge tools/run_tests.sh integration tests/integration`: `19 passed in 465.48s (0:07:45)`, exit 0.

Verdict: **green** at develop `1e3d726` (code; the checklist commit aece42c changes docs only). Unit 1684 at the previous gate to 1735 now (+51: DEF-0028 tests, 8d tests, the golden test). The golden regression test passes. Slow and gpu tiers not part of this gate. This does not by itself request `main`: owner items remain open.
