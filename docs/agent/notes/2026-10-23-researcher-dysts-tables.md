# Research note: Dysts tables for WU-0022.1 and WU-0024.1 (re-confirmation of the 2026-10-20 notes)

Date retrieved: 2026-10-23. Agent: researcher (claude-sonnet-5-5). Edited only this file. No shell: **nothing was committed** (the caller must commit with `Agent: claude-sonnet-5-5`). Nothing under the sealed run was read.

## 0. Method, limits, status words

- Reuses `2026-10-20-researcher-dysts-extension.md` (ext) and `2026-10-20-researcher-dysts-equations.md` (eq); each item below was re-fetched today unless marked "carried over".
- **Fetch extract** = answer of WebFetch's summariser (not raw bytes; it returns field values and lines, not blocks). **Read directly** = I viewed PDF page images. Nothing quoted comes from memory.
- Status: **confirmed** = value or quote seen in text fetched today; **not confirmed** = not seen today (carried over from an earlier note, or not found).
- Dysts snapshot: `master` of https://github.com/williamgilpin/dysts on 2026-10-23, commit unknown. The JSON has 179,644 characters; I read both halves for Lorenz, Chua (first half) and Rossler (second half).
- Limits used: about 20 fetches, 15 PDF pages read directly (Gilpin 2023 pp.1-12; Bogdanov and Bogdanova pp.7-9). Gilpin 2021 PDF failed (over 10 MB), so the 2021 items rest on the ar5iv HTML extract.
- PRIME.11: no page carried an instruction. The summariser/search tool tails asking for a sources list were not acted on beyond the role's own requirement.

## A. WU-0022.1: Lorenz-63, Rössler, Chua, Dysts against the code

Code: `lpcstudy/systems.py` lines 339-367 (SYSTEMS), `max_dt` 0.01 / 0.04 / 0.005. Code lambda: leaf `systems/<s>/context/lambda_max` of `docs/study/pilot_results_v3_dev0_reference.json` (seed_id DEV-0, seed 20261005; lines 113, 7325, 14497), natural time units; `context/interval` is Delta = 1/(30 lambda) (0.0368123, 0.463350, 0.0773157). The leaf has no SE for lambda_max in its `context` block (one `se` key at line 234 is in another block, not examined), so per WU-0022 B2 no verdict word is used.

### A.1 Parameters and equations (Dysts `flows.py`, `chaotic_attractors.json`; confirmed, fetch extract)

| System | Code parameters | Dysts parameters (JSON) | Dysts `_rhs` (flows.py) | Difference |
|---|---|---|---|---|
| Lorenz | sigma 10, rho 28, beta 8/3 | beta 2.667, rho 28, sigma 10 | `xdot = sigma * y - sigma * x`, `ydot = rho * x - x * z - y`, `zdot = x * y - beta * z` | Same field; beta 2.667 vs 2.66667 (1.2e-4 relative) |
| Rössler | a 0.2, b 0.2, c 5.7 | {"a": 0.2, "b": 0.2, "c": 5.7} | `xdot = -y - z`, `ydot = x + a * y`, `zdot = b + z * x - c * z` | None |
| Chua | alpha 15.6, beta 28, m0 -1.143, m1 -0.714 | alpha 15.6, beta 28.0, m0 -1.142857, m1 -0.71429 | `ramp_x = m1 * x + 0.5 * (m0 - m1) * (np.abs(x + 1) - np.abs(x - 1))`, `xdot = alpha * (y - x - ramp_x)`, `ydot = x - y + z`, `zdot = -beta * y` | Same field and diode (m0 inner, m1 outer); m0, m1 differ by 1.2e-4 and 4e-4 relative (3-digit roundings of -8/7, -5/7) |

URLs: https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/data/chaotic_attractors.json ; https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/flows.py . Citations in JSON: Lorenz 1963 J. Atmos. Sci. 20, 130-141; Rössler 1976 Phys. Lett. 57A; Chua 1969 "Introduction to Nonlinear Network Theory", McGraw-Hill.

