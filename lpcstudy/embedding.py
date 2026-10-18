"""Delay embedding: turn one measured signal into a state-like vector.

In this study we only "see" one number per time step (the observable x of a
chaotic system, plus noise). Takens' delay-embedding idea says that stacking
a few past values of x, ``(x_t, x_{t-tau}, ..., x_{t-(D-1) tau})``, gives a
vector that behaves like the hidden state of the system. The analog
forecaster (CP) searches for neighbors among such vectors, and the
physics-based forecaster (PLP) fits a state to them.

This module has three jobs:

* ``delay_vectors`` builds the stacked vectors;
* ``select_delay`` chooses the spacing ``tau`` between stacked values (the
  first minimum of the average mutual information, a measure of how much
  one value tells us about a later one);
* ``autocorrelation_time`` measures how long the signal "remembers" itself,
  which sets how far apart sampled states must be to count as independent.

``data.build_context`` uses ``select_delay`` and ``autocorrelation_time``
once per system. ``delay_vectors`` is also used by ``data``, ``ensemble``
and ``experiments`` whenever a window of past observations is needed.
"""

from __future__ import annotations

import numpy as np

MI_BINS = 32
"""Number of equal-count bins per axis in the mutual-information histogram."""


def delay_vectors(
    series: np.ndarray,
    indices: np.ndarray,
    delay: int,
    dim: int,
) -> np.ndarray:
    """Stack past values into delay vectors.

    For each time ``t`` in ``indices`` the vector is
    ``X_t = (x_t, x_{t-tau}, ..., x_{t-(D-1) tau})``, where ``tau`` is the
    delay and ``D`` is the embedding dimension.

    Parameters
    ----------
    series : np.ndarray
        The signal, shape ``(T,)`` (or ``(T, ...)``; the first axis is
        time).
    indices : np.ndarray
        Times ``t`` at which to build a vector. Each must satisfy
        ``t >= (D-1) tau`` so that all the past values exist.
    delay : int
        The delay ``tau`` in observation steps.
    dim : int
        The embedding dimension ``D`` (number of stacked values).

    Returns
    -------
    np.ndarray
        Array of shape ``(len(indices), D, ...)``.

    Raises
    ------
    ValueError
        If any index is too early to have the full history.
    """
    indices = np.asarray(indices)
    if np.any(indices < (dim - 1) * delay):
        raise ValueError("delay vector requested without full history")
    lags = np.arange(dim) * delay
    return series[indices[:, None] - lags[None, :]]


def mutual_information(series: np.ndarray, lag: int) -> float:
    """Estimate how much ``x_t`` tells us about ``x_{t+lag}``, in nats.

    The mutual information ``I(x_t; x_{t+lag})`` is zero when the two values
    are unrelated and grows as they become more predictable from each other.
    We estimate it from a two-dimensional histogram. Each axis is cut into
    ``MI_BINS`` bins that hold equally many points (quantile bins), so the
    estimate does not depend on how the values are scaled.

    Parameters
    ----------
    series : np.ndarray
        The signal, shape ``(T,)``.
    lag : int
        Time separation in steps (at least 1).

    Returns
    -------
    float
        The mutual information estimate in nats.
    """
    edges = np.quantile(series, np.linspace(0.0, 1.0, MI_BINS + 1))
    edges[-1] += 1e-12
    codes = np.clip(
        np.searchsorted(edges, series, side="right") - 1,
        0,
        MI_BINS - 1,
    )
    first, second = codes[:-lag], codes[lag:]
    joint = np.zeros((MI_BINS, MI_BINS))
    np.add.at(joint, (first, second), 1.0)
    joint /= joint.sum()
    marg_a = joint.sum(axis=1, keepdims=True)
    marg_b = joint.sum(axis=0, keepdims=True)
    mask = joint > 0
    return float(
        np.sum(joint[mask] * np.log(joint[mask] / (marg_a @ marg_b)[mask]))
    )


def select_delay(series: np.ndarray, max_lag: int) -> int:
    """Pick the delay at the first minimum of the mutual information.

    A good delay is one where ``x_{t-tau}`` adds new information to ``x_t``,
    so the mutual information between them has dropped. We compute it for
    lags ``1..max_lag``, smooth it with a 3-point moving average (this
    suppresses false minima caused by histogram noise), and return the lag of
    the first local minimum.

    Parameters
    ----------
    series : np.ndarray
        The signal, shape ``(T,)``.
    max_lag : int
        The largest lag examined.

    Returns
    -------
    int
        The selected delay. If the curve has no local minimum, this is the
        lag of the global minimum over ``1..max_lag``.
    """
    raw = np.array(
        [mutual_information(series, lag) for lag in range(1, max_lag + 1)]
    )
    values = np.convolve(
        np.pad(raw, 1, mode="edge"),
        np.ones(3) / 3.0,
        mode="valid",
    )
    for k in range(1, len(values) - 1):
        if values[k] < values[k - 1] and values[k] <= values[k + 1]:
            return k + 1
    return int(np.argmin(values)) + 1


def autocorrelation_time(series: np.ndarray, max_lag: int) -> int:
    """Find the lag at which the signal has mostly forgotten itself.

    The autocorrelation at lag ``k`` is the correlation between ``x_t`` and
    ``x_{t+k}``. Oscillating signals (such as Rossler) cross zero early and
    then come back, so we use the envelope ``max_{j >= k} |ACF(j)|``, the
    largest size the autocorrelation still reaches at any later lag. The
    autocorrelation time is the first lag where this envelope falls below
    ``1/e`` (about 0.37).

    Parameters
    ----------
    series : np.ndarray
        The signal, shape ``(T,)``.
    max_lag : int
        The largest lag examined. It is returned if the envelope never
        falls below ``1/e``.

    Returns
    -------
    int
        The autocorrelation time in steps.
    """
    centered = series - series.mean()
    n_fft = 1 << int(np.ceil(np.log2(2 * len(centered))))
    spectrum = np.fft.rfft(centered, n_fft)
    acf = np.fft.irfft(spectrum * np.conj(spectrum), n_fft)[: max_lag + 1]
    acf /= acf[0]
    envelope = np.maximum.accumulate(np.abs(acf)[::-1])[::-1]
    below = np.nonzero(envelope < np.exp(-1.0))[0]
    return int(below[0]) if below.size else max_lag
