
# Freeze gate 2026-10-18, commit 2fa4259a4ec4f698242127c5ade98c4f1990d73c (owner script)
- `LPC_GATE=freeze tools/run_tests.sh unit tests/unit`: exit 1, FAILED tests/unit/test_identifiers.py::test_criterion_text_is_the_v3_section_2_row 1 failed, 1868 passed in 134.14s (0:02:14) 
- `LPC_GATE=freeze tools/run_tests.sh integration tests/integration`: exit 0, ...................                                                      [100%] 19 passed in 451.41s (0:07:31) 
- `LPC_GATE=freeze tools/run_tests.sh slow tests/slow`: exit 0, -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html 158 passed, 14 warnings in 1183.69s (0:19:43) 
- `LPC_GATE=freeze tools/run_tests.sh gpu tests/gpu`: exit 1, FAILED tests/gpu/test_reproducibility.py::test_smoke_twice_on_gpu_is_bitwise_reproducible 1 failed in 369.89s (0:06:09) 

# Freeze gate 2026-10-18, commit df6ff85c0a2b0ae7276e43cb0d1118618399a5f3 (owner script)
- `LPC_GATE=freeze tools/run_tests.sh unit tests/unit`: exit 0, ......................................................................   [100%] 1870 passed in 138.86s (0:02:18) 
- `LPC_GATE=freeze tools/run_tests.sh integration tests/integration`: exit 0, ...................                                                      [100%] 19 passed in 453.51s (0:07:33) 
- `LPC_GATE=freeze tools/run_tests.sh slow tests/slow`: exit 0, -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html 158 passed, 14 warnings in 1167.66s (0:19:27) 
- `LPC_GATE=freeze tools/run_tests.sh gpu tests/gpu`: exit 0, .                                                                        [100%] 1 passed in 475.21s (0:07:55) 