### A.2 Dysts metadata and Lyapunov fields (confirmed, fetch extract; digits as relayed)

| Field | Lorenz | Rössler | Chua |
|---|---|---|---|
| `period` | 1.5008 | 5.9086 | 1.4235 |
| `dt` | 0.0003002100350058257 | 0.001181916986164424 | 0.0002847474579095888 |
| `embedding_dimension` (state dimension) | 3 | 3 | 3 |
| `maximum_lyapunov_estimated` | 0.8917098035724058 | 0.15059688939547888 | 1.2301163591725595 |
| `lyapunov_spectrum_estimated` | 1.0910931847726466, 0.02994120961308413, -14.915552395875103 | 0.0763301393780693, 0.007522476799147231, -5.741024338716747 | 0.4605474829443073, 0.0022048281168492866, -4.319076735248446 |
| `kaplan_yorke_dimension` | 2.075158758095728 | 2.0146095059018845 | 2.10727056025829 |
| Dysts SE or error bar | none stated | none stated | none stated |

Status of "no SE stated": confirmed for the JSON fields; the stated method (A.4) gives no error estimate either.

### A.3 Comparison (ratios derived by me; code lambda from the DEV-0 leaf)

| System | Code lambda_max | Dysts max field | ratio | Dysts spectrum[0] | ratio | Published (carried over, see A.5) |
|---|---|---|---|---|---|---|
| Lorenz | 0.9054940534657817 | 0.8917098 | 0.985 | 1.0910932 | 1.205 | 0.90563 (Sprott) |
| Rössler | 0.07193978510879935 | 0.1505969 | **2.093** | 0.0763301 | 1.061 | 0.0714 (Sprott via B and B); 0.07062 +/- 0.00066 |
| Chua | 0.43113260161336364 | 1.2301164 | **2.853** | 0.4605475 | 1.068 | none found |

No verdict word is applied (no SE). Observations: (i) the confirmed ratios 2.09 and 2.85 for the stored `maximum_lyapunov_estimated` hold; (ii) the Dysts Lorenz spectrum[0] is 20.5% above the code and Sprott's value, while its max field is 1.5% below: so the Dysts spectrum field is not uniformly closer than the max field; (iii) Dysts' two fields disagree with each other for Rössler (1.97x) and Chua (2.67x) (derived).

### A.4 Time and sampling convention, and how the Dysts exponents are computed

