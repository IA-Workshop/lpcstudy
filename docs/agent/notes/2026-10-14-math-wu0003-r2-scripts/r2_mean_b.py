"""R2 check 1: the mean dependence term b = mu - nu per rule at H_ref, from P0/P1 results (DEV-0).

mse_href (realized, over n x E eval draws) - regret_href (mean V_i(w_d) - V_i(w*_i), oracle moments)
- mse_href(A*) (realized, w* constant over draws) estimates mean_i b_i plus eval-draw noise of the
difference. A0, A1, A2, A4o (draw-constant weights) have b = 0: they are the controls (their value is
the noise of the difference). Read-only; no random number.
"""
import json, sys
RUNS = {"P0": "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/p0-1b20db9/runs/dev/p0/pilot/results.json",
        "P1": "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/p1-5b3fd8f/runs/dev/p1/pilot/results.json"}
for run, path in RUNS.items():
    r = json.load(open(path))
    for sysname, s in r["systems"].items():
        sc = s["scores"]
        star = sc["A*"]["mse"]["1LT"]
        row = []
        for rule in ("A0", "A1", "A2", "A4o", "A3", "A4", "A5"):
            mse = sc[rule]["mse"]["1LT"]; reg = sc[rule]["regret"]["1LT"]
            b = mse - reg - star
            row.append(f"{rule} b {b:+.4f} ({b/mse:+.3f} of mse {mse:.4f})")
        print(run, sysname, "mse(A*)", f"{star:.4f}")
        for x in row: print("   ", x)
