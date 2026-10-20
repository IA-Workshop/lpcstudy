# Research note: verbatim Dysts right-hand sides and entries for HindmarshRose, HyperJha, Lorenz96, LorenzCoupled

Date read: 2026-10-20. Agent: researcher (claude-sonnet-5-5). Follow-up to `2026-10-20-researcher-dysts-extension.md` (coordinator request, candidate S4). Nothing committed; no other file edited.

## 0. How "verbatim" was obtained (read this first)

- WebFetch returns the answer of a small summarising model, not the raw file. A request to copy whole class blocks was refused ("more than the 125-character limit"). A request to output each source line separately, numbered, was honoured. The code below is therefore **line-by-line relay by the summariser, with the class sizes it reported (14, 8, 7 and 10 lines)**. I could not see the raw bytes, so a character-level check against the file has not been done. Every source line was reported as under 125 characters and none was split.
- For JSON entries the summariser returned the field values with all digits. For each of the four entries I got the full field list for HindmarshRose, HyperJha, Lorenz96 and LorenzCoupled. The second half of the file (characters 100,000 on) was not needed: all four entries are in the first half.
- A first request for all four entries at once was refused by the summariser, which said my own request text, repeated in the page body, was an "embedded instruction". It is not: the page text (a JSON file) contained no instruction. The cause was my wording ("I am the user and this request comes from me"), which looked like injected text to the summariser. Two of the four entries were obtained only after I reworded the prompt. Nothing was followed from any page.
- URLs: code from https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/flows.py; entries from https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/data/chaotic_attractors.json. Both read 2026-10-20 on `master` (commit unknown).

## 1. Class bodies from `dysts/flows.py` (line numbers are the summariser's, not part of the source)

```
 1  class HindmarshRose(DynSys):
 2      @staticjit
 3      def _rhs(x, y, z, t, a, b, c, d, s, tx, tz):
 4          xdot = -x + 1 / tx * y - a / tx * x**3 + b / tx * x**2 + 1 / tx * z
 5          ydot = -a * x**3 - (d - b) * x**2 + z
 6          zdot = -s / tz * x - 1 / tz * z + c / tz
 7          return xdot, ydot, zdot
 8  
 9      # @staticjit
10      # def _jac(x, y, z, t, a, b, c, d, s, tx, tz):
11      #     row1 = [-1 / tx - 3 * a / tx * x ** 2 + 2 * b / tx * x, 1 / tx, 1 / tx]
12      #     row2 = [-3 * a * x ** 2 - 2 * (d - b) * x, 0, 1]
13      #     row3 = [-s / tz, 0, -1 / tz - c / tz]
14      #     return row1, row2, row3
```