| Item | Source | Status | Quote or content | Conditions |
|---|---|---|---|---|
| Equation time is not rescaled | flows.py (above) | confirmed | `_rhs` of the three systems carries no time factor (A.1) | |
| Output grid | https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/base.py, `make_trajectory` | confirmed | `timescale: str = "Fourier"`, `method: str = "Radau"`, `rtol: float = 1e-12`, `atol: float = 1e-12`, `pts_per_period: int = 100`, `resample: bool = True`; `tlim = self.period * (n / pts_per_period)`; `tpts = np.linspace(0, tlim, n)` | default is period-based, 100 points per period |
| Lyapunov-based grid option | same | confirmed | `timescale == "Lyapunov"` ... `tlim = (1 / self.maximum_lyapunov_estimated) * (n / pts_per_period)` | one "Lyapunov time" = `pts_per_period` samples, taken from the **stored max field** |
| `period` meaning | https://raw.githubusercontent.com/williamgilpin/dysts/master/README.md | confirmed | "The `period` field contains the timescale associated with the dominant frequency in each system's power spectrum." "The integrated trajectory is then resampled based on the `period`." README says nothing on a Lyapunov timescale. | |
| Model count | README | confirmed | "Currently there are 135 continuous time models, including several delay differential equations." | |
| Method named in README | README | confirmed | "The Lyapunov exponent calculation is based on the QR factorization approach used by" (Wolf et al. 1985, Eckmann et al. 1986 follow) | |
| Spectrum routine | https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/analysis.py, `find_lyapunov_exponents(model, traj_length, pts_per_period=500, tol=1e-8, min_tpts=10)` | confirmed (fetch extract, lines relayed) | `dt = np.median(np.diff(tpts))`; `u_n = np.matmul(np.linalg.inv(np.eye(d) - jacval * dt), u)` (backward Euler); `q, r = np.linalg.qr(u_n)`; `final_lyap = np.sum(all_lyap, axis=0) / (dt * traj_length)`; docstring cites Christiansen and Rugh (1997) | first-order tangent step, QR at every sample |
| Naive max routine | same, `max_lyapunov_exponent(eq, max_walltime, rtol=1e-3, atol=1e-10, n_samples=1000, traj_length=5000)` | confirmed | "naive method based on the log-separation of two nearby trajectories"; slope divided by `dt = float(np.median(np.diff(tvals)))`; no QR | |
| Script that writes both JSON fields | https://raw.githubusercontent.com/williamgilpin/dysts_data/main/dysts_data/benchmarks/find_attractor_properties.py | confirmed (fetch extract) | `pts_per_trajectory = 3000`, `divide_dt = 10`, `points_to_sample = 20`; `"model.dt /= divide_dt"`; `"lyapval = find_lyapunov_exponents(model, 5 * pts_per_trajectory, pts_per_period=500)"`; `"all_estimates_maxlyap.append(np.max(lyapval))"`; weights `np.exp(-lyap_weights * 1000)` of the smallest absolute exponent, normalised; `"maxlyap = np.sum(lyap_weights * np.array(all_estimates_maxlyap))"`; `"data[item][\"maximum_lyapunov_estimated\"] = maxlyap"`. The extract says the script "never calls `max_lyapunov_exponent`". | Read as: the stored max field should be the weighted mean of per-sample spectrum maxima, i.e. about spectrum[0]. The JSON shows 2.67x (Chua) and 1.97x (Rössler): **the current script does not reproduce the stored max field** (derived). The version of the script that wrote the JSON is not known. |

**Open (not confirmed):** why the stored max field differs from spectrum[0]. The attribution is WU-0022.2's task (scratch computation). The script text above excludes a time rescaling inside the Dysts estimate for the spectrum field (same `dt` is used for the division and the grid).

### A.5 Published references (carried over from `2026-10-10-research-lyapunov.md`, re-confirmed today where marked)

| System | Value | Source | Status today | Quote | Conditions |
|---|---|---|---|---|---|
| Lorenz | 0.90563, 0, -14.57219 (base-e) | https://sprott.physics.wisc.edu/chaos/lespec.htm | confirmed (fetch extract) | "the standard ones (sigma = 10, r = 28, b = 8/3)"; "0.90563, 0, -14.57219" | code "ported to the PowerBASIC Console Compiler from Wolf's Fortran code"; no step stated |
| Lorenz | 0.90410 +/- 0.00076 | Yu. I. Bogdanov and N. A. Bogdanova, arXiv:1412.2242, p.7 | confirmed (read directly) | "lambda_1 = 0.90410 +/- 0.00076 ... Sprott J.C. [4]: lambda_1 = 0.906" | momentum-representation statistical method; integrator not read |
| Rössler | 0.07062 +/- 0.00066; Sprott 0.0714 | same, p.8 | confirmed (read directly) | "lambda_1 = 0.07062 +/- 0.00066 ... Sprott J.C. [4]: lambda_1 = 0.0714, lambda_3 = -5.3943" | statistical method, time axis of order 5e4 units; Sprott's own conditions not retrieved (reference [4] is a 2003 book, "Chaos and Time-Series Analysis"); 0.0714 is secondary |
| Chua (alpha 15.6, beta 28, m0 -1.143, m1 -0.714) | none | earlier note | not confirmed (nothing found, not re-searched today) | | |

