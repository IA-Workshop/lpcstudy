# Research note: AMI first-minimum delay, Lorenz-63 x (WU-0013 follow-up)

Date retrieved: 2026-10-11. Researcher agent. Read-only; fetches: 2 searches (standard), 1 extended search, 4 fetches, about 12 PDF pages.

## Study context (read from the worktree)

- `select_delay` (lpcstudy/embedding.py:70): first local minimum of a 3-point-smoothed AMI curve; fallback global minimum.
- Test `test_regression_ami_delay_lorenz_band` (tests/unit/test_embedding.py:25): x of Lorenz-63 at dt = 0.0368, 32-equiprobable-bin AMI; band `3 <= delay <= 8` steps (0.110-0.294 time units). Current return value: 5 steps = 0.184 time units.
- dt = 0.0368 gives 1 Lyapunov time = 30 steps = 1.104 time units. Sigma, rho, beta were not re-read from systems.py or the methods v2 document by me beyond the dt given in the request.

## Findings

| Claim | Source | Status | Supporting quote | Conditions | Retrieved |
|---|---|---|---|---|---|
| AMI first minimum of Lorenz x near tau = 18 samples = 0.18 time units (dt = 0.01); a practitioner would choose tau_I = 60 (0.60 time units) | Deshmukh, Bradley, Garland, Meiss, "Using Curvature to Select the Time Lag for Delay Reconstruction", arXiv:2003.06509v1 (7 Mar 2020; preprint "in review at Chaos"); https://arxiv.org/abs/2003.06509 ; PDF p. 8, Sec. IV.B "Classic Lorenz Attractor", Fig. 5 | confirmed (I read the PDF page) | "for the standard parameters sigma = 10, beta = 8/3, and rho = 28. We use a fourth-order Runge-Kutta method with a fixed time step of 0.01 and integrate the system to t = 1000. Discarding the initial transient t < 100, we obtain a time series of length 90,000. As before, we take x(t) to be the measurement function. Fig. 5 shows the mean curvature and average mutual information plots for these data. The first minima of both curves fall near tau = 18. ... Indeed, based on this AMI profile, it is quite likely that a practitioner would actually choose tau_I = 60." | Observed x(t); RK4, dt = 0.01; 90,000 points; AMI by the `mutual` command of TISEAN (Sec. IV, p. 6; bin count not stated). The tau = 18 AMI minimum in Fig. 5 is a shallow shoulder (AMI about 0.65 at 18 against 0.7 near 30), and the deeper minimum is near tau = 60. Time units are my conversion (18 x 0.01). | 2026-10-11 |
| AMI first minimum of Lorenz x(t) at T = 10 "in units defined by the numerical integration step" | Abarbanel, Masuda, Rabinovich, Tumer, "Distribution of Mutual Information", arXiv:nlin/0011016v1 (9 Nov 2000); https://arxiv.org/abs/nlin/0011016 ; PDF p. 3 | confirmed as to the quote; time value `unconfirmed` (step size and Lorenz parameters not stated in this note) | "For the Lorenz system data set we used 2x10^6 values of the variable x(t). The first minimum of AMI for these data is at T = 10 in units defined by the numerical integration step." | Variable x; histogram bin count not stated; 2x10^6 points; the parameters and dt are not given, so no time-unit value. If the step were 0.01 the value would be 0.1 time units; that is unconfirmed (memory) and not checked. | 2026-10-11 |
| First minimum of mutual information of the Lorenz attractor at T = 0.16 natural time units (second, slightly lower, at 0.62) | E. Weeks (Emory), "Mutual Information to find delay coordinates", https://faculty.college.emory.edu/sites/weeks/research/tseries3.html (the physics.emory.edu URL returned 404) | partially supported (web page read through a summarizing fetch tool; informal course page, not peer reviewed) | "The first minimum occurs at T=0.16" ... "the second slightly lower minimum occurs at T=0.62" (as returned by the fetch tool; I did not see the raw page) | Variable and Lorenz parameters not stated on the page; "all times are in natural units"; estimator is Fraser-Swinney style, bin count not stated. | 2026-10-11 |
| Fraser and Swinney 1986, Phys. Rev. A 33, 1134: Lorenz example | Weeks page (secondary) says their test case is the Rossler attractor | not supported (no Lorenz delay found); original not retrieved | - | Not retrieved (paywalled; the search surfaced only bibliographic records). | 2026-10-11 |
| Kantz and Schreiber; Abarbanel book; Cao 1997; Kennel et al. | not retrieved | could not retrieve | - | Books and paywalled papers; no value taken from memory. | 2026-10-11 |

## Conversion to steps at dt = 0.0368

- 0.18 time units = 4.9 steps (Deshmukh et al.).
- 0.16 time units = 4.3 steps (Weeks, partially supported).
- 0.60 time units = 16.3 steps (the deeper AMI minimum in Deshmukh et al. Fig. 5).
- The Abarbanel et al. value, T = 10 integration steps, cannot be converted without the step size.

## Assessment: does it support a band tighter than [3, 8] steps?

- The two time-unit values that exist (0.16 and 0.18) sit inside [3, 8] and bracket the current value of 5 steps (0.184). They would support a band of roughly [4, 6] steps (0.147-0.221 time units).
- That tightening is weak. The only peer-reviewed-style source (a preprint) calls its 0.18 minimum shallow, and gives 0.60 as the delay a practitioner would pick. Estimators differ (TISEAN versus 32 equiprobable bins plus 3-point smoothing), and the Weeks value has unstated variable and parameters.
- The study's [3, 8] band is consistent with the cited values. The first-minimum location is estimator-dependent, so the evidence does not justify a tighter band without a stated estimator-matching tolerance. If the owner wants a cited anchor, use Deshmukh et al. (0.18 time units, x, standard parameters) as a consistency check, with a tolerance that reflects the shallowness of the minimum.

## Notes

No fetched page contained instructions addressed to the agent.
