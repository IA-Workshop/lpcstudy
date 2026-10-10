# Rulings for the owner's review (2026-10-10)

Prepared by claude-sonnet-5-5 (main session) for the human owner. Every row is a **proposal**; agents do not change criteria, decision rules or adopted governance (LPC.AI.12, GOV.49). Where a ruling changes adopted text (ROADMAP.md, v3, M2, DEVELOPMENT_WORKFLOW §4.2, `.claude/`), the amendment is the owner's edit; the wording is drafted below.

How I will record what you decide: one `DEC-nnnn` entry per ruling in `docs/agent/records/decisions.md` quoting your words (on the `develop` branch, merged to `main` only with your authorization), and the WU-0002 plans will cite them. Ledger entries (`authorization`, `ruling`, `note`) are yours to append; commands are in part C.

Evidence base: the concordance (`2026-10-10-v3-concordance.md`, D-01 to D-28), the applied-mathematician's analysis (`2026-10-10-math-view-referral-rulings.md`, on `develop`), the WU-0014 referral. **Not verified anywhere:** the effect of any new definition on the pilot's per-state statistics, because `pilot_results_v1.json` holds summaries only (no per-state w*, ε_s, δ, Λ̃). Effects shown come from synthetic models, a numpy RK4 stand-in for the three systems, or source reads, as marked.

## A. The WU-0014 referral (five items). Blocks parts of WU-0002.8, .9 and .10

| # | Question | Proposed ruling | Changes | Needs a number or choice from you |
| --- | --- | --- | --- | --- |
| A1 | Boundary convention (D-22) | One set rule for every criterion: **pass iff the interval lies inside the band; fail iff it misses the band entirely; otherwise inconclusive**, with each band exactly as v3 §2 writes it (strict for H2a, H2b, H2c, H2e, H3a; closed for H1b to H1d, H2d, H3c). H1a's ±25% band closed. Compare unrounded float64 values. K-rule tie counts as inside. | WU-0002.9 plan. No pilot effect. An open versus closed band is immaterial in practice: endpoints are continuous bootstrap quantiles, and their Monte Carlo SD at 2000 resamples (0.06 to 0.09 bootstrap SD) dwarfs any edge convention. | Confirm, or say which criterion you want different. |
| A2 | ROADMAP wording (D-23, D-27, D-28) | WU-0002.8 check becomes "no key for v1 H3b (p_eff)", since v3 has its own H3b (tree importances). WU-0002.1's "v3 drops E5" reads "v2 E5 (shift)". WU-0002.10's plan adds V7 slope-part and per-ρ tests (a strengthening). | ROADMAP rows (your edit) | Adopt the three wording changes. |
| A3 | Verdicts for non-interval criteria and for statistics that cannot be computed (D-24, D-18) | A statistic that cannot be computed is **inconclusive**, with reason and count recorded. A subset statistic needs at least **50 states (10 blocks of 5)** or it is inconclusive. Failed bootstrap resamples are counted at the unfavourable tail (today they are dropped silently, `statistics.py:161`). **H3a:** pass as v3 writes it, otherwise inconclusive; "fail" exists only if you set an equivalence margin on the regime-to-regime restricted-mean-survival-time difference. **H3b:** block-bootstrap intervals over refitted trees for the two importance criteria, with the stability fraction reported. | WU-0002.9 and the H3 code. Pilot: H3a "fail" on all three systems becomes "inconclusive"; the statistic itself is unchanged. | (i) The minimum count (50 proposed). (ii) Whether H3a may ever fail, and if so the margin. (iii) Fixed leaf count for the H3b trees (8 proposed; today `max(K, 4)` ties the importances to the data-chosen K). |
| A4 | Undocumented code definitions that change tested statistics (D-25) | See A4(a) to (i) below. | | |
| A5 | v3 silent or imprecise where M2 is specific (D-26) | M2 governs where v3 is silent. **K rule = calibration excess MSE within 5% of the minimum** (M2 §M7), not v3 §5's literal "calibration error" (total MSE would be 1.6 to 4.9 times looser on the pilot, from test-split curves, illustrative only). **State spacing = max(5·min(τ_ac, 1 LT), 1 LT)**, as the code does; block length 5 stays (at the coded spacings |ACF| ≤ 0.08, block-5 variance within 15% of iid, on a proxy statistic with numpy RK4; per-state w* not checked). **H1a "at both ρ"**, as M2 and E2 (the mathematician leans this way; ρ = 2% is less well identified). | v3 §4 and §5 text (your edit); no pilot effect | Confirm, especially "both ρ". |

### A4 detail: the definitions

