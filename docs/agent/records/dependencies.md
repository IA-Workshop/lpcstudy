# Dependencies

Why each direct dependency is carried (REPRO.9, SIMPL.4, LPC.PC.17). The exact pins are in `requirements.txt`. Adding or removing a dependency is a dated entry at the bottom of this file. The pins were last reviewed on 2026-10-10 (initial).

| Package | Pin | License | Why it is carried |
| --- | --- | --- | --- |
| jax, jaxlib | 0.11.2 | Apache-2.0 | RK4 flow maps, Jacobians by automatic differentiation, float64 on CPU and GPU |
| optax | 0.2.8 | Apache-2.0 | Adam and the cosine schedule for the state-estimator network and the learned allocator |
| numpy | 2.5.3 | BSD-3-Clause | arrays, random generators (`make_rng`) |
| scipy | 1.18.1 | BSD-3-Clause | k-d tree analog search (`cKDTree`); robust least squares and NNLS for the proxy fits; rank statistics |
| scikit-learn | 1.9.1 | BSD-3-Clause | gradient-boosted regressors (Q-N) and regression trees (regime maps) |
| matplotlib | 3.11.2 | Matplotlib (PSF-style) | figures |
| pytest | 9.1.1 | MIT | tests (development only) |

**GPU.** On the owner's workstation, install `jax[cuda12]==0.11.2` in place of the CPU wheel. The CUDA wheels come from PyPI. The code is unchanged.

**Python:** 3.13.

## Change log

- 2026-10-10: initial list. The versions are those the v1 pilot ran with (Claude).
- 2026-10-18 (claude-sonnet-5-5, main session; owner order "format code to 80 columns using black", code review of 2026-10-18): **black 26.10.1** is used as a formatting TOOL only, run with `uvx black==26.10.1` (an isolated, ephemeral environment). It is not installed in the project `.venv`, not in `requirements.txt`, not in `requirements.lock`, and not imported by any code or test. Configuration: `pyproject.toml` (`line-length = 80`, `target-version = py313`, `required-version = 26.10.1`). Licence MIT. Black's own safety check (the formatted code must have the same AST) stays on; no `--fast`. For the owner's confirmation at the dependency review (LPC.PC.17).