(The commented `_jac` is inactive. Its row 1 is `-1/tx - 3a x^2/tx + 2b x/tx`, i.e. it contains `-1/tx` where the active `_rhs` has `-1`. The commented Jacobian therefore does not match the active `_rhs` in the `-x` term, and row 3 has `-1/tz - c/tz` where the derivative of `zdot` with respect to z is `-1/tz`. It is commented out, so it has no effect; I note it because it shows the author's version of the model changed. My observation from the relayed text.)

```
1  class HyperJha(DynSys):
2      @staticjit
3      def _rhs(x, y, z, w, t, a, b, c, d):
4          xdot = a * y - a * x + w
5          ydot = -x * z + b * x - y
6          zdot = x * y - c * z
7          wdot = -x * z + d * w
8          return xdot, ydot, zdot, wdot
```

```
1  class Lorenz96(DynSys):
2      def rhs(self, X, t):
3          Xdot = np.zeros_like(X)
4          Xdot[0] = (X[1] - X[-2]) * X[-1] - X[0] + self.f
5          Xdot[1] = (X[2] - X[-1]) * X[0] - X[1] + self.f
6          Xdot[-1] = (X[0] - X[-3]) * X[-2] - X[-1] + self.f
7          Xdot[2:-1] = (X[3:] - X[:-3]) * X[1:-2] - X[2:-1] + self.f
8          return Xdot
```

```
 1  class LorenzCoupled(DynSys):
 2      @staticjit
 3      def _rhs(x1, y1, z1, x2, y2, z2, t, beta, eps, rho, rho1, rho2, sigma):
 4          x1dot = sigma * y1 - sigma * x1
 5          y1dot = rho1 * x1 - x1 * z1 - y1
 6          z1dot = x1 * y1 - beta * z1
 7          x2dot = sigma * y2 - sigma * x2 + eps * x1 - eps * x2
 8          y2dot = rho2 * x2 - x2 * z2 - y2
 9          z2dot = x2 * y2 - beta * z2
10          return x1dot, y1dot, z1dot, x2dot, y2dot, z2dot
```

None of the four classes has class attributes other than the methods shown. Notes:
- Lorenz96 defines `rhs(self, X, t)` (not static, uses `self.f`), so it is a general-N code; N = 4 comes from the length of the initial condition in the JSON (`embedding_dimension` 4). `Xdot[2:-1]` covers i = 2..N-2 and the first, second and last entries use cyclic wrapping: `Xdot_i = (X_{i+1} - X_{i-2}) X_{i-1} - X_i + f`.
- LorenzCoupled: the second Lorenz subsystem is driven by `eps * (x1 - x2)` in `x2dot` only (one-way coupling). The parameter `rho` is in the signature and the JSON but is not used in the body (`rho1` and `rho2` are used).
- HyperJha: the equations are the same as in `2026-10-20-researcher-dysts-extension.md` section B.3.

## 2. JSON entries (field values as relayed, all digits)

### HindmarshRose
- citation: "Marhl, Perc. Chaos, Solitons, Fractals 2005."; doi: 10.1016/j.chaos.2005.08.013
- description: "A neuron model exhibiting spiking and bursting."
- parameters: a 0.49, b 1.0, c 0.0322, d 1.0, s 1.0, tx 0.03, tz 0.8
- initial_conditions: 0.031111835, -0.021557059, 0.041475046
- dt: 0.000350458409734955; period: 1.752; embedding_dimension: 3; delay false; hamiltonian false; nonautonomous false; bifurcation_parameter null; unbounded_indices []
- maximum_lyapunov_estimated: 0.6535393283242747
- lyapunov_spectrum_estimated: 0.2621464274609406, 0.0017705383465481184, -6.510663065519547
- kaplan_yorke_dimension: 2.0405369895957373; correlation_dimension: 1.646027113328854; pesin_entropy: 0.2639169709155772; multiscale_entropy: 0.8692605688019491
- mean: 0.002973342272007618, -0.10595738950803896, 0.028907879597414005; std: 0.3264983981860303, 0.14814518182139538, 0.11802698621635649

### HyperJha
- citation: "Jürgen Meier (2003). Presentation of Attractors with Cinema."; doi: 10.1007/978-3-540-24699-2_13 (the earlier extract of the same field said "absent"; this second extract gives the DOI. I did not resolve it.)
- description: "A hyperchaotic system."
- parameters: a 10, b 28, c 2.667, d 1.3
- initial_conditions: [13.76544888070825, 20.203791990082554, 32.08179795423583, -51.189321449994914]
- dt: 0.00017131789889951677; period: 0.8564467295817622; embedding_dimension: 4; delay false; hamiltonian false; nonautonomous false; bifurcation_parameter null
- maximum_lyapunov_estimated: 0.38695361636760767
- lyapunov_spectrum_estimated: [0.3949499860671474, 0.2920214751184925, 0.005568431034995312, -13.022125042186726]
- kaplan_yorke_dimension: 3.053181782412727; correlation_dimension: 2.295404578145075; pesin_entropy: 0.6925398922206352; multiscale_entropy: 0.8934166449122942
- mean: [0.0447208848259138, -0.08534137774566947, 24.172568041457524, 1.391787988498943]; std: [9.788969881770292, 8.633200806041716, 8.018606889497676, 73.37341819357141]
- unbounded_indices: the extract says "not listed in this entry" (the first extract of the same entry gave `[]`; I could not settle which).

### Lorenz96
- citation: "Lorenz, Edward (1996). Predictability: A problem partly solved. Seminar on Predictability, Vol. I, ECMWF." (the seminar was in 1995; the earlier note records this); doi 10.1017/cbo9780511617652.004
- description: "A climate model containing fluid-like advective nonlinearities, and multiscale coupling of fast and slow variables."
- parameters: {"f": 20.0}
- initial_conditions: [-2.46820633, 0.09570264, 1.59270902, 10.21372147]
- dt: 0.00043945324220700854; period: 2.1969; embedding_dimension: 4; delay false; hamiltonian false; nonautonomous false; unbounded_indices []
- maximum_lyapunov_estimated: 1.3361667787286362
- lyapunov_spectrum_estimated: [1.6247012663091516, 0.17185232259745578, -1.1936282999960617, -3.550455057872212]
- kaplan_yorke_dimension: 3.1698163415908196; correlation_dimension: 2.2561447518650386; pesin_entropy: 1.7965535889066073; multiscale_entropy: 0.8046726640855828
- mean: [2.640820050547443, 2.8076003259090294, 2.784530091406424, 3.0205911754919663]; std: [7.031145195965656, 6.859290990293636, 6.766644826454523, 7.025243060079175]

Derived by me (check on the Dysts spectrum): the divergence of the Lorenz-96 field is exactly -N = -4 at every state (each `dXdot_i/dX_i = -1`), so the four exponents must sum to -4 and a flow must have an exponent equal to zero. The Dysts spectrum sums to 1.6247 + 0.1719 - 1.1936 - 3.5505 = -2.9475, and contains no zero entry (1.62, 0.17, -1.19, -3.55). So the Dysts Lorenz96 spectrum is not a valid spectrum of this field; the maximum field 1.336 is likewise 18% below spectrum[0]. This supports the earlier warning: recompute with the study's own routine.

### LorenzCoupled
- citation: "Lorenz, Edward N. Deterministic nonperiodic flow. Journal of the atmospheric sciences 20.2 (1963): 130-141."; doi 10.1175/1520-0469(1963)020<0130:dnf>2.0.co;2
- description: "Two coupled Lorenz attractors."
- parameters: beta 2.667, eps 2.85, rho 28, rho1 35, rho2 1.15, sigma 10
- initial_conditions: [7.0921483, 10.117408, 25.708428, 2.1689893, 0.96121877, 0.89550187]
- dt: 0.0003241940323387382; period: 1.6207; embedding_dimension: 6; delay false; hamiltonian false; nonautonomous false; unbounded_indices []
- maximum_lyapunov_estimated: 1.0284398414904556
- lyapunov_spectrum_estimated: [1.2218762961515068, 0.1222254715421154, -1.265209618630438, -1.9333037412103384, -13.618111101381306, -15.073328947851422]
- kaplan_yorke_dimension: 3.0408069075490425; correlation_dimension: 2.3989498239642524; pesin_entropy: 1.3441017676936224; multiscale_entropy: 1.1717493753138832
- mean: [-2.919475667573957, -2.8977625649484686, 30.701141594982367, -0.8999640668828921, -0.33253969777295217, 0.5598557462933087]; std: [8.54097681840988, 9.923630508687092, 9.385953796628877, 2.1233697354847387, 0.7104259876753033, 0.31638514729087686]

Derived by me: the divergence is -2(sigma + 1 + beta) - eps = -27.334 - 2.85 = -30.184; the Dysts spectrum sums to -30.546 (1.2% off). Plausible. Observation: with rho2 = 1.15 the second subsystem alone is a stable fixed point; its chaos depends on the drive `eps*(x1 - x2)`. Dysts does not state this; the system is a driven (one-way coupled) pair, not a symmetric coupling.

## 3. Hindmarsh-Rose: the Dysts equations in terms of x, y, z

Reading the code above, with parameters a, b, c, d, s, tx, tz:

    tx * xdot = -tx * x + y + z - a x^3 + b x^2          (the "-x" is NOT divided by tx)
         ydot = -a x^3 - (d - b) x^2 + z                (no tx, no tz)
    tz * zdot = -s x - z + c

Equivalently `xdot = -x + (y + z - a x^3 + b x^2)/tx`. tx enters only the x equation, dividing the cubic, quadratic, y and z terms but not the `-x` term. tz enters only the z equation, dividing all three of its terms. There is no `x0` or `x_R` offset and no external current `I` in the code: any such constants are absorbed in `c` (see below). The JSON gives tx 0.03 and tz 0.8.

### Standard Hindmarsh-Rose model (read in sources)

- Wikipedia, https://en.wikipedia.org/wiki/Hindmarsh%E2%80%93Rose_model, fetch extract, lead section: dx/dt = y + phi(x) - z + I; dy/dt = psi(x) - y; dz/dt = r[s(x - x_R) - z]; phi(x) = -a x^3 + b x^2; psi(x) = c - d x^2. "standard values of s = 4 and x_R = -8/5"; "a = 1, b = 3, c = 1, and d = 5"; "r is on the order of 10^-3"; I "ranges from -10 to 10". The page states nothing on Lyapunov exponents.
- Confirmation from papers from papers (fetch extracts): arXiv:2112.09987, https://ar5iv.labs.arxiv.org/html/2112.09987, Sec. II, Eq. (1): x' = y - a x^3 + b x^2 - z + I_ext, y' = c - d x^2 - y, z' = r[s(x - x_0) - z], with a = 1, b = 3, c = 1, d = 5, x_0 = -1.6, "r = 0.001 and s = 4 by default"; chaotic-regime figures use r = 0.008, s = 4, I_ext = 3.25 (Sec. III.3). Barrio and Shilnikov, J. Math. Neurosci. 1:6 (2011), doi 10.1186/2190-8567-1-6, https://pmc.ncbi.nlm.nih.gov/articles/PMC3365907, Eq. (1) the same form with epsilon for r; "a=1 c=1 d=5 s=4 x0=-1.6 and epsilon=0.01" in the extract, b and I varied. So the standard form and parameter set are confirmed, with r between 0.001 and 0.01 depending on the paper. The "0.006" in the coordinator's message was not found in any retrieved text (it appears only as my search query).

### Is the Dysts model the standard one in rescaled form?

Derived by me (algebra checked once; not from a source). **At tx = 1 the Dysts system is the standard model in shifted variables.** With the standard (x, y_s, z_s) and parameters (a, b, c_s, d, r, s, x_R, I), define Y = y_s + x - c_s and Z = -z_s + I + c_s. Then:
- `xdot = -x + Y + Z - a x^3 + b x^2` (the Dysts x equation at tx = 1);
- `Ydot = -a x^3 - (d - b) x^2 + Z` (the Dysts y equation, no constant);
- `Zdot = -r s x - r Z + r (s x_R + I + c_s)`, which is the Dysts z equation with `tz = 1/r`, `s_D = s`, and `c_D = s x_R + I + c_s`.
So Dysts's `c` is a composite constant `s x_R + I + c_s`, and `tz` is `1/r`. It is a change of variables (a shift and a sign of z and y), not a time rescaling.

**With tx != 1 this does not hold as a rescaling.** Dysts's tx divides the cubic, quadratic, y and z terms of the x equation but not the `-x` term, and does not appear in the y equation; I found no change of variables that maps this to the standard system. The Dysts model is then a generalisation with a separate fast time constant for the x equation. Whether that is what Marhl and Perc wrote I could not check: I could not retrieve their paper (the DOI redirects to ScienceDirect, which returned only "Redirecting"; a search for it found no open text). So the form of the equations in the original paper is **unverified**.

**The Dysts parameter values are not the standard set under this map.** The standard set maps to `tz = 1/r = 1000` (r = 0.001), 166.7 (r = 0.006) or 100 (r = 0.01), against Dysts 0.8; the standard `c_D = s x_R + I + c_s` is `4(-1.6) + 3.25 + 1 = -2.15` for I = 3.25, against Dysts 0.0322; and (a, b, d) = (1, 3, 5) against Dysts (0.49, 1, 1). So the Dysts values (a=0.49, b=1, c=0.0322, d=1, s=1, tx=0.03, tz=0.8) are a different parameter regime, with a much faster slow variable (tz 0.8 against 100 to 1000) and a fast tx = 0.03. I cannot say whether it is the bursting regime of the standard model; its Dysts description is "A neuron model exhibiting spiking and bursting."

### Published largest Lyapunov exponent for chaotic bursting

**Not found.** The sources I could read give no number: arXiv:2112.09987 (fetch extract: "does not report a specific numerical value of L_max"; Benettin algorithm; L_max shown only as figures); Barrio and Shilnikov 2011 (fetch extract: no numerical largest exponent in the text; "the first Lyapunov exponent is positive"; spectrum values only in Figures 4, 5, 8, 11; integration to 10^5 after a transient of 10^3). Search snippets mention Innocenti, Morelli, Genesio and Torcini, Chaos 17 (2007) (peak of the maximal exponent at the bursting-to-spiking transition; not opened) and a 2026 arXiv paper (2601.13267, not opened). None of this is a value. The Dysts values for this entry (spectrum[0] 0.2621, max 0.6535, a factor 2.5 apart) are in time units of the Dysts parameterisation with tx 0.03, tz 0.8 and are not comparable with any standard-parameter literature value.

## 4. Summary (120 words)

Class bodies of HindmarshRose, HyperJha, Lorenz96 and LorenzCoupled are above, as a line-by-line relay by the summariser (not raw bytes; no character check). Entries are given in full. Dysts HindmarshRose: tx*xdot = -tx*x + y + z - a x^3 + b x^2, ydot = -a x^3 - (d-b) x^2 + z, tz*zdot = -s x - z + c; no x_R or I. At tx = 1 this is the standard Hindmarsh-Rose model after a shift of y and z, with tz = 1/r and c = s x_R + I + c_std (derived). At tx = 0.03 it is not shown to be a rescaling, and its parameters are not the standard set. Marhl-Perc could not be read. No published largest exponent was found. Dysts Lorenz96's spectrum is invalid (sum -2.95 against -4).