| | Definition today | Proposed | Why | Effect |
| --- | --- | --- | --- | --- |
| (a) | Logit of w\* with w\* clipped to [0.01, 0.99]; 22 to 36% of pilot states have w\* = 0 | **Two-part test**, for H2a(ii) and for Q-N: (ii-a) partial correlation of the indicator 1{w\*=0} with Λ̃ given the seeds, over all states; (ii-b) partial correlation of logit w\* on states with 0 < w\* < 1. Both intervals inside (−0.1, 0.1) to pass; fail if either is entirely outside. Counts of w\*=0 and w\*=1 reported; add a third part for w\*=1 if it exceeds 5% of states. Q-N reports ΔR² for the interior logit and for the indicator. | The clip constant decides the verdict: on a synthetic model the statistic moves from 0.077 to 0.141 (across the 0.1 bound) as the clip goes from 1e-4 to 0.05, and the Q-N reading flips at the 0.05 edge. Interior-only misses an instability effect that acts only on the zero mass (reads 0.000 while the true effect is large). | Replaces the primary criterion H2a(ii) as v3 writes it (a v3 text amendment). Pilot H2a verdict does not depend on (ii): Rössler and Chua fail on (i). Q-N values change. [synthetic; pilot not verified] |
| (a2) | "Given both seeds" is a linear partial correlation | **Residualize on quadratic seed controls** (x, x², x₁x₂), fixed before the freeze | If the true relations are nonlinear, the linear version is biased under the null by −0.04 to −0.07 (and +0.08 for the indicator), a large part of the ±0.1 band; quadratic controls reduce it to ≤ 0.0012 in the synthetic model | A beyond-the-referral change to the test; whether E[Λ̃\|x] is nonlinear on the real systems is **not verified** |
| (b) | H2a(i) small-error regime applied per (state, horizon), at least 2 small-error horizons, range over those only, bootstrap over eligible states | Keep the rule, restricted to **initial segments** ({1,2} or {1,2,4} LT), report the median and count per span, bootstrap over all test states in time order with eligibility re-evaluated inside each resample; report the complete-case {1,2,4} version as a sensitivity | A non-contiguous set like {1,4} violates assumption A6; spans mix with Λ̃, which is the variable under test | Small pilot change; eligible count can only fall |
| (c) | Q-N gradient boosting has `l2_regularization=1.0` | Document it in M2 E3 before the freeze | Pre-data estimator choice; null ΔR² ≈ 0 with it | None |
| (d) | A5 tree: two-output CART on standardized (w\*(H_ref), log T), `min_samples_leaf = max(10, nE/50)` | Document and flag: its split criterion is not P3's curvature-weighted regret (the H3b weight tree is curvature-weighted) | | None |
| (e) | H3b trees `max_leaf_nodes = max(K, 4)` | **Change to a fixed leaf count** (8 proposed) | Impurity importances depend on tree size; tying them to K makes H3b depend on the K rule | H3b numbers change |
| (f) | H3a log-rank on the first evaluation draw | Keep and document | One observation per state keeps the test valid; costs power | None |
| (g) | E6 ±5%/±10% perturbation: one random sign per parameter | Keep; document the sign vector and seed | Reported only; one draw of the model-error direction | None |
| (h) | H1a's "independently estimated 1/d": median Levina–Bickel over test-sweep states, a point value without interval | **Use the mean of the per-state 1/d estimates, and pass if the interval of the ratio (1/d_fit)/(1/d_LB) lies inside [0.75, 1.25], bootstrapped jointly** | The median is biased low by 3.6%, which inflates 1/d by 3.7% and uses 15% of the ±25% band; the reference's variance is negligible (0.9 to 1.7%) | No pilot H1a verdict changes (inconclusive either way). Finite-N and curvature bias on the real attractors is **not verified** (epistemic). |
| (i) | H2c "better single forecaster" chosen on the same test means it is then tested on | Choose on the calibration split, or recompute inside each resample | Selecting the smaller mean on the same data biases the comparison (conservatively, but not pre-specified) | None on the pilot (A1 wins at 1 LT by 2 to 14× on every system) |

## B. Defects that need a design choice

