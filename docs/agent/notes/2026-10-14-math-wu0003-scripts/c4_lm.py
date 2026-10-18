"""M6: LM diagnostics per cell from existing DEV-0 pilot results (P0, P1).

DEVELOPMENT (DEV-0): not a hypothesis test. Reads results.json only.
Usage: python -I c4_lm.py <results.json> [...]
"""
import json, sys
for path in sys.argv[1:]:
    r = json.load(open(path))
    print("==", path, "seed_id", r["config"].get("seed_id"), "commit", r.get("provenance", {}).get("commit", "?"))
    for sysname, s in r["systems"].items():
        cells = s["handling"]["cells"]
        for cid, cell in cells.items():
            lm = cell.get("lm")
            if not lm:
                continue
            for kind in ("oracle", "eval"):
                k = lm["by_kind"].get(kind)
                if not k or not k["n_estimates"]:
                    continue
                rho = k["noise"]
                med = k["median_residual"] / rho**2 if k["median_residual"] is not None else None
                p95 = k["p95_residual"] / rho**2 if k["p95_residual"] is not None else None
                print(f"{sysname:9s} {cid:38s} {kind:6s} n={k['n_estimates']:7d} dof={k['gof_dof']} "
                      f"med c/r2={med:.3f} p95={p95:.2f} above={k['fraction_above_chi2']:.4f} "
                      f"late={k['fraction_late_progress']:.4f} nodec={k['fraction_no_decrease']} "
                      f"medit={k['median_iterations']}")
