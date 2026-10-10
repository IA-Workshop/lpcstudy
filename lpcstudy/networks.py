"""Small multilayer perceptrons: the state estimator ``psi`` and the error predictor.

Both networks are plain MLPs trained with Adam on mean-squared error. The state
estimator is trained with fresh observation noise drawn for every minibatch,
so it approximates the posterior-mean estimator of the latent state under the
attractor prior at the training noise level.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np
import optax

Params = list[tuple[jnp.ndarray, jnp.ndarray]]


def init_mlp(sizes: list[int], key: jax.Array) -> Params:
    """Initialize MLP weights (He-uniform) and zero biases.

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
        weight = jax.random.uniform(sub, (fan_in, fan_out), minval=-bound, maxval=bound)
        params.append((weight, jnp.zeros(fan_out)))
    return params


def apply_mlp(params: Params, inputs: jnp.ndarray) -> jnp.ndarray:
    """Forward pass with GELU hidden activations and a linear output.

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
    """A trained MLP with its input/output standardization.

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


def train_mlp(inputs: np.ndarray, targets: np.ndarray, width: int, epochs: int,
              seed: int, input_noise: float = 0.0, batch_size: int = 256,
              learning_rate: float = 2e-3, val_fraction: float = 0.1
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
    seed : int
        Seed for initialization, shuffling and input noise.
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
    rng = np.random.default_rng(seed)
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

    params = init_mlp([inputs.shape[1], width, width, targets.shape[1]],
                      jax.random.PRNGKey(seed))
    steps_per_epoch = max(1, len(train_idx) // batch_size)
    schedule = optax.cosine_decay_schedule(learning_rate, epochs * steps_per_epoch,
                                           alpha=0.01)
    optimizer = optax.adam(schedule)
    opt_state = optimizer.init(params)

    def loss_fn(p: Params, xb: jnp.ndarray, yb: jnp.ndarray) -> jnp.ndarray:
        return jnp.mean((apply_mlp(p, xb) - yb) ** 2)

    @jax.jit
    def run_epoch(p: Params, state: optax.OptState, key: jax.Array
                  ) -> tuple[Params, optax.OptState]:
        perm_key, noise_key = jax.random.split(key)
        perm = jax.random.permutation(perm_key, x_train.shape[0])
        perm = perm[: steps_per_epoch * batch_size].reshape(steps_per_epoch, batch_size)
        noise = jax.random.normal(noise_key, (steps_per_epoch, batch_size,
                                              x_train.shape[1])) * noise_scaled

        def step(carry, batch):
            p_c, s_c = carry
            idx, eps = batch
            grads = jax.grad(loss_fn)(p_c, x_train[idx] + eps, y_train[idx])
            updates, s_c = optimizer.update(grads, s_c, p_c)
            return (optax.apply_updates(p_c, updates), s_c), None

        (p, state), _ = jax.lax.scan(step, (p, state), (perm, noise))
        return p, state

    key = jax.random.PRNGKey(seed + 1)
    for _ in range(epochs):
        key, sub = jax.random.split(key)
        params, opt_state = run_epoch(params, opt_state, sub)

    net = TrainedNetwork(params=params, in_mean=in_mean, in_scale=in_scale,
                         out_mean=out_mean, out_scale=out_scale, val_loss=np.nan,
                         width=width)
    val_inputs = inputs[val_idx] + input_noise * rng.standard_normal(
        inputs[val_idx].shape)
    residual = np.asarray(net.predict(jnp.asarray(val_inputs))) - targets[val_idx]
    net.val_loss = float(np.mean(np.sum(residual**2, axis=1)))
    return net


def train_estimator(inputs: np.ndarray, targets: np.ndarray, noise: float,
                    widths: tuple[int, ...], epochs: int, seed: int
                    ) -> tuple[TrainedNetwork, dict[int, float]]:
    """Train ``psi`` at several widths and apply the capacity rule.

    The smallest width whose validation error is within 5% of the best is kept.

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
    seed : int
        Seed.

    Returns
    -------
    tuple[TrainedNetwork, dict[int, float]]
        Selected network and validation loss per width.
    """
    nets = {w: train_mlp(inputs, targets, w, epochs, seed + w, input_noise=noise)
            for w in widths}
    losses = {w: net.val_loss for w, net in nets.items()}
    best = min(losses.values())
    chosen = min(w for w, loss in losses.items() if loss <= 1.05 * best)
    return nets[chosen], losses


def estimator_jacobian_norm(net: TrainedNetwork) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Frobenius norm of ``d psi / d X`` as a vectorized function.

    Parameters
    ----------
    net : TrainedNetwork
        Trained state estimator.

    Returns
    -------
    Callable[[jnp.ndarray], jnp.ndarray]
        Maps inputs ``(n, D)`` to norms ``(n,)``.
    """
    jac = jax.vmap(jax.jacfwd(lambda x: net.predict(x)))
    return jax.jit(lambda xs: jnp.sqrt(jnp.sum(jac(xs) ** 2, axis=(1, 2))))
