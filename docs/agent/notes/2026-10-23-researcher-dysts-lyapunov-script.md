# Research note: how the Dysts `maximum_lyapunov_estimated` field was produced (WU-0022.2 follow-up)

Date retrieved: 2026-10-23. Agent: researcher (claude-sonnet-5-5). Edited only this file. **I cannot commit (no shell): the coordinator commits it.** Follows `2026-10-23-researcher-dysts-tables.md` (section A.4, open item 1). I did not read `docs/agent/notes/2026-10-23-math-chua-attribution.md`.

Reading limits: all items are WebFetch extracts (summariser output, not raw bytes). The summariser declined to print the whole function bodies, so the code is relayed as numbered descriptions with short quotes. GitHub commit pages showed no dates for two commits and no diffs for the JSON. Dysts snapshot: `master` on 2026-10-23, commit hash not shown.

## 1. `max_lyapunov_exponent` (the "naive" estimator)

Source: https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/analysis.py (function 12 of 23 in the file). Status: confirmed (fetch extract).

| Item | Content as relayed |
|---|---|
| Signature | `max_lyapunov_exponent(eq: DynSys, max_walltime: float, rtol: float = 1e-3, atol: float = 1e-10, n_samples: int = 1000, traj_length: int = 5000, **kwargs) -> float | None` |
| Docstring | first line: "Calculate the lyapunov spectrum of the system using a naive method based on the"; the function returns one float; its example uses the stale name `dysts.lyapunov_exponent_naive(eq)`; no function of that name exists in the file |
| Perturbation | `eps = atol` (1e-10), `eps_max = rtol` (1e-3). `eq.ic *= 1 + eps * (np.random.random(eq.ic.shape) - 0.5)`: relative, about +/-5e-11 per component, random direction. The in-place `*=` also changes the stored `ic` array |
| Initial conditions | `sample_initial_conditions(eq, n_samples, traj_length=max(traj_length, n_samples), pts_per_period=15)`; that helper makes a trajectory with `resample=True`, `postprocess=False` and picks rows with `np.random.choice` (no seed in the helper; `np.random.seed(ind)` is set per sample in the main loop) |
| Integration | `eq.make_trajectory` through `ComputationHolder(..., timeout=max_walltime, resample=True, ...)`; `make_trajectory` defaults are Radau, rtol=1e-12, atol=1e-12, `pts_per_period=100` (`base.py`, see tables note A.4); the grid is period-based, so time is in equation units. The number of steps is `traj_length` samples (5000 by default) |
| Transient | none: "There is no discard of initial transient points" (extract; the start is a sampled point of an earlier trajectory, not a perturbed-from-the-attractor start) |
| Renormalisation | none. A single pair of trajectories is followed; no rescaling of the separation |
| Fit window | separation `np.linalg.norm(traj1 - traj2, axis=1) / np.linalg.norm(traj1, axis=1)`; both series truncated at the last index where it is below `eps_max = 1e-3` (`np.where(separation < eps_max)[0][-1]`); IndexError unhandled if none |
| Per-pair exponent | `calculate_lyapunov_exponent(traj1, traj2, dt=float(np.median(np.diff(tvals))))`: log of the row-wise Euclidean separation, `linregress` against `np.arange(n)` over the whole truncated series, no offset; returns `slope / dt`. Time unit = equation time (grid step `dt`) |
| Result | mean over the successful samples; `None` if none; warning if under 60% succeed or if the median cutoff is below 100 (`pts_per_period` local) |

## 2. Which script wrote the JSON field: evidence, by item

| Item | Source URL | Status | Quote or content |
|---|---|---|---|
| `find_attractor_properties.py` writes the field in its current form | https://raw.githubusercontent.com/williamgilpin/dysts_data/main/dysts_data/benchmarks/find_attractor_properties.py | confirmed (fetch extract) | `"all_estimates_maxlyap.append(np.max(lyapval))"` after `"lyapval = find_lyapunov_exponents(model, 5 * pts_per_trajectory, pts_per_period=500)"`; `"data[item][\"maximum_lyapunov_estimated\"] = maxlyap"`; `"The script never calls max_lyapunov_exponent"`. That is the QR/backward-Euler spectrum routine, so this script's max field would be about spectrum[0]. Last commit shown for the file: 18 Sep 2024, "add dysts benchmark results" (`ba2ed13`; history view possibly incomplete) |
| Script that uses the naive routine | https://raw.githubusercontent.com/williamgilpin/dysts_data/main/dysts_data/benchmarks/calculate_all_lyapunov_exponents.py | confirmed (fetch extract) | `from dysts.analysis import lyapunov_exponent_naive`; `lyap = lyapunov_exponent_naive(eq)`; `f.write(f"{equation_name}: {lyap} \n")` to `lyapunov_exponents.txt`. The script writes a text file, **not** the JSON field. It calls the old name of what is now `max_lyapunov_exponent` (my inference from the stale docstring name; no text links them explicitly) |
| An old results file from the naive method | https://github.com/williamgilpin/dysts/blob/5163792ec17715108c8a081bb38cde3f7cc02a77/benchmarks/lyapunov_exponents_naive_median.txt | confirmed (fetch extract, 127 lines; no header; no `Lorenz:` line was shown) | `Chua: 1.1892760672523286`; `Rossler: 0.14412835520457712`; `LorenzCoupled: 1.0422924652259984`; `Lorenz96: 1.2773952803239483`; `HyperRossler: 0.14524149131970293`; `HindmarshRose: 0.6179081524660212`; `HyperJha: 0.36283598263065275`. Not found at the current `dysts_data` path (HTTP 404 for `dysts_data/benchmarks/lyapunov_exponents_naive_median.txt`) |
| Commit that updated the JSON values with that file | https://github.com/williamgilpin/dysts/commit/5163792ec17715108c8a081bb38cde3f7cc02a77 | confirmed (fetch extract); the date is not shown on the page (the file history lists "update lyapunov exponent values" as 5 Feb 2023); the diff was not visible | message "update lyapunov exponent values"; 3 files changed (+25/-84): `benchmarks/figure_forecasting_benchmarks_figures.ipynb`, `benchmarks/lyapunov_exponents_naive_median.txt`, `dysts/data/chaotic_attractors.json`; parent `17dfa1203112320be983268ea625fff417c1d6c7` |
| JSON file history | https://github.com/williamgilpin/dysts/commits/master/dysts/data/chaotic_attractors.json | confirmed (fetch extract; list paginated, older commits possibly omitted) | later changes after the 2023 commit: 2 May 2024 `0235980` "improved integration timestep calculation"; 6 Sep 2024 `29809f6` "added statistics for continuous systems" (body: "computed mean and std for all continuous systems - included script in dysts/data - updated dysts/data/chaotic_attractors.json"); 8 Dec 2024 `216337b` "hand tune some systems"; 29 Dec 2024 `6166f96` "update some dysts json metadata"; 1 Jan 2026 `69aa3bc`, `ca2a509` (DOIs). Commit messages do not say whether the Lyapunov fields were rewritten after Feb 2023 |

