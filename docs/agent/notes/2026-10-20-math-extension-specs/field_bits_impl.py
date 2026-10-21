"""Why the cached lambda of S5 and S6 differs by about 1e-15 relative between
my scripts and the implementation (S4 bitwise): compare the code's field and
my field, and their jax.jacfwd Jacobians, bitwise on 1000 orbit states
(PYTHONPATH = wu/ext-impl2; DEVELOPMENT)."""

import sys
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ext_common  # noqa: E402

for name, mine in (("hyper_jha", ext_common.hyper_jha_field), ("lorenz96_4", ext_common.lorenz96_field), ("hindmarsh_rose", ext_common.hindmarsh_rose_field)):
    spec = SYSTEMS[name]
    step = make_flow_step(spec, spec.params, 20 * spec.max_dt)
    orbit = simulate_trajectory(step, jnp.asarray(spec.initial_state), 6000)[5000:]
    f_code = np.asarray(jax.vmap(lambda s: spec.field_fn(s, spec.params))(jnp.asarray(orbit)))
    f_mine = np.asarray(jax.vmap(lambda s: mine(s, spec.params))(jnp.asarray(orbit)))
    j_code = np.asarray(jax.vmap(jax.jacfwd(lambda s: spec.field_fn(s, spec.params)))(jnp.asarray(orbit)))
    j_mine = np.asarray(jax.vmap(jax.jacfwd(lambda s: mine(s, spec.params)))(jnp.asarray(orbit)))
    # one RK4 flow step from the same states, both specs
    my_spec = ext_common.CANDIDATES[{"hyper_jha": "S5", "lorenz96_4": "S6", "hindmarsh_rose": "S4"}[name]]()
    s_code = np.asarray(jax.vmap(step)(jnp.asarray(orbit)))
    s_mine = np.asarray(jax.vmap(make_flow_step(my_spec, my_spec.params, 20 * spec.max_dt))(jnp.asarray(orbit)))
    print(f"{name}: field bitwise-equal rows {int(np.all(f_code == f_mine, axis=1).sum())}/1000 (max diff {np.max(np.abs(f_code-f_mine)):.2e}); "
          f"jacfwd bitwise-equal {int(np.all(j_code == j_mine, axis=(1,2)).sum())}/1000 (max diff {np.max(np.abs(j_code-j_mine)):.2e}); "
          f"one flow step bitwise-equal {int(np.all(s_code == s_mine, axis=1).sum())}/1000 (max diff {np.max(np.abs(s_code-s_mine)):.2e})")
