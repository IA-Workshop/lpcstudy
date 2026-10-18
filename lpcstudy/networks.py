"""Small neural networks (MLPs): the state-estimator guess and the allocator.

An MLP (multilayer perceptron) is a simple feed-forward neural network. The
physics-based forecaster (PLP) must estimate the hidden state of the system
from a noisy delay vector. ``estimation.py`` does this in two stages, and the
first stage is an MLP built and trained here: it predicts a starting guess for
the state, and the model-based refinement then polishes that guess.
``allocation.py`` reuses ``train_mlp`` for its learned error predictor.

The networks are trained with the Adam optimizer on mean-squared error. For
the state estimator, fresh observation noise is drawn for every minibatch, so
the network approximates the posterior-mean estimator of the state (the
average of the states that could have produced the observation) under the
attractor prior, at the training noise level. ``train_estimator`` trains
several widths and keeps the smallest one that is nearly as good as the best.
The weights are fingerprinted with the digest from ``provenance.py``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np
import optax

from .provenance import array_digest

Params = list[tuple[jnp.ndarray, jnp.ndarray]]


def init_mlp(sizes: list[int], key: jax.Array) -> Params:
    """Initialize MLP weights (He-uniform) and zero biases.

    He-uniform draws each weight uniformly in ``[-b, b]`` with
    ``b = sqrt(6 / fan_in)``, a standard choice that keeps the signal size
    steady from layer to layer.

    Parameters
    ----------
    sizes : list[int]
        Layer widths including input and output.
    key : jax.Array
        PRNG key.

    Returns
    -------
    Params
        List of ``(weight, bias)`` pairs.
    """
    params: Params = []
    for fan_in, fan_out in zip(sizes[:-1], sizes[1:]):
        key, sub = jax.random.split(key)
        bound = jnp.sqrt(6.0 / fan_in)
        weight = jax.random.uniform(
            sub, (fan_in, fan_out), minval=-bound, maxval=bound
        )
        params.append((weight, jnp.zeros(fan_out)))
    return params


def apply_mlp(params: Params, inputs: jnp.ndarray) -> jnp.ndarray:
    """Run a forward pass with GELU hidden activations and a linear output.

    GELU is a smooth activation function (a softened version of ReLU).

    Parameters
    ----------
    params : Params
        Network parameters.
    inputs : jnp.ndarray
        Inputs of shape ``(..., d_in)``.

    Returns
    -------
    jnp.ndarray
        Outputs of shape ``(..., d_out)``.
    """
    hidden = inputs
    for weight, bias in params[:-1]:
        hidden = jax.nn.gelu(hidden @ weight + bias)
    weight, bias = params[-1]
    return hidden @ weight + bias


@dataclass
class TrainedNetwork:
    """A trained MLP together with its input and output standardization.

    Standardization means subtracting a mean and dividing by a scale so that
    the network sees values of order one. ``predict`` undoes it, so callers
    work in the original units.

    Attributes
    ----------
    params : Params
        Network parameters.
    in_mean, in_scale : np.ndarray
        Input standardization.
    out_mean, out_scale : np.ndarray
        Output de-standardization.
    val_loss : float
        Validation mean-squared error in original output units (per sample,
        summed over output dimensions).
    width : int
        Hidden width.
    """

    params: Params
    in_mean: np.ndarray
    in_scale: np.ndarray
    out_mean: np.ndarray
    out_scale: np.ndarray
    val_loss: float
    width: int

    def weights_digest(self) -> str:
        """Return the SHA-256 digest of the weights, as a provenance record.

        The arrays are concatenated in the order W1, b1, W2, b2, ... (each
        flattened in C order, as float64) and hashed as
        :func:`lpcstudy.provenance.array_digest` does. So the digest covers
        the parameters ``params`` only; the standardization arrays (``in_mean``
        and the others) are functions of the training data and are not
        included. It is provenance (WU-0003.7a, O7): a difference between two
        runs separates "same trajectory, other weights" from "same weights".

        Returns
        -------
        str
            64 lowercase hexadecimal characters.

        Raises
        ------
        TypeError
            If any parameter array is not float64. Nothing is converted
            silently (PRIME.4): a float32 parameter next to float64 ones would
            otherwise be promoted by the concatenation.
        """
        arrays = [np.asarray(a) for layer in self.params for a in layer]
        bad = sorted({str(a.dtype) for a in arrays if a.dtype != np.float64})
        if bad:
            raise TypeError(
                f"weights_digest needs float64 parameters, got {', '.join(bad)}"
            )
        return array_digest(np.concatenate([a.ravel() for a in arrays]))

    def predict(self, inputs: jnp.ndarray) -> jnp.ndarray:
        """Evaluate the network in original units.

        Parameters
        ----------
        inputs : jnp.ndarray
            Inputs of shape ``(..., d_in)``.

        Returns
        -------
        jnp.ndarray
            Predictions of shape ``(..., d_out)``.
        """
        scaled = (inputs - self.in_mean) / self.in_scale
        return apply_mlp(self.params, scaled) * self.out_scale + self.out_mean


def train_mlp(
    inputs: np.ndarray,
    targets: np.ndarray,
    width: int,
    epochs: int,
    rng: np.random.Generator,
    input_noise: float = 0.0,
    batch_size: int = 256,
    learning_rate: float = 2e-3,
    val_fraction: float = 0.1,
) -> TrainedNetwork:
    """Train a two-hidden-layer MLP by minibatch Adam on mean-squared error.

    Parameters
    ----------
    inputs : np.ndarray
        Clean inputs, shape ``(n, d_in)``.
    targets : np.ndarray
        Targets, shape ``(n, d_out)``.
    width : int
        Hidden width.
    epochs : int
        Passes over the training data.
    rng : np.random.Generator
        The only source of randomness, consumed in a fixed order
        (WU-0002.14, M7): first the 32-bit seeds of the two JAX keys
        (initialization, then the epoch stream), each
        ``int(rng.integers(0, 2**32))``; then the validation permutation;
        then, after training, the validation input noise. The keys come first
        so that they do not depend on ``len(inputs)`` through the amount of
        stream that ``Generator.permutation`` consumes. The caller builds the
        generator from ``make_rng`` labels. Needs owner review before freeze.
    input_noise : float, optional
        Standard deviation of Gaussian noise added to inputs, redrawn for
        every minibatch (and once for the validation set).
    batch_size : int, optional
        Minibatch size.
    learning_rate : float, optional
        Peak learning rate (cosine decay to 1% of it).
    val_fraction : float, optional
        Fraction of samples held out for validation.

    Returns
    -------
    TrainedNetwork
        Trained network and its validation loss.
    """
    # M7: 32-bit JAX keys, drawn first.
    init_seed = int(rng.integers(0, 2**32))
    epoch_seed = int(rng.integers(0, 2**32))
    n_samples = len(inputs)
    order = rng.permutation(n_samples)
    n_val = max(1, int(val_fraction * n_samples))
    val_idx, train_idx = order[:n_val], order[n_val:]
    in_mean = inputs[train_idx].mean(axis=0)
    in_scale = np.sqrt(inputs[train_idx].var(axis=0) + input_noise**2)
    out_mean = targets[train_idx].mean(axis=0)
    out_scale = targets[train_idx].std(axis=0) + 1e-12
    x_train = jnp.asarray((inputs[train_idx] - in_mean) / in_scale)
    y_train = jnp.asarray((targets[train_idx] - out_mean) / out_scale)
    noise_scaled = jnp.asarray(input_noise / in_scale)

    params = init_mlp(
        [inputs.shape[1], width, width, targets.shape[1]],
        jax.random.PRNGKey(init_seed),
    )
    steps_per_epoch = max(1, len(train_idx) // batch_size)
    schedule = optax.cosine_decay_schedule(
        learning_rate, epochs * steps_per_epoch, alpha=0.01
    )
    optimizer = optax.adam(schedule)
    opt_state = optimizer.init(params)

    def loss_fn(p: Params, xb: jnp.ndarray, yb: jnp.ndarray) -> jnp.ndarray:
        return jnp.mean((apply_mlp(p, xb) - yb) ** 2)

    @jax.jit
    def run_epoch(
        p: Params, state: optax.OptState, key: jax.Array
    ) -> tuple[Params, optax.OptState]:
        perm_key, noise_key = jax.random.split(key)
        perm = jax.random.permutation(perm_key, x_train.shape[0])
        perm = perm[: steps_per_epoch * batch_size].reshape(
            steps_per_epoch, batch_size
        )
        noise = (
            jax.random.normal(
                noise_key, (steps_per_epoch, batch_size, x_train.shape[1])
            )
            * noise_scaled
        )

        def step(carry, batch):
            p_c, s_c = carry
            idx, eps = batch
            grads = jax.grad(loss_fn)(p_c, x_train[idx] + eps, y_train[idx])
            updates, s_c = optimizer.update(grads, s_c, p_c)
            return (optax.apply_updates(p_c, updates), s_c), None

        (p, state), _ = jax.lax.scan(step, (p, state), (perm, noise))
        return p, state

    key = jax.random.PRNGKey(epoch_seed)
    for _ in range(epochs):
        key, sub = jax.random.split(key)
        params, opt_state = run_epoch(params, opt_state, sub)

    net = TrainedNetwork(
        params=params,
        in_mean=in_mean,
        in_scale=in_scale,
        out_mean=out_mean,
        out_scale=out_scale,
        val_loss=np.nan,
        width=width,
    )
    val_inputs = inputs[val_idx] + input_noise * rng.standard_normal(
        inputs[val_idx].shape
    )
    residual = (
        np.asarray(net.predict(jnp.asarray(val_inputs))) - targets[val_idx]
    )
    net.val_loss = float(np.mean(np.sum(residual**2, axis=1)))
    return net


def train_estimator(
    inputs: np.ndarray,
    targets: np.ndarray,
    noise: float,
    widths: tuple[int, ...],
    epochs: int,
    stream: Callable[[int], np.random.Generator],
) -> tuple[TrainedNetwork, dict[int, float]]:
    """Train the state estimator ``psi`` at several widths and pick one.

    The capacity rule keeps the smallest width whose validation error is
    within 5% of the best, which avoids paying for a larger network that is
    not meaningfully better.

    Parameters
    ----------
    inputs : np.ndarray
        Noise-free delay vectors, shape ``(n, D)``.
    targets : np.ndarray
        Whitened latent states, shape ``(n, m)``.
    noise : float
        Observation-noise level (fraction of ``sigma_x``) used in training.
    widths : tuple[int, ...]
        Candidate hidden widths.
    epochs : int
        Training epochs.
    stream : Callable[[int], np.random.Generator]
        Maps a width to a *fresh* generator for that width's network (the
        caller builds it from ``make_rng`` labels that include the width), so
        the widths are trained from independent streams that do not depend on
        which other widths are trained. Needs owner review before freeze.

    Returns
    -------
    tuple[TrainedNetwork, dict[int, float]]
        Selected network and validation loss per width.
    """
    nets = {
        w: train_mlp(inputs, targets, w, epochs, stream(w), input_noise=noise)
        for w in widths
    }
    losses = {w: net.val_loss for w, net in nets.items()}
    best = min(losses.values())
    chosen = min(w for w, loss in losses.items() if loss <= 1.05 * best)
    return nets[chosen], losses
