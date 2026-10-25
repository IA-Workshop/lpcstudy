"""WU-0037: tables from the per-draw arrays written by ``diag.py``.

DEVELOPMENT (DEV-3): not a hypothesis test.

Reads ``<dir>/<system>.npz`` and the stored V7 leaves, and prints markdown:

* V7 quantities per estimator variant: the median over states of
  ``delta_i/(rho nu_i)`` at each rho with a moving-block bootstrap 95%
  interval (block 5, 2000 resamples, as V7), the median per-state slope of
  ``ln delta`` on ``ln rho`` with its interval, and whether both would sit in
  [0.9, 1.1];
* ``ms_pp`` is derived here: per draw, the lower final cost of ``prod`` and
  ``pair_nn`` (the two-start estimator proposed as fix F1);
* far-draw accounting for the production estimator: a draw is *far* when its
  final cost exceeds the 0.999 chi-square quantile times rho^2 (the code's own
  goodness-of-fit indicator); a far draw is a *wrong local minimum* when the
  truth-started LM reaches a cost lower by more than 1e-9 relative;
* the network start error of converged and far draws, and the empirical
  probability of reaching the truth basin by start-error bin;
* the truth-started ratio by bins of rho nu (linear-regime check).

Bootstrap generators come from ``lpcstudy.data.make_rng(seed, "WU-0037",
system, ...)``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from lpcstudy.data import make_rng
from lpcstudy.estimation import gof_threshold
from lpcstudy.seeds import load_registry, resolve_dev_seed
from lpcstudy.statistics import block_bootstrap_dropped

LEVELS = (0.005, 0.01, 0.02, 0.05)
VARIANTS = ("prod", "it30", "it60", "cont", "pair_nn", "analog", "ms2", "ms_pp", "ms3", "truth", "best_truth")


def with_ms_pp(z) -> dict:
    """Add the two-start variant ``ms_pp``: the lower final cost of ``prod`` and ``pair_nn``."""
    out = dict(z)
    for r in LEVELS:
        cs = np.stack([z[f"{r:g}/prod/cost"], z[f"{r:g}/pair_nn/cost"]])
        es = np.stack([z[f"{r:g}/prod/err"], z[f"{r:g}/pair_nn/err"]])
        j = np.argmin(cs, axis=0)
        idx = np.arange(cs.shape[1])
        out[f"{r:g}/ms_pp/err"], out[f"{r:g}/ms_pp/cost"] = es[j, idx], cs[j, idx]
    return out
LABEL = "DEVELOPMENT (DEV-3): not a hypothesis test"
RUNS = {
    "lorenz63_r166": "ext-run-974519a/runs/dev/ext-lorenz63_r166-gpu/full",
    "rossler_z": "ext-run-974519a/runs/dev/ext-rossler_z-gpu/full",
    "rossler_hyper": "ext-run-974519a/runs/dev/ext-rossler_hyper-gpu/full",
    "hindmarsh_rose": "ext-run-392a069/runs/dev/ext-hindmarsh_rose-gpu/full",
    "hyper_jha": "ext-run-392a069/runs/dev/ext-hyper_jha-gpu/full",
    "lorenz96_4": "ext-run-392a069/runs/dev/ext-lorenz96_4-gpu/full",
    "lorenz63": "ens-3dec086/runs/dev/ens-DEV-3/full",
}
RUN = Path("/home/brianm/projects/physics/chaos/lpcstudy-wt/run")
SEED = resolve_dev_seed(
    "DEV-3",
    load_registry(Path("/home/brianm/projects/physics/chaos/lpcstudy-wt/wu/0037-v7-diagnosis/seeds/development_seeds.json")),
)  # asserted against the stored run config below


def boot(stat, n, rng):
    est, lo, hi, _ = block_bootstrap_dropped(stat, n, 2000, 5, rng, 0.95)
    return est, lo, hi


def main(directory: Path, system: str) -> None:
    z = with_ms_pp(np.load(directory / f"{system}.npz"))
    stored = json.loads((RUN / RUNS[system] / "results.json").read_text())
    assert stored["config"]["seed"] == SEED
    v7s = stored["systems"][system]["V7"]
    n = int(z["n_states"])
    m_draws = int(z["n_draws"])
    nu = z["nu"]
    spec_dim = {"rossler_hyper": 4, "hyper_jha": 4, "lorenz96_4": 4}.get(system, 3)
    chi = gof_threshold(7 - spec_dim)
    print(f"## {system}  ({LABEL})\n")
    print(f"{n} test-sweep states (the first {n} of the stored run's 1000), M = {m_draws} draws, "
          f"CPU reproduction; nu median {np.median(nu):.3g} (p10 {np.quantile(nu, .1):.3g}, "
          f"p90 {np.quantile(nu, .9):.3g}).\n")
    # V7 per variant
    print("| variant | " + " | ".join(f"median ratio rho={r:g} [95% CI]" for r in LEVELS)
          + " | median slope [95% CI] | both in [0.9, 1.1] |")
    print("|---|" + "---|" * (len(LEVELS) + 2))
    print("| stored V7 (1000 states, GPU) | " + " | ".join(
        f"{v7s['efficiency_median_by_noise'][f'{r:g}']:.4g} "
        f"[{v7s['efficiency_ci_by_noise'][f'{r:g}'][0]:.3g}, {v7s['efficiency_ci_by_noise'][f'{r:g}'][1]:.3g}]"
        for r in LEVELS) + f" | {v7s['median_slope']:.4g} [{v7s['ci'][0]:.3g}, {v7s['ci'][1]:.3g}] | "
        f"{v7s['pass']} |")
    logs = np.log(np.array(LEVELS))
    cen = logs - logs.mean()
    for var in VARIANTS:
        if f"{LEVELS[0]:g}/{var}/err" not in z:
            continue
        deltas = np.column_stack([
            np.sqrt((z[f"{r:g}/{var}/err"].reshape(n, m_draws) ** 2).mean(axis=1)) for r in LEVELS
        ])
        ratios = deltas / (np.array(LEVELS)[None, :] * nu[:, None])
        slopes = (np.log(deltas) - np.log(deltas).mean(axis=1, keepdims=True)) @ cen / np.sum(cen**2)
        cells, ok = [], True
        for i, r in enumerate(LEVELS):
            est, lo, hi = boot(lambda idx: float(np.median(ratios[idx, i])), n,
                               make_rng(SEED, "WU-0037", system, var, f"{r:g}"))
            ok &= 0.9 <= est <= 1.1
            cells.append(f"{est:.4g} [{lo:.3g}, {hi:.3g}]")
        est, lo, hi = boot(lambda idx: float(np.median(slopes[idx])), n,
                           make_rng(SEED, "WU-0037", system, var, "slope"))
        ok &= 0.9 <= est <= 1.1
        print(f"| {var} | " + " | ".join(cells) + f" | {est:.4g} [{lo:.3g}, {hi:.3g}] | {ok} |")
    bad = {v: [int((~np.isfinite(z[f"{r:g}/{v}/err"])).sum()) for r in LEVELS]
           for v in VARIANTS if f"{LEVELS[0]:g}/{v}/err" in z}
    bad = {v: c for v, c in bad.items() if any(c)}
    if bad:
        print("\nNon-finite estimates (draws per rho; the package replaces them by the invariant mean and "
              "counts them, this script does not, so the medians above are NaN where any occur): "
              + "; ".join(f"{v} {c}" for v, c in bad.items()))
    print()
    # far-draw accounting
    print("| rho | far draws (prod) | states with >= 1 far draw | wrong local min (truth cost lower) "
          "| states with >= 1 wrong-local-min draw | far with cost <= truth's | far draws (it60) | far (ms3) | far (truth) | median start err, near / far "
          "| median ratio of states with no far draw (prod) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in LEVELS:
        cp, ct = z[f"{r:g}/prod/cost"], z[f"{r:g}/truth/cost"]
        far = cp > chi * r**2
        wrong = far & (cp > ct * (1 + 1e-9))
        same = far & ~wrong
        se = z[f"{r:g}/start_err"]
        far_s = far.reshape(n, m_draws).any(axis=1)
        d = np.sqrt((z[f"{r:g}/prod/err"].reshape(n, m_draws) ** 2).mean(axis=1)) / (r * nu)
        nf = lambda v: (z[f"{r:g}/{v}/cost"] > chi * r**2).mean()
        print(f"| {r:g} | {far.mean():.4f} | {far_s.mean():.3f} | {wrong.mean():.4f} | "
              f"{wrong.reshape(n, m_draws).any(axis=1).mean():.3f} | {same.mean():.4f} | "
              f"{nf('it60'):.4f} | {nf('ms3'):.4f} | {nf('truth'):.4f} | "
              f"{np.median(se[~far]):.3g} / {np.median(se[far]) if far.any() else float('nan'):.3g} | "
              f"{np.median(d[~far_s]) if (~far_s).any() else float('nan'):.4g} |")
    print()
    # basin: P(not far | start error bin), pooled over levels
    se_all = np.concatenate([z[f"{r:g}/start_err"] for r in LEVELS])
    far_all = np.concatenate([z[f"{r:g}/prod/cost"] > chi * r**2 for r in LEVELS])
    edges = [0, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6, np.inf]
    print("Network start error (whitened, window start) against the share of draws that end far, pooled over rho:\n")
    print("| start error bin | draws | share far |")
    print("|---|---|---|")
    for a, b in zip(edges[:-1], edges[1:]):
        sel = (se_all >= a) & (se_all < b)
        if sel.sum():
            print(f"| [{a:g}, {b:g}) | {sel.sum()} | {far_all[sel].mean():.3f} |")
    print()
    # linear regime: truth-start ratio by bins of rho nu
    print("Truth-started LM (15 iterations): per-state ratio by bins of rho*nu (whitened):\n")
    print("| rho nu bin | states x levels | median ratio | p90 ratio |")
    print("|---|---|---|---|")
    rn, rt = [], []
    for r in LEVELS:
        dt = np.sqrt((z[f"{r:g}/truth/err"].reshape(n, m_draws) ** 2).mean(axis=1))
        rn.append(r * nu)
        rt.append(dt / (r * nu))
    rn, rt = np.concatenate(rn), np.concatenate(rt)
    for a, b in zip([0, 0.01, 0.03, 0.1, 0.3, 1.0], [0.01, 0.03, 0.1, 0.3, 1.0, np.inf]):
        sel = (rn >= a) & (rn < b)
        if sel.sum():
            print(f"| [{a:g}, {b:g}) | {sel.sum()} | {np.median(rt[sel]):.4g} | {np.quantile(rt[sel], .9):.4g} |")
    print()


if __name__ == "__main__":
    d = Path(sys.argv[1])
    for s in sys.argv[2:]:
        if (d / f"{s}.npz").exists():
            main(d, s)
