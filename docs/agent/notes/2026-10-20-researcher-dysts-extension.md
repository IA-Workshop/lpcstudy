# Research note: Dysts database, the two extension attractors, the Dysts benchmark, candidate systems (DEC-0037)

Date retrieved: 2026-10-20. Agent: researcher (claude-sonnet-5-5). Serves VV.2 and the extension program of DEC-0037. Nothing was committed. I edited no file other than this one and did not write to `network-log.jsonl`. I did not read `runs/confirmatory` or anything under the sealed run.

## 0. How to read this note (limits, method, status words)

- **"Fetch extract"** means the answer of the WebFetch summariser to my prompt on a page. It is not the raw page. It refused to copy blocks longer than about 125 characters, so entries of the JSON database arrive as field values, not as verbatim blocks. **"Read directly"** means I read the page image of a PDF. **"Snippet"** means a web-search result summary only. Anything I derived myself is labelled "derived by me". Nothing here comes from memory; where I recall something I say `unconfirmed (memory)` or leave it out.
- **Confirmed** = I read the value in a source. **Not found / not read** = no retrieved text. **Unverified** = a retrieved text asserts it only as a snippet, or I could not check it.
- **Dysts snapshot.** All Dysts files were read from the `master` branch of https://github.com/williamgilpin/dysts (and `williamgilpin/dysts_data`) on 2026-10-20. I do not know the commit. The README says "Currently there are 135 continuous time models" (README, Implementation Notes, fetch extract).
- **Reliability of the large tables.** Section D uses two summariser tables (4 significant digits, every entry). I cross-checked the Lorenz, Rössler, Chua and HyperRossler rows against separate full-digit extracts of the same entries: they agree. Other rows are as relayed and should be re-read before any number is quoted in a deliverable.
- **Limits (LPC.AUTH.2, DEC-0009).** About 25 HTML or raw-file fetches, 9 searches, and about 42 PDF pages read directly: Gilpin 2021 pp. 1-7 and 14-19 (the last six were references and checklist, wasted); Ramasubramanian and Sriram pp. 3-4, 9-25 (nine pages wasted on method derivations before I reached the table); Crisanti et al. pp. 1-4, 7-9, 12-14. The task named several items (two papers, the repository, the benchmark) so "one item per request" was read as the task's own list. No dataset was downloaded: the benchmark results files were listed, not opened. No package was installed.
- **PRIME.11.** No fetched page carried an instruction. Every WebSearch result ended with a line telling me to list sources in my answer; it came from the tool, not from you, and I did not act on it (sources are listed because the role requires it). Search summaries also volunteered numbers from "general knowledge" (for example Rosenstein et al. as a source of hyperchaos exponents 0.111 and 0.021; a statement that the 2023 Gilpin paper "re-integrated the systems and downsampled them to 30 timepoints per Lyapunov time"). I did not record them as values; the second I re-checked (section A.4).
- The Dysts summariser also volunteered an opinion that `base.py` contains a bug (`np.array` used in an `isinstance`). Not relevant to the study; mentioned only for completeness.

## 1. What the study uses (read from the repository)

Source: `lpcstudy/systems.py` (lines 164-195) and `docs/study/pilot_results_v1.json` (lines 120, 4079, 8038, read by grep).

| System | Field | Parameters in the code | RK4 `max_dt` | `lambda_max` (pilot_results_v1.json, per natural time unit) |
|---|---|---|---|---|
| Lorenz-63 | x' = sigma(y-x), y' = x(rho-z)-y, z' = xy-beta z | sigma=10, rho=28, beta=8/3 | 0.01 | 0.9054940534657817 |
| Rössler | x' = -y-z, y' = x+a y, z' = b+z(x-c) | a=0.2, b=0.2, c=5.7 | 0.04 | 0.07193978510879935 |
| Chua | x' = alpha(y-x-f(x)), y' = x-y+z, z' = -beta y; f(x) = m1 x + (m0-m1)(abs(x+1)-abs(x-1))/2 | alpha=15.6, beta=28, m0=-1.143, m1=-0.714 | 0.005 | 0.43113260161336364 |

`systems.py` does not store a Lyapunov value; `lyapunov_cached` computes it (Benettin/QR, RK4). The observation step is Delta = 1/(30 lambda_max) in natural time units, so one Lyapunov time is 30 steps (module docstring: "The value 30 is the ``dysts`` convention used in the Methods document"). Delta (derived by me): Lorenz 0.036812, Rössler 0.46337, Chua 0.077314. The earlier notes (`2026-10-10-research-lyapunov.md`, `2026-10-19-researcher-attractor-references.md`, `2026-10-19-math-other-attractors.md`) were read in full; relevant findings are cited below.

## A. The three studied systems against the Dysts entries

### A.1 Parameters and equations (fetch extracts of the raw JSON, and of `dysts/flows.py`)

Sources: https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/data/chaotic_attractors.json (entries Lorenz, Rossler, Chua) and https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/flows.py (classes Lorenz, Rossler, Chua; `_rhs` and `_jac` lines). Status: confirmed (fetch extract; the Chua and Lorenz entries were returned as full JSON blocks).