## 3. Comparison of the 2023 text values with the stored JSON fields (derived by me)

| System | `lyapunov_exponents_naive_median.txt` (5163792) | JSON `maximum_lyapunov_estimated` (read today) | ratio JSON/txt | Code lambda (DEV-0 leaf) | txt / code |
|---|---|---|---|---|---|
| Rössler | 0.14412836 | 0.15059689 | 1.045 | 0.07193979 | 2.003 |
| Chua | 1.18927607 | 1.23011636 | 1.034 | 0.43113260 | 2.759 |
| HyperRossler | 0.14524149 | 0.17188496 | 1.183 | | |
| Lorenz96 | 1.27739528 | 1.33616678 | 1.046 | | |
| LorenzCoupled | 1.04229247 | 1.02843984 | 0.987 | | |
| HindmarshRose | 0.61790815 | 0.65353933 | 1.058 | | |
| HyperJha | 0.36283598 | 0.38695362 | 1.066 | | |

Today's JSON fields are all within 18% of the 2023 naive-method values (within 7% for six of seven), while for Rössler and Chua they sit about 2x and 2.8x above the code's QR/Benettin value and above Dysts' own spectrum[0]. Spectrum[0] for Lorenz96 (1.6247) and HyperRossler (0.2786) is also far from these (derived).

## 4. What the text supports about the 2.09x and 2.85x ratios

- **Supported:** the stored max field has the size of the 2023 naive log-separation estimates (Rössler 0.144 against 0.1506; Chua 1.189 against 1.230), not that of the QR spectrum of the same JSON entry (0.0763; 0.4605). So the field was most probably produced by (a version of) the naive method of section 1, not by `find_attractor_properties.py` in its current form (whose max would be about spectrum[0]). This is an inference from numerical proximity plus a commit that updates both files together; **no text states "the JSON field came from `max_lyapunov_exponent`".** Status: not confirmed.
- **Not supported, not shown:** why the naive method gives about 2x (Rössler) and 2.8x (Chua) the Benettin value. The code in section 1 has features that could bias a slope of log-separation: no renormalisation, a random relative perturbation of 1e-10 in all directions (including stable directions), no transient or fit offset (the fit starts at the first sample), a window ending at a relative separation of 1e-3, and per-sample division by a grid `dt`. The text gives no evidence of which of these, if any, inflates the estimate. Each is untested; a scratch computation would be needed (re-implementing the 14 relayed lines and running it on the study's Rössler and Chua). Not done here (no shell).
- **Not supported:** that the 2023 text file is the source of the current JSON values. Today's values differ from it by 3-18%, and four later commits touched the JSON (table above) without a message saying the Lyapunov fields changed. The generation script and commit for the current JSON values are unknown.
- Time units: both routines divide by the grid step in equation time, so a unit mismatch is not shown by the text (the QR spectrum is on the same grid). It is not an explanation by the texts read.

## 5. Unconfirmed items

1. That the JSON field was written by `max_lyapunov_exponent` (inference only; name `lyapunov_exponent_naive` vs `max_lyapunov_exponent` link is inferred).
2. The date of commit `5163792` (page shows no date; the 5 Feb 2023 date is from the file history list) and the diff of the JSON in that commit (not visible).
3. Which commit produced today's JSON max values; the diffs of `29809f6`, `6166f96`, `216337b` were not seen.
4. The cause of the inflation (hypotheses in section 4, untested).
5. A `Lorenz:` line in the 2023 text file (not shown by the extract; the Lorenz row is therefore missing from section 3).
6. Verbatim bodies of the functions: the summariser refused to print them; the descriptions are relays.
7. Whether older commits of `find_attractor_properties.py` (before the single commit shown) used the naive method.
