"""DEF-0015 mechanism (DEVELOPMENT): JAX differentiates |x| at NaN as the x < 0 branch
(select(x >= 0, t, -t)), so the Chua flow-map Jacobian at a NaN state is the constant
outer-region matrix and Benettin returns its unstable rate (0.30550 per time unit)."""
import sys
from pathlib import Path
import jax, jax.numpy as jnp
import numpy as np
jax.config.update("jax_enable_x64", True)
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from lpcstudy.systems import SYSTEMS, make_flow_step
print("d|x|/dx at nan:", jax.jvp(jnp.abs, (jnp.nan,), (1.0,))[1], "| maximum(1, nan) =", jnp.maximum(1.0, jnp.nan))
f = make_flow_step(SYSTEMS["chua"], SYSTEMS["chua"].params, 0.1)
J = np.asarray(jax.jacfwd(f)(jnp.array([jnp.nan] * 3)))
print("Jacobian finite at NaN state:", bool(np.isfinite(J).all()),
      "rate =", np.log(np.abs(np.linalg.eigvals(J)).max()) / 0.1)
