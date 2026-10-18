"""lpcstudy: research code for a study of two chaotic-system forecasters.

The study compares two ways of forecasting a chaotic system from noisy
measurements of one variable:

* the analog forecaster (CP), which finds similar situations in stored past
  data and follows what happened next;
* the physics-based forecaster (PLP), which estimates the hidden state and
  runs the known equations forward.

It asks whether four local predictability conditions (recurrence,
observability, instability and noise sensitivity) decide how to blend the
two forecasts with a weight ``w*``. The test runs on three systems
(Lorenz-63, Rossler and Chua). The verdict is "supported" only if all three
systems pass.

How the pieces in this folder fit together:

* Settings and randomness: ``config`` (every design constant), ``seeds``
  (which master seed a run may use), ``data.make_rng`` (the only source of
  random numbers).
* Data: ``systems`` (the equations), ``embedding`` (delay vectors), ``data``
  (trajectories, units and splits).
* Forecasting and experiments: ``ensemble``, ``oracle``, ``estimation``,
  ``allocation``, ``dynamics``, ``networks``, ``pipeline``, ``experiments``,
  ``analysis``, ``validation``, ``statistics``.
* Records and reports: ``identifiers`` (hypothesis names), ``provenance``
  (what produced a result), ``report`` and ``budget`` (verdicts, tables and
  figures), ``dump`` (per-state arrays).
* Entry point: ``__main__`` (``python -m lpcstudy``).

Only development seeds are used in development; the sealed confirmatory seed
is never touched (LPC.PC.7).
"""
