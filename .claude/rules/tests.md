---
paths:
  - "tests/**"
---

# Test rules (VV.7, LPC.PC.21, NVVUQ.5–7)

- **Docstring.** Every test's docstring states the behavior it fixes, its **reference**, and the **justification of its tolerance**.
- **Regression guards.** A test against the code's own earlier output is a regression guard: name it `test_regression_*` and say so. It is not correctness evidence.
- **Fix the code, not the test.** Never loosen a tolerance, change a reference or skip a test to make it pass. If the test is wrong, record the decision in `docs/agent/records/decisions.md` and keep the original in history (QA.6, PRIME.2).
- **Statistical tests** use fixed seeds and enough replications that their own Monte Carlo error is below the tolerance. State that error in the test.
- **Layout and tiers.** `tests/unit/test_<module>.py` mirrors `lpcstudy/<module>.py`. `tests/integration/`, `tests/slow/` and `tests/gpu/` carry their markers from the directory (WU-0010). Place a test by its cost and device, not by convenience.
- **Once.** Never run a test twice without a change between the runs (DEVELOPMENT_WORKFLOW.md §4.4).
- **Speed.** Keep each test under 5 s. Slow tests get `@pytest.mark.slow` and a reason.
