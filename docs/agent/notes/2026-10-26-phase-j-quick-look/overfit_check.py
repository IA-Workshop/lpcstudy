"""WU-0048a: why the learned weights lose to A2 (diagnostic, oracle profile).

PROTOTYPE, DEVELOPMENT (DEV-2), old code c9bb981: not a hypothesis test.

For each system and horizon, on the oracle profile, this prints:

* the Kish effective sample size ``(sum k)^2 / sum k^2`` of the curvature
  weights ``kappa`` (all 1000 test states, and the mean over the 5 training
  sets of 800), and the share of ``sum kappa`` held by the top 1% of states;
* the gain share G of the full profile with the Q-N learner in sample
  (fitted and scored on the same 800 training states, mean over folds) and
  out of fold (as in ``quick_look.py``);
* the out-of-fold G of the full profile and of {R, O} with one heavily
  regularized learner (sensitivity only; not the plan's learner):
  ``max_iter=50, max_leaf_nodes=4, min_samples_leaf=100``, the other
  settings of ``qn_regressor``.

No interval; point estimates only. Writes ``overfit_check.json``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import quick_look as ql  # noqa: E402


class ShrunkLearner(ql.Learner):
    """The Q-N regressor with fewer, smaller trees and larger leaves."""

    def fit_predict(self, x_train, u, weight, x_test, cst):
        model = ql.qn_regressor(self.seed).set_params(
            max_iter=50, max_leaf_nodes=4, min_samples_leaf=100
        )
        model.fit(x_train, u, sample_weight=weight)
        raw = model.predict(x_test)
        self.n_fits += 1
        return np.clip(raw, 0.0, 1.0), int((raw < 0).sum()), int((raw > 1).sum())


def kish(k: np.ndarray) -> float:
    """Kish effective sample size of weights ``k``."""
    return float(k.sum() ** 2 / (k * k).sum())


def main() -> None:
    results = json.loads((ql.DATA / "results.json").read_text())
    seed = int(results["config"]["seed"])
    base, shrunk = ql.Learner(seed), ShrunkLearner(seed)
    full, ro = (0, 1, 2, 3), (0, 1)
    out = {"label": ql.LABEL, "systems": {}}
    for system in ql.SYSTEMS:
        d = ql.load_system(system)
        n = d["ec"].shape[0]
        folds = np.array_split(np.arange(n), ql.N_FOLDS)
        x = d["x_oracle"]
        rows = {}
        for h in range(len(d["horizons"])):
            ec, ep, c = d["ec"][:, h], d["ep"][:, h], d["c"][:, h]
            kappa = ec + ep - 2.0 * c
            fit_ok = kappa > ql.KAPPA_REL_TINY * (ec + ep)
            u = np.where(fit_ok, (ep - c) / np.where(fit_ok, kappa, 1.0), 0.0)
            v_star, _ = ql.optimal_v(ec, ep, c)
            w_a2, consts = ql.a2_weights(ec, ep, c, folds)
            l_a2 = (ql.hybrid_v(w_a2, ec, ep, c) - v_star).mean()

            def gain(w):
                return float(1.0 - (ql.hybrid_v(w, ec, ep, c) - v_star).mean() / l_a2)

            g_in = []
            for test in folds:
                train = np.setdiff1d(np.arange(n), test)
                w_tr, _, _ = base.fit_predict(x[train], u[train], kappa[train],
                                              x[train], None)
                a2 = consts[len(g_in)]
                vt = ql.hybrid_v(w_tr, ec[train], ep[train], c[train])
                va = ql.hybrid_v(a2, ec[train], ep[train], c[train])
                g_in.append(float(1.0 - (vt - v_star[train]).mean()
                                  / (va - v_star[train]).mean()))
            top = np.sort(kappa)[::-1][: n // 100].sum() / kappa.sum()
            oof = {}
            for name, learner, cols in (("qn_full", base, full),
                                        ("shrunk_full", shrunk, full),
                                        ("shrunk_RO", shrunk, ro)):
                w, _, _ = ql.cross_fit(learner, x, u, kappa, fit_ok, folds,
                                       cols, None)
                oof[name] = gain(w[:, 0])
            rows[str(h)] = {
                "horizon_lt": float(d["horizons"][h] / d["steps_per_lt"]),
                "kish_all": kish(kappa),
                "kish_train_mean": float(np.mean([
                    kish(kappa[np.setdiff1d(np.arange(n), t)]) for t in folds])),
                "top1pct_kappa_share": float(top),
                "a2_constants": consts,
                "G_in_sample_qn_full": float(np.mean(g_in)),
                "G_oof": oof,
            }
            r = rows[str(h)]
            print(f"{system} {r['horizon_lt']:.3g} LT  kish {r['kish_all']:.0f} "
                  f"(train {r['kish_train_mean']:.0f})  top1% {top:.2f}  "
                  f"A2 {min(consts):.3f}-{max(consts):.3f}  "
                  f"G in {r['G_in_sample_qn_full']:.2f}  oof qn {oof['qn_full']:.2f}"
                  f"  shrunk full {oof['shrunk_full']:.2f}  RO {oof['shrunk_RO']:.2f}",
                  flush=True)
        out["systems"][system] = rows
    (HERE / "overfit_check.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
