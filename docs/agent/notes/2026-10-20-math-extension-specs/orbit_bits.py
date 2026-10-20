"""Does the permuted (z, x, y) Rossler orbit equal the registry orbit bitwise?
5000 steps at the registry's Benettin interval 0.8 from the same physical
point; and the per-step tangent growth of both (DEVELOPMENT)."""

import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory

from ext_common import CANDIDATES

ros, s3 = SYSTEMS["rossler"], CANDIDATES["S3"]()
a = simulate_trajectory(make_flow_step(ros, ros.params, 0.8), jnp.asarray((1.0, 1.0, 0.0)), 5000)
b = simulate_trajectory(make_flow_step(s3, s3.params, 0.8), jnp.asarray((0.0, 1.0, 1.0)), 5000)
b_perm = b[:, [1, 2, 0]]  # back to (x, y, z)
eq = np.all(a == b_perm, axis=1)
first = int(np.argmin(eq)) if not eq.all() else -1
print(f"bitwise equal rows: {int(eq.sum())} of {len(eq)}; first differing step {first}")
if first >= 0:
    print(f"  at that step: registry {a[first]!r}, permuted {b_perm[first]!r}, abs diff {np.abs(a[first]-b_perm[first])}")
    # one-step check from the same state
    sa = jnp.asarray(a[first - 1])
    fa = make_flow_step(ros, ros.params, 0.8)
    fb = make_flow_step(s3, s3.params, 0.8)
    one_a = np.asarray(fa(sa)); one_b = np.asarray(fb(jnp.asarray(a[first - 1][[2, 0, 1]])))[[1, 2, 0]]
    print(f"  one step from the same state: diff {one_a - one_b}")
