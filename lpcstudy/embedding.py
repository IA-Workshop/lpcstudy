"""Delay embedding, delay selection and autocorrelation time."""

from __future__ import annotations

import numpy as np


def delay_vectors(series: np.ndarray, indices: np.ndarray, delay: int,
                  dim: int) -> np.ndarray:
    """Build delay vectors ``X_t = (x_t, x_{t-tau}, ..., x_{t-(D-1)tau})``.

    Parameters
    ----------
    series : np.ndarray
        Scalar series of shape ``(T,)`` (or ``(T, ...)``; leading axis is time).
    indices : np.ndarray
        Time indices ``t`` (each must satisfy ``t >= (D-1) tau``).
    delay : int
        Delay ``tau_d`` in observation steps.
    dim : int
        Embedding dimension ``D``.

    Returns
    -------
    np.ndarray
        Array of shape ``(len(indices), D, ...)``.

    Raises
    ------
    ValueError
        If any index lacks the required history.
    """
    indices = np.asarray(indices)
    if np.any(indices < (dim - 1) * delay):
        raise ValueError("delay vector requested without full history")
    lags = np.arange(dim) * delay
    return series[indices[:, None] - lags[None, :]]


def mutual_information(series: np.ndarray, lag: int, n_bins: int = 32) -> float:
    """Histogram estimate of ``I(x_t; x_{t+lag})`` in nats.

    Parameters
    ----------
    series : np.ndarray
        Scalar series.
    lag : int
        Lag in steps (``>= 1``).
    n_bins : int, optional
        Number of equiprobable bins per axis.

    Returns
    -------
    float
        Mutual information estimate.
    """
    edges = np.quantile(series, np.linspace(0.0, 1.0, n_bins + 1))
    edges[-1] += 1e-12
    codes = np.clip(np.searchsorted(edges, series, side="right") - 1, 0, n_bins - 1)
    first, second = codes[:-lag], codes[lag:]
    joint = np.zeros((n_bins, n_bins))
    np.add.at(joint, (first, second), 1.0)
    joint /= joint.sum()
    marg_a = joint.sum(axis=1, keepdims=True)
    marg_b = joint.sum(axis=0, keepdims=True)
    mask = joint > 0
    return float(np.sum(joint[mask] * np.log(joint[mask] / (marg_a @ marg_b)[mask])))


def select_delay(series: np.ndarray, max_lag: int) -> int:
    """Delay at the first local minimum of the (3-point smoothed) average mutual information.

    Parameters
    ----------
    series : np.ndarray
        Scalar series.
    max_lag : int
        Largest lag examined.

    Returns
    -------
    int
        Selected delay (falls back to the global minimum over ``1..max_lag``).
    """
    raw = np.array([mutual_information(series, lag) for lag in range(1, max_lag + 1)])
    # Three-point moving average suppresses spurious minima from histogram noise.
    values = np.convolve(np.pad(raw, 1, mode="edge"), np.ones(3) / 3.0, mode="valid")
    for k in range(1, len(values) - 1):
        if values[k] < values[k - 1] and values[k] <= values[k + 1]:
            return k + 1
    return int(np.argmin(values)) + 1


def autocorrelation_time(series: np.ndarray, max_lag: int) -> int:
    """Lag at which the autocorrelation envelope falls below ``1/e``.

    The envelope at lag ``k`` is ``max_{j >= k} |ACF(j)|`` so that oscillatory
    (phase-coherent) signals are not declared decorrelated at their first zero.

    Parameters
    ----------
    series : np.ndarray
        Scalar series.
    max_lag : int
        Largest lag examined; returned if the envelope never falls below ``1/e``.

    Returns
    -------
    int
        Autocorrelation time in steps.
    """
    centered = series - series.mean()
    n_fft = 1 << int(np.ceil(np.log2(2 * len(centered))))
    spectrum = np.fft.rfft(centered, n_fft)
    acf = np.fft.irfft(spectrum * np.conj(spectrum), n_fft)[: max_lag + 1]
    acf /= acf[0]
    envelope = np.maximum.accumulate(np.abs(acf)[::-1])[::-1]
    below = np.nonzero(envelope < np.exp(-1.0))[0]
    return int(below[0]) if below.size else max_lag
