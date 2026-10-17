"""Q2: rel of the H1a interval leaves of the kernel pair under s = max(|lo|, |hi|) of the reference
interval (B1 item 4 (a)) and unscaled |d|/|ref|. DEVELOPMENT (DEV-0): read-only."""
import json, sys
A, B = (json.load(open(p))["systems"]["lorenz63"]["H1a"]["by_noise"]["0.01"] for p in sys.argv[1:3])
for name, ci in (("ratio", "ratio_ci"), ("fitted_inverse_dim", "ci_inverse_dim")):
    s = max(abs(A[ci][0]), abs(A[ci][1]))
    for label, a, b in ((name, A[name], B[name]), (f"{ci}[0]", A[ci][0], B[ci][0]), (f"{ci}[1]", A[ci][1], B[ci][1])):
        d = abs(a - b)
        print(f"{label:20s} |d| {d:.4e}  s {s:.6f}  |d|/s {d / s:.4e}  |d|/|ref| {d / abs(a):.4e}")
a, b = A["floor_rms"], B["floor_rms"]
print(f"{'floor_rms':20s} |d| {abs(a - b):.4e}  class (g) |d|/|ref| {abs(a - b) / a:.4e}")
