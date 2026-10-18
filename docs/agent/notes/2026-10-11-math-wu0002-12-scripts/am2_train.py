"""AM2 E1: does a 1-ulp perturbation of one initial weight survive minibatch-Adam training?
Synthetic Lorenz-63 delay vectors -> whitened state, the code's train_mlp (CPU, float64)."""
import sys, time
import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np
import lpcstudy.networks as nw

def lorenz_traj(n, dt=0.01, sub=4):
    def f(s):
        x, y, z = s
        return np.array([10*(y-x), x*(28-z)-y, x*y-8/3*z])
    s = np.array([1.0, 1.0, 20.0]); out = np.empty((n, 3))
    for i in range(2000*sub + n*sub):
        k1=f(s);k2=f(s+dt/2*k1);k3=f(s+dt/2*k2);k4=f(s+dt*k3)
        s = s + dt/6*(k1+2*k2+2*k3+k4)
        j = i - 2000*sub
        if j >= 0 and j % sub == 0: out[j//sub] = s
    return out

n_pairs = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 25
width = int(sys.argv[3]) if len(sys.argv) > 3 else 64
D, lag = 7, 5
traj = lorenz_traj(n_pairs + D*lag + 10)
x = (traj[:, 0] - traj[:, 0].mean()) / traj[:, 0].std()
cov = np.cov(traj.T); w_ = np.linalg.inv(np.linalg.cholesky(cov))
idx = np.arange((D-1)*lag, (D-1)*lag + n_pairs)
inputs = np.stack([x[idx - k*lag] for k in range(D)], axis=1)
targets = (traj[idx] - traj.mean(0)) @ w_.T
rng = np.random.default_rng(5)
test_in = inputs[rng.choice(n_pairs, 2000, replace=False)] + 0.01*rng.standard_normal((2000, D))

orig_init = nw.init_mlp
def make_init(mode):
    def init(sizes, key):
        p = orig_init(sizes, key)
        if mode == "ulp":
            w0, b0 = p[0]
            w0 = w0.at[0, 0].set(jnp.nextafter(w0[0, 0], jnp.inf))
            p[0] = (w0, b0)
        return p
    return init

pert_in = np.nextafter(inputs, np.where(rng.random(inputs.shape) < 0.5, -np.inf, np.inf))
import optax
orig_adam = optax.adam
def ulp_grad():
    def init_fn(params):
        return optax.EmptyState()
    def update_fn(updates, state, params=None):
        return jax.tree_util.tree_map(lambda g: g * (1.0 + PERT[0] * jnp.sign(jnp.sin(g * 1e6 + 0.3))), updates), state
    return optax.GradientTransformation(init_fn, update_fn)
class OptaxShim:
    def __getattr__(self, k):
        return getattr(optax, k)
    def adam(self, sched):
        return optax.chain(ulp_grad(), orig_adam(sched)) if MODE[0] == "grad" else orig_adam(sched)
MODE = ["none"]
PERT = [float(sys.argv[4]) if len(sys.argv) > 4 else 2.0**-52]
nw.optax = OptaxShim()
def run(mode, seed):
    MODE[0] = mode
    nw.init_mlp = make_init(mode)
    t = time.time()
    data = pert_in if mode == "data" else inputs
    net = nw.train_mlp(data, targets, width, epochs, seed, input_noise=0.01)
    pred = np.asarray(net.predict(jnp.asarray(test_in)))
    flat = np.concatenate([np.ravel(np.asarray(a)) for wb in net.params for a in wb])
    return net.val_loss, pred, flat, time.time() - t

base = run("none", 100)
ulp = run("ulp", 100)
other = run("none", 101)
err_rms = np.sqrt(np.mean(np.sum((base[1] - ((test_in*0)[:, :3])) ** 2, 1)))  # placeholder not used
grad = run("grad", 100)
for name, r in [("ulp", ulp), ("grad", grad), ("seed+1", other)]:
    dw = np.max(np.abs(r[2] - base[2])) / np.max(np.abs(base[2]))
    dpred = np.sqrt(np.mean(np.sum((r[1] - base[1])**2, 1)))
    print(f"{name:7s} epochs={epochs} width={width} n={n_pairs}: rel val_loss diff {abs(r[0]/base[0]-1):.3e}; "
          f"max|dW|/max|W| {dw:.3e}; rms pred diff {dpred:.3e} (sqrt val_loss {np.sqrt(base[0]):.3e}); t={r[3]:.1f}s")
