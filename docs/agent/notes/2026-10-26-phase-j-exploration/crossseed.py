import json, sys
runs = [json.load(open(p)) for p in sys.argv[1:]]
seeds = [r["run"]["seed_id"] for r in runs]
AB = {"undetermined": "u", "negligible": "n", "small": "s", "substantial": "S", "lowers": "L",
      "needed, size not determined": "d", "no interaction gain; the pair model fits worse": "w",
      "interaction gain detected": "D", "no interaction gain detected": "-"}
def code(row):
    return AB.get(row["reading"], "?") + ("*" if row.get("reason") == "n_eff < 50" else "")
cols = [(h, k) for h in ("8", "30", "120") for k in ("oracle", "deployable")]
print("Readings side by side, " + " / ".join(seeds) + " (no pooling, no new statistic). Codes: S substantial, d needed (size not det.), s small, n negligible, L lowers, u undetermined (u* n_eff<50); B: D detected, - none, w pair fits worse. 'agree' = identical code on every seed in that cell.")
print("| sys | row | " + " | ".join(f"{int(h)/30:.2f} LT {k[:3]}" for h, k in cols) + " | cells agreeing |")
print("|---|---|" + "---|" * (len(cols) + 1))
def emit(sys_, label, getter):
    cells, agree, total = [], 0, 0
    for h, k in cols:
        try:
            codes = [code(getter(r["systems"][sys_], h, k)) for r in runs]
        except KeyError:
            cells.append(""); continue
        total += 1
        same = len(set(codes)) == 1
        agree += same
        cells.append("/".join(codes) + (" =" if same else ""))
    print(f"| {sys_} | {label} | " + " | ".join(cells) + f" | {agree}/{total} |")
for s in runs[0]["systems"]:
    for x in "ROIN":
        emit(s, f"A drop-{x} (MSE)", lambda res, h, k, x=x: res["allocation"][h][k]["drop_one"][x]["mse_ratio"])
    for pr in ("RI", "OI"):
        emit(s, f"B {pr} (logit)", lambda res, h, k, pr=pr: res["interactions"][h][k]["logit"]["pairs"][pr])
    for rung, lab in (("none", "constant"), ("separation", "separation"), ("RO", "RO"), ("X+F", "X+F")):
        emit(s, f"D {lab} vs F", lambda res, h, k, rung=rung: res["allocation"][h][k]["ladder"]["vs_full"][rung]["mse_ratio"])
print("\nHorizon decision (one target; columns oracle / deployable)")
print("| sys | row | oracle | deployable |"); print("|---|---|---|---|")
for s in runs[0]["systems"]:
    for x in "ROIN":
        cells = []
        for k in ("oracle", "deployable"):
            codes = [code(r["systems"][s]["horizon"][k]["drop_one"][x]["pinball_ratio"]) for r in runs]
            cells.append("/".join(codes) + (" =" if len(set(codes)) == 1 else ""))
        print(f"| {s} | drop-{x} (pinball) | " + " | ".join(cells) + " |")
    for pr in ("RI", "OI", "RO"):
        cells = []
        for k in ("oracle", "deployable"):
            codes = [code(r["systems"][s]["horizon"][k]["interactions"]["pairs"][pr]) for r in runs]
            cells.append("/".join(codes) + (" =" if len(set(codes)) == 1 else ""))
        print(f"| {s} | B {pr} (median ln T) | " + " | ".join(cells) + " |")