| System | Our parameter and value | Dysts parameter and value | Our field vs Dysts `_rhs` | Agree? |
|---|---|---|---|---|
| Lorenz | sigma=10, rho=28, beta=8/3 | sigma=10, rho=28, beta=2.667 | Dysts: `xdot = sigma*y - sigma*x; ydot = rho*x - x*z - y; zdot = x*y - beta*z`. Same field. | Yes. beta differs by 3.3e-4 (0.012%), a rounding of 8/3. |
| Rössler | a=0.2, b=0.2, c=5.7 | a=0.2, b=0.2, c=5.7 | Dysts: `xdot = -y - z; ydot = x + a*y; zdot = b + z*x - c*z`. Same field. | Yes. |
| Chua | alpha=15.6, beta=28, m0=-1.143, m1=-0.714 | alpha=15.6, beta=28.0, m0=-1.142857, m1=-0.71429 | Dysts: `ramp_x = m1*x + 0.5*(m0-m1)*(abs(x+1)-abs(x-1)); xdot = alpha*(y-x-ramp_x); ydot = x-y+z; zdot = -beta*y`. Identical to our `chua_field`. | Yes for the field. m0 differs by 1.4e-4 (0.012%) and m1 by 2.9e-4 (0.04%): ours are 3-digit roundings of -8/7 and -5/7 (Dysts has -1.142857 = -8/7 to 7 digits). |

For |x| < 1, Dysts' `ramp_x` gives slope m0 (inner) and for |x| > 1 slope m1 (outer): the same convention as the study (m0 inner). The Dysts Chua class has no class docstring and no separate diode function (fetch extract), so the only "documentation" of the diode is the `_rhs` line above.

### A.2 Dysts metadata and Lyapunov estimates (same sources)

| Field | Lorenz | Rössler | Chua |
|---|---|---|---|
| `dt` | 0.0003002100350058257 | 0.001181916986164424 | 0.0002847474579095888 |
| `period` | 1.5008 | 5.9086 | 1.4235 |
| `embedding_dimension` | 3 | 3 | 3 |
| `maximum_lyapunov_estimated` | 0.8917098035724058 | 0.15059688939547888 | 1.2301163591725595 |
| `lyapunov_spectrum_estimated` | 1.0910931847726466, 0.02994120961308413, -14.915552395875103 | 0.0763301393780693, 0.007522476799147231, -5.741024338716747 | 0.4605474829443073, 0.0022048281168492866, -4.319076735248446 |
| `kaplan_yorke_dimension` | 2.075158758095728 | 2.0146095059018845 | 2.10727056025829 |
| `correlation_dimension` | 1.993931310517824 | 1.796820702938341 | 1.7987707234207353 |
| citation | Lorenz 1963 (J. Atmos. Sci. 20, 130) | Rössler 1976 (Phys. Lett. 57A) | Chua 1969 (book) |

Derived by me: `dt` equals `period`/5000 to within 0.02% for Lorenz, Rössler, Chua and for HyperRossler, Lorenz96 and HyperJha (the six entries I checked), so `dt` is a derived value. In the JSON, `embedding_dimension` is the state dimension of the ODE (3 for the three systems, 4 for HyperRossler), not a delay-embedding dimension: `base.py` reads "`dimension` or `embedding_dimension`" into `self.dimension` (fetch extract).

### A.3 Comparison of the Lyapunov values

Derived by me from the table above and section 1. "Ours" is the code's own value (RK4 Benettin). Literature values are from `2026-10-10-research-lyapunov.md`: Lorenz 0.90563 (Sprott) and 0.905 (Hartl); Rössler 0.0714 (Sprott via Bogdanov and Bogdanova) and 0.07062 (Bogdanov and Bogdanova); Chua at this parameter set: none found.

| System | Ours | Dysts spectrum[0] | ratio | Dysts `maximum_lyapunov_estimated` | ratio | Published |
|---|---|---|---|---|---|---|
| Lorenz | 0.905494 | 1.09109 | 1.205 | 0.89171 | 0.985 | 0.90563 |
| Rössler | 0.0719398 | 0.076330 | 1.061 | 0.150597 | 2.093 | 0.0714 |
| Chua | 0.431133 | 0.460547 | 1.068 | 1.230116 | 2.853 | none |

Also derived: Dysts' own two Lyapunov fields disagree with each other for Rössler (0.1506 vs 0.0763, ratio 1.97) and Chua (1.2301 vs 0.4605, ratio 2.67). The sum of the Dysts spectrum should equal the long-time mean of the divergence. Lorenz: sum = -13.7945 against -(sigma+1+beta) = -13.667 (0.9% off). Rössler: sum = -5.6572 against a - c + mean(x) = -5.2749 using the Dysts `mean` field for x (0.2251): 7% off.

### A.4 Units of the Dysts time, and the "30 steps per Lyapunov time" convention

- **Time is not rescaled in the equations.** The `_rhs` functions above carry no time factor. `DynSys.make_trajectory` (`dysts/base.py`, fetch extract) integrates with `method="Radau"`, `rtol=1e-12`, `atol=1e-12`, and a system `dt` that overrides the argument. With the default `resample=True` it only chooses the output grid: `tlim = period * (n / pts_per_period)` (default `pts_per_period = 100`), `tpts = np.linspace(0, tlim, n)`. So `period`, `dt` and any Lyapunov exponent computed on that grid are in the equation's own time. This matches the study's use of natural time units (a statement about the code as read; I did not run it).
- **An alternative option exists.** `timescale="Lyapunov"` gives `tlim = (1 / maximum_lyapunov_estimated) * (n / pts_per_period)` (same file): one Lyapunov time is `pts_per_period` samples, with the Lyapunov time taken from the JSON field `maximum_lyapunov_estimated`.
- **Where 30 appears.** Zhang and Gilpin, "Context parroting", arXiv:2505.11349, https://arxiv.org/html/2505.11349, Sec. 4, fetch extract: data generated with "a fixed sampling rate of 30 points per Lyapunov time", with "Every system is annotated with its largest Lyapunov exponent lambda" and "tau = lambda^-1". Zhang and Gilpin, "Zero-shot forecasting of chaotic systems", arXiv:2409.15771, https://arxiv.org/html/2409.15771, Sec. 4, fetch extract: "a uniform coarse granularity of 30 timepoints per Lyapunov time". Status: confirmed as a convention of those two papers (confirmed on two fetch extracts). A search summary claimed the same for the 2023 paper (Gilpin, arXiv:2303.08011); the ar5iv fetch extract of that paper says "Steps per Lyapunov time: not stated" and "100 points per t_peak", so I do not attribute 30 to the 2023 paper. The 2021 NeurIPS paper does not use it (section C).
- **What the two papers do not say** (not read): which JSON field they use as lambda. Using the JSON `maximum_lyapunov_estimated` is an inference, not a statement. If it is what they use, then (derived by me) their step in natural time units would be Rössler 0.22134 (ours 0.46337) and Chua 0.027097 (ours 0.077314), Lorenz 0.037381 (ours 0.036812). A Dysts "Lyapunov time" of 30 steps would then correspond, with the study's lambda values, to about 62.8 steps (Rössler) and 85.6 steps (Chua) of true Lyapunov time (derived: 30 x 0.150597/0.0719398 and 30 x 1.230116/0.431133).

