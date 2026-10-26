"""WU-0045b: diagnostics behind the rulings on WU-0048 points 2 and 3.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test. The input is the
phase J DEV-1 full run (schema /3 dumps, run commit f701a47), test split for
scoring. The analysis code is ``lpcstudy.contribution`` of WU-0048 commit
108d7d5, imported from its worktree (it is not on develop yet).

* Point 2: per deployable reference rule, the effective size (sum x)^2 / sum
  x^2 of four candidates: the realized excess S - V(w*) (mixed signs), its
  absolute value, the substituted (moment-form) excess mean_j V(g_ij) - V(w*)
  (>= 0), and kappa.
* Point 3: the exact per-state decomposition of the paired dependence bias
  D_i - D_i(A1) = T0 + T1 + T2 (see the note's addendum), for the learned
  deployable rules RON and ROIN and the stored A4, at H = 8 on Chua; plus
  the share of each term carried by the top 5 states.

Usage (CPU, one thread)::

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19 \
        /path/to/.venv/bin/python -I rulings_0045b.py > rulings_0045b.out.md
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import numpy as np

CONTRIB_TREE = pathlib.Path(
    "/home/brianm/projects/physics/chaos/lpcstudy-wt/wu/0048-contrib-abd"
)
CONTRIB_COMMIT = "108d7d5"
RUN = pathlib.Path(
    "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-1/full"
)
LABEL = "DEVELOPMENT (DEV-1): exploratory, not a hypothesis test"

head = subprocess.run(
    ["git", "-C", str(CONTRIB_TREE), "rev-parse", "--short=7", "HEAD"],
    capture_output=True, text=True, check=True,
).stdout.strip()
assert head == CONTRIB_COMMIT, head
sys.path.insert(0, str(CONTRIB_TREE))
from lpcstudy import contribution as cb  # noqa: E402

SYSTEMS = ("lorenz63", "rossler", "chua")


def load(system: str) -> tuple[cb.SystemData, int]:
    z = np.load(RUN / "states" / f"{system}.npz")
    arrays = {k: z[k] for k in z.files}
    assert str(arrays["meta/seed_id"]) == "DEV-1"
    seed = int(json.loads((RUN / "results.json").read_text())["config"]["seed"])
    return cb.SystemData.from_arrays(arrays), seed


def kish(x: np.ndarray) -> float:
    return float(np.sum(x) ** 2 / np.sum(x**2))


def fit_rules(data: cb.SystemData, seed: int, column: int, names: tuple[str, ...]):
    h = int(data.horizons[column])
    tr = cb.allocation_targets(*(data.train[k][:, h - 1] for k in ("E_C", "E_P", "C")))
    jobs = cb.allocation_jobs(data, column, "deployable", tr)
    learner = cb.Learner(seed=seed)
    return {n: cb.run_job((jobs[f"A/{n}"], learner)).pred for n in names}


def pieces(data: cb.SystemData, column: int):
    h = int(data.horizons[column])
    t = data.test
    mom = tuple(t[k][:, h - 1] for k in ("E_C", "E_P", "C"))
    te = cb.allocation_targets(*mom)
    e_c, e_p = t["cp_err"][:, :, column], t["plp_err"][:, :, column]
    return mom, te, e_c, e_p


def neff_row(name, g, mom, te, e_c, e_p) -> str:
    g = np.clip(g, 0, 1)
    realized = cb.realized_score(g, e_c, e_p) - te.v_star
    subst = np.mean(cb.quad_mse(g, *(m[:, None] for m in mom)), axis=1) - te.v_star
    return (f"{name} | {kish(realized):.1f} | {kish(np.abs(realized)):.1f} | "
            f"{kish(subst):.1f} | {kish(te.kappa):.1f}")


def decomposition(g, mom, te, e_c, e_p) -> dict:
    """Exact: D_i - D_i(A1) = T0 + T1 + T2 with w = wbar + d over the E draws.

    a = e_P Delta - (C - E_P), b = Delta^2 - kappa, Delta = e_C - e_P;
    T0 = mean_j (2 wbar a + wbar^2 b), T1 = mean_j 2 d (a + wbar b),
    T2 = mean_j d^2 b.
    """
    g = np.clip(g, 0, 1)
    EC, EP, C = (m[:, None] for m in mom)
    delta = e_c - e_p
    a = e_p * delta - (C - EP)
    b = delta**2 - (EC + EP - 2 * C)
    wbar = g.mean(axis=1, keepdims=True)
    d = g - wbar
    t0 = np.mean(2 * wbar * a + wbar**2 * b, axis=1)
    t1 = np.mean(2 * d * (a + wbar * b), axis=1)
    t2 = np.mean(d**2 * b, axis=1)
    s = cb.realized_score(g, e_c, e_p) - np.mean(e_p**2, axis=1)
    q = np.mean(cb.quad_mse(g, EC, EP, C), axis=1) - EP[:, 0]
    total = s - q
    assert np.allclose(t0 + t1 + t2, total, rtol=1e-9, atol=1e-15 * np.abs(EP).max())
    top = np.argsort(np.abs(total))[::-1][:5]
    return dict(total=total, t0=t0, t1=t1, t2=t2, top=top, drawsd=g.std(axis=1, ddof=1),
                maxdelta2=np.max(delta**2, axis=1), kappa=te.kappa)


def main() -> None:
    print(f"# WU-0045b diagnostics\n\n{LABEL}; analysis code {CONTRIB_COMMIT}.\n")
    print("## Point 2: effective size of the reference rule's per-state excess (deployable)\n")
    print("| system | H | rule | realized S - V(w*) | abs(realized) | substituted mean_j V(g) - V(w*) "
          "| kappa |")
    print("|---|---|---|---|---|---|---|")
    fitted = {}
    for s in SYSTEMS:
        data, seed = load(s)
        for column in range(len(data.horizons)):
            mom, te, e_c, e_p = pieces(data, column)
            h = int(data.horizons[column])
            rules = {"A4 (stored)": data.test["a4_weight"][:, :, column]}
            if (s, column) in (("rossler", 0), ("chua", 0)):
                fit = fit_rules(data, seed, column, ("ROIN", "RON"))
                fitted[s] = (data, fit)
                rules.update(fit)
            for name, g in rules.items():
                print(f"| {s} | {h} | " + neff_row(name, g, mom, te, e_c, e_p) + " |")
    print()

    print("## Point 3: exact decomposition of the paired dependence bias, Chua, H = 8\n")
    print("Means over the 1000 test states, in units of the mean V of the rule; "
          "T0 = noise at the draw-mean weight, T1 = 2 Cov(d, h) part, T2 = Cov(d^2, Delta^2) part. "
          "Top-5 share: share of the sum of the term carried by the 5 states with the largest |D|.\n")
    data, fit = fitted["chua"]
    mom, te, e_c, e_p = pieces(data, 0)
    print("| rule | mean draw-SD of w | total/V | T0/V | T1/V | T2/V | top-5 share of total | "
          "top-5 share of T1 | top-5 share of T2 |")
    print("|---|---|---|---|---|---|---|---|---|")
    rules = {"A4 (stored)": data.test["a4_weight"][:, :, 0], **fit}
    details = {}
    for name, g in rules.items():
        r = decomposition(g, mom, te, e_c, e_p)
        details[name] = r
        v = np.mean(cb.quad_mse(np.clip(g, 0, 1), *(m[:, None] for m in mom)))
        top = r["top"]
        share = lambda x: float(x[top].sum() / x.sum())  # noqa: E731
        print(f"| {name} | {r['drawsd'].mean():.4f} | {r['total'].mean() / v:+.4f} | "
              f"{r['t0'].mean() / v:+.4f} | {r['t1'].mean() / v:+.4f} | {r['t2'].mean() / v:+.4f} | "
              f"{share(r['total']):.2f} | {share(r['t1']):.2f} | {share(r['t2']):.2f} |")
    print()
    r = details["RON"]
    print("RON, the five states with the largest |D_i| (paired):\n")
    print("| state | D_i / mean V | T1_i / mean V | T2_i / mean V | draw-SD of w | kappa / median kappa "
          "| max_j Delta^2 / kappa |")
    print("|---|---|---|---|---|---|---|")
    v = np.mean(cb.quad_mse(np.clip(fit["RON"], 0, 1), *(m[:, None] for m in mom)))
    for i in r["top"]:
        print(f"| {i} | {r['total'][i] / v:+.3f} | {r['t1'][i] / v:+.3f} | {r['t2'][i] / v:+.3f} | "
              f"{r['drawsd'][i]:.3f} | {r['kappa'][i] / np.median(r['kappa']):.1f} | "
              f"{r['maxdelta2'][i] / r['kappa'][i]:.1f} |")
    print()


if __name__ == "__main__":
    main()
