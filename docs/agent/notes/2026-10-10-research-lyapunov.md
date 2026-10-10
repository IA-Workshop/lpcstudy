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
