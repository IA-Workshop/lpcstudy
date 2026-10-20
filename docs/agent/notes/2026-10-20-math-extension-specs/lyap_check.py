"""Same-host check of the registry Rossler exponent against the pilot
reference (0.07193978510879935) and against the permuted S3 spec at the same
Benettin settings; and the code's cache value for S1 at max_dt 0.01."""

from lpcstudy.systems import SYSTEMS, lyapunov_guarded

from ext_common import CANDIDATES

ros = SYSTEMS["rossler"]
lam_r, mx = lyapunov_guarded(ros, 20 * ros.max_dt, 100_000, 5_000)
print(f"registry rossler on this host: {lam_r!r} (max|x| {mx:.4f}); pilot reference 0.07193978510879935; equal bits: {lam_r == 0.07193978510879935}")
s3 = CANDIDATES["S3"]()
lam_3, mz = lyapunov_guarded(s3, 20 * s3.max_dt, 100_000, 5_000)
print(f"permuted (z, x, y) rossler: {lam_3!r} (max|z| {mz:.4f}); relative difference {lam_3/lam_r-1:+.3%}")
s1 = CANDIDATES["S1"]()
lam_1, m1 = lyapunov_guarded(s1, 20 * s1.max_dt, 100_000, 5_000)
print(f"S1 at max_dt {s1.max_dt}: cache value {lam_1!r} (max|x| {m1:.3f}); interval {20*s1.max_dt}, run {100_000*20*s1.max_dt:.0f} time units")
