"""WU-0037: stored V7 and LM diagnostics per system and noise level.

DEVELOPMENT (DEV-3): not a hypothesis test.

Reads only stored leaves of ``results.json`` of the DEV-3 development runs
(extension systems S1 to S6 and the frozen ensemble run ens-DEV-3). Nothing is
recomputed except the ratios c/rho^2 of stored LM residual quantiles.
Standard library only; run with ``python3 -I stored_lm.py``.
"""

import json
from pathlib import Path

RUN = Path("/home/brianm/projects/physics/chaos/lpcstudy-wt/run")
SOURCES = {
    "ens-DEV-3": RUN / "ens-3dec086/runs/dev/ens-DEV-3/full/results.json",
    "S1": RUN / "ext-run-974519a/runs/dev/ext-rossler_hyper-gpu/full/results.json",
    "S2": RUN / "ext-run-974519a/runs/dev/ext-lorenz63_r166-gpu/full/results.json",
    "S3": RUN / "ext-run-974519a/runs/dev/ext-rossler_z-gpu/full/results.json",
    "S4": RUN / "ext-run-392a069/runs/dev/ext-hindmarsh_rose-gpu/full/results.json",
    "S5": RUN / "ext-run-392a069/runs/dev/ext-hyper_jha-gpu/full/results.json",
    "S6": RUN / "ext-run-392a069/runs/dev/ext-lorenz96_4-gpu/full/results.json",
}
LABEL = "DEVELOPMENT (DEV-3): not a hypothesis test"


def cell_key(rho: float) -> str:
    kind = "core" if rho == 0.01 else "sweep"
    return f"base|rho={rho:g}|n_lib=10000|{kind}"


def main() -> None:
    print(f"# Stored V7 and LM leaves. {LABEL}\n")
    for tag, path in SOURCES.items():
        res = json.loads(path.read_text())
        print(f"## {tag} ({path.relative_to(RUN)}); seed_id {res['config']['seed_id']}")
        for system, s in res["systems"].items():
            v7 = s["V7"]
            print(f"\n### {system}: V7 pass {v7['pass']}, median slope "
                  f"{v7['median_slope']:.4f} CI {[round(x, 4) for x in v7['ci']]}")
            print("| rho | V7 median delta/(rho nu) | 95% CI | LM n | median c/rho^2 | p95 c/rho^2 | "
                  "frac c/rho^2 > chi2_0.999 | median accepted | frac late | dof | net val loss (chosen width) |")
            print("|---|---|---|---|---|---|---|---|---|---|---|")
            for rho in res["config"]["noise_levels"]:
                k = f"{rho:g}"
                med = v7["efficiency_median_by_noise"][k]
                ci = v7["efficiency_ci_by_noise"][k]
                lm = s["handling"]["cells"][cell_key(rho)]["lm"]["by_kind"]["oracle"]
                est = [v for kk, v in res["estimators"].items()
                       if kk.startswith(f"('{system}', 7,") and kk.endswith(f", {rho})")]
                loss = (f"{est[0]['val_loss_by_width'][str(est[0]['chosen_width'])]:.4f} "
                        f"({est[0]['chosen_width']})") if est else "n/a"
                mr = lm["median_residual"] / rho**2
                pr = lm["p95_residual"] / rho**2 if lm["p95_residual"] is not None else float("nan")
                print(f"| {rho:g} | {med:.4g} | [{ci[0]:.4g}, {ci[1]:.4g}] | {lm['n_estimates']} | "
                      f"{mr:.3g} | {pr:.3g} | {lm['fraction_above_chi2']:.4f} | "
                      f"{lm['median_iterations']:.0f} | {lm['fraction_late_progress']:.3f} | "
                      f"{lm['gof_dof']} | {loss} |")
        print()


if __name__ == "__main__":
    main()
