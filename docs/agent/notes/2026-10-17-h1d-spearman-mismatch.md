# H1d `nhat` Spearman: the three reproduction MISMATCHES of the first real-run report (R1, DEV-1 pilot)

DEVELOPMENT (DEV-1; the R1 dump at develop c9bb981, read-only): not a hypothesis test. Agent: claude-sonnet-5-5 (developer of `tools/rehearsal_diagnostics.py`). Scripts and logs: `2026-10-17-h1d-spearman-mismatch-scripts/` (commands in its README). Nothing in `lpcstudy/` or the run directory was edited or written; no preset was run.

## 0. Answer

**The cause is a loss of order in the stored array, not a defect of the tool and not of production.** The dump stores `core/profile[:, :, 3] = log(N-hat + c)` with `c = NOISE_SENS_FLOOR = 1e-2` (`allocation.deployable_profile`), and production's H1d `nhat` pair uses the **raw** `ev.noise_sens[:, 0]` (`analysis.h1d_proxies`, line 741). The transform is strictly increasing in exact arithmetic but **not injective in float64** where `N-hat` is far below `c`: `log(N-hat + c)` resolves `N-hat` only to about `ulp(log c) c = 8.9e-18`. A large share of the states have `N-hat` at the round-off level (1e-15 to 1e-13: 211, 156 and 134 of 500 are below 1e-12, in Lorenz-63, Rössler and Chua). Several of those raw values differ by less than 9e-18, so they are distinct in production (distinct ranks) and tied in the dump (mid-ranks). That changes Spearman by 3.5e-6, 1.1e-5 and 8.6e-5.

## 1. Evidence

All three other H1d rows, which use `profile` columns 0 to 2 and the same code path, reproduce **bitwise** (`probe2.log`: `analog_seed`, `estimation_seed`, `growth`, differences 0.0), on every system. So the tool's ranks, the exclusion set (`n_states` 500, `n_excluded_nonfinite` 0 in both), the pairing with the dumped oracles and the mid-rank handling are right. The `nhat` oracle is `core/N` = `m.noise_sens`, the same array as production's.

| System | leaf (production, raw N-hat) | dump column 3 (mid-ranks) | difference | ties in column 3 (states in tied groups) | Spearman over all tie-breaks of column 3 |
| --- | --- | --- | --- | --- | --- |
| Lorenz-63 | 0.6253384767 | 0.6253419658 | +3.49e-6 | 33 (60 states in 27 groups) | [0.625044, 0.625638]: contains the leaf |
| Rössler | 0.6229817515 | 0.6229708429 | −1.09e-5 | 33 (56 states in 23 groups) | [0.622572, 0.623368]: contains the leaf |
| Chua | 0.5750938101 | 0.5750074725 | −8.63e-5 | 47 (71 states in 24 groups) | [0.574375, 0.575636]: contains the leaf |

- **The constant is right.** The smallest column-3 value is `log(c) + 2e-13` (`-4.6051701859879` against `log(0.01) = -4.6051701859881`), so `c = 1e-2`.
- **The ties are in the tail only.** Each tied group sits at raw `N-hat` of 1e-14 to 2e-14 (`probe4.log`), for example three Lorenz-63 states at `x = -4.60517018598683`; their oracle `N` values differ (1.2e-13, 0.21, 2.6), so the true order inside a group is not the mid-rank order, and a different tie order moves the statistic.
- **The leaf lies inside the interval of all tie-breaks of the dump column** in all three systems. That bounds the difference by the tie structure and is what the cause predicts (the true order is one of the tie-breaks).
- **Columns 1 and 2 also have ties** (Chua: 61 and 54), and they reproduce bitwise: those ties are present in production's raw arrays too. Only column 3 (`log(x + c)` with `x` far below `c`) loses order.

The values near 1e-14 are round-off noise of `retrieval_spread` (identical analogs), so the order production gives them is arbitrary in the first place; this does not make the dump reproduce production.

## 2. What is and is not wrong

- **Tool:** no defect. Its Spearman and its influence series are right for the array it reads. The reproduction check is doing its job: the array in the dump cannot reproduce a statistic that depends on the order of values closer than its resolution.
- **Production:** no defect.
- **Dump (schema `lpcstudy.states/2`):** `core/profile` is a transformed copy, and column 3 cannot reproduce `H1d/rows/nhat/spearman`. The same information loss would affect any criterion that ranks column 3 (Q-N features are trees on it, not ranks, and are unaffected in order).
- **What the exact fix is:** store the **raw** first-draw proxy of the H1d pairs, `ev.noise_sens[:, 0]` at least (and, for symmetry, `eps_hat[:, 0]`, `delta_hat[:, 0]`, `ev.growth_proxy[:, 0]`, which already reproduce bitwise through the profile and need no change). Production arrays: `rules.proxies.seeds(ev, noise)` and `ev.noise_sens` in `analysis.h1d_proxies`. That is a dump change (a new key, for example `h1d/nhat_raw`, schema `/3`): it needs a plan row and review, and I have not made it.

## 3. Effect on the rehearsal, and R5

- **Validity of the readings.** Only the reproduction of one reported pair (`nhat`, which has no verdict in v3 section 2 and 8) is affected, by at most 9e-5 in a correlation of 0.6; its influence series differs from the production one by the rank order of at most 71 states among 500, which moves acf(1) and the block-variance ratios negligibly (not quantified here). Nothing else is affected: 3 systems x 3 other H1d rows and every other check MATCH.
- **R5 (the full DEV-2 GPU run with the dump) can go ahead on the current code.** It needs no dump fix for any verdict, interval or diagnostic. The consequence is on the **exit code** of the diagnostics report: `nhat` will again be a MISMATCH (exit 1, a false DEF) at full size, where the tie fraction is similar. To avoid that without a dump change, the tool should treat the case it can recognise: when the stored column has ties, compute the interval of the statistic over all tie-breaks of that column and, if the leaf lies inside it, report "not computable exactly: the transform created ties; leaf within the tie-break bound [lo, hi]" (exit 2, counted, never exit 0), and a MISMATCH only if the leaf is outside the interval. That is a normal fix round of the tool (a test with a constructed column whose transform collapses two raw values); I propose it and can do it on request. The alternative, storing the raw `noise_sens`, makes the check exact and is the better long-term fix; it can wait for a later dump version.
- **Not a reason to hold R5:** the dump is otherwise sound (all other reproduction checks MATCH, stack SAME).

## 4. Uncertainty

The mechanism (collapse of near-equal tiny values by `log(x + c)`) is established by the tie structure, the groups' raw magnitudes and the containment of the leaf in the tie-break interval; I cannot recover the raw values from the dump, so the exact production order inside each tied group is not reproduced here (that is what the stored array cannot give). The claim that the order of the values near 1e-14 is arbitrary comes from reading `retrieval_spread`'s use on identical analogs; it is not tested here.
