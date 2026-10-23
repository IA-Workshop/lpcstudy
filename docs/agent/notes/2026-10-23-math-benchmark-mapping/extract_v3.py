"""Read-only extraction of the V3 leaves for the benchmark mapping (WU-0024.2/.3).

DEVELOPMENT seeds only (DEV-1, DEV-3, DEV-4). The script computes no statistic.
It prints:

* stored leaves, each with its leaf path: ``systems/<s>/validation/cp_median_vpt_lyapunov``,
  ``systems/<s>/context/{lambda_max, interval, obs_scale}``, ``systems/<s>/validation/gate``,
  provenance and config;
* the SHA-256 of each ``results.json``;
* stated unit conversions only. Each formula is written out in ``conversions``.

The Dysts fields are copied from docs/agent/notes/2026-10-23-researcher-dysts-tables.md
section A.2 (confirmed, fetch extract, 2026-10-23). Conversions that use the Dysts
``maximum_lyapunov_estimated`` field are CONDITIONAL. Which lambda Zhang and Gilpin use
is not confirmed (that note, item D.2).

Run with ``python3 -I extract_v3.py``. Standard library only, CPU, read-only.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RUN_ROOT = Path("/home/brianm/projects/physics/chaos/lpcstudy-wt/run")
ENSEMBLE = {
    seed: RUN_ROOT / f"ens-3dec086/runs/dev/ens-{seed}/full" for seed in ("DEV-1", "DEV-3", "DEV-4")
}
EXTENSION = {
    "rossler_hyper": RUN_ROOT / "ext-run-974519a/runs/dev/ext-rossler_hyper-gpu/full",
    "lorenz63_r166": RUN_ROOT / "ext-run-974519a/runs/dev/ext-lorenz63_r166-gpu/full",
    "rossler_z": RUN_ROOT / "ext-run-974519a/runs/dev/ext-rossler_z-gpu/full",
    "hindmarsh_rose": RUN_ROOT / "ext-run-392a069/runs/dev/ext-hindmarsh_rose-gpu/full",
    "hyper_jha": RUN_ROOT / "ext-run-392a069/runs/dev/ext-hyper_jha-gpu/full",
    "lorenz96_4": RUN_ROOT / "ext-run-392a069/runs/dev/ext-lorenz96_4-gpu/full",
}
# Dysts JSON fields (researcher note 2026-10-23, A.2): period, maximum_lyapunov_estimated,
# lyapunov_spectrum_estimated[0].
DYSTS = {
    "lorenz63": (1.5008, 0.8917098035724058, 1.0910931847726466),
    "rossler": (5.9086, 0.15059688939547888, 0.0763301393780693),
    "chua": (1.4235, 1.2301163591725595, 0.4605474829443073),
}
CONTEXT_POINTS = 512  # Zhang and Gilpin, context length (2505.11349 Fig. 2; 2409.15771 Sec. 4)
TEST_POINTS = 300  # Zhang and Gilpin, forecast window
POINTS_PER_TAU = 30  # Zhang and Gilpin, Sec. 4
TRAIN_PERIODS = 10  # Gilpin 2023 App. C(4): t* = 10 t_peak


def sha256(path: Path) -> str:
    """Return the SHA-256 of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(folder: Path) -> tuple[dict, dict, str]:
    """Return (results, meta, sha256 of results.json) of one run folder."""
    res_path = folder / "results.json"
    return (
        json.loads(res_path.read_text()),
        json.loads((folder / "run.meta.json").read_text()),
        sha256(res_path),
    )


def provenance(name: str, res: dict, meta: dict, digest: str) -> str:
    """One provenance row."""
    prov = res["provenance"]
    cfg = prov["config"]
    return (
        f"| {name} | {meta['seed_id']} | {prov.get('seed_kind')} | {prov['label']} | "
        f"{prov['promoted']} | {prov['commit'][:7]} | {prov['dirty']} | {prov['complete']} | "
        f"{cfg['steps_per_lyapunov']} | {cfg['horizon_max_lyapunov']} | {cfg['core_noise']} | "
        f"{cfg['core_library']} | {cfg['n_test']} | `{digest}` |"
    )


def v3_row(name: str, system: str, block: dict) -> str:
    """Stored V3 leaf with its context and gate."""
    ctx = block["context"]
    v3 = block["validation"]["cp_median_vpt_lyapunov"]
    gate = "PASS" if block["validation"]["gate"]["gate_pass"] else "FAIL (PROVISIONAL)"
    return (
        f"| {name} | {system} | {v3!r} | {round(v3 * 30, 6)} | {ctx['lambda_max']!r} | "
        f"{ctx['interval']!r} | {ctx['obs_scale']!r} | {gate} |"
    )


def conversions(name: str, system: str, block: dict) -> list[str]:
    """Stated unit conversions for one frozen system (formulas printed beside values)."""
    lam = block["context"]["lambda_max"]
    v3 = block["validation"]["cp_median_vpt_lyapunov"]
    period, lam_max_field, lam_spec0 = DYSTS[system]
    return [
        f"| {name} | {system} | T = V3/lambda = {v3 / lam:.6g} | T/t_peak = {v3 / lam / period:.4g} | "
        f"V3 x lambda_max_field/lambda = {v3 * lam_max_field / lam:.4g} (conditional) | "
        f"V3 x spectrum0/lambda = {v3 * lam_spec0 / lam:.4g} | "
        f"10 t_peak x lambda = {TRAIN_PERIODS * period * lam:.4g} LT | "
        f"512/30 x lambda/lambda_max_field = {CONTEXT_POINTS / POINTS_PER_TAU * lam / lam_max_field:.4g} LT (conditional) | "
        f"300/30 x lambda/lambda_max_field = {TEST_POINTS / POINTS_PER_TAU * lam / lam_max_field:.4g} LT (conditional) | "
        f"ratio lambda_max_field/lambda = {lam_max_field / lam:.4g} |"
    ]


def main() -> int:
    """Print every table in Markdown."""
    runs = {f"ens-{k}": load(v) for k, v in ENSEMBLE.items()}
    runs.update({f"ext-{k}": load(v) for k, v in EXTENSION.items()})
    print("## Provenance\n")
    print("| run | seed_id | seed_kind | label | promoted | commit | dirty | complete | steps/LT | "
          "H_max (LT) | core rho | core n_lib | n_test | SHA-256 results.json |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for name, (res, meta, digest) in runs.items():
        print(provenance(name, res, meta, digest))
    print("\n## V3 leaves (systems/<s>/validation/cp_median_vpt_lyapunov; context/*)\n")
    print("| run | system | V3 (LT) | V3 x 30 (steps) | lambda_max | interval | obs_scale | gate |")
    print("|---|---|---|---|---|---|---|---|")
    for name, (res, _, _) in runs.items():
        for system, block in res["systems"].items():
            print(v3_row(name, system, block))
    print("\n## Stated conversions (frozen systems only)\n")
    for name, (res, _, _) in runs.items():
        if not name.startswith("ens-"):
            continue
        for system, block in res["systems"].items():
            print("\n".join(conversions(name, system, block)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
