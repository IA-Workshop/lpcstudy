"""M5: worst-case finite-M bias bound F1 of the H2a(i) median range at M = 200, 300, 399, against the
pilot half-width and the projected full half-width (factor 0.717 from m3_projection).

F1(M) = (3/sqrt(pi)) * h(M) / z_0.975 with h(M) = h(200) * sqrt(200 / M) (V4 median half-width;
WU-0008 M3); M needed for F1 < 0.1 hw_full. L^2/M = 100/M > 0.25 holds for M <= 399 (H-M1, H-M2).
DEVELOPMENT (DEV-0): not a hypothesis test. Reads results.json only.
"""
import json, math, sys
z = 1.959963984540054
for path in sys.argv[1:]:
    tag = "P0" if "p0-" in path else "P1"
    r = json.load(open(path))
    for s, sd in r["systems"].items():
        h200 = sd["validation"]["convergence"]["200"]["median_half_width"]
        h50 = sd["validation"]["convergence"]["50"]["median_half_width"]
        h800 = sd["validation"]["convergence"]["800"]["median_half_width"]
        ci = sd["H2a"]["range_ci"]; hw = (ci[1] - ci[0]) / 2; hwf = hw * 0.717
        line = [f"{tag} {s:9s} h50/h200/h800 = {h50:.4f}/{h200:.4f}/{h800:.4f} "
                f"(obs. order in M: {math.log(h50/h200)/math.log(4):.2f}, {math.log(h200/h800)/math.log(4):.2f}); "
                f"hw pilot {hw:.4f}, full {hwf:.4f}"]
        for M in (200, 300, 399):
            f1 = 3 / math.sqrt(math.pi) * h200 * math.sqrt(200 / M) / z
            line.append(f"   M={M}: F1 = {f1:.4f} = {f1/hw:.2f} hw_pilot = {f1/hwf:.2f} hw_full; L2/M = {100/M:.4f}")
        f1_200 = 3 / math.sqrt(math.pi) * h200 / z
        mneed = 200 * (f1_200 / (0.1 * hwf)) ** 2
        line.append(f"   M needed for F1 < 0.1 hw_full: {mneed:,.0f}")
        print("\n".join(line))
