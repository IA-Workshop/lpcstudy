---
paths:
  - "lpcstudy/**/*.py"
  - "tools/**/*.py"
---

# Numerical code rules (LPC.PC.21, NVVUQ)

- **float64 everywhere.** A precision change is a recorded decision in `docs/agent/records/decisions.md`.
- **Randomness** comes only from `lpcstudy.data.make_rng(seed, *labels)`, with the run's master seed. Never use unseeded generators or the global NumPy state.
- **No silent handling** (PRIME.4, NVVUQ.11). Every clip, non-finite replacement, fallback, early exit or swallowed exception is counted and written to the results and `run.log`.
- **Conventions.**
  - Time is in steps, and in Lyapunov times (1 LT = 30 steps).
  - Noise ρ is a fraction of σ_x.
  - Latent states are whitened.
  - Errors are measured against the noise-free truth; horizons against the noisy observation.

  Name variables so the convention is visible, and never convert silently (INTPR.4).
- **Contracts.** Check shapes and validity ranges where data enters a function (DSGN.2), and raise with an actionable message.
- **Theorem mapping.** Functions that compute w*, the curvature, excess MSE or the regime weights implement Theorems P1 and P3 of the v3 proposal. Their docstrings cite the theorem part they implement.
- **Tests and simplicity.** Every new function needs a test against an independent reference (skill `numerical-test`). Keep the obvious implementation; optimize only against a measured shortfall (RSRC.4).
