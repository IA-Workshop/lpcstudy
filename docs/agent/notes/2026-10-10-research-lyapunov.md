# Research note: published largest Lyapunov exponents (WU-0007.1)

Date retrieved: 2026-10-10. Agent: researcher. Serves NVVUQ.13(a), VV.2, ROADMAP WU-0007.1.

## Scope and limits

- Web use is logged by the hook `.claude/hooks/web_gate.py` to `docs/agent/records/network-log.jsonl`. I did not write to that file.
- Page budget (LPC.AUTH.2, 50 pages): about 21 documents fetched and 20 PDF pages read, plus about 10 searches. I am at or near the limit and stopped. Several arXiv and journal PDFs came back from WebFetch as undecoded binary. I read some of them page by page with the PDF reader, and about 8 of those pages were not useful (Hartl p.6, chao-dyn/9909029 pp.5-8, Elhadj 2007 pp.1-4).
- WebFetch answers come from a small summarising model, not the raw page. A quote marked "fetch extract" is as returned by that tool. A quote marked "read directly" I read from the page image of the PDF.
- Fetched text carried no instructions. I found nothing to report under PRIME.11.
- Status vocabulary: `confirmed` means I read the value in a source and have a quote. `not found` means no source retrieved. No value in this note comes from memory.

## What the code uses (read from the repository)

Source: `lpcstudy/systems.py` lines 157-169, and `lpcstudy/data.py` lines 172-194 and 220-224.

| System | Equations in the code | Parameters in the code | RK4 `max_dt` |
|---|---|---|---|
| Lorenz-63 | x' = sigma(y-x), y' = x(rho-z)-y, z' = xy-beta z | sigma=10, rho=28, beta=8/3 | 0.01 |
| Rössler | x' = -y-z, y' = x+a y, z' = b+z(x-c) | a=0.2, b=0.2, c=5.7 | 0.04 |
| Chua (piecewise-linear diode) | x' = alpha(y-x-f(x)), y' = x-y+z, z' = -beta y; f(x) = m1 x + (m0-m1)(abs(x+1)-abs(x-1))/2 | alpha=15.6, beta=28, m0=-1.143, m1=-0.714 | 0.005 |

The code does not hard-code lambda_max. `lyapunov_cached` computes it by Benettin/QR with fixed-step RK4. It uses a tangent-propagation step of 20*max_dt, 100,000 averaging steps and 5,000 burn-in steps. `build_context` then sets the observation interval to Delta = 1/(30*lambda_max) in natural time units. The values 0.905, 0.0719 and 0.431 appear in Methods v2 §M2 (a table in `docs/study/methods_experimental_procedures_v2.md`, lines 69-73). No code file contains them.

## Findings (one row per system)

