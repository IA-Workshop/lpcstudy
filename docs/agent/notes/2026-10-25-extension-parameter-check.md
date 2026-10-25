# Extension parameter check S1 to S6 (WU-0044)

Date retrieved: 2026-10-25. Agent: researcher (claude-sonnet-5-5). Unit WU-0044 (ROADMAP section 9; ledger seq 44, waiver condition seq 45). Code read: `lpcstudy/systems.py` in worktree `lpcstudy-wt/wu/0044-param-check` (field functions lines 39-288, SYSTEMS lines 338-451). I edited no file other than this note. I have no shell: **nothing was committed** (see section 0).

## 0. Method, limits, status words, and what could not be done

- **Fetch extract** = the answer of WebFetch's summariser, not raw bytes. **Read directly** = I viewed PDF page images myself. Nothing here is from memory unless labelled `unconfirmed (memory)`; none is used as confirmation.
- Status: `match` = the code agrees term by term / value by value with text I read today (quote given). `mismatch` = both texts differ (both given). `unconfirmed` = no source text retrieved that states or settles the item.
- Dysts snapshot: `master` of https://github.com/williamgilpin/dysts on 2026-10-25, commit unknown. Class bodies in `flows.py` were relayed line by line by the summariser (each line numbered, under 125 characters); the earlier notes' relay of 2026-10-20 and 2026-10-23 gives identical lines. Character-level fidelity is not checked.
- Two kinds of rows: **model specification** (equations, parameters: the question of the owner's waiver) and **Dysts' stored Lyapunov fields** (not model specifications; the study never used them, see section 7).
- **Network log.** The project hook writes the log entries automatically, to the **main checkout's** file `/home/brianm/projects/physics/chaos/lpcstudy/docs/agent/records/network-log.jsonl` (lines 416 to 445 are this session, 30 entries, all researcher). The worktree's copy of the log (315 lines) is older and was not changed. I cannot commit; the caller must copy or commit those lines on the branch. I did not edit the log by hand.
- **Original papers not retrievable.** Marhl and Perc 2005 (doi 10.1016/j.chaos.2005.08.013): redirect to linkinghub, then ScienceDirect HTTP 403. Rössler 1979 (doi 10.1016/0375-9601(79)90150-6): redirect to linkinghub, not followed (paywall). Meier 2003 chapter (doi 10.1007/978-3-540-24699-2_13): Springer redirected to an authorisation page. The "Jha 2002" paper named by a secondary source: not found by two searches. Scholarpedia "Hyperchaos": certificate expired. Lorenz 1963 (AMS PDF): HTTP 403; MIT copy: host not found.
- PRIME.11: no page carried an instruction. Search results ended with a line asking for a sources list (tool text, not acted on beyond the role's requirement). The summariser of the arXiv 2605.10685 page volunteered that two forms of Hyper-Jha "should be reconciled"; that is the summariser's remark, recorded in S5 as data.
- Limits: about 27 fetches plus 13 PDF pages read directly (R&S pp.16, 24; Lorenz 1996 pp.4, 5, 7-10; M&P pp.1, 3, 6, 7 of the scan; B&B p.8), 8 searches.

## 1. S1 `rossler_hyper` (hyperchaotic Rössler, Rössler 1979)

Code (`rossler_hyper_field`): `[-y - z, x + a y + w, b + x z, -c z + d w]`; params a 0.25, b 3.0, c 0.5, d 0.05; observed index 0 (x).
Sources: [D] Dysts `flows.py` class HyperRossler and JSON entry HyperRossler, https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/flows.py and https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/data/chaotic_attractors.json; [RS] K. Ramasubramanian and M. S. Sriram, arXiv:chao-dyn/9909029, https://arxiv.org/pdf/chao-dyn/9909029 (read directly); [W] https://en.wikipedia.org/wiki/Hyperchaos (fetch extract).

| Term | Code | Source value | Quote | Source | Status |
|---|---|---|---|---|---|
| x' | `-y - z` | `-y - z` | D: `xdot = -y - z`; RS eq. (57): `z1' = -(z2 + z3)` | D; RS p.16 | match |
| y' | `x + a y + w` | `x + a y + w` | D: `ydot = x + a * y + w`; RS: `z2' = z1 + a z2 + z4` | D; RS p.16 | match |
| z' | `b + x z` | `b + x z` | D: `zdot = b + x * z`; RS: `z3' = b + z1 z3` | D; RS p.16 | match |
| w' | `-c z + d w` | `-c z + d w` (Dysts); RS `c' z4 - d' z3` with their (c', d') = (0.05, 0.5) | D: `wdot = -c * z + d * w`; RS: `z4' = c z4 - d z3`, "where a, b, c and d are parameters whose values are taken to be 0.25, 3.0, 0.05 and 0.5 respectively". RS's c, d are the study's d, c (names swapped; same field) | D; RS p.16 | match |
| w' (further source) | same | `-0.5 z + 0.05 w` | W: "x' = -y - z, y' = x + 0.25 y + w, z' = 3 + x z, w' = -0.5 z + 0.05 w" (the page does not label it Rössler's 1979 system; it cites Rössler's "An equation for hyperchaos" for the 1979 pair) | W | match |
| a | 0.25 | 0.25 | JSON `"parameters": {"a": 0.25, "b": 3.0, "c": 0.5, "d": 0.05}` | D | match |
| b | 3.0 | 3.0 | same; RS "3.0" | D; RS | match |
| c | 0.5 | 0.5 | same; RS d' = 0.5 | D; RS | match |
| d | 0.05 | 0.05 | same; RS c' = 0.05 | D; RS | match |
| observed coordinate | index 0 = x | Dysts state order (x, y, z, w) | `_rhs(x, y, z, w, t, a, b, c, d)` | D | match (a study design choice; no source prescribes it) |
| citation | Rössler 1979 | "Rossler, O. E. (1979). An equation for hyperchaos." doi 10.1016/0375-9601(79)90150-6 | JSON `citation`, `doi` | D | match for the citation text; original paper itself not retrieved (paywall) |
| lambda_1 | 0.11252 (spec note 0.11252 +- 0.00056; cached 0.11251662) | 0.1121 (standard method), 0.1128 (new method), t = 1e5 | RS Table 1 p.24: "0.1121 / 0.0196 / -0.0000 / -25.1886" (method 1), "0.1128 / 0.0214 / -0.0000 / -24.7527" (method 3) | RS p.24 | match (+0.4% vs 0.1121; inside the 0.1121-0.1128 spread of two methods) |
| lambda_2 | 0.02072 | 0.0196 to 0.0214 | RS Table 1 as above | RS p.24 | match (inside the spread) |
| lambda_3 | -0.00001 | -0.0000 | same | RS p.24 | match |
| lambda_4 | -24.765 | -25.1886 / -24.7527 | same | RS p.24 | match (inside the spread) |
| Kaplan-Yorke d | 3.005 | none stated in any source; 3 + (0.1121 + 0.0196 + 0)/25.1886 = 3.0052 is arithmetic by me on RS Table 1 | (no source quote) | derived | unconfirmed as a stated value; consistent with the derivation |
| lambda_1 vs Dysts field | 0.1125 | Dysts `lyapunov_spectrum_estimated` [0.27859233648384435, -7.749198930652314e-05, -0.3014660985555502, -70.26609894565237]; `maximum_lyapunov_estimated` 0.1718849632568779 | JSON entry HyperRossler | D | mismatch (Dysts field, not a model spec; study never used it) |
| Kaplan-Yorke vs Dysts field | 3.005 | `kaplan_yorke_dimension` 2.916384112225743 | same | D | mismatch (Dysts field; follows its disputed spectrum) |

Summary S1: 15 match, 2 mismatch (both Dysts stored Lyapunov fields, not the specification), 1 unconfirmed (KY stated nowhere). Equations and parameters: all match, with two sources besides Dysts (RS, W). Rössler 1979 itself was not read.

## 2. S2 `lorenz63_r166` (Lorenz-63 at rho = 166.1)

Code: `lorenz63_field` = `[sigma (y - x), x (rho - z) - y, x y - beta z]`; sigma 10, rho 166.1, beta 8/3; observed index 0 (x).
Sources: [MP] P. Manneville and Y. Pomeau, "Different ways to turbulence in dissipative dynamical systems", Physica D 1, 219-226 (1980), scan read directly at http://math.la.asu.edu/~dieter/courses/Chaos/Pomeau_Manneville_1.pdf; [W] https://en.wikipedia.org/wiki/Lorenz_system (fetch extract); [D] Dysts (above).

| Term | Code | Source value | Quote | Source | Status |
|---|---|---|---|---|---|
| x' | `sigma (y - x)` | `sigma (y - x)` | MP p.219: "x' = sigma(y - x)"; D Lorenz: `xdot = sigma * y - sigma * x` | MP p.219; D | match |
| y' | `x (rho - z) - y` | `-x z + r x - y` | MP p.219: "y' = -xz + rx - y"; D: `ydot = rho * x - x * z - y` | MP p.219; D | match |
| z' | `x y - beta z` | `x y - b z` | MP p.219: "z' = xy - bz"; D: `zdot = x * y - beta * z` | MP p.219; D | match |
| sigma | 10 | 10 | MP abstract: "The Lorenz model is studied in details for sigma = 10, b = 8/3 and 145 < r < 170"; W: "Lorenz used the values sigma = 10, rho = 28, and beta = 8/3" | MP p.219; W | match |
| beta | 8/3 | 8/3 | MP abstract (above) | MP | match |
| rho = 166.1 | 166.1 | A value in the studied range; the threshold r_c = 166.07 | MP p.224: "a precise determination of the intermittency threshold r_c = 166.07"; Fig. 4 p.221 shows z at r = 166, 166.1, 166.3, 167 (panel labels read "r=166", "r=1661", "r=1663", "r=167" in the scan); Fig. 13 p.225 axis labels 166.1, 166.2, 166.3 | MP pp.221, 224, 225 | match (166.1 is 0.03 above r_c and is a plotted value; the paper does not prescribe it) |
| observed coordinate | index 0 = x | Lorenz state order (x, y, z) | D `_rhs(x, y, z, t, beta, rho, sigma)` | D | match (study design choice) |
| Dysts entry at r = 166.1 | none | none: no entry at rho 166.1 in either half of the JSON (first half: Lorenz rho 28; second half: no Lorenz63 or rho 166.1 entry) | fetch extracts | D | unconfirmed (no Dysts entry to match; none is required) |
| lambda_max | 0.6217 (cached 0.6217010) | no published value at r = 166.1 | MP p.224 gives only a scaling argument: "the mean correlation (or the inverse of the Lyapunov number [17]) is then expected to diverge as N_l itself ... that is to say as 1/sqrt(r - r_c)" (no number) | MP p.224 | unconfirmed |
| Kaplan-Yorke d | 2.044 | none stated | (earlier notes: none found) | | unconfirmed |

Reference only: the Lorenz-63 KY at rho = 28 is "2.06+-0.01" (W); not applicable to rho = 166.1.

Summary S2: 7 match, 0 mismatch, 3 unconfirmed (Dysts entry absent, lambda_max, KY). Lorenz 1963 itself was not retrieved (403); the equations match the 1980 paper, which is the source for the parameter regime.

## 3. S3 `rossler_z` (Rössler observed through z, state order (z, x, y))

Code (`rossler_zfirst_field`): `[b + z (x - c), -y - z, x + a y]` for state (z, x, y); a 0.2, b 0.2, c 5.7; observed index 0 (= Rössler z).
Sources: [D] Dysts class Rossler and JSON entry Rossler; [W] https://en.wikipedia.org/wiki/R%C3%B6ssler_attractor (fetch extract); [BB] Yu. I. Bogdanov and N. A. Bogdanova, arXiv:1412.2242, https://arxiv.org/pdf/1412.2242, p.8 (read directly).

| Term | Code | Source value | Quote | Source | Status |
|---|---|---|---|---|---|
| z' | `b + z (x - c)` | `b + z (x - c)` | D: `zdot = b + z * x - c * z`; W: "dz/dt = b + z(x - c)" | D; W | match |
| x' | `-y - z` | `-y - z` | D: `xdot = -y - z`; W: "dx/dt = -y - z" | D; W | match |
| y' | `x + a y` | `x + a y` | D: `ydot = x + a * y`; W: "dy/dt = x + ay" | D; W | match |
| a | 0.2 | 0.2 | JSON `"parameters": {a: 0.2, b: 0.2, c: 5.7}`; W: "Rössler studied the chaotic attractor with a = 0.2, b = 0.2, and c = 5.7" | D; W | match |
| b | 0.2 | 0.2 | same | D; W | match |
| c | 5.7 | 5.7 | same | D; W | match |
| state permutation (z, x, y) | index 0 = z | Dysts order (x, y, z) | the field is the registry Rössler with coordinates relabelled; checked term by term above | D | match (relabelling only; observing z is the study's design choice) |
| lambda_max | 0.07133 (cached 0.07133265, SE 0.23%) | 0.07062 +- 0.00066; Sprott 0.0714 (secondary) | BB p.8: "lambda_1 = 0.07062 +- 0.00066, lambda_2 = 0.000048 +- 0.00018, lambda_3 = -5.3937 +- 0.0018. Our values are close to the values obtained by Sprott J.C. [4]: lambda_1 = 0.0714, lambda_3 = -5.3943" | BB p.8 | match (+1.0% vs 0.07062, 1.1 sigma; -0.1% vs 0.0714). The a, b, c of the BB computation are not stated on p.8 (other pages not read) |
| lambda_max vs Dysts spectrum[0] | 0.07133 | Dysts `lyapunov_spectrum_estimated`[0] 0.0763301393780693 | JSON entry Rossler | D | match (+7%, as in earlier notes; Dysts field) |
| lambda_max vs Dysts max field | 0.07133 | `maximum_lyapunov_estimated` 0.15059688939547888 | same | D | mismatch (2.1 times; Dysts field, not a spec) |
| Kaplan-Yorke d | no S3 value in the specification notes | BB p.8: 2.013; D `kaplan_yorke_dimension` 2.0146095059018845 | BB: "d_KY = 2.013 (Rössler strange attractor)" | BB; D | unconfirmed (no study value to compare; the two sources agree with each other) |

Summary S3: 9 match (3 terms, a, b, c, permutation, lambda_max vs BB, vs Dysts spectrum[0]), 1 mismatch (Dysts max field, not the spec), 1 unconfirmed (KY).

## 4. S4 `hindmarsh_rose` (Hindmarsh-Rose type, Dysts parameterisation)

Code: `x' = -x + y/tx - a x^3/tx + b x^2/tx + z/tx`; `y' = -a x^3 - (d - b) x^2 + z`; `z' = (-s x - z + c)/tz`; a 0.49, b 1.0, c 0.0322, d 1.0, s 1.0, tx 0.03, tz 0.8; observed index 0 (x).
Sources: [D] Dysts `flows.py` class HindmarshRose and JSON entry HindmarshRose. Original: Marhl and Perc, Chaos, Solitons and Fractals 2005, doi 10.1016/j.chaos.2005.08.013, **not retrievable** (section 0). No other text states the Dysts parameterisation (one extended search found nothing).

| Term | Code | Source value | Quote | Source | Status |
|---|---|---|---|---|---|
| x', term -x | `-x` | `-x` | D line 4: `xdot = -x + 1 / tx * y - a / tx * x**3 + b / tx * x**2 + 1 / tx * z` | D | match (to Dysts) |
| x', term y/tx | `+y/tx` | `+1/tx * y` | same line | D | match |
| x', term a x^3/tx | `-a x^3/tx` | `-a/tx * x**3` | same line | D | match |
| x', term b x^2/tx | `+b x^2/tx` | `+b/tx * x**2` | same line | D | match |
| x', term z/tx | `+z/tx` | `+1/tx * z` | same line | D | match |
| y', all terms | `-a x^3 - (d - b) x^2 + z` | same | D line 5: `ydot = -a * x**3 - (d - b) * x**2 + z` | D | match |
| z', all terms | `(-s x - z + c)/tz` | `-s/tz * x - 1/tz * z + c/tz` | D line 6: `zdot = -s / tz * x - 1 / tz * z + c / tz` | D | match |
| a | 0.49 | 0.49 | JSON `"parameters": {"a": 0.49, "b": 1.0, "c": 0.0322, "d": 1.0, "s": 1.0, "tx": 0.03, "tz": 0.8}` | D | match |
| b | 1.0 | 1.0 | same | D | match |
| c | 0.0322 | 0.0322 | same | D | match |
| d | 1.0 | 1.0 | same | D | match |
| s | 1.0 | 1.0 | same | D | match |
| tx | 0.03 | 0.03 | same | D | match |
| tz | 0.8 | 0.8 | same | D | match |
| observed coordinate | index 0 = x | Dysts state order (x, y, z) | `_rhs(x, y, z, t, ...)` | D | match (design choice) |
| lambda_2 | +0.00002 | 0.0017705383465481184 | JSON entry HindmarshRose | D | match (both zero within the study's error; Dysts shows 0.0018) |
| Equations and parameters vs the original paper (Marhl and Perc 2005) | as above | not retrieved | JSON `citation`: "Marhl, Perc. Chaos, Solitons, Fractals 2005." | | unconfirmed |
| Relation to the standard Hindmarsh-Rose model | | Standard form has `x' = y - a x^3 + b x^2 - z + I`, `y' = c - d x^2 - y`, `z' = r [s (x - x_0) - z]`, a = 1, b = 3, c = 1, d = 5, s = 4, x_0 = -1.6 | arXiv:2112.09987 Eq. (1) (earlier note 2026-10-20, fetch extract, not re-fetched today) | | unconfirmed (the Dysts form at tx = 0.03 is not shown to be a rescaling of the standard model; the code docstring says so; the algebra at tx = 1 is in the earlier note, not a source) |
| lambda_1 | 0.21635 (cached 0.21688) | Dysts spectrum[0] 0.2621464274609406; max field 0.6535393283242747 | JSON entry HindmarshRose | D | mismatch (Dysts field vs study: 0.2164 against 0.2621, ratio 0.83; max field 3.0 times; no independent literature value; Dysts uses a first-order tangent method, earlier note) |
| lambda_3 | -6.363 | -6.510663065519547 | same | D | mismatch (2.3%; Dysts field) |
| Kaplan-Yorke d | 2.034 | 2.0405369895957373 | same | D | mismatch in value (0.3%; Dysts field; the study's d is from its own spectrum) |

Summary S4: 16 match (all equation terms, all seven parameters, observed coordinate, lambda_2), 3 mismatch (all Dysts stored Lyapunov fields), 2 unconfirmed (original paper not retrieved; relation to the standard model). **The specification matches Dysts exactly; whether it matches Marhl and Perc is not established.**

## 5. S5 `hyper_jha` (Dysts HyperJha)

Code: `[a (y - x) + w, -x z + b x - y, x y - c z, -x z + d w]`; a 10.0, b 28.0, c 2.667, d 1.3; observed index 0 (x).
Sources: [D] Dysts `flows.py` class HyperJha and JSON entry HyperJha. Original per Dysts: "Jürgen Meier (2003). Presentation of Attractors with Cinema.", doi 10.1007/978-3-540-24699-2_13 (Springer: not retrievable). [S2605] "GESR: A Genetic Programming-Based Symbolic Regression Method with Gene Editing", arXiv:2605.10685, https://arxiv.org/html/2605.10685, Appendix J (fetch extract; it cites a key `jha2002hyperchaos`).

| Term | Code | Source value | Quote | Source | Status |
|---|---|---|---|---|---|
| x' | `a (y - x) + w` | `a*y - a*x + w` | D line 4: `xdot = a * y - a * x + w` | D | match |
| y' | `-x z + b x - y` | `-x*z + b*x - y` | D line 5: `ydot = -x * z + b * x - y` | D | match |
| z' | `x y - c z` | `x*y - c*z` | D line 6: `zdot = x * y - c * z` | D | match |
| w' | `-x z + d w` | `-x*z + d*w` | D line 7: `wdot = -x * z + d * w` | D | match |
| a | 10.0 | 10 | JSON `"parameters": {"a": 10, "b": 28, "c": 2.667, "d": 1.3}` | D | match |
| b | 28.0 | 28 | same | D | match |
| c | 2.667 | 2.667 | same | D | match |
| d | 1.3 | 1.3 | same | D | match |
| observed coordinate | index 0 = x | Dysts order (x, y, z, w) | `_rhs(x, y, z, w, t, a, b, c, d)` | D | match (design choice) |
| Divergence | -a - 1 - c + d = -12.367 | -12.367 (arithmetic on the Dysts field) | derived by me: d(x')/dx = -a, d(y')/dy = -1, d(z')/dz = -c, d(w')/dw = +d; -10 - 1 - 2.667 + 1.3 = -12.367 | derived | match (code and docstring agree with the Dysts field) |
| Spectrum sum | -12.367 +- 0.002 (study) | Dysts sum = -12.330 (arithmetic by me) | | derived | match for the study (equals the divergence); Dysts sum is 0.3% off |
| Secondary source, Table 10 of arXiv:2605.10685 | as above | same four equations, a = 10, b = 28, c = 2.667, d = 1.3 | fetch extract: "Hyper-Jha (Appendix J, Table 10): x' = a(y - x) + w, y' = -xz + bx - y, z' = xy - cz, w' = -xz + dw. Parameters: a = 10, b = 28, c = 2.667, d = 1.3" | S2605 | match to Dysts, but plausibly derived from Dysts (the values 2.667 and 1.3 are Dysts', and it uses Dysts' system names); not independent evidence |
| lambda_3 | -0.00000 | 0.005568431034995312 | JSON entry HyperJha | D | match (zero within error) |
| Equations and parameters vs the original (Meier 2003 / "Jha 2002") | as above | not retrieved | JSON `citation`: "Jürgen Meier (2003). Presentation of Attractors with Cinema."; `description`: "A hyperchaotic system." | | unconfirmed |
| **Secondary source, body text Eq. (9) of arXiv:2605.10685** | | y' = c x - y - x z; w' = -d y; no parameter values | fetch extract: "The Hyper-Jha equations in the appendix body text (Eq. 9) differ from Table 10. There, y' = cx - y - xz and w' = -dy, and the text gives no parameter values." A web-search summariser said the same ("a linear term in y ... -dy") | S2605 | **mismatch inside that secondary source** (its body text disagrees with its own Table 10 and with Dysts in two terms: y' has `c x` where Dysts has `b x`; w' has `-d y` where Dysts has `-x z + d w`). Not resolved: I could not read the raw page (the summariser relayed it) or the original. This does not show that Dysts is wrong, but the original definition of "Hyper-Jha" is not established |
| lambda_1, lambda_2 | 0.35600, 0.21168 | Dysts spectrum 0.3949499860671474, 0.2920214751184925; max 0.38695361636760767 | JSON entry HyperJha | D | mismatch (Dysts fields; ratios 0.90 and 0.72; lambda_2/lambda_1 is 0.59 for the study, 0.74 for Dysts) |
| lambda_4 | -12.935 | -13.022125042186726 | same | D | mismatch (0.7%; Dysts field) |
| Kaplan-Yorke d | 3.044 | 3.053181782412727 | same | D | mismatch in value (0.3%; Dysts field) |

Summary S5: 13 match (all four equation terms, four parameters, observed coordinate, divergence, spectrum-sum check, Table 10 of S2605, lambda_3), 4 mismatch (3 Dysts stored fields; **1 conflict inside a secondary source between its Table 10 and its Eq. (9)**), 1 unconfirmed (original paper not retrieved). **This is the weakest system: Dysts' citation is a visualisation-software chapter (weak provenance, as noted on 2026-10-20), no primary text could be read, and the one secondary text that was read contradicts itself.**

## 6. S6 `lorenz96_4` (Lorenz-96, N = 4, F = 20)

Code (`lorenz96_ring_field`): `(roll(X, -1) - roll(X, 2)) * roll(X, 1) - X + F`, i.e. `X_k' = (X_{k+1} - X_{k-2}) X_{k-1} - X_k + F`, cyclic; F = 20.0; dim 4; observed index 0 (X_1).
Sources: [L96] E. N. Lorenz, "Predictability: A problem partly solved", Seminar on Predictability, Vol. I, ECMWF, scan read directly at https://www.ecmwf.int/sites/default/files/elibrary/1995/75462-predictability-problem-partly-solved_0.pdf, pp.4, 5, 7, 9, 10; [W] https://en.wikipedia.org/wiki/Lorenz_96_model; [D] Dysts class Lorenz96 and JSON entry Lorenz96.

| Term | Code | Source value | Quote | Source | Status |
|---|---|---|---|---|---|
| field, all terms and signs | `(X_{k+1} - X_{k-2}) X_{k-1} - X_k + F` | `-X_{k-2} X_{k-1} + X_{k-1} X_{k+1} - X_k + F` | L96 p.4 Eq. (1): "dX_k/dt = -X_{k-2} X_{k-1} + X_{k-1} X_{k+1} - X_k + F"; W: "dx_i/dt = (x_{i+1} - x_{i-2}) x_{i-1} - x_i + F". Algebraically equal | L96 p.4; W | match |
| field vs Dysts code | same | `Xdot[0] = (X[1] - X[-2]) * X[-1] - X[0] + self.f`; `Xdot[1] = (X[2] - X[-1]) * X[0] - X[1] + self.f`; `Xdot[-1] = (X[0] - X[-3]) * X[-2] - X[-1] + self.f`; `Xdot[2:-1] = (X[3:] - X[:-3]) * X[1:-2] - X[2:-1] + self.f` | D class Lorenz96 lines 4-7. Checked by hand for N = 4: each line equals `(X_{k+1} - X_{k-2}) X_{k-1} - X_k + f` with cyclic indices; the code's roll(-1), roll(2), roll(1) give X_{k+1}, X_{k-2}, X_{k-1} | D | match |
| cyclic closure | modulo N | X_{k-K} = X_k, X_{k+K} = X_k | L96 p.4: "The definition of X_k is to be extended to all values of k by letting X_{k-K} and X_{k+K} equal X_k" | L96 p.4 | match |
| K = 4 allowed | N = 4 | "We assume that K > 3"; K = 4 used in Fig. 2b | L96 p.5: "We assume that K > 3; the equations are of little interest otherwise"; p.7 Fig. 2 caption: "with K = 4, and with F = 18.0 ... and F = 15.0"; p.10: "with K reduced to 4 and F increased to 18.0" | L96 pp.5, 7, 10 | match for N = 4 as a permitted size |
| F = 20 | 20.0 | Dysts `"parameters": {"f": 20.0}` | JSON entry Lorenz96 | D | match to Dysts |
| N = 4 in Dysts | 4 | `embedding_dimension` 4; `initial_conditions` of length 4 | JSON entry Lorenz96 | D | match |
| observed coordinate | index 0 = X_1 | Dysts `X[0]` | D class Lorenz96 | D | match (design choice) |
| divergence | -N = -4 | derived by me: d(X_k')/dX_k = -1 for each k | | derived | match to the study's own check (spectrum sum -4.00016) |
| F = 20 vs Lorenz 1996 | 20.0 | Lorenz uses F = 8.0 and 10.0 (K = 36), 18.0 and 15.0 (K = 4); F = 20 does not occur on pp.4-10 | L96 p.9: "With K = 36 and F = 8.0 or 10.0"; p.10: "F increased to 18.0"; "F has been reduced to 15.0, producing a system that is not chaotic at all" | L96 | unconfirmed (F = 20 at N = 4 has no source other than Dysts; pages 1-3 and 11 onward were not read) |
| lambda_1 | 1.20184 (cached 1.20184) | Dysts spectrum[0] 1.6247012663091516; max 1.3361667787286362 | JSON entry Lorenz96 | D | mismatch (Dysts fields; ratios 0.74 and 0.90) |
| lambda_2 | +0.00000 | 0.17185232259745578 | same | D | mismatch (Dysts shows a second positive exponent; a flow must have a zero exponent) |
| lambda_3, lambda_4 | -1.588, -3.614 | -1.1936282999960617, -3.550455057872212 | same | D | mismatch (Dysts fields) |
| Kaplan-Yorke d | 2.757 | 3.1698163415908196 | same | D | mismatch (Dysts field) |

Reason for the Dysts mismatches: Dysts sum = 1.6247 + 0.1719 - 1.1936 - 3.5505 = -2.9475 (arithmetic by me), against the exact -4; the study's spectrum sums to -4.000. The Dysts fields cannot be the spectrum of this field.

Summary S6: 8 match, 4 mismatch (all Dysts stored Lyapunov fields), 1 unconfirmed (F = 20 at N = 4 has no source other than Dysts). Equation and cyclic form confirmed by Lorenz's own Eq. (1).

## 7. Cross-system findings

1. **Equations and parameters.** For all six systems the code's vector field and parameter values equal the Dysts `flows.py` and JSON text term by term, with no sign or coefficient difference. S1, S2, S3 and S6 are also confirmed by a source independent of Dysts that I read (R&S and Wikipedia; Manneville and Pomeau 1980; Wikipedia and Bogdanov and Bogdanova; Lorenz 1996).
2. **Not confirmed against an original source:** S4 (Marhl and Perc 2005: not retrievable; no other text gives the Dysts form) and S5 (Meier 2003 / "Jha 2002": not retrievable; one secondary source contradicts itself, section 5). Both match Dysts exactly. This is the open item for the owner's waiver condition: a "not confirmed", not a found mismatch of the code against its cited Dysts entry. The S5 secondary-source conflict is the one unresolved discrepancy of text.
3. **The study's own Lyapunov values (spectra, KY) are the study's computations, not source values.** Against independent literature: S1 matches (R&S Table 1); S3 matches (B&B p.8); S2, S4, S5, S6 have no published value (unconfirmed). Against the Dysts stored fields, S1, S4, S5, S6 and the max field of S3 mismatch (listed per system). The notes of 2026-10-20 and 2026-10-23 already established that those Dysts fields are internally inconsistent (S6 sum -2.95 against the exact -4; S1 contradicts R&S; the max field is 2.1 to 2.85 times the spectrum field for Rössler and Chua). The specification notes state that the study used none of them; I found no use in `systems.py`.
4. **Code comments.** The `systems.py` S1 docstring says the equations were "confirmed against Dysts `HyperRossler` on 2026-10-20": consistent with today. The S4 docstring says "Marhl and Perc (2005) was not read": still true. The S5 docstring says "as relayed in full from Dysts": consistent, but the original is unread.
5. S5 uses c = 2.667 exactly as Dysts; S2 uses beta = 8/3 as Manneville and Pomeau. These are different systems and each matches its own source.

## 8. Retrieval list (the hook recorded these in the main checkout's network-log.jsonl, lines 416-445)

Dysts `flows.py` (1), Dysts JSON (2 fetches, two halves), arxiv chao-dyn/9909029, arxiv 2605.10685 (pdf, html twice), Springer chapter (redirect), doi 10.1016/j.chaos.2005.08.013 (redirect), ScienceDirect S0960077905006223 (403), doi 10.1016/0375-9601(79)90150-6 (redirect), Wikipedia Lorenz_96_model, Rössler_attractor, Lorenz_system, Hyperchaos, ECMWF Lorenz 1996 PDF, math.la.asu.edu Pomeau_Manneville_1.pdf, arxiv 1412.2242, eaps4.mit.edu (host not found), journals.ametsoc.org (403), scholarpedia (certificate expired); 8 web searches.