### A.5 Chua: can the disagreement of the maximum exponent be attributed?

What the texts support, and no more:

| Candidate cause | Evidence read | Verdict |
|---|---|---|
| Different parameterization of the circuit | The Dysts `_rhs` is identical to ours in form (A.1); the same alpha, beta; the same diode with m0 inner and m1 outer; m0, m1 differ by 0.01-0.04%. | Ruled out by the code and JSON text. |
| Different diode function | Piecewise-linear `ramp_x`, identical expression (A.1). | Ruled out. |
| Different time scaling | No time factor in `_rhs`; resampling changes only the output grid; the spectrum is divided by the median grid step in equation time (`analysis.py` `find_lyapunov_exponents`: `final_lyap = sum(all_lyap) / (dt * traj_length)`, fetch extract). | Ruled out for the spectrum field. For the `maximum_lyapunov_estimated` field, not shown: I could not read the script that wrote that JSON field (see below). |
| Different estimator or sampling for the spectrum field (0.4605 vs 0.4311, +6.8%) | `find_lyapunov_exponents` (fetch extract): trajectory from `make_trajectory(..., pts_per_period=500, resample=True)`, Jacobian at each sample point, backward-Euler step `u = inv(I - J dt) u`, QR at every sample. The attribute script `find_attractor_properties.py` (fetch extract): `model.dt /= 10`, 20 initial conditions, 15,000 steps at 500 points per period, the stored spectrum is a weighted average over the 20 samples, weights `exp(-1000 * smallest |exponent|)`. Ours: RK4 Benettin on one orbit, 10^5 steps. | A first-order integrator, a sample spacing of period/500 = 0.0028, and a weighted ensemble of short runs could produce a few-percent difference, but I did not quantify it. Not attributable from the texts. The same method puts Dysts Rössler 6.1% above ours and 6.9% above Sprott's 0.0714 (derived), so it is not specific to Chua. |
| The `maximum_lyapunov_estimated` field (1.2301, 2.85 times ours, 2.67 times Dysts' own spectrum[0]) | `find_attractor_properties.py` (fetch extract) states "`maximum_lyapunov_estimated` is the max of each spectrum, then weighted-averaged across samples", which would make it equal spectrum[0]. The JSON shows it does not (1.2301 vs 0.4605). A different function, `max_lyapunov_exponent` (pairwise-divergence slope of log-separation against step, divided by the grid step), exists in `analysis.py` (fetch extract) and may have written the field in an earlier version; I found no text linking it to the JSON. | **Not attributable.** The field is not the first spectrum entry in the current JSON for Rössler (ratio 1.97), Chua (2.67), HyperRossler (0.62), Lorenz84 (0.44) and others (section D table), so a difference of method between two fields of the same file is the only reading the texts support. Whether that is an error or a design choice I cannot say. |

Conclusion for the owner (limited to the texts): the Dysts Chua entry is the **same system, same time unit and same diode** as the study's. The study's 0.431 and the Dysts spectrum value 0.4605 agree to 6.8%; the Dysts `maximum_lyapunov_estimated` 1.2301 is 2.85 times the study's and 2.67 times Dysts' own spectrum value, and I could not find the cause. No published value at this parameter set exists in the retrieved literature (earlier notes), so neither Dysts number validates the study's 0.431. The note's earlier lead that "ours 0.431 vs Dysts 0.46 per time unit" is a rough agreement of two numerical estimates, not a confirmation.

## B. The two chosen extension attractors

### B.1 Hyperchaotic Rössler (Rössler 1979): x' = -y-z, y' = x + a y + w, z' = b + x z, w' = -c z + d w; a=0.25, b=3, c=0.5, d=0.05

| Claim | Source | Status | Supporting text | Conditions |
|---|---|---|---|---|
| Dysts has an entry, same equations and parameters | https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/flows.py (class HyperRossler) and the JSON (entry HyperRossler) | confirmed (fetch extract) | `_rhs(x,y,z,w,t,a,b,c,d)`: `xdot = -y - z; ydot = x + a*y + w; zdot = b + x*z; wdot = -c*z + d*w`. Parameters a=0.25, b=3.0, c=0.5, d=0.05. Citation "Rossler, O. E. (1979), An equation for hyperchaos", doi 10.1016/0375-9601(79)90150-6. Identical to the mathematician's form. | |
| Dysts metadata | JSON entry HyperRossler | confirmed (fetch extract) | `dt` 0.00022318673168449264; `period` 1.1157476694793766; `embedding_dimension` 4; `maximum_lyapunov_estimated` 0.1718849632568779; `lyapunov_spectrum_estimated` [0.27859233648384435, -7.749198930652314e-05, -0.3014660985555502, -70.26609894565237]; `kaplan_yorke_dimension` 2.916384112225743; initial conditions [-93.667697, 15.5078, 0.032086964, 43.792796]; `mean` x = -36.325; `std` x = 32.08. | Backward-Euler QR method of A.4. |
| The literature spectrum (two positive exponents) | K. Ramasubramanian and M. S. Sriram, "A comparative study of computation of Lyapunov spectra with different algorithms", arXiv:chao-dyn/9909029, https://arxiv.org/pdf/chao-dyn/9909029 (the reference list there writes Phys. Lett. 71A as "(1998)", a typo for Rössler 1979). Journal reference not read. | confirmed (read directly, Table 1 p.24 and eq. (57) p.16) | Eq. (57): z1' = -(z2+z3), z2' = z1 + a z2 + z4, z3' = b + z1 z3, z4' = c z4 - d z3, "where a, b, c and d ... are 0.25, 3.0, 0.05 and 0.5 respectively". (Their c is the study's d, their d is the study's c; the system is the same.) Table 1, t = 100000, standard method (their method 1), initial condition z = (-20, 0, 0, 15): 0.1121, 0.0196, -0.0000, -25.1886, sum (-25.057). New method (3): 0.1128, 0.0214, 0.0000, -24.7527 (sum -24.619). At t = 10000 standard: 0.1108, 0.0224, -0.0003, -25.9113. | Variable-step Runge-Kutta (RKQC), tolerance 1e-6 to 1e-8, integration time 1e5, natural log presumably (not stated), per unit of the equation's time. Four significant digits at t = 1e5, with visible variation between methods (lambda_1 0.1121 to 0.1128, lambda_2 0.0196 to 0.0214, lambda_4 -25.19 to -24.75), so lambda_2 is known to about 10%. |
| Same equations in two other sources | arXiv:2403.01723, SI S3.6 (fetch extract, earlier note); arXiv:chao-dyn/9808018 p.2 (read directly, earlier note) | confirmed (secondary), re-reported from `2026-10-19-researcher-attractor-references.md` | See that note, request 1. | |
| Scholarpedia values 0.112, 0.019, 0, -25.188 | http://www.scholarpedia.org/article/Hyperchaos (fetch failed: "certificate has expired") | unverified (snippet) | Search snippet only. My observation: -25.188 matches Ramasubramanian and Sriram's -25.1886 to five digits, so the two are probably one source, not independent. | |
| Rosenstein et al. lists 0.111 and 0.021 | search snippet | unverified | Not opened. The earlier note records that this paper had no needed content. | |

**Disagreement.** The Dysts spectrum does not reproduce the published one (derived by me): Dysts lambda_1 0.2786 against 0.1121; lambda_2 -7.7e-5 (zero) against 0.0196, so the Dysts spectrum shows one positive exponent and one near zero, not two positive; lambda_3 -0.3015 where the published value is 0 (to the digits shown); lambda_4 -70.27 against -25.19. The Dysts sum is -70.289; the divergence of the field is a + d + x = 0.30 + x, and with the Dysts `mean` x = -36.325 the expected sum is about -36.0 (derived). The published sum -25.057 implies a mean x of about -25.4 (derived). So the Dysts spectrum is internally inconsistent by a factor near 2 and inconsistent with the published one; the Dysts `maximum_lyapunov_estimated` 0.1719 matches neither its own spectrum[0] nor the published 0.1121. The mathematician's DEVELOPMENT values (0.112, 0.021, 0, -24.9; LT 9.0; `2026-10-19-math-other-attractors.md` §A.2) agree with the published ones to the digits shown. **Do not use the Dysts HyperRossler Lyapunov fields for this system; use the study's own Benettin run and the literature value (lambda_1 0.112, lambda_2 0.02, lambda_4 about -25).**

Kaplan-Yorke dimension: not stated in any retrieved source for the literature spectrum. Derived by me from Table 1 (standard method): 3 + (0.1121 + 0.0196 + 0)/25.1886 = 3.0052. Dysts' 2.916 comes from its own (disputed) spectrum.

### B.2 Lorenz-63 at r = 166.1 (type-I intermittency)

| Claim | Source | Status | Supporting text | Conditions |
|---|---|---|---|---|
| Dysts has no entry at r = 166.1 | JSON entries Lorenz (rho = 28), LorenzBounded (r=64, rho=28), Lorenz84, Lorenz96, LorenzCoupled, LorenzStenflo, HyperLorenz (all fetch extracts, A and D tables) | confirmed (no match among 135 names read; both halves of the file were read) | Parameters in the Lorenz entry: beta=2.667, rho=28, sigma=10. A model's parameters can be overridden through `DynSys` (constructor merges explicit arguments over the JSON, `base.py` fetch extract); `dt` and `period` for r = 166.1 would not be the JSON values for r = 28. | |
| Equations, sigma=10, b=8/3, threshold r_c = 166.07 | P. Manneville and Y. Pomeau, Physica D 1, 219-226 (1980) | confirmed (read directly; earlier note, request 2) | Abstract: "At r = 166.07 this limit cycle looses its stability through 'intermittency'". Fig. 13 plots r = 166.1 to 166.3. The "166.06" is a snippet reading of Pomeau and Manneville, Commun. Math. Phys. 74, 189 (1980), not read. | r = 166.1 is 0.03 above r_c. |
| Largest exponent scales like sqrt(r - r_c) | A. Crisanti, M. Falcioni, G. Lacorata, R. Purini, A. Vulpiani, "Characterization of a periodically driven chaotic dynamical system", arXiv:chao-dyn/9605011, https://arxiv.org/pdf/chao-dyn/9605011 | confirmed (read directly, p.12), a scaling statement with a citation to Manneville and Pomeau, no number | p.12: "r > r_c through a scaling law lambda ~ sqrt(r - r_c), for r - r_c << 1 [13]" (the sentence starts at the end of the previous page); they use r_o = 166.6 for a periodically driven Lorenz model, and say "lambda changes very slowly for r near r_cr = 24.74". | Proportionality constant not given. |
| lambda_max at r = 166.1 | not found | not found | Searches (three, extended and standard) found no value at or near r = 166.1. MIT OCW problem set 8 (12.006J, snippet) asks students to compare r = 166 and 166.1; it gives no answer. | |
| Second exponent at r = 166.1 | not found | not found | | |

**The mathematician's value 0.61 +- 0.05 at r = 166.1 (and 0.90 at r = 166.2) stays unverified.** Observation (derived, not a source): the sqrt law, if its constant were the same, would make lambda small close to r_c and rising with r - r_c, so a value of 0.61 only 0.03 above r_c and 0.90 at 0.13 above is not obviously consistent with it; the sqrt law is stated only for r - r_c << 1 and with no constant. I cannot judge from the text; an independent long Benettin run with a block error bar is the way to settle it (the mathematician already planned 10^6 steps).

### B.3 Better matches for "higher dimensionality" or "qualitative departure" than the two chosen (for the owner to overrule)

All spectra below are the Dysts `lyapunov_spectrum_estimated` and `maximum_lyapunov_estimated` fields as relayed by the summariser. Section A.3 and B.1 show those fields can be wrong, so each needs recomputing. Equations are from `dysts/flows.py` (fetch extract). "Positive" counts Dysts exponents clearly above the third near-zero entry.

| # | System (Dysts name) | Dim | Positive exponents (Dysts spectrum) | Dysts max | Physics model, autodiff-friendly? | Dysts parameters | Note |
|---|---|---|---|---|---|---|---|
| 1 | **Lorenz-96** (`Lorenz96`) | 4 | 2: 1.625, 0.1719 (then -1.194, -3.550); KY 3.170 | 1.336 | Yes: quadratic, periodic coupling `(X[i+1]-X[i-2])X[i-1]-X[i]+F` | f=20 | Higher dimension (4, KY 3.2) with a ratio lambda_2/lambda_1 of 0.11. Lorenz's own paper used K=4 only at F=15 and 18 (earlier note); F=20 is not checked against a source. |
| 2 | **Coupled Lorenz** (`LorenzCoupled`) | 6 | 2: 1.222, 0.1222 (then -1.265, -1.933, -13.62, -15.07); KY 3.041 | 1.028 | Yes (two Lorenz oscillators with coupling) | beta=2.667, eps=2.85, rho=28, rho1=35, rho2=1.15, sigma=10 | Highest dimension in the shortlist; cost times 2 to 3; equations not read here (only the class name and parameters). |
| 3 | **Hyper Lu** (`HyperLu`) | 4 | 2: 1.086, 0.4754 (third 0.0285 near zero, then -19.31); KY 3.082 | 1.043 | Yes, polynomial: `xdot = a(y-x)+w; ydot = -xz + cy; zdot = xy - bz; wdot = dw + xz` | a=36, b=3, c=20, d=1.3 | Citation in the JSON: Chen, Lu, Lu and Yu 2006, Physica A, doi 10.1016/j.physa.2005.09.039. A hyperchaotic Lorenz-family system with two growth rates of ratio 2.3. |
| 4 | **Hyper Jha** (`HyperJha`) | 4 | 2: 0.3949, 0.2920 (third 0.0056, then -13.02); KY 3.053 | 0.3870 | Yes, polynomial: `xdot = a(y-x)+w; ydot = -xz + bx - y; zdot = xy - cz; wdot = -xz + dw` | a=10, b=28, c=2.667, d=1.3 | Two comparable rates (ratio 1.35): the strongest contrast to hyper-Rössler (0.19). JSON citation is a web page (Meier 2003), weak. |
| 5 | **Hindmarsh-Rose** (`HindmarshRose`) | 3 | 1: 0.2621 (max 0.6535) | 0.6535 | Yes, cubic: slow-fast neuron model `xdot = -x + y/tx - a x^3/tx + b x^2/tx + z/tx`, etc. | a=0.49, b=1, c=0.0322, d=1, s=1, tx=0.03, tz=0.8 | Qualitative departure (bursting, two time scales: tx=0.03 against tz=0.8). RK4 `max_dt` must resolve tx. Citation: Marhl and Perc 2005. |
| 6 | **Colpitts** (`Colpitts`) | 3 | 1: 0.1375 | 0.3736 | Piecewise-linear in the exponential-drive term (`fz = -u (1 - Heaviside(u))`, `u = z - (e-1)`): continuous, derivative jumps; like Chua | a=30, b=0.8, c=20, d=0.08, e=10 | A second piecewise-smooth circuit; mean x about 9.6, so the study's whitening and orbit bound on x[0] need a nonzero centre. |

Ranked by my reading of the owner's wording (higher dimension first, then qualitative departure): 2, 1, 4, 3, 5, 6. Not on the list because of failed machinery: Hamiltonian (DoublePendulum, HenonHeiles, SwingingAtwood, NuclearQuadrupole, ArnoldWeb), delay systems and nonautonomous systems (section D).

## C. The Dysts forecasting benchmark

### C.1 What was measured, by source

| Item | Gilpin 2021 (arXiv:2110.05266, https://arxiv.org/pdf/2110.05266) | Gilpin 2023 (arXiv:2303.08011, https://ar5iv.labs.arxiv.org/html/2303.08011) | Zhang and Gilpin 2025 (arXiv:2505.11349; 2409.15771) |
|---|---|---|---|
| Source status | read directly pp. 1-7 of the v1 PDF; the supplementary appendix is not in that PDF | fetch extract only (the last 13,555 characters, references, were read; no appendix numbers) | fetch extract only |
| Systems | "131 known chaotic dynamical systems", 16 precomputed trajectories each: coarse and fine sampling, train and test from different initial conditions, multivariate and univariate, with and without Brownian noise (Sec. 2, "Scale and structure") | 135 systems | 135 systems; 20 random initial conditions each |
| Sampling | "optimal integration timestep and dominant timescale (used for aligning timescales across systems)"; "all systems are aligned to the same average period" (Sec. 3, Task 1). Benchmark files named `pts_per_period_100`, `periods_12` train, `periods_60` or `periods_12` test (`classical_benchmarks.py`, fetch extract) | integration step t_max/10, resampled to 100 points per dominant period; Lyapunov-time scaling for reporting | 30 points per Lyapunov time (Sec. 4); trajectory length 10^5 (2505.11349) or 812 points (2409.15771) |
| Train/test | train 12 periods; validation = the last 1/6 of the train series; test with long test file: first 1/6 used to fit, the rest 5/6 forecast (`classical_benchmarks.py`); forecast horizon = the whole held-out segment | history about 10 periods (about 1000 points) plus 200 validation points; horizons to 50 periods | context 512 (2409.15771: 512 train, 300 test = about 10 Lyapunov times); 2505.11349: next 300 points, "equivalent to 10 Lyapunov times" (the extract printed a doubled digit string) |
| Metrics | eight metrics (MSE, MASE, MAE, MARRE, abs CV, 1 - r^2, MAPE, sMAPE); sMAPE is the reported one ("Hereafter, we report sMAPE errors"). No valid prediction time. | sMAPE; valid prediction time = "latest time when SMAPE<50" (App. A, fetch extract), alternative "first doubling of accumulated pointwise errors"; reported in lambda_max t units | VPT = "first forecast horizon at which the sMAPE exceeds a fixed threshold epsilon", epsilon = 30 (2409.15771 Sec. 4, fetch extract); 2505.11349 reports VPT in Table 5 but its definition was not in the text I read |
| Normalisation by Lyapunov time | none in the 2021 text; `classical_benchmarks.py` applies none | yes (lambda_max t) | yes (tau = 1/lambda, lambda = Dysts annotation) |
| Noise | observational noise sweep script `sweep_noise.py`: independent Gaussian noise of scale `granularity * std(train_data)` for `np.linspace(0, 5, 10)`, i.e. 0 to 5 times the series' standard deviation in 10 levels (fetch extract); the paper only says noise "increased to a level dominating the signal" | none in the main experiments | Gaussian noise at levels 1e-3, 1e-2, 1e-1 on trajectories normalised to zero mean and unit standard deviation (2505.11349 App. E, fetch extract) |
| Models | 15 named of "16": NBEATS, Transformer, LSTM, TCN, Prophet, exponential smoothing, Theta, 4Theta, random forest, ARIMA, AutoARIMA, Fourier regression, linear regression, three naive baselines (mean, seasonal, drift). No analog or nearest-neighbor baseline. No model with physics knowledge. | 24 methods incl. ESN, NVAR (next-generation reservoir), neural ODE; "It does not evaluate nearest-neighbor, analog, or known-equation models" (fetch extract) | Chronos family, NBEATS, TiDE, NVAR, Transformer, LSTM (2409.15771); context parroting = a 1-nearest-neighbor search in the delay-embedded space of the context (2505.11349 Sec. 3: "can be seen as a nearest neighbor algorithm in the D-dimensional delay-embedded space"), plus simplex projection, DynaMix, TimesFM, TimeMoE |
| Per-system numbers for Lorenz, Rössler, Chua | none in the 2021 text; the per-system results are in `dysts_data/benchmarks/results/*.json.gz` (listed, not opened: dataset limit) | none (named only as examples) | not in the text I read |

Repository files seen (not opened; `https://github.com/williamgilpin/dysts_data/tree/main/dysts_data/benchmarks`, fetch extract of the directory listing): `classical_benchmarks.py`, `compute_benchmarks_multivariate.py`, `esn_benchmarks.py`, `nvar_benchmarks.py`, `node_benchmarks.py`, `sweep_noise.py`, `sweep_granularity.py`, `find_attractor_properties.py`, `calculate_all_lyapunov_exponents.py`, a `results` directory with 28+ files (for example `results_test_multivariate__pts_per_period_100__periods_12.json.gz`, `results_esn_multivariate.json`), `hyperparameters`, `saved_models`. `BENCHMARKS.md` (fetch extract) lists the tasks (forecasting, importance sampling, transfer learning, symbolic regression, neural ODE) and says nothing about metrics, horizons or noise levels.

### C.2 One number that sits near ours

2505.11349 Appendix E, Table 5 (fetch extract, section "Valid prediction time across noise levels", caption: "higher is better"): at noise level 10^-2, context parroting 2.10 +- 0.18, Chronos 1.65 +- 0.18, TimesFM 1.05 +- 0.19, TimeMoE 0.92 +- 0.16, Chronos Bolt 0.79 +- 0.18. Units not stated in the extract; the VPT definition for this table was not in the text; the average is across systems (not a named system) as far as the extract shows. This is an uncontrolled comparison, listed only because noise 10^-2 of a unit-variance series is about 1% of sigma and the method is analog-like.

### C.3 What can and cannot be compared with the study's quantities

The study's CP median first-horizon-with-error-above-0.2 of the attractor scale, in Lyapunov times, at rho = 1% of sigma_x: 1.97 (Lorenz), 3.43 (Rössler), 2.8 (Chua).

| Aspect | Verdict |
|---|---|
| Quantity | **Cannot be compared directly.** The study uses an absolute error threshold (0.2 of the attractor scale) on a per-state forecast with the library held apart from the query; Dysts 2021 reports sMAPE averaged over a whole forecast window of tens of periods (no horizon, no threshold); the 2023 and 2025 papers use VPT with an sMAPE threshold of 30 or 50 (sMAPE is relative, scale-free in a different way). I read no per-system number for Lorenz, Rössler or Chua in any of the three papers. |
| Time unit | **Not aligned.** The study fixes 30 steps per its own Lyapunov time. Zhang and Gilpin use 30 points per Lyapunov time with the Dysts annotation, which for Rössler and Chua is 2.1 and 2.85 times the study's lambda (A.3, A.4): their "Lyapunov times" for those systems are not the study's. The 2021 paper uses periods, not Lyapunov times. |
| Noise | Closest: 2505.11349 App. E at 10^-2 of a unit-variance series (about the study's rho = 1% of sigma_x); the 2021 sweep uses multiples of the standard deviation from 0 to 5 in 10 steps (no 1% level; its 0.556 sigma and larger are far above). |
| Analog baseline | Closest: context parroting, a 1-nearest-neighbor delay-embedding forecaster (2505.11349). It differs from CP: its library is the context (512 or 2000 points, or longer in other experiments), not an independent library of the study's size; CP's details (k, delay embedding) should be compared in the reader's own documents. |
| Physics-based baseline | The Dysts papers have no model with a known equation (2023 extract states this). PLP (known equations, estimated state) has **no counterpart**. The ESN, NVAR and neural-ODE models of 2023 are data-driven, not physics-based. |
| Metrics that could be reported by the study for a fair comparison | VPT with sMAPE threshold 30 (2409.15771) and 50 (2023 appendix) computed on the study's own forecasts, in Lyapunov times from the study's lambda. Descriptive only. |

## D. Candidate Dysts systems for the further comparison runs (item 2)

### D.1 Method and caveats

I read the Dysts JSON in two halves (characters 0-100,000 and 100,000 to the end) with a prompt that asked for a table of every entry. The table below is a selection from those two tables. Every number is as relayed by the summariser, 4 significant digits. Lyapunov fields are the Dysts fields and are unreliable (A.3, B.1): in the first half the maximum field differs from spectrum[0] by factors from 0.44 to 2.67 for many entries. Rank the candidates only after recomputing lambda with the study's Benettin routine.

Needs, from the owner: smooth or piecewise-smooth autonomous ODE with an exact model, at most 6 dimensions, one dominant positive exponent or two, bounded attractor, a well-defined Lyapunov time.

### D.2 Proposed list (up to 8, ranked for the study)

Ranking criteria (mine): (a) vector field exact, autonomous, polynomial or piecewise-linear; (b) at most 6 dimensions; (c) adds a property the three studied systems lack; (d) lower risk to the machinery. Section B.3 gives the same systems again in the owner's "dimensionality or departure" order; here the order is by risk-adjusted fit.

| Rank | Dysts name | Dim | Positive exponents (Dysts spectrum) | Dysts max | Parameters (Dysts) | What it adds | What would break the machinery |
|---|---|---|---|---|---|---|---|
| 1 | `Lorenz96` | 4 | 2: 1.625, 0.1719 | 1.336 | f=20 | dimension 4, KY 3.2 | PLP needs D >= m + 1 = 5 delays (the study's D = 7 is enough); the estimator's width rule; two exponents with a ratio 0.11 (Lyapunov time dominated by lambda_1). |
| 2 | `HyperLu` | 4 | 2: 1.086, 0.4754 | 1.043 | a=36, b=3, c=20, d=1.3 | two comparable growth rates | w std 43.6 (the 4th coordinate has a large range); stiffness (lambda_4 = -19.3 against lambda_1 = 1.09): RK4 `max_dt` from the V6 halving check. |
| 3 | `HyperJha` | 4 | 2: 0.3949, 0.2920 | 0.3870 | a=10, b=28, c=2.667, d=1.3 | rate ratio 1.35 | w std 73 (largest range); "the Lyapunov time" is ambiguous with two comparable rates; JSON source is a web page. |
| 4 | `HindmarshRose` | 3 | 1: 0.2621 | 0.6535 | a=0.49, b=1, c=0.0322, d=1, s=1, tx=0.03, tz=0.8 | bursting, two time scales | tx = 0.03 requires a small `max_dt`; the delay window of 6 tau may straddle a burst and a quiet phase; mean and std of x are 0.003 and 0.33 (small-scale coordinates). |
| 5 | `Chen` | 3 | 1: 2.047 | 2.006 | a=35, b=3, c=28 | a Lorenz-family system with spectrum fields that agree with each other (the only entry here where spectrum[0] and max agree to 2%) | Low novelty (Lorenz-like with a=35, c=28); fast (period 0.587), Delta = 1/(30 lambda_max) about 0.017; orbit bound on x (std 8.4). |
| 6 | `Colpitts` | 3 | 1: 0.1375 | 0.3736 | a=30, b=0.8, c=20, d=0.08, e=10 | a second piecewise-linear circuit (like Chua) | The vector field is the ReLU-type `-u(1 - Heaviside(u))`: derivative jumps at u = 0 (the saltation argument of the math note applies); the first coordinate has mean 9.6 and std 1.15, so the study's whitening and the orbit bound centred on 0 must change. |
| 7 | `Arneodo` | 3 | 1: 0.2429 | 0.2374 | a=-5.5, b=4.5, c=1, d=-1 | a cubic jerk system (x''' = -a x - b x' - c x'' + d x^3) | x mean -1.67 and an asymmetric orbit (x std 1.01, z std 3.39); the observed coordinate x is smooth. The twin `Coullet` has parameters a=-0.8, b=1.1, c=0.45, d=-1 (spectrum 0.1489). |
| 8 | `LorenzCoupled` | 6 | 2: 1.222, 0.1222 | 1.028 | beta=2.667, eps=2.85, rho=28, rho1=35, rho2=1.15, sigma=10 | dimension 6, KY 3.0 | Cost times about 3 or more; D must exceed 2 x KY = 6; equations not read (class name and parameters only). |

### D.3 Not ranked, with the reason (from the Dysts fields and flags)

- **Nonautonomous** (the JSON flag `nonautonomous: true`): ArnoldWeb, BickleyJet, BlinkingRotlet, BlinkingVortex, DoubleGyre, Duffing, FluidTrampoline, ForcedBrusselator, ForcedFitzHughNagumo, ForcedVanDerPol, InteriorSquirmer, LidDrivenCavityFlow, OscillatingFlow, StickSlipOscillator, TurchinHanski, CircadianRhythm. The study's `field_fn(state, params)` is autonomous.
- **Delay** (flag `delay: true`, embedding_dimension 10): IkedaDelay, MackeyGlass, PiecewiseCircuit, ScrollDelay, SprottDelay, VossDelay.
- **Hamiltonian** (flag `hamiltonian: true`): DoublePendulum (angles are unbounded and the Dysts spectrum is not symmetric: 8.464, 0.4641, -0.1735, -10.81), HenonHeiles (spectrum 0.02675, 0.0115, -1.4e-5, -0.01115: not symmetric), SwingingAtwood, NuclearQuadrupole, ArnoldWeb. The math note rated Hénon-Heiles medium risk (sticky islands).
- **Dysts fields that look wrong for a dissipative chaotic flow** (derived: spectra that are not sorted into one clearly positive, one zero and negative values, or a Kaplan-Yorke dimension that exceeds the dimension): SprottA (spectrum 0.02926, 0.00499, -0.001556; KY 60.67), NoseHoover (KY 6.213 in 3 dimensions), Bouali2 (KY 16.47), BelousovZhabotinsky (lambda 114.6: stiff), CaTwoPlusQuasiperiodic (KY 4.548), MacArthur and other 10-dimensional systems. These must not be taken as chaotic from the JSON alone.
- Other single-exponent 3D smooth systems with Dysts parameters, all in the JSON and plausible but with weaker novelty: Halvorsen (a=1.4, b=4; spectrum 0.5862, max 0.6964; cyclic symmetry; mean x about -3.2), Aizawa (a=0.95, b=0.7, c=0.6, d=3.5, e=0.25, f=0.1; spectrum 0.08948, 0.02031, -0.3091 which has a second positive entry that is probably a zero), RabinovichFabrikant (a=1.1, g=0.87; the system is known to have escaping orbits; `unconfirmed (memory)`), Lu-Chen, Qi (4D, cubic terms), HyperBao, HyperCai (4D, lambda_2 = 0.1285 against lambda_1 = 1.634, ratio 0.08), HyperQi (fast: lambda 13.9, period 0.06).

## E. What I could not read

- The script that writes the JSON field `maximum_lyapunov_estimated` (not in `find_attractor_properties.py` as the summariser described it; the `dysts/analysis.py` function `max_lyapunov_exponent` is a candidate, with no link read). Hence A.5's last row stays open.
- The Dysts documentation website (I read the README, `flows.py`, `base.py`, `analysis.py` through the summariser only).
- The 2021 paper's supplementary appendix (Lyapunov method "see supplementary material"): not in the arXiv v1 PDF I received; the ar5iv extract confirms the supplement exists. The 2021 benchmark results (JSON files), not opened by the dataset limit.
- Primary Rössler 1979 (Phys. Lett. A 71, 155), Pomeau and Manneville 1980 (CMP), Scholarpedia "Hyperchaos" (certificate expired).
- Definition of VPT and per-system numbers in arXiv:2505.11349 (the extract had the Table 5 caption and values only), per-system VPT in arXiv:2303.08011, and the journal reference of Ramasubramanian and Sriram (Phys. D reference not read in the file).
- Literature spectra for the Section D systems (all spectra there are Dysts fields).
- The published lambda_max and lambda_2 at Lorenz r = 166.1.

## F. Summary (200 words)

Confirmed: the Dysts Lorenz, Rössler and Chua entries use the same equations, the same Chua diode (m0 inner, m1 outer), and the equation's own time (no rescaling) as the study. Parameters differ only by rounding (beta 2.667; m0 -1.142857, m1 -0.71429). The hyperchaotic Rössler system and Dysts entry HyperRossler match the mathematician's equations and parameters. Ramasubramanian and Sriram's Table 1 gives the published spectrum: 0.1121, 0.0196, 0, -25.19 (read directly). "30 points per Lyapunov time" is a Zhang and Gilpin convention (fetch extracts).

Disagree: Dysts `maximum_lyapunov_estimated` is 2.09 (Rössler) and 2.85 (Chua) times the study's values. Dysts' own spectrum[0] is within 6 to 7% of the study's. The cause is not shown in any text I read. The Dysts HyperRossler spectrum (0.279, 0, -0.30, -70.3) contradicts the published one (derived).

Could not read: the script that writes the maximum field; any lambda at Lorenz r = 166.1 (the 0.61 stays unverified); per-system Dysts benchmark numbers; Rössler 1979 and Scholarpedia. The Dysts benchmark uses sMAPE, 100 points per period and no analog or physics baseline in 2021, so direct comparison is not possible.

Sources: all URLs are in the tables above.
