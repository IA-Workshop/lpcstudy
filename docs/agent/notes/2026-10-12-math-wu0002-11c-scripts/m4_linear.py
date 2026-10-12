"""M4: G2 and G3 constants on the linear spec f(s) = diag(a) s (DEVELOPMENT, deterministic).

interval = 0.1, max_dt = 0.03 -> substeps = ceil(0.1/0.03) = 4, dt = 0.025.
Reference: RK4 amplification R(z) = 1 + z + z^2/2 + z^3/6 + z^4/24, in exact rationals
(fractions) to rule out reference rounding; then evaluation of the production code path.
"""
import dataclasses, math, struct, sys
from fractions import Fraction as Fr
import numpy as np
import jax.numpy as jnp
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[4]))
from lpcstudy.systems import SystemSpec, make_flow_step, simulate_trajectory
from m2_bitwise import old, new

INTERVAL, MAX_DT = 0.1, 0.03
sub = max(1, math.ceil(INTERVAL / MAX_DT)); dt = INTERVAL / sub
print("substeps", sub, "dt", repr(dt))

def R(z):
    return 1 + z + z * z / 2 + z ** 3 / 6 + z ** 4 / 24

# ---- G2: a = (0.5, -1, -2), s0 = (1, 1, 1), B = 3
a1 = Fr(dt) * Fr(0.5)  # exact rational of the float dt times 0.5
r = R(a1)
n = 0; val = Fr(1)
while val <= 3:
    n += 1; val = val * r ** sub
prev = val / r ** sub
print(f"G2: first failing state index n = {n}; x_(n-1) = {float(prev):.12f}, x_n = {float(val):.12f}; "
      f"relative margins below {float((3 - prev) / 3):.3e}, above {float((val - 3) / 3):.3e}")
lin = lambda a: (lambda s, p: jnp.asarray(a) * s)
spec2 = SystemSpec(name="lin2", field_fn=lin((0.5, -1.0, -2.0)), params={}, dim=3,
                   observed_index=0, initial_state=(1.0, 1.0, 1.0), max_dt=MAX_DT)
traj = simulate_trajectory(make_flow_step(spec2, {}, INTERVAL), jnp.asarray(spec2.initial_state), 40)
k = int(np.argmax(np.abs(traj[:, 0]) > 3))
print(f"  production simulate_trajectory: first |x|>3 at row {k}; rel error of x_n vs exact "
      f"{abs(traj[n,0] - float(val)) / float(val):.2e}")
for burn, nst in ((50, 100), (10, 100)):
    lam, mx, f = new(spec2, INTERVAL, nst, burn, 3.0, True)
    lam2, mx2, f2 = new(spec2, INTERVAL, nst, burn, 3.0, False)
    print(f"  scratch guarded Benettin burn={burn}: first_fail (burn-in carried) {f}; (plan placement) {f2}")

# ---- G3: a = (-0.1, -0.5, -1.0), s0 = (1, 1, 1), n_steps = 1000, burn = 10
spec3 = dataclasses.replace(spec2, name="lin3", field_fn=lin((-0.1, -0.5, -1.0)))
z = Fr(dt) * Fr(-0.1)
exact = sub * math.log1p(float(R(z) - 1)) / INTERVAL   # log1p of the exact rational tail
# reference rounding check with mpmath-free high precision: series of log(R(z)) in Fractions
lnR = Fr(0); w = R(z) - 1
for j in range(1, 30):
    lnR += (-1) ** (j + 1) * w ** j / j
exact_hp = float(sub * lnR / Fr(INTERVAL))
print(f"G3: lambda_ref (log1p) = {exact!r}; high-precision = {exact_hp!r}; rel diff {abs(exact-exact_hp)/abs(exact_hp):.1e}")
for burn in (10, 0):
    lam_o = old(spec3, INTERVAL, 1000, burn)
    lam_n, mx, f = new(spec3, INTERVAL, 1000, burn, 3.0, True)
    lam_p, mxp, fp = new(spec3, INTERVAL, 1000, burn, 3.0, False)
    print(f"  burn={burn}: estimate_lyapunov {lam_o!r}, rel err {abs(lam_o-exact_hp)/abs(exact_hp):.2e}; "
          f"guarded bitwise equal {struct.pack('<d',lam_o)==struct.pack('<d',lam_n)}; "
          f"orbit max (burn-in carried) {mx!r}; (plan placement) {mxp!r}; "
          f"plan formula R^(burn*sub) = {float(R(z)**(burn*sub))!r}")
