#!/usr/bin/env python3
"""WU-0041b: stored A4 coefficients and the A0/A1/A4 MSE at H_ref.

DEVELOPMENT (DEV-1, DEV-3, DEV-4): not a hypothesis test. Stored leaves only
(``systems/<s>/fitted/{analog_proxy,estimation_proxy}``, ``scores/<rule>/
mse_href``, ``H2c/best_single``), read from the development run folders
under ``lpcstudy-wt/run/`` (never a confirmatory folder). The ratios
MSE(A0)/MSE(A4) and MSE(A1)/MSE(A4) are the zero-mode values that r(a) and
r(a') reduce to when b and b' are at the boundary (stage 1 note, section 3.5);
they are point values, no interval. S2 to S6 are V7-failed runs (estimator
before the fixes F1/F2), so their a', b' and A1 values describe the unfixed
estimator. Run: ``python3 -I a4_coefficients.py`` (standard library).
"""

import json
from pathlib import Path

RUN = Path("/home/brianm/projects/physics/chaos/lpcstudy-wt/run")
CELLS = [
    ("ens-DEV-1", "ens-3dec086/runs/dev/ens-DEV-1", ("lorenz63", "rossler", "chua")),
    ("ens-DEV-3", "ens-3dec086/runs/dev/ens-DEV-3", ("lorenz63", "rossler", "chua")),
    ("ens-DEV-4", "ens-3dec086/runs/dev/ens-DEV-4", ("lorenz63", "rossler", "chua")),
    ("DEV-3", "ext-run-974519a/runs/dev/ext-rossler_hyper-gpu", ("rossler_hyper",)),
    ("DEV-3", "ext-run-974519a/runs/dev/ext-lorenz63_r166-gpu", ("lorenz63_r166",)),
    ("DEV-3", "ext-run-974519a/runs/dev/ext-rossler_z-gpu", ("rossler_z",)),
    ("DEV-3", "ext-run-392a069/runs/dev/ext-hindmarsh_rose-gpu", ("hindmarsh_rose",)),
    ("DEV-3", "ext-run-392a069/runs/dev/ext-hyper_jha-gpu", ("hyper_jha",)),
    ("DEV-3", "ext-run-392a069/runs/dev/ext-lorenz96_4-gpu", ("lorenz96_4",)),
]


def find_results(folder: Path) -> Path | None:
    for p in sorted(folder.rglob("results.json")):
        if "confirmatory" not in p.parts:
            return p
    return None


def main() -> None:
    print("DEVELOPMENT: not a hypothesis test.\n")
    print("| run | system | a | b | a' | b' | a/a' | MSE A0/A4 | MSE A1/A4 |"
          " best single (cal.) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for label, sub, systems in CELLS:
        path = find_results(RUN / sub)
        if path is None:
            print(f"| {label} | {systems} | not found | | | | | | | |")
            continue
        r = json.loads(path.read_text())
        for s in systems:
            sy = r["systems"][s]
            f = sy["fitted"]
            a, b = f["analog_proxy"]["slope"], f["analog_proxy"]["floor"]
            a2, b2 = (f["estimation_proxy"]["slope"],
                      f["estimation_proxy"]["floor"])
            m = {k: sy["scores"][k]["mse_href"] for k in ("A0", "A1", "A4")}
            best = sy["H2c"]["best_single"]
            print(f"| {label} | {s} | {a:.4f} | {b:.1e} | {a2:.4f} | {b2:.2e} |"
                  f" {a/a2:.3f} | {m['A0']/m['A4']:.3f} |"
                  f" {m['A1']/m['A4']:.3f} | {best} |")


if __name__ == "__main__":
    main()
