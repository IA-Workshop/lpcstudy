import json, sys
r = json.load(open(sys.argv[1]))
f = lambda v: "-" if v is None else f"{v:.3g}"
ci = lambda row: f"[{f(row['ci'][0])}, {f(row['ci'][1])}]"
AB = {"undetermined": "und", "negligible": "negl", "small": "small", "substantial": "subst",
      "lowers": "lowers", "needed, size not determined": "needed",
      "no interaction gain; the pair model fits worse": "fits worse",
      "interaction gain detected": "DETECTED", "no interaction gain detected": "none"}
def rd(row):
    return AB.get(row["reading"], row["reading"]) + ("*" if row.get("reason") == "n_eff < 50" else "")
H = ("8", "30", "120")
print(r["label"], "| run commit", r["run"]["commit"][:7], "| analysis", r["analysis"]["commit"][:7], "dirty", r["analysis"]["dirty"])
print("\nChecks")
for s, res in r["systems"].items():
    c = res["checks"]; fl = []
    for h, b in res["allocation"].items():
        for rule, d in b["deployable"]["dependence_bias"].items():
            if d["reading"] != "no detectable dependence bias":
                fl.append(f"H={h} {rule}: {d['reading']} (t1+t2/V {f(d['dependence']['rel'])}, z {f(d['paired']['z'])})")
    print(f"- {s}: f1 {c['f1_state_mse']['within_1e-12']}, g drop-N {c['g_wu0039b']['drop_N_reproduced']} all {c['g_wu0039b']['all_rows_reproduced']}, {res['seconds']:.0f}s; (f2) flagged {len(fl)}: " + "; ".join(fl[:6]) + (" ..." if len(fl) > 6 else ""))
print("\nA. Allocation drop-one MSE(F\\X)/MSE(F) [CI 1-0.05/4] reading (* = n_eff<50); Shapley share of phi_A R/O/I/N")
print("| sys | H | prof | n_eff k / x~ | R | O | I | N | phi share R/O/I/N |"); print("|---|---|---|---|---|---|---|---|---|")
for s, res in r["systems"].items():
    for h in H:
        for k, b in res["allocation"][h].items():
            cells = [f"{f(b['drop_one'][x]['mse_ratio']['ratio'])} {ci(b['drop_one'][x]['mse_ratio'])} {rd(b['drop_one'][x]['mse_ratio'])}" for x in "ROIN"]
            sh = b["shapley_L_A"]["rows"]
            print(f"| {s} | {b['horizon']} | {k[:3]} | {f(b['n_eff_kappa'])} / {f(b['n_eff_constant_excess'])} | " + " | ".join(cells) + " | " + "/".join(f(sh[x]["share"]) for x in "ROIN") + " |")
print("\nB. Primary pairs, logit u interior: Delta [CI 1-0.05/6], Holm p, reading")
print("| sys | H | prof | R x I | O x I | other pairs detected |"); print("|---|---|---|---|---|---|")
for s, res in r["systems"].items():
    for h in H:
        for k, parts in res["interactions"][h].items():
            p = parts["logit"]["pairs"]; hz = res["allocation"][h][k]["horizon"]
            oth = ",".join(n for n, row in p.items() if row["detected"] and n not in ("RI", "OI")) or "none"
            cell = lambda n: f"{f(p[n]['difference'])} {ci(p[n])} p={f(p[n]['p_holm'])} {rd(p[n])}"
            print(f"| {s} | {hz} | {k[:3]} | {cell('RI')} | {cell('OI')} | {oth} |")
print("\nD. Allocation ladder, key rungs: MSE(rung)/MSE(F) [CI 1-0.05/m] reading; gaps (L_A)")
print("| sys | H | prof | constant | separation | RO | X+F | theory gap (UB) | estimation gap |"); print("|---|---|---|---|---|---|---|---|---|")
for s, res in r["systems"].items():
    for h in H:
        g = res["gaps"][h]
        for k, b in res["allocation"][h].items():
            v = b["ladder"]["vs_full"]
            cell = lambda n: f"{f(v[n]['mse_ratio']['ratio'])} {ci(v[n]['mse_ratio'])} {rd(v[n]['mse_ratio'])}"
            gap = (f"{f(g['theory_gap_upper_bound']['estimate'])} {ci(g['theory_gap_upper_bound'])}",
                   f"{f(g['estimation_gap']['estimate'])} {ci(g['estimation_gap'])}") if k == "oracle" else ("", "")
            print(f"| {s} | {b['horizon']} | {k[:3]} | {cell('none')} | {cell('separation')} | {cell('RO')} | {cell('X+F')} | {gap[0]} | {gap[1]} |")
print("\nHorizon (Y = ln min(T_c, 240)): drop-one pinball ratio [CI 1-0.05/4] reading; Harrell's C")
print("| sys | prof | R | O | I | N | C(F) | C(X+F) | C(Lyapunov rank) | pairs detected |"); print("|---|---|---|---|---|---|---|---|---|---|")
for s, res in r["systems"].items():
    for k, b in res["horizon"].items():
        cells = [f"{f(b['drop_one'][x]['pinball_ratio']['ratio'])} {ci(b['drop_one'][x]['pinball_ratio'])} {rd(b['drop_one'][x]['pinball_ratio'])}" for x in "ROIN"]
        det = ",".join(n for n, row in b["interactions"]["pairs"].items() if row["detected"]) or "none"
        print(f"| {s} | {k[:3]} | " + " | ".join(cells) + f" | {f(b['rows']['ROIN']['c_index']['c_index'])} | {f(b['rows']['X+F']['c_index']['c_index'])} | {f(b['lyapunov_rank']['c_index'])} | {det} |")