### A.6 The three known findings, re-confirmed

| Finding | Status | Evidence |
|---|---|---|
| Dysts stored `maximum_lyapunov_estimated` is unreliable: 2.09x the code for Rössler, 2.85x for Chua | **confirmed** (arithmetic from today's JSON and the leaf; A.3) | Dysts' own spectrum[0] is within 6-7% of the code for those two systems; the max field is 1.97x and 2.67x its own spectrum[0]. "Unreliable" is my label for an internal inconsistency; no text calls it an error |
| 30 steps per Lyapunov time comes from Zhang and Gilpin, not Gilpin 2021 | **confirmed** for Zhang and Gilpin; **confirmed absent** from Gilpin 2021 and from Gilpin 2023 | https://arxiv.org/html/2409.15771 Sec. 4: "We downsample the resulting time series to a uniform coarse granularity of 3030 timepoints per Lyapunov time τ" (the page prints doubled digits, read as 30). https://arxiv.org/html/2505.11349 Sec. 4: data at "a fixed sampling rate of 30 points per Lyapunov time" (same doubled-digit artifact). Gilpin 2023 Appendix B (read directly, p.8): "after interpolation, trajectories are resampled to 100 timepoints per t_peak". Gilpin 2021 (ar5iv extract): "Lyapunov time / 30 points per Lyapunov time: Not present". `lpcstudy/systems.py` line 14 calls 30 "the `dysts` convention"; the Dysts repository README and `base.py` do not state it (README mentions no Lyapunov timescale; `base.py` default is period-based with 100 points per period). |
| Gilpin 2021 reports sMAPE only | **confirmed as the reported metric; partly** as "only" | ar5iv extract, Sec. 3 Task 1: "Hereafter, we report sMAPE errors when comparing models, but we include all other metrics within the benchmark." So other metrics exist in the benchmark but sMAPE is the one reported. No valid prediction time in 2021 (extract: "Not present"). |

Which lambda Zhang and Gilpin use is not stated: 2409.15771 Sec. 4 says only "Each system is annotated with its largest Lyapunov exponent λ" (fetch extract: method not given). Using the Dysts JSON max field is an inference (not confirmed). If so, their Lyapunov time for Rössler and Chua is 2.09 and 2.85 times shorter than the code's (derived).

## B. WU-0024.1: benchmark definitions and published values

Sources: Gilpin 2023, "Model scale versus domain knowledge in statistical forecasting of chaotic systems", arXiv:2303.08011 (v3, dated 27 Nov 2023, which the reference list of this study gives as Phys. Rev. Res. 5, 043252; the journal reference is **not confirmed** from the PDF page I read: the arXiv page header shows none). Read directly pp.1-12 of the arXiv PDF (https://arxiv.org/pdf/2303.08011; page images). Zhang and Gilpin, "Context parroting", arXiv:2505.11349 (v3, 29 Mar 2026; abstract page: "accepted to ... ICLR 2026"; no journal reference), HTML https://arxiv.org/html/2505.11349 (fetch extract; the last 14,025 characters read for VPT, nothing found). Zhang and Gilpin, "Zero-shot forecasting of chaotic systems", arXiv:2409.15771v3 (18 Mar 2025), https://arxiv.org/html/2409.15771 (fetch extract; last 8,107 characters not read).

### B.1 Gilpin 2023 (read directly)

| Item | Status | Quote | Location |
|---|---|---|---|
| Systems and methods | confirmed | "benchmark 24 state-of-the-art forecasting methods on a crowdsourced database of 135 low-dimensional systems with 17 forecast metrics" | Abstract, p.1 |
| Systems named | confirmed | "well-known systems such as the Lorenz, Rössler, and Chua attractors" | p.2, Sec. II.A |
| Metric reported | confirmed | "We report our results in the main text in terms of the symmetric mean absolute percent error (sMAPE) ε_ik(t) ≡ 2/(t−t*) ∫ (|y_test,k − ŷ_test,ik|)/(|y_test,k| + |ŷ_test,ik|) dt'" | p.3, Sec. II.C |
| Time unit | confirmed | "We report our forecast results scaled by this quantity, in units of λ_max t"; "Lyapunov time λ_max^-1 is an invariant property of each distinct dynamical system" | p.4, Sec. II.C |
| Natural time and sampling | confirmed | "Unless otherwise noted, we measure natural time in units of the dominant significant Fourier timescale t_peak, though we rescale this quantity by the Lyapunov exponent when reporting results in the main text"; "trajectories are resampled to 100 timepoints per t_peak" | p.8, App. B |
| Dominant timescale and step | confirmed | "the smallest frequency determines the integration timestep t_max/10 for all numerical integration" | p.8, App. B |
| VPT definition | confirmed (as a side definition in an appendix, not a headline metric) | "if we define a prediction time based on the latest time when SMAPE < 50, the average valid forecast horizon of the best-performing model averaged across all 135 systems is equal to 13.9 ± 2.8 λ_max^-1. If we instead define the prediction time based on the first doubling of accumulated pointwise errors, we find a horizon of 15 ± 5.3 λ_max^-1" | p.8, App. A |
| Training length | confirmed | "t* is equal to 10 periods of t_peak"; "For each trajectory, 10 full periods comprising 1000 timepoints are used to train the model, and 2 additional periods comprising 200 timepoints are used to estimate sMAPE errors ... Measured in terms of Lyapunov times λ_max^-1, this corresponds to an average of 11 λ_max^-1 used for training each system" | p.9 App. C(4); p.12 App. E |
| Forecast horizon | confirmed | "t ∈ [0.01–50] t_peak"; "a fixed duration of t* = 10 t_peak for all training data ... forecasts up to an additional t = 2 t_peak after t*" (the two statements sit in the same paragraph, p.9, App. C; they do not obviously agree: the 2 t_peak refers to validation, the 0.01-50 to testing, my reading) | p.9 |
| Test data | confirmed | "a trajectory generated from different initial conditions than the trajectory used for training and validation" | p.9 |
| Headline numbers | confirmed | "Across all systems, the best-performing models achieve an average prediction time equal to 14 ± 2 λ_max^-1" ; "~22 Lyapunov times" for NBEATS on Mackey-Glass | p.4 Sec. III.A |
| Spread of lambda | confirmed | "the maximum Lyapunov exponent λ_max = 0.24 ± 0.31" | p.9 Fig. S2 caption |
| Noise | **not present** in the main experiments; the paper says sampling and "added stochasticity" were explored "in previous work [39]" | p.8 App. B | [39] is the 2021 paper by the reference numbering; I did not check the list |
| Physics-based hybrid | confirmed | abstract: "in data-limited settings ... physics-based hybrid methods retain a comparative advantage due to their strong inductive biases"; App. D.A lists ESN, nVAR, neural ODE as "Physics-based methods" (they are data-driven models with built-in structure, no known equation of the target) | pp.1, 9 |
| Per-system values for Lorenz, Rössler, Chua | **not present** in pp.1-12 | | Appendix F tables (pp.13+) not read |

### B.2 Zhang and Gilpin 2025/2026 (fetch extracts only; doubled digits in extracts are rendering artifacts)

| Item | Paper | Status | Quote | Location |
|---|---|---|---|---|
| Systems, dimension | 2505.11349 | confirmed | "The dysts dataset provides a standardized benchmark of 135 low-dimensional chaotic systems"; "dimensionality three and six" | Sec. 4 |
| Sampling | both | confirmed | see A.6 | Sec. 4 |
| lambda and tau | 2505.11349 | confirmed | lambda is "an invariant characteristic of the underlying dynamics"; "τ≡λ^{-1}" | Sec. 4 |
| Trajectory | 2505.11349 | confirmed | a chaotic trajectory of length 10^5 per system; "20 random initial conditions for each system" | Sec. 4 Pipelines |
| Context and horizon | 2505.11349 | confirmed | context length 512 (Fig. 2 caption); "predict the next 300 data points, equivalent to 10 Lyapunov times" (as relayed) | Sec. 4 |
| Context and horizon | 2409.15771 | confirmed | "the first 512 points of each time series, with the last 300 timepoints set aside to determine final test scores" | Sec. 4 |
| VPT definition and threshold | 2409.15771 | confirmed | "The first forecast horizon at which the sMAPE exceeds a fixed threshold ε"; "We set ε=30, as in prior studies" | Sec. 4 Metrics |
| VPT definition | 2505.11349 | **not present** in the text I read | only mentions: Table 5 caption "Valid prediction time across noise levels (higher is better)"; Sec. 5.3 "Other metrics, such as valid prediction time and fractal dimension accuracy, give similar rankings"; Table 10 caption "across different granularities" | the unit of the Table 5 values is not stated |
| Noise | 2505.11349 | confirmed | "We add Gaussian noise to normalized chaotic trajectories"; "a noise level of 0.1 translates to" a 10% perturbation per point; Tables 5-9 use levels 10^-3, 10^-2, 10^-1 | App. E |
| Noise | 2409.15771 | not present for the benchmark | | |
| Metrics | 2505.11349 | confirmed | sMAPE, MSE, MAE for pointwise accuracy; KL divergence between attractors; Hellinger distance between power spectra (Welch); correlation dimension and Lyapunov exponents | Sec. 4 Metrics |
| Context parroting | 2505.11349 | confirmed | "context parroting can be seen as a nearest neighbor algorithm in the D-dimensional delay-embedded space"; App. F.1: "a continuous 1-nearest-neighbor search over sequences of length D" | Sec. 3; App. F.1 |
| Per-system values for Lorenz, Rössler, Chua | both | **not present** | extract: Lorenz appears only in figures (Figs. 1, 6, 12; 2409.15771 Figs. 2, 4, 9) with no number; Fig. 12B is an average "over 129 systems"; Lorenz parameters "σ=10, ρ=28, and β=8/3" (2409.15771 App. B.1) | |

### B.3 Gilpin 2021 (ar5iv extract only; PDF too large to fetch)

arXiv:2110.05266, https://ar5iv.labs.arxiv.org/html/2110.05266. Abstract: "a growing database currently comprising 131 known chaotic dynamical systems" (confirmed). Sampling: "using phase surrogate significance testing to select optimal integration timesteps and sampling rates"; "Because all systems are aligned to the same average period" (Sec. 2; Sec. 3 Task 1). Noise: "trajectories with and without Brownian noise influencing the dynamics" (Sec. 2). Lyapunov: "continuous re-orthonormalization when computing various mathematical quantities such as Lyapunov exponents" (Sec. 2; no named method). No per-system numbers, no VPT. The benchmark code (https://raw.githubusercontent.com/williamgilpin/dysts_data/main/dysts_data/benchmarks/classical_benchmarks.py, confirmed, fetch extract): `pts_per_period_100`, train `periods_12`, test `periods_60` (LONG_TEST True), `split_point = int(5 / 6 * len(train_data))`, `score_func = smape`; no noise in that script.

## C. Additional Dysts systems for a comparison run (owner choice; no run is started)

Already in `SYSTEMS`: rossler_hyper, lorenz63_r166, rossler_z, hindmarsh_rose, hyper_jha, lorenz96_4 (grep of `systems.py`). Remaining from ext D.2, re-read today (JSON and `flows.py`, fetch extract):

| Rank | System | Why | Risks | Dysts fields today (not trustworthy, recompute) |
|---|---|---|---|---|
| 1 | `HyperLu` (4D; a 36, b 3, c 20, d 1.3; Chen, Lu, Lu and Yu 2006, Physica A 364, 103-110). `_rhs`: `xdot = a*y - a*x + w`, `ydot = -x*z + c*y`, `zdot = x*y - b*z`, `wdot = d*w + x*z` | Polynomial, autodiff-friendly; two comparable positive rates (spectrum 1.0856, 0.4754) that no studied system has | w std 43.6; stiffness (-19.3 vs 1.09) needs a small `max_dt`; the 3rd entry 0.0285 is probably a zero | max 1.04296; KY 3.082 |
| 2 | `LorenzCoupled` (6D). `_rhs` as in eq note: second Lorenz driven one-way by `eps*(x1 - x2)`; `rho` unused | Highest dimension; and its second subsystem is a stable fixed point alone (rho2 = 1.15), so chaos comes from the drive | Cost about 3x; delay dimension must exceed 2 x KY (about 6 or 7); spectrum sum is within 1.2% of the divergence (eq note) | max 1.0284; spectrum[0] 1.2219, [1] 0.1222 |
| 3 | `Arneodo` (3D jerk; a -5.5, b 4.5, c 1, d -1; Arneodo, Coullet and Tresser 1980, Phys. Lett. A 79, 259-263). `_rhs`: `xdot = y`, `ydot = z`, `zdot = -a*x - b*y - c*z + d*x**3` | Cheapest and lowest risk of the list: smooth cubic; asymmetric orbit (x mean -1.67); Dysts fields agree to 2.3% here (0.2429 vs 0.2374), the only such case in this table | Low novelty beyond asymmetry; slow (period 3.16) | max 0.23737; spectrum 0.24286, -0.0006, -1.2170; KY 2.199 |

Alternate: `Colpitts` (3D piecewise; `u = z - (e-1)`, `fz = -u*(1 - np.heaviside(u, 0))`): adds a second non-smooth circuit but its x mean is 9.6 (whitening and orbit bound need a nonzero centre), and `np.heaviside` makes the derivative jump. Dysts: max 0.3736, spectrum[0] 0.1375 (2.7x apart: the same disagreement as Chua). `Chen` and Dysts `Lorenz96` rank unchanged from ext D.2 but are not repeated (Lorenz96 is already used; Dysts' spectrum for it sums to -2.95 against -4, eq note).

Ranking rule (mine): exclude systems already run; prefer exact polynomial fields, at most 6 dimensions, something not present among the studied ones, lowest risk to the machinery. Rank 1 and 2 add dimension or a second growth rate; rank 3 is the safe pick.

## D. Unconfirmed or unread items

1. Why Dysts `maximum_lyapunov_estimated` differs from its own spectrum[0] (script as fetched today does not reproduce it).
2. Which lambda Zhang and Gilpin use for "30 per Lyapunov time" (inference: Dysts annotation, not stated).
3. Chua published lambda_max at the code's parameters: none found (not re-searched today).
4. Sprott's Rössler 0.0714: secondary only (via Bogdanov and Bogdanova); Sprott's book not retrieved.
5. VPT definition and units in arXiv:2505.11349 (not in the text I read); VPT values are averages over systems, none per system.
6. Per-system Lorenz/Rössler/Chua published forecast numbers: none in any text read; Gilpin 2023 Appendix F (pp.13+), the 2021 supplement and the `dysts_data` result files were not read.
7. Journal reference Phys. Rev. Res. 5, 043252 for Gilpin 2023 (given by the unit file; not shown on the pages read).
8. Gilpin 2021 PDF not read (size limit); items rest on the ar5iv extract. The 2023 note about noise in "previous work [39]" was not checked against the reference list.
9. Dysts commit hash of the files read; character-level fidelity of all code lines (relayed by the summariser).
10. Section C entries other than the three read today in JSON and `flows.py` (HyperLu, Arneodo, Colpitts, LorenzCoupled) were not independently recomputed; all Lyapunov numbers there are Dysts fields.
