
# Freeze gate 2026-10-18, commit 2fa4259a4ec4f698242127c5ade98c4f1990d73c (owner script)
- `LPC_GATE=freeze tools/run_tests.sh unit tests/unit`: exit 1, FAILED tests/unit/test_identifiers.py::test_criterion_text_is_the_v3_section_2_row 1 failed, 1868 passed in 134.14s (0:02:14) 
- `LPC_GATE=freeze tools/run_tests.sh integration tests/integration`: exit 0, ...................                                                      [100%] 19 passed in 451.41s (0:07:31) 
- `LPC_GATE=freeze tools/run_tests.sh slow tests/slow`: exit 0, -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html 158 passed, 14 warnings in 1183.69s (0:19:43) 
- `LPC_GATE=freeze tools/run_tests.sh gpu tests/gpu`: exit 1, FAILED tests/gpu/test_reproducibility.py::test_smoke_twice_on_gpu_is_bitwise_reproducible 1 failed in 369.89s (0:06:09) 
