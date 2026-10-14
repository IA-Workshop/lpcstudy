"""M3: projected full-preset half-widths from the DEV-0 pilots P0 and P1, with the M3 factors.

factor = sqrt(n_pilot / n_full) x B factor (1.014 at 1-0.05/3, 1.007 at 95%: m3_bfactor.log)
         x kappa (draw factor for eval-draw MSE criteria, E 2 -> 4: [1/sqrt2, 1])
         x fit factor (Q-N training 900 -> 3000: [0.61, 1] logit/log_horizon, [0.74, 1] indicator;
           synthetic, WU-0006 A9 against M4).
Prints lower/upper projected hw. Compares with the v3 section 7 statements.
DEVELOPMENT (DEV-0): not a hypothesis test. Reads results.json only.
"""
import json, math, sys
P = 1 - 0.05 / 3
BF = {P: 1.014, 0.95: 1.007}
s2 = math.sqrt(0.5); s3 = math.sqrt(0.3)
# name: (path to block, interval key, level, n-factor, extra factor range)
crit = [
    ("H1b PLP slope", "H1b/PLP", "ci", .95, s2, (1, 1)),
    ("H1c PLP median ratio", "H1c/PLP", "ci", .95, s2, (1, 1)),
    ("H1d analog_seed", "H1d/rows/analog_seed", "interval", .95, s2, (1, 1)),
    ("H1a ratio rho=.01", "H1a/by_noise/0.01", "ratio_ci", .95, s3, (1, 1)),
    ("Q-N oracle logit", "Q-N/oracle/logit_w_interior", "ci", .95, s2, (0.61, 1)),
    ("Q-N oracle zero-ind", "Q-N/oracle/w_zero_indicator", "ci", .95, s2, (0.74, 1)),
    ("Q-N oracle log_hor", "Q-N/oracle/log_horizon", "ci", .95, s2, (0.61, 1)),
    ("H2a(i)", "H2a", "range_ci", P, s2, (1, 1)),
    ("H2a(ii) zero", "H2a/part_ii/zero", "ci", P, s2, (1, 1)),
    ("H2a(ii) interior", "H2a/part_ii/interior", "ci", P, s2, (1, 1)),
    ("H2b(i)", "H2b/noise", "ci", P, s3, (1, 1)),
    ("H2b(ii)", "H2b/library_change", "ci", P, s3, (1, 1)),
    ("H2c A4-A2", "H2c/A4_minus_A2", "ci", .95, s2, (s2, 1)),
    ("H2c A4-A1", "H2c/A4_minus_A1", "ci", .95, s2, (s2, 1)),
    ("H2d", "H2d", "ci", .95, s2, (s2, 1)),
    ("H2e rho=.01", "H2e/by_noise/0.01", "ci", .95, s3, (1, 1)),
    ("H2e rho=.02", "H2e/by_noise/0.02", "ci", .95, s3, (1, 1)),
    ("H3c", "H3c", "ci", P, s2, (s2, 1)),
]
def get(d, p):
    for k in p.split("/"):
        d = d[k]
    return d
for path in sys.argv[1:]:
    r = json.load(open(path))
    print("==", path.split("/runs/")[0].split("/")[-1], r["config"]["seed_id"], "B =", r["config"]["bootstrap_resamples"])
    print(f"{'criterion':22s} {'system':9s} {'hw pilot':>9s} {'factor lo-hi':>13s} {'hw full lo-hi':>17s}  note")
    for name, blk, ci, lvl, fn, (xl, xh) in crit:
        for s, sysd in r["systems"].items():
            try:
                c = get(sysd, blk)[ci]
            except KeyError:
                continue
            hw = (c[1] - c[0]) / 2
            fl, fh = fn * BF[lvl] * xl, fn * BF[lvl] * xh
            note = ""
            if name.startswith("H2a(ii)"):
                note = f"pass needs |pc| < 0.1 - hw: {0.1 - hw*fh:+.3f} .. {0.1 - hw*fl:+.3f}"
            print(f"{name:22s} {s:9s} {hw:9.4f} {fl:6.3f}-{fh:5.3f}  {hw*fl:8.4f}-{hw*fh:7.4f}  {note}")
