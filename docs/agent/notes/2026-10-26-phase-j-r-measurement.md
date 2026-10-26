# Phase J: the M-6 measurement of r, and the replication tool (WU-0051b)

**Every number in this note is DEVELOPMENT (DEV-1, DEV-3, DEV-4): exploratory, not a hypothesis test.** No held-out seed (DEV-5 to DEV-9) and no confirmatory seed was drawn, read or used. Nothing here is set beside CONF-1.

- **Author:** developer (claude-opus-5-5), 2026-10-26. Unit WU-0051b. Minimal formality.
- **Inputs:** the phase J full-preset runs at run commit f701a47, `lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-{1,3,4}/full`.
- **Analysis records.** I reran `tools/lpc_contrib.py` and `tools/lpc_contrib_ce.py` at the branch base 2b2891c (clean detached worktree, CPU, `nice -n 19`, 4 workers, about 27 min per seed) into `contrib-2b2891c` and `contrib-ce-2b2891c`. Every leaf of the six records equals the ea0bd77 and 5889351 records, apart from `analysis`, `seconds` and `abd`. The figure digests are identical. So the numbers below are those of the existing exploration outputs, now at one analysis commit.
- **Script and output:** `2026-10-26-phase-j-r-measurement/r_measurement.py` writes `r_measurement.out.md`. It takes a few seconds on the CPU and reproduces the M-6 table as a self-check.

## r on the exploration seeds

**DEVELOPMENT (DEV-1, DEV-3, DEV-4): exploratory, not a hypothesis test.**

- **Within-seed SE:** half the row's interval width over z at the row's level.
- **Between-seed SD:** the sample SD of the three point estimates (n = 3, 2 df).
- **Scales:** log for the MSE and pinball ratios. B's Δ and C2's retained share are on their own scale; the retained share can be ≤ 0, so it has no log.
- **Two values of r:**
  - r_tot = SD / mean SE is M-6's literal definition. Because the three point estimates also differ by their own sampling error, plugging r_tot into p = Φ(−1.96/√(1 + r²)) counts that error twice. It is conservative.
  - r_omit = √max(r_tot² − 1, 0) is the part the interval omits, which is what the formula assumes.

| family | rows | r_tot median [Q1, Q3] | r_tot RMS | r_omit median [Q1, Q3] | r_omit RMS |
|---|---|---|---|---|---|
| allocation drop-one (MSE ratio) | 120 | 1.05 [0.71, 1.48] | 1.22 | 0.34 [0, 1.09] | 0.86 |
| horizon drop-one (pinball ratio) | 24 | 0.81 [0.48, 1.24] | 1.02 | 0 [0, 0.74] | 0.67 |
| B Δ (all parts; 180 of them on the logit scale) | 612 | 0.98 [0.64, 1.47] | 1.24 | 0 [0, 1.08] | 0.91 |
| D rungs vs F (allocation and horizon) | 372 | 1.01 [0.63, 1.45] | 1.25 | 0.17 [0, 1.05] | 0.92 |
| C2 retained (19 rows excluded: a bound not finite) | 83 | 1.38 [0.90, 2.23] | 1.84 | 0.94 [0, 2.00] | 1.60 |

Rows that no guard blocked on any seed give slightly lower values: allocation drop-one r_tot median 0.95 (60 rows), D 0.93 (211 rows). The full table, including the B parts, is in `r_measurement.out.md`.

**Mapped by M-6's formulas** (p = Φ(−1.96/√(1 + r²)), P4 = 5p⁴(1 − p) + p⁵ for "at least 4 of 5"):

| family | r used | p | P4 | expected false replications per 1000 null rows |
|---|---|---|---|---|
| A, B, D (r_tot median ≈ 1.0) | 1.0 | 0.08 | 2–3·10⁻⁴ | 0.2–0.3 |
| A, B, D (r_tot RMS ≈ 1.25) | 1.25 | 0.11 | 6–7·10⁻⁴ | 0.6–0.7 |
| A, B, D (r_tot Q3 ≈ 1.47) | 1.47 | 0.135 | 1.5·10⁻³ | 1.5 |
| C2 retained, r_tot median | 1.38 | 0.125 | 1.1·10⁻³ | 1.1 |
| C2 retained, r_tot RMS | 1.84 | 0.175 | 4.0·10⁻³ | 4.0 |
| C2 retained, r_tot Q3 | 2.23 | 0.21 | 8.3·10⁻³ | 8.3 |