| Defect | Options | Recommendation |
| --- | --- | --- |
| **DEF-0010**: seeds of 2³² or more crash scikit-learn (`random_state` limit), at `analysis.py:295`, `:678`, `:680`, `allocation.py:358`. DEV-1 to DEV-4 and any 62-bit confirmatory seed. Blocks the WU-0003 rehearsal. | **A.** Derive a 32-bit `random_state` from `make_rng(seed, "sklearn", label)` for every seed, DEV-0 included. Uniform and in line with the make_rng rule; DEV-0's scikit-learn streams change, so the WU-0002.12 regression against the pilot cannot be bitwise for anything those streams touch. **B.** Use the raw seed when it is below 2³², the derived value otherwise. DEV-0 is unchanged, so the regression stays exact, and the DEV-1 rehearsal exercises the same derived path the confirmatory run will use. Two code paths, pinned by a test. **C.** Restrict seeds to below 2³². Not recommended: the DEV values are already registered and recorded, and it cuts entropy. | **B**, because the pilot regression is the only anchor that the code still computes what the pilot computed. A is the cleaner design if you accept a non-bitwise scikit-learn part. |
| **DEF-0011**: the 1/d reference pool is drawn with `np.random.default_rng(0)` at `oracle.py:101`, outside `make_rng`; other `default_rng(seed)` call sites exist (`dynamics.py:147`, `validation.py:107,147`, `statistics.py:151`, `networks.py:145`, `experiments.py:88`) and have not been audited | **1.** Keep until the WU-0002.12 regression, then route through `make_rng(config.seed, "oracle-pool")` with the effect recorded. **2.** Change now (pilot-incompatible numbers for H1a's reference). **3.** Keep permanently and document the pool as seed-independent by design. | **1**, plus an audit of the other `default_rng` sites in WU-0002.11. |

## C. Confirmations and owner actions (no analysis needed)

| Item | Proposed | How |
| --- | --- | --- |
| DEC-0003 (blast-radius tool follows §4.2 as written) and the **Q2 gap**: a change to `systems.py` or `config.py` does not select `test_dynamics.py` or `test_embedding.py`, which import `systems` | Confirm DEC-0003. Amend §4.2 so a test file is also selected when a module it imports changes (only adds tests, ~1 s) | Edit §4.2 (adopted governance) |
| DEC-0004 (WU-0001 answers), DEC-0005 (WU-0012 answers), DEC-0006 (derived peak-RSS test bound) | Confirm all three | Reply, or append `ruling` entries |
| WU-0009.2 disposition | Accept the direct run of `tests/test_core.py` as the stand-in for `tools/run_tests.sh unit` (which could not exist before WU-0012). WU-0009 can then close. | Reply |
| Web retrieval cap (LPC.AUTH.2, 50 pages per unit) | Lift it, so the researcher can retrieve (i) the Chua Lyapunov exponent (not found yet), (ii) a cited AMI delay for Lorenz-63 (its test band is uncited), (iii) the XLA flag that caps CPU threads in jax 0.11.2. The cap is an adopted authorization: your statement in chat does not change it. alphaXiv tools are not in the `researcher` agent's tool list; adding them is a `.claude/agents/researcher.md` edit. | Append a ledger entry (below) and edit the agent file if you want alphaXiv |
| Ledger entries 4 and 6 carry the placeholders `<you>` and `...` | Append a `note` entry stating the actor and the full authorization list | Command below |
| Fields still blank in adopted files | Human owner name (`project-constitution.md:11`), agent operating-cost discipline (LPC.PC.23 and LPC.AUTH.4) | Edit and adopt |
| `.claude/` edits that are not mine to make | (1) the skills' `2>/dev/null \|\| echo` fallback hides `test_impact.py` errors (`test-impact` and `independent-review` skills); (2) `.claude/rules/test-discipline.md:18`, `.claude/skills/test-impact/SKILL.md:27`, `DEVELOPMENT_WORKFLOW.md` lines 89 and 138 and `ROADMAP.md` line 11 still name `tests/test_core.py` as the live suite; (3) §4.2's import-graph table needs rows for the new `seeds` and `provenance` modules; (4) settings and the hook still allow the old `flock ... python -m lpcstudy --preset` form, and GPU-tier test runs are not counted in the 60 GPU-hours | Owner edits |
| Not implemented, for you before the freeze | Refuse a confirmatory run on a dirty tree or unknown commit (DEC-0004 Q6). Also record `VmHWM` next to `ru_maxrss`, because a child process inherits its launcher's peak (DEC-0006). | Rulings |

### Ledger commands (for you to run; replace the placeholders)

```
python3 tools/ledger.py append --type authorization --actor "<name>" --role "human owner" \
  --authority "LPC.AUTH.2" \
  --summary "Lift the 50-pages-per-unit cap on researcher retrievals; researcher may use the alphaXiv connectors for papers (stated in session 2026-10-10)"

python3 tools/ledger.py append --type note --actor "<name>" --role "human owner" \
  --authority "GOV.36" \
  --summary "Entries 4 and 6 were appended with the placeholder actor and a truncated summary; the actor is <name> and the authorizations granted are: <list the LPC.AUTH identifiers>"
```

## What happens after your rulings

- WU-0002.1 (removals) and WU-0002.2 (the one identifier table) do not depend on any ruling above and can start as soon as you say go; I have not started them because you asked for the rulings first.
- The remaining WU-0002 sub-tasks are planned against your rulings: .3 (excess MSE, regime weight, K rule: A5), .4 and .5 (H1: A4(h)), .6 (Q-N: A4(a)), .7, .8 and .9 (A1, A3, A4(e), (i)), .10 (A2), .11 (counters: DEF-0001, plus the two uncounted cases in `statistics.py`).
- DEF-0010's fix is planned in WU-0002 per your choice in part B; the DEV-1 rehearsal (WU-0003) cannot run before it.
