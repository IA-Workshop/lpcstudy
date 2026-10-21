"""WU-0028: exploratory theorem measurements on existing per-state dumps.

DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test.

Analysis record, not part of the package. Reads only the stored arrays of
``states/<system>.npz`` (schema lpcstudy.states/2). No run, no GPU.

Parts
  (a) P1(d'): realized hybrid gain against T_m(sqrt2 theta) - T_m(theta),
      on the stored 5-point horizon grid.
  (b) N4: f(rho, r) identity and gain prediction on the grid; dependence of
      f at H_ref on library size from the sweep groups (H_ref moments only).
  (c) N6: curvature-weighted R_c^2 of u on the profile; predicted floor
      against the observed regret of the stored rules.
  (d) N8 (partial): rank correlation of w* with rho, by N group.

Study conventions reused (not redefined): first passage is
``sqrt(mse + rho^2) > theta`` (lpcstudy.oracle.characteristic_horizon),
theta = primary_threshold = 0.2, rho = core_noise = 0.01 (config defaults;
the dump does not store them), u = (E_P - C)/c with c = E_C + E_P - 2C.

Usage: python theory_dump_checks.py ROOT_FULL ROOT_PILOT OUTDIR
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr
from sklearn.tree import DecisionTreeRegressor

LABEL = "DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test"
THETA = 0.2
RHO_CORE = 0.01
SYSTEMS = ("lorenz63", "rossler", "chua")
STABLE_N = 1e-9          # N is exactly 0 up to round-off (~1e-13) when the analog never changes
KS = (2, 3, 4, 5, 6, 8, 12, 16)   # config.regime_counts


# ------------------------------------------------------------------ helpers
def first_passage(mse, thr_sq):
    """Index of the first grid column with mse > thr_sq (k if censored)."""
    ex = mse > thr_sq
    return np.where(ex.any(axis=1), ex.argmax(axis=1), mse.shape[1])


def steps(idx, hor):
    """Grid horizon in steps of index idx (inf if censored)."""
    h = np.append(hor.astype(float), np.inf)
    return h[idx]


def lower_steps(idx, hor):
    """Left end of the bracket (previous grid point; 0 before the first)."""
    h = np.concatenate([[0.0], hor.astype(float), [hor[-1]]])
    return h[idx]       # idx=0 -> 0 ; idx=j -> hor[j-1] ; idx=k -> hor[k-1]


def f_corr(EC, EP, C):
    """N4: f(rho, r) = (1-rho^2)/(1+r-2 rho sqrt r), r = min/max, rho = C/sqrt(EC EP)."""
    r = np.minimum(EC, EP) / np.maximum(EC, EP)
    rho = C / np.sqrt(EC * EP)
    return (1 - rho**2) / (1 + r - 2 * rho * np.sqrt(r)), rho, r


def hybrid(EC, EP, C):
    c = EC + EP - 2 * C
    w = np.clip((EP - C) / np.maximum(c, 1e-300), 0, 1)
    return w**2 * EC + (1 - w) ** 2 * EP + 2 * w * (1 - w) * C, w


def wquant(x, q=(5, 25, 50, 75, 95)):
    x = x[np.isfinite(x)]
    return [float(v) for v in np.percentile(x, q)] if x.size else [float("nan")] * len(q)


def row_spearman(W):
    """Per-row Spearman (average ranks); NaN for a constant row."""
    R = np.apply_along_axis(rankdata, 1, W)
    R = R - R.mean(axis=1, keepdims=True)
    den = np.sqrt((R**2).sum(1))
    # correlation of ranks with the rank of rho (rho increasing): ranks 1..m
    m = W.shape[1]
    x = np.arange(1, m + 1, dtype=float)
    x -= x.mean()
    num = R @ x
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / (den * np.sqrt((x**2).sum())), np.nan)


# ------------------------------------------------------------ (a) P1(d')
def part_a(EC, EP, C, hor, Lam, rho=RHO_CORE, theta=THETA):
    n, k = EC.shape
    env = np.minimum(EC, EP)
    hyb, _ = hybrid(EC, EP, C)
    t2 = theta**2 - rho**2                       # study rule: mse > theta^2 - rho^2
    i_m = first_passage(env, t2)
    i_h = first_passage(hyb, t2)
    i_1s = first_passage(env, 2 * theta**2 - rho**2)      # T_m(sqrt2 theta), study rule
    i_1t = first_passage(env, 2 * (theta**2 - rho**2))    # T_m(sqrt2 theta'), exact for noise
    Tm, Th = steps(i_m, hor), steps(i_h, hor)
    out = {"n": int(n), "grid": [int(h) for h in hor],
           "n_Tm_censored": int((i_m == k).sum()),
           "n_Th_censored": int((i_h == k).sum())}
    # lower bound (no hypothesis): T_h >= T_m
    lb_viol = int((i_h < i_m).sum())
    out["lower_bound_violations_all_states"] = lb_viol
    rows = np.arange(n)
    for name, i_1 in (("study_rule_sqrt2_theta", i_1s), ("noise_exact_sqrt2_theta_prime", i_1t)):
        H1 = steps(i_1, hor)
        cens1 = i_1 == k
        okm = i_m < k
        cH1 = C[rows, np.minimum(i_1, k - 1)]
        pos = okm & ~cens1 & (cH1 >= 0)
        neg = okm & ~cens1 & ~(cH1 >= 0)
        G = Th - Tm
        B = H1 - Tm
        viol = pos & (Th > H1)
        viol_neg = neg & (Th > H1)
        # interval (true 1-step) classification, certain-violation / certain-consistent
        g_lo = lower_steps(i_h, hor) - Tm        # true T_h > lower_steps; true T_m <= Tm
        g_lo = np.where(i_h == k, np.inf, g_lo)  # censored hybrid: > H_max
        b_hi = H1 - lower_steps(i_m, hor)
        cert_viol = pos & (g_lo >= b_hi) & np.isfinite(g_lo)
        d = {
            "n_Tm_uncensored": int(okm.sum()),
            "n_H1_censored(bound infinite, not testable)": int((okm & cens1).sum()),
            "n_tested(C>=0 at H1)": int(pos.sum()),
            "n_C_negative_at_H1(hypothesis fails)": int(neg.sum()),
            "violations_among_tested": int(viol.sum()),
            "violations_among_C_negative": int(viol_neg.sum()),
            "tested_gain_zero": int((pos & (G == 0)).sum()),
            "tested_gain_positive": int((pos & (G > 0)).sum()),
            "tested_bound_positive(informative: H1 in a later grid cell than T_m)": int((pos & (B > 0)).sum()),
            "tested_gain_equals_bound_and_positive(tight)": int((pos & (G == B) & (B > 0)).sum()),
            "tested_gain_equals_bound_both_zero(vacuous)": int((pos & (G == 0) & (B == 0)).sum()),
            "tested_bound_positive_and_gain_zero(slack)": int((pos & (B > 0) & (G == 0)).sum()),
            "tested_gain_steps_distribution": {str(int(v)): int(((G == v) & pos).sum())
                                               for v in np.unique(G[pos & np.isfinite(G)])},
            "tested_bound_steps_distribution": {str(int(v)): int(((B == v) & pos).sum())
                                                for v in np.unique(B[pos & np.isfinite(B)])},
            "certain_violations_after_bracketing_true_steps": int(cert_viol.sum()),
        }
        # reported-only study screen ln2/(2 Lambda_bar) on tested states (grid-resolved)
        scr = pos & (Lam > 0)
        d["screen_ln2_over_2Lambda: n"] = int(scr.sum())
        d["screen: gain > ln2/(2 Lambda_bar) (grid-resolved)"] = int((scr & (G > np.log(2) / (2 * np.where(Lam > 0, Lam, 1)))).sum())
        out[name] = d
    out["note_resolution"] = ("gains and bounds are differences of grid points {8,15,30,60,120}; "
                              "adjacent gaps 7,15,30,60 steps (0.23, 0.5, 1, 2 LT)")
    return out


# ----------------------------------------------------------------- (b) N4
def part_b(EC, EP, C, hor, Lam, ref, sweeps, rho=RHO_CORE, theta=THETA):
    n, k = EC.shape
    env = np.minimum(EC, EP)
    hyb, w = hybrid(EC, EP, C)
    f, rr, r = f_corr(EC, EP, C)
    interior = (C <= env) & (EC + EP - 2 * C > 0)
    ratio = hyb / env
    out = {"identity_rows_interior": int(interior.sum()), "identity_rows_total": int(interior.size),
           "identity_max_abs_diff(V/min vs f)": float(np.max(np.abs(ratio[interior] - f[interior]))),
           "rows_with_C_gt_min(clipped, f not exact)": int((~interior).sum())}
    t2 = theta**2 - rho**2
    i_m = first_passage(env, t2)
    i_h = first_passage(hyb, t2)
    ok = i_m < k
    rows = np.arange(n)
    fj = np.where(ok, f[rows, np.minimum(i_m, k - 1)], np.nan)
    fj_valid = ok & np.isfinite(fj) & interior[rows, np.minimum(i_m, k - 1)]
    # predicted: first grid step with envelope mse > (theta^2 - rho^2)/f_j
    thr = np.where(fj_valid, t2 / np.where(fj_valid, fj, 1), np.inf)
    ex = env > thr[:, None]
    i_p = np.where(ex.any(1), ex.argmax(1), k)
    Tm, Th, Tp = steps(i_m, hor), steps(i_h, hor), steps(i_p, hor)
    # hypothesis of N4(b): f at the step T_pred >= f_j
    f_at_p = np.where(i_p < k, f[rows, np.minimum(i_p, k - 1)], np.nan)
    hyp = fj_valid & (i_p < k) & (f_at_p >= fj)
    viol = hyp & (Th > Tp)
    out.update({
        "n_Tm_uncensored": int(ok.sum()),
        "n_f_valid_at_crossing": int(fj_valid.sum()),
        "n_pred_uncensored": int((fj_valid & (i_p < k)).sum()),
        "n_hypothesis_met(f(T_pred)>=f_j)": int(hyp.sum()),
        "violations_of_bound_T_h<=T_pred": int(viol.sum()),
        "f_at_crossing_quantiles5_25_50_75_95": wquant(fj[fj_valid]),
        "rho_at_crossing_quantiles": wquant(rr[rows, np.minimum(i_m, k - 1)][fj_valid]),
        "pred_gain_zero": int((hyp & (Tp - Tm == 0)).sum()),
        "realized_gain_equals_pred(grid) among hyp": int((hyp & ((Th - Tm) == (Tp - Tm))).sum()),
        "realized_gain_less_than_pred among hyp": int((hyp & ((Th - Tm) < (Tp - Tm))).sum()),
        "realized_gain_zero among hyp": int((hyp & (Th - Tm == 0)).sum()),
        "pred_bound_steps_distribution": {str(int(v)): int((hyp & ((Tp - Tm) == v)).sum())
                                          for v in np.unique((Tp - Tm)[hyp])},
        "realized_gain_steps_distribution": {str(int(v)): int((hyp & ((Th - Tm) == v)).sum())
                                             for v in np.unique((Th - Tm)[hyp & np.isfinite(Th - Tm)])},
    })
    # library dependence at H_ref (sweep H_ref moments only)
    lib = {}
    for (rho_s, nl), g in sweeps.items():
        m = len(g["E_C"])
        ec, ep, c_ = g["E_C"], g["E_P"], g["C"]
        mn = np.minimum(ec, ep)
        inter = (c_ <= mn) & (ec + ep - 2 * c_ > 0)
        fs, rs, rr_ = f_corr(ec, ep, c_)
        lam = Lam[:m]
        pe = np.where(inter & (lam > 0) & (fs > 0), np.log(1 / np.where(fs > 0, fs, 1)) / (2 * np.where(lam > 0, lam, 1)), np.nan)
        lib[f"rho={rho_s:g}|n_lib={nl}"] = {
            "n_states": int(m), "frac_C_negative": float((c_ < 0).mean()),
            "frac_interior(C<=min)": float(inter.mean()),
            "median_varrho_raw": float(np.median(rs)),
            "median_r": float(np.median(rr_)),
            "median_f(interior)": float(np.median(fs[inter])),
            "median_hybrid_ratio_V/min(clipped weight)": float(np.median(hybrid(ec[:, None], ep[:, None], c_[:, None])[0][:, 0] / mn)),
            "median_exp_gain_ln(1/f)/(2Lambda_bar)_steps(Lambda>0,interior)": float(np.nanmedian(pe)),
            "n_exp_pred": int(np.isfinite(pe).sum()),
        }
    out["library_dependence_H_ref"] = lib
    # paired change from smallest to largest library, per rho
    paired = {}
    for rho_s in sorted({k_[0] for k_ in sweeps}):
        ns = sorted(nl for (r_, nl) in sweeps if r_ == rho_s)
        if len(ns) < 2:
            continue
        a, b = sweeps[(rho_s, ns[0])], sweeps[(rho_s, ns[-1])]
        fa, fb = [np.minimum(x["E_C"], x["E_P"]) for x in (a, b)], None
        f1 = f_corr(a["E_C"], a["E_P"], a["C"])
        f2 = f_corr(b["E_C"], b["E_P"], b["C"])
        ia = (a["C"] <= np.minimum(a["E_C"], a["E_P"]))
        ib = (b["C"] <= np.minimum(b["E_C"], b["E_P"]))
        both = ia & ib
        paired[f"rho={rho_s:g}: n_lib {ns[0]} -> {ns[-1]}"] = {
            "n_pairs(both interior)": int(both.sum()),
            "median_paired_change_in_f": float(np.median(f2[0][both] - f1[0][both])),
            "frac_f_increased": float((f2[0][both] > f1[0][both]).mean()),
            "median_paired_change_in_varrho": float(np.median(f2[1][both] - f1[1][both])),
            "frac_varrho_increased": float((f2[1][both] > f1[1][both]).mean()),
        }
    out["paired_library_change"] = paired
    return out


# ----------------------------------------------------------------- (c) N6
def wmean_leaf(u, wt, leaf):
    """Per-leaf c-weighted mean of u, broadcast back; also the identity pieces."""
    uleaf = np.zeros_like(u)
    for l in np.unique(leaf):
        s = leaf == l
        uleaf[s] = (wt[s] * u[s]).sum() / wt[s].sum()
    return uleaf


def rc2_from_fit(u, wt, fit):
    ub = (wt * u).sum() / wt.sum()
    tot = (wt * (u - ub) ** 2).sum()
    flo = (wt * (u - fit) ** 2).sum()
    btw = (wt * (fit - ub) ** 2).sum()
    return {"excess_global": tot / len(u), "floor": flo / len(u), "between": btw / len(u),
            "R_c2": 1 - flo / tot, "pythagoras_residual": float((tot - flo - btw) / tot)}


def cart_fit(F, u, wt, K):
    t = DecisionTreeRegressor(max_leaf_nodes=K, min_samples_leaf=max(10, len(u) // 50), random_state=0)
    t.fit(F, u, sample_weight=wt)
    return t


def cart_scores(F, u, wt, K, group):
    """In-sample R_c^2 and two-fold (contiguous halves of states) cross-fitted R_c^2."""
    t = cart_fit(F, u, wt, K)
    ins = rc2_from_fit(u, wt, t.predict(F))["R_c2"]
    sse_t = sse_g = 0.0
    for a in (0, 1):
        tr, te = group == a, group != a
        tt = cart_fit(F[tr], u[tr], wt[tr], K)
        ub = (wt[tr] * u[tr]).sum() / wt[tr].sum()
        sse_t += (wt[te] * (u[te] - tt.predict(F[te])) ** 2).sum()
        sse_g += (wt[te] * (u[te] - ub) ** 2).sum()
    return ins, 1 - sse_t / sse_g, int(t.get_n_leaves())


def part_c(z, hor, ref):
    EC, EP, C = (z["core/" + k][:, ref] for k in ("E_C", "E_P", "C"))
    n = len(EC)
    c = EC + EP - 2 * C
    u = (EP - C) / c
    out = {"n_states": int(n), "n_c_nonpositive_or_nonfinite": int((~(c > 0) | ~np.isfinite(u)).sum()),
           "frac_u_outside_[0,1](clipped states; N6 assumes none)": float(((u < 0) | (u > 1)).mean()),
           "frac_u_lt_0": float((u < 0).mean()), "frac_u_gt_1": float((u > 1).mean())}
    keep = (c > 0) & np.isfinite(u)
    Fo = z["qn/oracle/x_test"]
    Fd = z["core/profile"]                         # (n, E, 4)
    E = Fd.shape[1]
    half = (np.arange(n) >= n // 2).astype(int)
    res = {}
    for subset, mask in (("all_states", keep), ("interior_only(u in [0,1])", keep & (u >= 0) & (u <= 1))):
        for prof in ("oracle", "deployable"):
            if prof == "oracle":
                F, uu, wt, grp = Fo[mask], u[mask], c[mask], half[mask]
                good = np.isfinite(F).all(1)
                F, uu, wt, grp = F[good], uu[good], wt[good], grp[good]
                leaf = None
            else:
                Fp = Fd[mask].reshape(-1, 4)
                uu = np.repeat(u[mask], E)
                wt = np.repeat(c[mask], E)
                grp = np.repeat(half[mask], E)
                good = np.isfinite(Fp).all(1)
                F, uu, wt, grp = Fp[good], uu[good], wt[good], grp[good]
                leaf = np.asarray(z["core/a5_leaf"])[mask].reshape(-1)[good]
            d = {"n_points": int(len(uu)), "n_nonfinite_profile_rows_dropped": int((~good).sum())}
            ub = (wt * uu).sum() / wt.sum()
            d["best_global_weight_ubar"] = float(ub)
            d["excess_global_E[c(u-ubar)^2]"] = float((wt * (uu - ub) ** 2).sum() / len(uu))
            X = np.column_stack([np.ones(len(uu)), F])
            sw = np.sqrt(wt)
            beta = np.linalg.lstsq(X * sw[:, None], uu * sw, rcond=None)[0]
            d["linear_weighted_R_c2(in-sample)"] = rc2_from_fit(uu, wt, X @ beta)["R_c2"]
            sse_l = sse_g = 0.0
            for a_ in (0, 1):
                tr, te = grp == a_, grp != a_
                bt = np.linalg.lstsq(X[tr] * sw[tr, None], uu[tr] * sw[tr], rcond=None)[0]
                ubt = (wt[tr] * uu[tr]).sum() / wt[tr].sum()
                sse_l += (wt[te] * (uu[te] - X[te] @ bt) ** 2).sum()
                sse_g += (wt[te] * (uu[te] - ubt) ** 2).sum()
            d["linear_weighted_R_c2(cross_fit_halves)"] = 1 - sse_l / sse_g
            if leaf is not None:
                ul = wmean_leaf(uu, wt, leaf)
                lf = rc2_from_fit(uu, wt, ul)
                lf["n_leaves"] = int(len(np.unique(leaf)))
                # clip-consistent regrets (exact excess_mse definition): leaf weight and global
                # weight clipped to [0,1] as in P3(a); comparable with the observed rule regrets
                ucl = np.clip(uu, 0, 1)
                lf["regret_clip_leaf_map_in_sample"] = float(np.mean(wt * ((np.clip(ul, 0, 1) - uu) ** 2 - (ucl - uu) ** 2)))
                lf["regret_clip_best_global"] = float(np.mean(wt * ((np.clip(ub, 0, 1) - uu) ** 2 - (ucl - uu) ** 2)))
                d["stored_A5_leaf_map(in-sample on test)"] = lf
            d["cart_by_K(in_sample, cross_fit_halves, leaves)"] = {
                str(K): [round(v, 6) if isinstance(v, float) else v for v in cart_scores(F, uu, wt, K, grp)] for K in KS}
            res[f"{subset}/{prof}"] = d
    out["R_c2"] = res
    # observed regret of stored rules at H_ref (excess over A*, oracle moments, exact definition)
    uc = np.clip(u, 0, 1)
    reg = {}
    for rule in ("A2", "A3", "A4", "A5"):
        w = z[f"core/weight_href/{rule}"]
        ex = c[:, None] * ((w - u[:, None]) ** 2 - (uc[:, None] - u[:, None]) ** 2)
        d = {"mean_excess_oracle_moments": float(np.mean(ex[keep]))}
        sm = z[f"core/state_mse/{rule}"][:, ref] - z["core/state_mse/A*"][:, ref]
        d["mean_realized_state_mse_minus_A*"] = float(np.mean(sm[keep]))
        reg[rule] = d
    out["observed_regret_H_ref"] = reg
    out["A5_distinct_leaves_in_test"] = int(len(np.unique(z["core/a5_leaf"])))
    return out


# ----------------------------------------------------------------- (d) N8
def part_d(z, sweeps):
    rhos = sorted({r for (r, nl) in sweeps if nl == 10000})
    W = np.column_stack([sweeps[(r, 10000)]["w_star_href"] for r in rhos])
    nS = W.shape[0]
    N = z["core/N"][:nS]
    rs = row_spearman(W)
    nz = N[N >= STABLE_N]
    med = float(np.median(nz)) if nz.size else float("nan")
    groups = {"N=0 (analog never changes under noise; stable proxy)": N < STABLE_N,
              "N>0 low (<= median positive N)": (N >= STABLE_N) & (N <= med),
              "N>0 high (> median positive N)": N > med}
    out = {"rho_levels": rhos, "n_states": int(nS), "median_positive_N": med,
           "N_zero_threshold": STABLE_N,
           "frac_wstar_zero_at_all_levels": float((W.max(1) == 0).mean())}
    mono = (np.diff(W, axis=1) >= 0).all(1)
    inc = (np.diff(W, axis=1) > 0).mean(1)
    gs = {}
    for name, m in groups.items():
        r = rs[m]
        d = {"n": int(m.sum()), "n_rank_corr_defined": int(np.isfinite(r).sum()),
             "n_constant_w(undefined)": int((~np.isfinite(r)).sum()),
             "median_spearman": float(np.nanmedian(r)) if np.isfinite(r).any() else float("nan"),
             "q25_q75_spearman": [float(v) for v in np.nanpercentile(r, [25, 75])] if np.isfinite(r).any() else None,
             "frac_spearman_eq_+1": float((r[np.isfinite(r)] > 1 - 1e-9).mean()) if np.isfinite(r).any() else float("nan"),
             "frac_spearman_gt_0": float((r[np.isfinite(r)] > 0).mean()) if np.isfinite(r).any() else float("nan"),
             "frac_nondecreasing_in_rho": float(mono[m].mean()) if m.any() else float("nan"),
             "mean_frac_of_steps_increasing": float(inc[m].mean()) if m.any() else float("nan")}
        gs[name] = d
    out["groups"] = gs
    out["median_wstar_by_rho"] = {f"{r:g}": float(np.median(W[:, i])) for i, r in enumerate(rhos)}
    return out


# ----------------------------------------------------------------- loading
SW = re.compile(r"^sweep/rho=([0-9.eE+-]+)\|n_lib=(\d+)/E_C$")


def load_sweeps(z):
    out = {}
    for k in z.files:
        m = SW.match(k)
        if m:
            g = k[:-len("E_C")]
            out[(float(m.group(1)), int(m.group(2)))] = {
                nm: z[g + nm] for nm in ("E_C", "E_P", "C", "w_star_href")}
    return out


def run_dump(path, tag):
    z = np.load(path)
    sys_name, seed = str(z["meta/system"]), str(z["meta/seed_id"])
    hor = z["core/horizons"]
    ref = int(z["core/ref_index"])
    EC, EP, C = (z["core/" + k] for k in ("E_C", "E_P", "C"))
    Lam = z["core/Lambda_bar"]
    sw = load_sweeps(z)
    res = {"label": LABEL, "system": sys_name, "seed_id": seed, "preset": str(z["meta/preset"]),
           "dump": str(path), "n_states": int(EC.shape[0]), "horizons": [int(h) for h in hor],
           "nonfinite_in_E_C_E_P_C": int((~np.isfinite(EC)).sum() + (~np.isfinite(EP)).sum() + (~np.isfinite(C)).sum())}
    # consistency checks of the stored arrays
    c = EC + EP - 2 * C
    w = np.clip((EP - C) / np.maximum(c, 1e-300), 0, 1)
    res["check_wstar_recomputed_max_abs_diff"] = float(np.nanmax(np.abs(w - z["core/w_star"])))
    g = sw.get((RHO_CORE, 10000))
    if g is not None:
        nS = len(g["E_C"])
        res["check_sweep_core_view_E_C_max_abs_diff"] = float(np.max(np.abs(g["E_C"] - EC[:nS, ref])))
        res["check_sweep_core_view_w_star_max_abs_diff"] = float(np.max(np.abs(g["w_star_href"] - z["core/w_star"][:nS, ref])))
    res["a_P1dprime"] = part_a(EC, EP, C, hor, Lam)
    res["b_N4"] = part_b(EC, EP, C, hor, Lam, ref, sw)
    res["c_N6"] = part_c(z, hor, ref)
    res["d_N8"] = part_d(z, sw)
    return res


# --------------------------------------------------------------- self-test
def selftest():
    """Known-answer checks (independent references stated in each block)."""
    msgs = []
    hor = np.array([8, 15, 30, 60, 120])
    rho = RHO_CORE
    # T1: grid first passage == lpcstudy.oracle.characteristic_horizon on contiguous horizons.
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from lpcstudy.oracle import characteristic_horizon
    rng = np.random.default_rng(1)
    mse = np.cumsum(rng.random((200, 120)) * 0.01, axis=1) * rng.random((200, 1))
    ref_t, ref_ev = characteristic_horizon(mse, np.arange(1, 121), rho, THETA)
    i = first_passage(mse, THETA**2 - rho**2)
    mine = np.where(i < 120, i + 1, 120)
    # tolerance: exact integer equality except sqrt(mse+rho^2)>theta vs mse>theta^2-rho^2 at
    # round-off ties (measure zero for random floats); expect 0 mismatches
    assert (mine == ref_t).all(), "T1 first passage differs from oracle.characteristic_horizon"
    msgs.append("T1 ok: first passage equals oracle.characteristic_horizon on 200 random curves (0 mismatches)")
    # T2: manufactured gain 60 = bound 60 (EC=EP=m2, C=0 => h2=m2/2). Hand-computed:
    # theta'^2 = .04-1e-4 = .0399 ; m2(60)=.06 crosses at 60; h2(60)=.03<.0399 -> crosses at 120 ;
    # study rule at sqrt2 theta: mse > .0799 -> 120. gain=120-60=60, bound=120-60=60.
    m2 = np.array([[0.001, 0.002, 0.003, 0.06, 0.5]])
    out = part_a(m2, m2, np.zeros_like(m2), hor, np.array([0.05]))
    d = out["study_rule_sqrt2_theta"]
    assert d["n_tested(C>=0 at H1)"] == 1 and d["violations_among_tested"] == 0
    assert d["tested_gain_equals_bound_and_positive(tight)"] == 1 and d["tested_gain_steps_distribution"] == {"60": 1}, d
    msgs.append("T2 ok: manufactured gain 60 steps = bound 60 steps, 0 violations, flagged tight")
    # T3: C<0 with C=-0.9 m2: f=(1-.81)/(2+1.8)=0.05 exactly (hand formula), h2=.05 m2.
    C3 = -0.9 * m2
    out = part_a(m2, m2, C3, hor, np.array([0.05]))
    d = out["study_rule_sqrt2_theta"]
    assert d["n_C_negative_at_H1(hypothesis fails)"] == 1 and d["violations_among_C_negative"] == 1 and d["n_tested(C>=0 at H1)"] == 0, d
    fv = f_corr(m2, m2, C3)[0]
    assert np.allclose(fv, 0.05, atol=1e-14)
    hy = hybrid(m2, m2, C3)[0] / m2
    assert np.allclose(hy, 0.05, atol=1e-12)      # round-off: few ops, 1e-12 generous
    msgs.append("T3 ok: C<0 state classified outside hypothesis, bound exceeded there; f=0.05 and V/min=0.05")
    # T3b: N4 part_b identity + gain prediction on T2 data: f=1/(1+1)=.5 at crossing (idx 3),
    # predicted threshold .0399/.5=.0798 -> first env> .0798 is idx 4 (120): pred gain 60 = realized 60.
    outb = part_b(m2, m2, np.zeros_like(m2), hor, np.array([0.05]), 2, {})
    assert outb["identity_max_abs_diff(V/min vs f)"] < 1e-12
    assert outb["n_hypothesis_met(f(T_pred)>=f_j)"] == 1 and outb["violations_of_bound_T_h<=T_pred"] == 0
    assert outb["realized_gain_equals_pred(grid) among hyp"] == 1
    msgs.append("T3b ok: N4 identity to 1e-12; predicted gain 60 = realized 60")
    # T4: N6. Piecewise-constant u on two cells => leaf-map R_c^2 = 1; CART K=2 recovers it.
    rng = np.random.default_rng(2)
    n = 4000
    F = rng.normal(size=(n, 4))
    cw = rng.random(n) + 0.1
    u = np.where(F[:, 0] > 0, 0.8, 0.2)
    assert abs(rc2_from_fit(u, cw, wmean_leaf(u, cw, (F[:, 0] > 0).astype(int)))["R_c2"] - 1) < 1e-12
    ins, cf, nl = cart_scores(F, u, cw, 2, (np.arange(n) >= n // 2).astype(int))
    assert ins > 0.999 and cf > 0.999
    # independent u: expected in-sample R^2 of the best split ~ 2 ln n / n ~ 0.004; tol 0.02 (5x)
    un = rng.random(n)
    ins2, cf2, _ = cart_scores(F, un, cw, 2, (np.arange(n) >= n // 2).astype(int))
    assert ins2 < 0.02 and cf2 < 0.02
    # Pythagoras identity on random partition: round-off only
    lf = rng.integers(0, 5, n)
    p = rc2_from_fit(un, cw, wmean_leaf(un, cw, lf))
    assert abs(p["pythagoras_residual"]) < 1e-12
    msgs.append("T4 ok: R_c2=1 for u constant on cells; independent u gives R_c2<0.02; Pythagoras residual < 1e-12")
    # T5: row Spearman against scipy.stats.spearmanr on random rows, and monotone known answers.
    Wt = rng.random((50, 4))
    mine5 = row_spearman(Wt)
    ref5 = np.array([spearmanr(np.arange(4), r)[0] for r in Wt])
    assert np.allclose(mine5, ref5, atol=1e-12)
    known = row_spearman(np.array([[0.1, 0.2, 0.3, 0.9], [0.9, 0.5, 0.2, 0.0], [0, 0, 0, 0.0]]))
    # round-off of a few flops: 1e-12
    assert abs(known[0] - 1) < 1e-12 and abs(known[1] + 1) < 1e-12 and np.isnan(known[2])
    msgs.append("T5 ok: row Spearman equals scipy.stats.spearmanr (1e-12); +1, -1, NaN-for-constant known cases")
    return msgs


# -------------------------------------------------------------------- main
def fmt(v):
    if isinstance(v, float):
        return f"{v:.4g}"
    if isinstance(v, list):
        return "[" + ", ".join(fmt(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k}: {fmt(x)}" for k, x in v.items()) + "}"
    return str(v)


def md_flat(d, indent=0):
    lines = []
    for k, v in d.items():
        if isinstance(v, dict) and v and all(isinstance(x, dict) for x in v.values()):
            lines.append("  " * indent + f"- **{k}**")
            lines += md_flat(v, indent + 1)
        else:
            lines.append("  " * indent + f"- {k}: {fmt(v)}")
    return lines


def main():
    # inf - inf = NaN occurs only on states masked out of every count (censored first passage)
    np.seterr(invalid="ignore")
    full, pilot, outdir = (Path(a) for a in sys.argv[1:4])
    outdir.mkdir(parents=True, exist_ok=True)
    print(LABEL)
    for m in selftest():
        print(m)
    allres = {}
    md = [f"# Tables (generated by theory_dump_checks.py)\n\n{LABEL}\n"]
    for root, tag in ((full, "DEV-2 full"), (pilot, "DEV-1 pilot")):
        for s in SYSTEMS:
            p = root / f"{s}.npz"
            print("running", tag, s, flush=True)
            r = run_dump(p, tag)
            allres[f"{tag}/{s}"] = r
            md.append(f"\n## {tag}, {s} ({r['n_states']} test states)\n")
            md += md_flat({k: v for k, v in r.items() if k not in ("label",)})
    (outdir / "results.json").write_text(json.dumps(allres, indent=1, default=float))
    (outdir / "tables.md").write_text("\n".join(md) + "\n")
    print("wrote", outdir)


if __name__ == "__main__":
    main()