With r_omit in place of r_tot, every rate falls: the A, B and D medians give P4 ≤ 5·10⁻⁶, and C2's RMS gives 2.2·10⁻³.

**What it implies.**

- **A, B, D.** The three seeds' point estimates scatter about as much as the within-seed intervals predict (median r_tot ≈ 1, median r_omit ≈ 0 to 0.3). Training and realization variance adds little beyond the bootstrap SE. Every family summary is below M-6's robustness bound r ≤ 2. "At least 4 of 5" then keeps the false-replication rate per null row at ≤ 1.5·10⁻³ even at the upper quartile.
- **C2 retained is the noisiest family.** Its RMS is 1.84 and its upper quartile 2.23 exceeds 2. A ratio of two skill differences moves more between seeds than its interval says. M-6 says the rule is not changed for this. The J7 report should state the expected count for the C2 rows: about 4 per 1000 null rows at the RMS, and 8 at the upper quartile.
- **Per-seed p is smaller at the rows' own levels.** M-6 uses z = 1.96. At their family levels the rows have z = 2.50 (A, 1 − 0.05/4) and z = 2.64 (B, 1 − 0.05/6). At the RMS r, p is then 0.057 (A) and 0.049 (B), and P4 is 4.9·10⁻⁵ and 2.7·10⁻⁵.
- **Multiplicity.** The tool classifies 3489 rows per seed, not all null; the C1 rows repeat D's ladder rows. At P4 ≤ 7·10⁻⁴, that is at most about 2.4 expected false replications if every row were null.

**How imprecise r is with 3 seeds.**

- **Per row.** The SD has 2 degrees of freedom, so the true SD lies between 0.52 and 6.28 times its estimate (95%). One row's r says almost nothing.
- **Medians.** For a common r, the median of the per-row ratios is biased low by a factor √ln 2 = 0.83. The RMS estimates r² without that bias, but a few large rows drive it.
- **Correlation across rows.** All rows of a family share the same three realizations and fitted models, so a family summary carries far fewer than 2 × (rows) degrees of freedom. A seed-level effect, such as one unusual realization, moves every row at once.
- **Reading.** Treat the table as "r is about 1 for A, B and D, and about 1.5 to 2 for C2, uncertain by a factor of about 2". It is not a precise constant.

## The replication tool (`tools/lpc_replicate.py`)

- **The rule.** The tool applies M-6 mechanically to N seeds' `contrib.json` and `ce.json` of one analysis commit. Each seed's directory must hold both records, so in WU-0052 both tools are run with the same `--out`, and `lpc_contrib_ce.py` with `--abd`.
- **Claims.** Every reading word is mapped to bound claims on the row's true quantity. The full table is in the tool's `VOCABULARY` and in `replication.md`.
- **Words with no claim** never count toward the minimum and never contradict:
  - undetermined, not identifiable and every "not determined (…)";
  - the non-detections "no interaction gain detected", "no difference detected", "no detectable dependence bias", and the realized-noise outlier.

  So a B null is replicable only through the loss-ratio row's "negligible", not through the pair row.
- **E-H2a.** "consistent" and "not consistent" cannot contradict. A Spearman(m, I) in (0, 0.1) satisfies both rules.
- **E-H3c.** The claims are point thresholds (there is no interval), so its "consistent" always contradicts its "not consistent".
- **Exploratory dry run.** `--exploratory` on DEV-1, DEV-3 and DEV-4 at 2b2891c (at least 3 of 3; output `runs/dev/replication-explore-2b2891c/`) classified 3489 rows: 1072 replicated, 9 contradicted, 2408 not replicated. 256 of the rows that were not replicated have a replicated claim.
  - Two of the contradicted rows are B loss ratios ("substantial" against "negligible").
  - Three are C2 rows ("keeps most" against "loses most", or retains more against retains less).
  - Four are (f2) dependence-bias rows: two of these read "detectable" on all three seeds, with opposite signs.

  This is a plumbing check, not the rule.