| System | Claim: published lambda_max (per unit time) | Source (URL or DOI) | Status | Supporting quote | Conditions of the source's estimate | Retrieved |
|---|---|---|---|---|---|---|
| Lorenz-63, sigma=10, r=28, b=8/3 | 0.90563 (Sprott). Independent: 0.905 +/- 0.003 (Hartl). Own estimate in a third paper: 0.90410 +/- 0.00076. | (1) J. C. Sprott, "Lyapunov Exponent Spectrum Software", https://sprott.physics.wisc.edu/chaos/lespec.htm (page dated May 26, 2005, revised Nov 10, 2010). (2) M. D. Hartl, "Lyapunov exponents in constrained and unconstrained ordinary differential equations", arXiv:physics/0303077, DOI 10.48550/arXiv.physics/0303077 (submitted to Phys. Rev. E, not stated as published). (3) Yu. I. Bogdanov and N. A. Bogdanova, "The study of Lorenz and Rössler strange attractors by means of quantum theory", arXiv:1412.2242. | confirmed | (1) fetch extract: "the parameters used for the Lorenz attractor are the standard ones (sigma = 10, r = 28, b = 8/3)"; exponents "0.90563, 0, -14.57219", Kaplan-Yorke dimension "2.06215". (2) read directly, Fig. 2 caption, p.3: "The slope of the rescaled line is the Lyapunov exponent (lambda_max = 0.905 +/- 0.003; see Sec. II D 1)"; parameters p.2: "sigma = 10, b = 8/3, and r = 28". (3) read directly, p.7: "lambda_1 = 0.90410 +/- 0.00076 ... Our values are close to the values obtained by Sprott J.C. [4] and Kuznetsov S.P. [5]: lambda_1 = 0.906, lambda_3 = -14.572 (Sprott); lambda_1 = 0.897, lambda_3 = -14.563 (Kuznetsov)". | (1) Equations, integrator, step and run length are not stated on the page, which links to `wolfflow.bas`/`wolfflow.exe`. (2) Rescaled deviation-vector method; the integrator, step and run length were not in the pages I read (pp.1-3 and 6). The Fig. 2 initial deviation is 1e-8, rescaling at 1e-2. (3) Statistical (momentum-representation) method; integrator not read. Units: per unit of the Lorenz time variable. | 2026-10-10 |
| Rössler, a=b=0.2, c=5.7 (the code's set) | 0.0714 (Sprott, as cited by Bogdanov & Bogdanova). Own estimate in that paper: 0.07062 +/- 0.00066. | Yu. I. Bogdanov and N. A. Bogdanova, "The study of Lorenz and Rössler strange attractors by means of quantum theory", arXiv:1412.2242. Sprott's original ([4] in that paper) was not retrieved. | confirmed for the Bogdanov & Bogdanova own value. The Sprott 0.0714 is confirmed only as cited by them (secondary). | Read directly, p.2: "F1 = -x2 - x3, F2 = x1 + a x2, F3 = b + x1 x3 - c x3, where a = 0.2, b = 0.2, c = 5.7" (same field as the code). Read directly, p.8: "lambda_1 = 0.07062 +/- 0.00066, lambda_2 = 0.000048 +/- 0.00018, lambda_3 = -5.3937 +/- 0.0018. Our values are close to the values obtained by Sprott J.C. [4]: lambda_1 = 0.0714, lambda_3 = -5.3943". | Statistical estimate by the authors' momentum-representation method (Figs. 6-7: slope of accumulated data, time axis of order 5e4 units). Integrator and step were not in the pages I read (pp.1-8 of the PDF). Sprott's own conditions are unknown. Units: per unit of the Rössler time variable. | 2026-10-10 |
| Chua, piecewise-linear diode, alpha=15.6, beta=28, m0=-1.143, m1=-0.714 (the code's set) | not found | Searched; no source retrieved that reports lambda_max for this parameter set. | not found (nothing to confirm) | None. See "Items looked at for Chua" below. | None. | 2026-10-10 |

### Items looked at for Chua (none confirms a published value)

- Parameter set only: chuacircuits.com MATLAB listing (https://chuacircuits.com/matlab), seen as a search result snippet and not fetched. The snippet gives alpha=15.6, beta=28, m0=-1.143, m1=-0.714, ode45 from [0.7, 0, 0], and no exponent. Status: not confirmed beyond the snippet.
- dysts database `chaotic_attractors.json` (https://raw.githubusercontent.com/williamgilpin/dysts/master/dysts/data/chaotic_attractors.json), fetch extract: entry "Chua" has parameters alpha=15.6, beta=28.0, m0=-1.142857, m1=-0.71429, "lyapunov_spectrum_estimated": [0.4605474829443073, 0.0022048281168492866, -4.319076735248446], "maximum_lyapunov_estimated": 1.2301163591725595, "dt": 0.0002847474579095888, "period": 1.4235. Status: this is a software dataset, not a published estimate. Its time unit and the meaning of the two fields are not stated in what I retrieved. The same extract gives for Lorenz "maximum_lyapunov_estimated": 0.8917 with spectrum [1.0911, 0.0299, -14.9156], and for Rössler spectrum [0.0763, 0.0075, -5.741] with "maximum_lyapunov_estimated": 0.1506. These do not agree with the published values above, so I do not treat dysts as a reference. The Methods v2 text calls the 30-steps-per-Lyapunov-time convention the "dysts convention". I did not check the dysts documentation for that.
- Elhadj (2007), Radioengineering 16(2) 40-43, read directly: a different system (not the dimensionless Chua equations, parameters a, c, m0=-0.43, m1=0.41). Not relevant.
- The 1984 Matsumoto, Chua and Komuro memo (https://www2.eecs.berkeley.edu/Pubs/TechRpts/1984/ERL-m-84-73.pdf) was a search hit, not retrieved. The snippet says only that the double scroll has one positive, one zero and one negative exponent (no value).
- Unretrieved leads for a follow-up request: Matsumoto, Chua and Komuro, IEEE Trans. Circuits Syst. 32(8) 1985, "The double scroll"; the Chua circuit reference book; Sprott's book "Chaos and Time-Series Analysis" (2003), which Bogdanov & Bogdanova cite as [4] for Lorenz and Rössler.

### Other values seen only as search-result snippets (not read, not confirmed)

- Rössler lambda_1 = 0.072 (arXiv:1805.06644, Kuptsov and Kuznetsov; I fetched the abstract page, which does not mention Rössler, and could not read the body text).
- Rössler 0.0729 from a Julia Discourse post (b=0.2; run conditions not read).
- Lorenz 0.905 +/- 0.005 attributed to an earlier study in arXiv:2202.12075, App. C.1 (snippet only).

## Units and conversion to the code's convention

- Every published value above is per unit of the system's natural time variable. The code's time is in steps, with Delta in natural time units per step (`SystemSpec.max_dt` and the `interval` argument, "natural time units" in the docstrings).
- The code sets Delta = 1/(30 * lambda_max), so one Lyapunov time is 30 steps and lambda_max per step equals 1/30 = 0.0333 by construction. The conversion is lambda_step = lambda_time * Delta, and the number of steps per Lyapunov time is 1/lambda_step. Any error in lambda_max moves Delta in proportion (a 1% error in lambda_max is a 1% error in Delta, and the actual Lyapunov time is then 30 * lambda_code / lambda_true steps).
- Delta that follows from each value (natural time units), for orientation only: Lorenz 0.9056 gives 0.0368; Rössler 0.0714 gives 0.4669, 0.0706 gives 0.4721, 0.0719 gives 0.4636; Chua 0.431 gives 0.0773.
- Because the code computes lambda_max itself, the validation in WU-0007.2 compares the code's estimate with the published value in natural time units. It does not compare in steps.

## Comparison with Methods v2 §M2 (no judgement on which is right)

| System | Methods v2 §M2 | Published value retrieved | Difference |
|---|---|---|---|
| Lorenz-63 | 0.905 | 0.90563 (Sprott); 0.905 +/- 0.003 (Hartl); 0.9041 +/- 0.0008 (Bogdanov and Bogdanova) | 0.905 is 0.0006 below Sprott's value. It matches Hartl's value and is within about 1.1 of Bogdanov and Bogdanova's stated standard errors. Consistent at three digits. |
| Rössler | 0.0719 | 0.0714 (Sprott, cited by Bogdanov and Bogdanova); 0.07062 +/- 0.00066 (Bogdanov and Bogdanova) | 0.0719 is 0.0005 (0.7%) above Sprott's value and 0.0013 above Bogdanov and Bogdanova's, about 1.9 of their stated standard errors. Different in the third significant digit. |
| Chua | 0.431 | none retrieved | Cannot be compared. The dysts spectrum entry 0.4605 (units and meaning unclear, parameters m0=-1.142857, m1=-0.71429) is the only nearby number and is not a published estimate. |

Open points for the caller:

- Whether Methods v2's 0.0719 and 0.431 came from the code's own runs or from a source is not stated in the text I read. I did not search the pilot results.
- A published value for Chua at alpha=15.6, beta=28 has not been confirmed. WU-0007.1's acceptance criterion ("each row confirmed") is met for Lorenz and Rössler, with the Rössler Sprott value only as cited in a secondary source, and is not met for Chua. A further request (with a page budget) is needed to retrieve the Matsumoto-Chua-Komuro paper or Sprott's book, or the owner may record Chua as a known limitation (NVVUQ.13).
- Rössler in the code has `max_dt` 0.04 and a tangent step of 0.8 time units (20 * 0.04), and Chua 0.1 (20 * 0.005); the published estimates' integrator and step were not retrieved, so no like-for-like step comparison is possible.

---
Correction (2026-10-10, claude-sonnet-5-5, main session; appended, nothing above edited): the researcher's hand-back states that the Lorenz-63 value 0.905 in Methods v2 §M2 is about 1.2 (not 1.1) standard errors from Bogdanov & Bogdanova's own estimate; the "about 1.1" in the comparison section above is the one in error. Status of the Chua row: no confirmed published value; the 50-page budget of LPC.AUTH.2 for this unit is exhausted, so further retrieval needs an owner decision (see the WU-0007 queue entry when it is opened).

---

## Chua follow-up (2026-10-11)

Agent: researcher (claude-sonnet-5-5). Appended; nothing above edited. Authority: DEC-0009 (retrieval cap removed for the season; other limits unchanged: individual papers and pages only, no datasets, no crawling). Every fetch is logged by the hook. I did not write to `network-log.jsonl`. Nothing was committed.

### Result in one paragraph

No source I could retrieve reports a largest Lyapunov exponent of the autonomous dimensionless Chua system at alpha=15.6, beta=28, m0=-1.143 (= -8/7 rounded), m1=-0.714 (= -5/7 rounded). The Chua row of WU-0007.1 therefore stays `not found`. Methods v2's 0.431 is not matched by any retrieved source. The only exponent I read directly in a primary Chua source is Matsumoto, Chua and Komuro's 1984 memorandum, and it is for a different parameter set (alpha=9, beta=100/7 in dimensionless form, derived below), with mu_1 about 0.23 per unit of the memo's own circuit time.

### What "our system" is (read from `lpcstudy/systems.py` lines 74-101 and 145-148 and Methods v2 §M2 lines 69-73)

- Field: x' = alpha(y - x - f(x)), y' = x - y + z, z' = -beta y, with f(x) = m1 x + (m0 - m1)(|x+1| - |x-1|)/2. Inside |x| < 1 the diode slope is m0 (inner, -1.143); outside it is m1 (outer, -0.714). No gamma term (gamma = 0). This is the Kennedy/Chua dimensionless form. Parameters: alpha=15.6, beta=28.0, m0=-1.143, m1=-0.714. The values -8/7 = -1.142857 and -5/7 = -0.714286 differ from the code's rounded values by 2.9e-4 and 4.3e-4 (0.03% and 0.06%); I treat that as the same system to the precision of any published exponent, but the code's system is strictly a slightly perturbed one.
- Time: the dimensionless time of the Chua equations (one unit = the code's `max_dt` units; RK4 `max_dt` 0.005). The code's step is Delta = 1/(30 lambda_max) in these units.
- Methods v2 §M2 states 0.431 for this set. I could not find where that number comes from.

### Candidates, one row each

| # | Candidate (what it says) | Source and URL | Status | Quote | Parameters, integrator, time unit | Match to our system |
|---|---|---|---|---|---|---|
| 1 | Sprott's Lyapunov Exponent Spectrum Software page: does it list Chua? | https://sprott.physics.wisc.edu/chaos/lespec.htm (fetch extract) | confirmed: Chua is NOT listed | fetch extract: "the page does not list Chua's circuit or Chua's attractor. It covers only two systems: Hénon map (a = 1.4, b = 0.3) ... and Lorenz attractor (sigma = 10, r = 28, b = 8/3)". | Henon 0.419217, -1.623190; Lorenz 0.90563, 0, -14.57219 | No Chua value on the page. |
| 2 | Matsumoto, Chua, Komuro, "A Double-Scroll Chaotic Attractor from a Third Order Reciprocal Circuit", Memorandum UCB/ERL M84/73, 31 Aug 1984 (the memo version of "The Double Scroll"). mu_1 about 0.23, mu_2 about 0, mu_3 about -0.28; Lyapunov dimension 2.82. | https://www2.eecs.berkeley.edu/Pubs/TechRpts/1984/ERL-m-84-73.pdf (scanned PDF; I read pages directly: PDF pp. 4-6, 27-29, 30-31 = memo pp. 1-6 and 22-25) | confirmed (read directly) for the memo's own parameter set; NOT our set | memo p.1: "Lyapunov exponents and Lyapunov dimension are computed. The attractor has one positive, one zero and one negative Lyapunov exponent." Memo p.24, (3.23): "mu_1(x_0) ~ 0.23, mu_2(x_0) ~ 0, mu_3(x_0) ~ -0.28". Memo p.25, (3.25): "d_L = 2 + (mu_1+mu_2)/|mu_3| ~ 2.82". Memo p.2, (1.3): "1/C1 = 9, 1/C2 = 1, 1/L = 7, G = 0.7, m0 = -0.5, m1 = -0.8, B_p = 1". | Circuit equations (1.1) in the memo's dimensional-style time (C2 = 1, G = 0.7). Memo p.23: "we chose tau = 10 with the Runge-Kutta step size 0.005". Memo p.22: x_0 = (-1.7713, 0.0527854, 1.74606), e = (1,1,1)/sqrt(3), T = 3000. Memo p.24: "The convergence, however, seems to be very slow. At T = 3000 it is still increasing in an extremely slow manner." mu_1+mu_2+mu_3 = -0.05 (3.22). Accuracy digits: two. | Different parameters (below). The same RK step (0.005) as our Chua `max_dt`. |
| 3 | Chua, Komuro, Matsumoto, "The Double Scroll Family, Parts I and II", Memorandum UCB/ERL M85/102, 4 Dec 1985. | https://www2.eecs.berkeley.edu/Pubs/TechRpts/1985/ERL-85-102.pdf (read PDF pp. 2-4 directly) | no Lyapunov value seen | Abstract, Part I: "a rigorous mathematical proof that the double scroll is indeed chaotic ... Poincare maps". | Analytical (normal form, Poincare maps). I read only the title and the Part I abstract; the rest was not read. | No exponent seen. |
| 4 | Matsumoto, Chua, Komuro, "The Double Scroll", IEEE Trans. Circuits Syst. CAS-32(8), 797-818, Aug 1985. | Citation as given in a 1986 Berkeley memo, via search result. I found no DOI. Full text is behind IEEE Xplore (not retrieved). | could not retrieve | None. | None. | Unknown. The memo (row 2) is its precursor, so the IEEE paper's exponents may be the same, but I did not read it. |
| 5 | Wolf, Swift, Swinney, Vastano (1985), Physica D 16, 285-317. Does it test Chua? | Search snippets only (bibliographic data). The HAL record (hal-01654059) returned an "Access Denied" bot-protection page, and the UCSC PDF copy failed certificate verification. I did not try to get around either. | could not retrieve | Search snippet (not read in the paper): "tested on model systems with known Lyapunov spectra, and applied to data for the Belousov-Zhabotinskii reaction and Couette-Taylor flow." | None. | Nothing seen mentions Chua. Its model systems predate the double scroll by months, so a Chua test is unlikely, but I could not read the paper. |
| 6 | Kuznetsov and Leonov Chua papers on Lyapunov dimension. Leonov and Kuznetsov, "The Lyapunov dimension, convergency and entropy for a dynamical model of Chua memristor circuit". | arXiv:1801.09679, https://ar5iv.arxiv.org/html/1801.09679 (fetch extract) | confirmed: no numerical exponents | fetch extract: "No parameter set in this document has reported numerical Lyapunov exponents or Lyapunov dimension values. The paper keeps alpha, beta, m0, m1, gamma, and x0 symbolic throughout." | Memristor model with a gamma term; equation form x' = alpha(y - x - f(x)), same convention as ours. | No numbers. |
| 7 | Kuznetsov, Kuznetsova, Leonov, Mokaev, Stankevich, "Localization of hidden Chua attractors by the describing function method" | arXiv:1705.02311 (abstract page only) | no value seen | fetch extract: "The paper studies the Chua circuit with five linear elements and a saturation nonlinearity ... A new configuration of hidden Chua attractors is presented." | Hidden attractors, not the classical double scroll. Body text not read. | No value seen. |
| 8 | Ensemble Reservoir Computing for Physical Systems, Chua entry: lambda_top about 0.46 | arXiv:2601.21807, https://arxiv.org/html/2601.21807 (fetch extract of Sec. IV.2.4 and VIII.1) | read via fetch extract only; a secondary, driven-system value; NOT a reference | fetch extract: "where a=15.6, b=28.0, m0=-1.143, m1=-0.714, iota=2.0"; "The maximum conditional Lyapunov exponent is lambda_top about 0.46"; Sec. VIII.1: "We calculated lambda_top using an algorithm described by J. C. Sprott [Sprott 2003]" and "we call lambda_top the maximum conditional Lyapunov exponent when the system is driven by an external input." | dt = 0.05 (integrator not named for Chua). The extracted equation reads dx/dt = a(y - x + f(x)) + iota u_t, i.e. a drive term and a possibly different sign for f; so the system and the exponent are not the autonomous system's. The same paper gives Lorenz lambda_top about 1.0265, which is not the published 0.906, so its exponents are not in the natural-time autonomous convention. | Same alpha, beta, m0, m1 numbers, but a driven system and a different quantity. Do not use as a reference. (The number happens to equal dysts' 0.4605 to two digits; I did not investigate why.) |
| 9 | Dynamics and Computational Principles of Echo State Networks, Table 2: Chua lambda_max = 0.428400, Lyapunov time 2.334267 | arXiv:2504.11757, https://arxiv.org/html/2504.11757 (fetch extract, Sec. 2.1, Table 1, Table 2, Sec. 5.7) | read via fetch extract only; cited to reference [93] not retrieved; NOT confirmed | fetch extract: "Table 2 ... lists lambda_max = 0.428400 and a Lyapunov time of 2.334267 for Chua, citing reference [93]." Table 1: "alpha = 9, beta = 14, m0 = -1.143, m1 = -0.714. Step size 0.02, initial value {1, 1, 1}" and "RK4". Fig. 2(d) caption: "Parameters: alpha=15.6, beta=28." | The paper is internally inconsistent: Table 1 gives alpha=9, beta=14 while the Fig. 2(d) caption gives alpha=15.6, beta=28. How 0.4284 was obtained is not stated ("appears to be cited"). 1/0.4284 = 2.3343, consistent with the stated Lyapunov time. | Unknown which parameter set the 0.4284 belongs to. Not usable as a reference. Note that 0.4284 is about 0.4% below Methods v2's 0.431. I cannot say whether that is a coincidence. |
| 10 | dysts JSON (excluded by the request) | Not used. The earlier note records 0.4605 for the Chua spectrum entry. | excluded | n/a | n/a | n/a |

### Mismatch analysis for candidate 2 (the only primary exponent found)

Derived by me, not stated in the memo: the memo's equations (1.1) with C1 = 1/9, C2 = 1, L = 1/7, G = 0.7 map to Chua's dimensionless form by tau = t G / C2 = 0.7 t, alpha = C2/C1 = 9, beta = C2/(L G^2) = 7/0.49 = 14.286 (= 100/7), and the diode slopes divided by G. From memo p.2, (1.2), g(v) = m1 v inside |v| < B_p (I checked: for |v| < B_p, g = m0 v + (m1-m0)v = m1 v) and m0 outside, so the memo's inner slope is -0.8 and outer slope is -0.5. Divided by G = 0.7 these are -8/7 inner and -5/7 outer, which are our code's m0 (inner) = -1.143 and m1 (outer) = -0.714 in our naming. Note that the memo's m0/m1 labels are swapped relative to our code's (the memo calls the outer slope m0; the code calls the inner slope m0).

So the memo's set equals alpha = 9, beta = 100/7, m0 = -8/7, m1 = -5/7: the m values agree with ours, alpha and beta do not (15.6 and 28 in the code). If the memo's mu_1 = 0.23 is per unit of memo time, then per unit of dimensionless time it is 0.23 / 0.7 = 0.33 (derived, unconfirmed; two digits, with the memo's own caveat that convergence at T = 3000 was still slow and the sum was -0.05, not clearly the -divergence). That 0.33 is not our system and cannot validate lambda_max at alpha = 15.6, beta = 28. It does give a published case (alpha = 9, beta = 100/7, m0 = -8/7, m1 = -5/7) on which the code's Lyapunov routine could be checked, if the owner wants a primary reference for the Chua field and the Benettin implementation. The comparison would need the memo's time convention (divide by 0.7) and a tolerance that reflects two digits and slow convergence. This is a suggestion for the caller; it is not tested.

### Dimensionless time convention

- The code's Chua time is the standard dimensionless time (tau = t G / C2) in which the equations take the alpha, beta form with unit coefficient on the y - x and x - y + z terms. A published exponent is comparable only if it is per unit of that same tau. The memo's time is a scaled circuit time (factor 0.7 above), so memo exponents are not directly per unit tau.
- Candidates 8 and 9 do not state their time unit for the exponent (they state dt = 0.05 and 0.02, which suggests the dimensionless tau, but I did not verify that).

### Things I did not retrieve (for the record)

- Scholarpedia "Chua circuit" (http://www.scholarpedia.org/article/Chua_circuit): the fetch failed with "certificate has expired" on http, https and the var.scholarpedia.org host. The search snippet says it uses alpha = 15.6 with m0 = -8/7, m1 = -5/7 and scans beta over about 25 to 51; I did not read it, so I do not know whether it gives an exponent.
- Guégan and Leroux, "Local Lyapunov exponents: Zero plays no role in forecasting chaotic systems" (HEC Montréal cahier 08-10; InTech chapter 2011): search results say they use Rössler, Lorenz and Chua. The HEC PDF returned 404 and the HAL page returned an access-denied bot page. Not read.
- Sprott, "Chaos and Time-Series Analysis" (2003): not online; no Chua value is known to me from it.
- Bilotta and Pantano, "A Gallery of Chua Attractors" (Int. J. Bifurc. Chaos, 2007-2008; e.g. https://worldscientific.com/doi/10.1142/S0218127407017537): search snippets say Lyapunov exponents are given for some attractors, using their own parameterisation. Not read, not checked for alpha = 15.6, beta = 28.
- Kennedy (1993), "Three steps to chaos, Part II: A Chua's circuit primer": not retrieved.
- A Lund bachelor thesis ("The Anatomy of the Chua circuit", 2014, abstract and front matter read), a Georgia Tech student report set, a Georgian conference abstract (Tugushi; read in full: the abstract states no value), Pivka, Wu and Huang 1994 (read PDF pp. 1-2 only), Lin and Chua ERL M91/32 (unrelated), Akhmet and Fen arXiv:1205.1166 (abstract only: it mentions alpha = 15.6, beta = 25.58 in a snippet, no exponent): none gives a value for our set. The Berkeley, Lund and similar PDFs I read are for different circuits or physical measurements.

### Notes on the search tool output (PRIME.11)

- Fetched page text carried no instructions. The search tool's own result text contained boilerplate asking me to list sources, and two result summaries volunteered numbers "from memory" (a spectrum of about (0.33, 0, -14.9) for the classic Chua; "about 0.3 per unit time"). I did not use or record them as values. Status of those numbers: `unconfirmed (memory)`, no source.
- Two sites (HAL, HEC) returned bot-protection or error pages; I did not try to bypass them.

### Status for WU-0007.1, Chua row

`not found`: no confirmed published lambda_max at alpha = 15.6, beta = 28, m0 = -1.143, m1 = -0.714 (autonomous, per unit of the dimensionless time). Methods v2's 0.431 has no retrieved source and is not contradicted by one either. Options for the owner: (a) record Chua as a known limitation (NVVUQ.13); (b) have a request retrieve the IEEE 1985 paper, the Scholarpedia page (if the certificate is fixed), Guégan and Leroux, or Bilotta and Pantano by an approved route; (c) use the memo's alpha = 9, beta = 100/7 case as a primary check of the Chua field and the Benettin routine (expected about 0.33 per unit dimensionless time, derived, two digits).
