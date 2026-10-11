"""The identifier table of the study: v3 hypothesis ids, roles and criterion texts.

One table, used by ``analysis`` (result keys), ``experiments`` (result keys) and ``report``
(verdicts, the Markdown table and figure keys), so that no module spells an identifier of its
own. The rows are the 14 rows of the identifier map in ``docs/study/decision_log_lpc.md``
("v3 ID | v2 ID | Role"); the ``criterion`` text is the statistic and the pass rule of the
hypothesis tables of ``docs/study/proposal_and_methods_v3.md`` section 2, verbatim with the
Markdown escapes removed (for the gain bound, the sentence after the RQ3 table).

This module defines no statistic, band, level or verdict rule: it names things. The v2 ids and
the v1 keys that appear below are historical data of the map, not live identifiers of the code.

WU-0002.2. WU-0002.9 consumes ``role`` (verdict rows) and ``pending`` (the gain bound only).
"""

from dataclasses import dataclass

GAIN_BOUND_PENDING = ("the gain-bound screen row (amendments note section 11; "
                      "ROADMAP row not yet opened)")
"""What the gain-bound row waits for: concordance D-21(b), (c) (screen on the raw covariance at
every horizon, report the subset and the per-screen counts, no bar). It has no WU number yet
(DEC-0016 O2)."""


@dataclass(frozen=True)
class Hypothesis:
    """One row of the identifier table.

    Attributes
    ----------
    v3_id : str
        Identifier of the v3 proposal (``(reported)`` for the gain bound, as in the decision log).
    v2_id : str
        Identifier of Methods v2 for the same hypothesis.
    key : str
        Key of the result in ``results["systems"][system]`` and of the entry in ``verdicts``.
    role : str
        ``primary``, ``secondary``, ``estimate`` or ``reported``.
    criterion : str
        ``"<statistic>; pass if <rule>"`` from v3 section 2 (the sentence itself for ``reported``).
    pending : tuple[str, ...]
        ROADMAP sub-tasks (or the named gap, if its row is not yet opened) whose row names this id
        and may change the statistic computed under ``key``. While non-empty, the report marks
        the row as computed with the v1 statistic.
    """

    v3_id: str
    v2_id: str
    key: str
    role: str
    criterion: str
    pending: tuple[str, ...] = ()


HYPOTHESIS_TABLE: tuple[Hypothesis, ...] = (
    Hypothesis(
        "H1a", "H1b", "H1a", "secondary",
        "Fit of the median ε_s² to b² N_lib^(−2/d) + f²; pass if interval of 1/d within ±25% "
        "of the independently estimated 1/d"),
    Hypothesis(
        "H1b", "H1c", "H1b", "secondary",
        "Slope of log r.m.s. PLP error on log(g_H δ/√m) at H_ref; pass if in [0.8, 1.2]"),
    Hypothesis(
        "H1c", "H1d", "H1c", "secondary",
        "Median of Λ̄ × dT/d ln θ (PLP); pass if in [0.8, 1.25]"),
    Hypothesis(
        "H1d", "H1e", "H1d", "secondary",
        "Spearman correlation, each; pass if ≥ 0.7"),
    Hypothesis(
        "Q-N", "Q-N", "Q-N", "estimate",
        "Out-of-sample gain in R² (ΔR²) for predicting logit w*, with exact (oracle) values; "
        "pass if read by the table in §7"),
    Hypothesis(
        "H2a", "H2a", "H2a", "primary",
        "(i) median range of w* over 1, 2, 4 LT in the small-error regime; (ii) partial "
        "correlation of logit w* with Λ̃ given both seeds; pass if (i) interval below 0.1 and "
        "(ii) interval inside (−0.1, 0.1)"),
    Hypothesis(
        "H2b", "H2b", "H2b", "primary",
        "(i) mean per-state rank correlation of w* with ρ; (ii) mean paired change in w* from "
        "N_lib = 10³ to 10⁴ at ρ = 1%; pass if both lower bounds > 0"),
    Hypothesis(
        "H2c", "H2c", "H2c", "secondary",
        "Paired MSE differences at H_ref; pass if both upper bounds < 0"),
    Hypothesis(
        "H2d", "H2d", "H2d", "secondary",
        "MSE ratio minus 1 at H_ref; pass if upper bound ≤ 0.10"),
    Hypothesis(
        "H2e", "H2f", "H2e", "secondary",
        "Median per-state change in error correlation, N_lib 10³ → 10⁵; pass if lower bound > 0 "
        "at ρ = 1% and 2%"),
    Hypothesis(
        "(reported)", "H2e", "gain_bound", "reported",
        "The hybrid's horizon gain over the better forecaster is reported against the P1 bound, "
        "without a pass/fail bar.", (GAIN_BOUND_PENDING,)),
    Hypothesis(
        "H3a", "H3a", "H3a", "secondary",
        "Holm-adjusted log-rank tests between consecutive regimes; pass if all p < 0.01"),
    Hypothesis(
        "H3b", "H3c", "H3b", "secondary",
        "Importances in a weight tree and a horizon tree; pass if weight tree: Λ̃ < 0.2; "
        "horizon tree: Λ̃ highest"),
    Hypothesis(
        "H3c", "H3d", "H3c", "primary",
        "MSE ratio, regimes / closed form, at H_ref; pass if upper bound ≤ 1.05"),
)

def check_keys(result: dict) -> None:
    """Raise if a key of ``result`` looks like a hypothesis id but is not a key of the table.

    A key looks like a hypothesis id when it is ``Q-N``, ``T1`` or ``H`` followed by a digit and
    a letter ``a`` to ``f``. This makes a leftover v1 or v2 id (``H1f``, ``H3d``, ``T1``) a loud
    error where results are assembled, not a silent extra key.

    Parameters
    ----------
    result : dict
        A dict of results keyed by identifiers.

    Raises
    ------
    ValueError
        Naming the offending keys.
    """
    keys = {row.key for row in HYPOTHESIS_TABLE}
    bad = sorted(k for k in result if k not in keys and isinstance(k, str) and (
        k in ("Q-N", "T1") or (len(k) == 3 and k[0] == "H" and k[1].isdigit()
                               and k[2] in "abcdef")))
    if bad:
        raise ValueError(f"keys {bad} are not identifiers of the table; "
                         f"valid keys: {sorted(keys)}")


# The correction table of the decision log (v1 key in the code of the pilot -> v3 key), for
# reading ``docs/study/pilot_results_v1.json`` (WU-0002.12). ``None`` marks a dropped result.
V1_KEY_MAP: dict[str, str | None] = {
    "H1a": "V7",
    "H1b": "H1a",
    "H1c": "H1b",
    "H1d": "H1c",
    "H1e": "H1d",
    "H1f": "Q-N",
    "H2a": "H2a",
    "H2b": "H2b",
    "H2c": "H2c",
    "H2d": "H2d",
    "H2e": "gain_bound",
    "H3a": "H3a",
    "H3b": None,
    "H3c": "H3b",
    "H3d": "H3c",
    "T1": None,
}


# WU-0008.4: the declaration of each quantity of interest (NVVUQ.3, NVVUQ.22), keyed by the table
# key. Text from v3 sections 2, 5, 7 and 8 and Methods v2 section M12; it names the statistic, the
# error that would change a decision and the decision informed, and defines no band or level. The
# report prints it (``budget.qoi_declaration_lines``); the criterion column is ``row.criterion``.
QOI_FIELDS: tuple[str, ...] = ("definition", "units", "decision_error", "decision", "status")
"""The five fields of each declaration (``criterion`` is the table's own text)."""

_SECONDARY = ("secondary, pre-registered in v3 section 2; 95% interval, no multiplicity "
              "adjustment (v3 section 7); exploratory on development seeds")
_PRIMARY = ("primary, confirmatory by design; level 1 − 0.05/3 (v3 section 7); exploratory on "
            "development seeds, confirmatory only in the confirmatory run")
_EDGE = ("an interval half-width (sampling, numerical or proxy) comparable to the distance of the "
         "estimate from the band edge or bound would move the verdict between pass, fail and "
         "inconclusive (v3 section 7)")

QOI_DECLARATIONS: dict[str, dict[str, str]] = {
    "H1a": {
        "definition": "1/d from the fit of the median analog seed ε_s² to b² N_lib^(−2/d) + f² "
                      "over library sizes, per noise level, against the Levina–Bickel local "
                      "dimension estimate 1/d_LB",
        "units": "1/d dimensionless; ε_s in whitened latent units; N_lib in library states; ρ a "
                 "fraction of σ_x",
        "decision_error": "an interval half-width, or an error in 1/d_LB, comparable to the ±25% "
                          "band (about ±0.13 at 1/d ≈ 0.5, Methods v2 M12) changes the verdict",
        "decision": "whether the analog seed shrinks with library size as nearest-neighbor "
                    "theory predicts (RQ1, mechanism); informs no allocation choice",
        "status": _SECONDARY},
    "H1b": {
        "definition": "slope of log r.m.s. PLP error on log(g_H δ/√m) at H_ref = 1 LT, with g_H "
                      "the amplifier and δ the estimation seed; PLP only, because the test "
                      "assumes isotropic seeds (v3 section 8)",
        "units": "slope dimensionless; errors in units of σ_x against the noise-free truth, "
                 "clipped at 10 σ_x; H_ref = 30 steps",
        "decision_error": _EDGE + " (band [0.8, 1.2])",
        "decision": "whether PLP error is the seed times the amplifier (RQ1, mechanism)",
        "status": _SECONDARY},
    "H1c": {
        "definition": "median over states of Λ̄ × dT/d ln θ for PLP, with Λ̄ the slope of ln g_H "
                      "over 1 LT, T the characteristic horizon and θ the error tolerance",
        "units": "product dimensionless; T in steps (30 steps = 1 LT); θ a fraction of σ_x",
        "decision_error": _EDGE + " (band [0.8, 1.25])",
        "decision": "whether the horizon grows with log tolerance at rate 1/Λ (RQ1, mechanism)",
        "status": _SECONDARY},
    "H1d": {
        "definition": "Spearman correlation, over states, of each deployable estimate (ε̂, δ̂, Λ̂) "
                      "with its exact (oracle) value; N̂ is reported, not tested (v3 section 8)",
        "units": "correlation dimensionless; the estimates are the dimensionless profile "
                 "coordinates of v3 section 5",
        "decision_error": _EDGE + " (bound 0.7)",
        "decision": "whether the deployable proxies track their exact values, which bounds what "
                    "deployable allocation can achieve (RQ1)",
        "status": _SECONDARY},
    "Q-N": {
        "definition": "out-of-sample gain ΔR² from adding N to the other three conditions, for "
                      "predicting logit w* at 1 LT with exact (oracle) values; the deployable "
                      "version is secondary",
        "units": "ΔR² dimensionless; logit w* on states with 0 < w* < 1, with the counts of "
                 "w* = 0 and w* = 1 reported; N in units of ρ",
        "decision_error": "an interval half-width (projected 0.04, Methods v2 M12) that moves a "
                          "bound across 0 or across 0.05 changes the reading of the table of v3 "
                          "section 7",
        "decision": "whether noise sensitivity adds information beyond recurrence, "
                    "observability and instability (RQ1); a reading, not a test",
        "status": "pre-registered estimate, read by the table of v3 section 7, no pass/fail; "
                  "exploratory on development seeds"},
    "H2a": {
        "definition": "(i) median over eligible states of the range of w* over the initial "
                      "segment of the horizons 1, 2 and 4 LT at which both r.m.s. errors are at "
                      "most 0.5 σ_x (eligible: at least two such leading horizons); (ii) at H_ref, "
                      "the partial correlation with Λ̃ of the indicator 1{w* = 0} over all states, "
                      "of logit w* over the states with 0 < w* < 1, and, if w* = 1 in more than "
                      "5% of the states, of the indicator 1{w* = 1} over all states, each given "
                      "the seeds through quadratic controls (ln ε_s/ρ, ln δ/ρ, their squares and "
                      "their product; DEC-0008 A4)",
        "units": "w* in [0, 1], the optimal weight on CP; Λ̃ = 30 Λ̄ (per 30 steps); the "
                 "small-error regime is r.m.s. error at most 0.5 σ_x for both forecasters; "
                 "horizons in LT (30 steps); H_ref = 30 steps",
        "decision_error": "(i) the edge is the bound 0.1: a half-width comparable to the distance "
                          "of the median range from 0.1 changes the verdict (Methods v2 M12: pilot "
                          "medians 0.12 to 0.28, projected half-width 0.04); (ii) a half-width "
                          "near the band half-width 0.1 means it can be refuted but essentially "
                          "cannot pass: passing needs |r| within about 0.01 of zero",
        "decision": "whether the optimal weight separates from horizon and instability once the "
                    "seeds are fixed, which licenses allocating on the seeds alone (RQ2)",
        "status": _PRIMARY},
    "H2b": {
        "definition": "(i) mean over states of the per-state Spearman correlation of w* with ρ; "
                      "(ii) mean paired change in w* from N_lib = 10³ to 10⁴ at ρ = 1%",
        "units": "(i) correlation dimensionless; (ii) change in w* in [0, 1]; ρ a fraction of "
                 "σ_x; N_lib in library states; w* at the reference horizon",
        "decision_error": "a lower bound within the half-width of zero (projected 0.05 for (i), "
                          "0.03 for (ii), Methods v2 M12); a draw-noise or estimator error of "
                          "that size changes the verdict",
        "decision": "whether the two interventions, noise and library size, move the weight as "
                    "the theory predicts (RQ2)",
        "status": _PRIMARY},
    "H2c": {
        "definition": "paired MSE differences at H_ref: A4 − A2 (global weight) and A4 − the "
                      "better single forecaster, with A4o − A2 reported",
        "units": "squared error in units of σ_x² against the noise-free truth, clipped at 10 σ_x; "
                 "relative difference in percent",
        "decision_error": _EDGE + " (both upper bounds < 0); the deployable proxies, not the "
                          "theory, limit A4 (v3 section 8)",
        "decision": "whether the closed-form allocator beats a global weight and the better "
                    "single forecaster (RQ2, allocation)",
        "status": _SECONDARY},
    "H2d": {
        "definition": "MSE of the closed form A4 over the MSE of the learned allocator A3, "
                      "minus 1, at H_ref",
        "units": "ratio dimensionless (excess as a fraction); H_ref = 30 steps",
        "decision_error": _EDGE + " (upper bound 0.10)",
        "decision": "whether the closed form is within 10% of a learned allocator (RQ2, "
                    "allocation)",
        "status": _SECONDARY},
    "H2e": {
        "definition": "median per-state change in the correlation of the CP and PLP errors "
                      "from N_lib = 10³ to 10⁵, at ρ = 1% and 2%",
        "units": "correlation change dimensionless; ρ a fraction of σ_x; N_lib in library states",
        "decision_error": _EDGE + " (lower bound 0 at both noise levels)",
        "decision": "whether the two errors become correlated as the library grows (noise "
                    "matching, RQ2)",
        "status": "secondary, added after the pilot showed the effect and tested on fresh seeds "
                  "(v3 section 2); 95% interval, no multiplicity adjustment; exploratory on "
                  "development seeds"},
    "gain_bound": {
        "definition": "fraction of screened states in which the hybrid's horizon gain over the "
                      "better forecaster lies within the P1 bound, with the maximum gain and the "
                      "counts screened out (growth ≤ 0, censored, covariance < 0)",
        "units": "fraction dimensionless; gain in LT (30 steps)",
        "decision_error": "none: there is no bar, so no error moves a verdict; the screened-out "
                          "counts qualify what the fraction describes",
        "decision": "none: the gain is reported against the P1 bound, without a pass/fail bar "
                    "(v3 section 2)",
        "status": "reported only, no pass/fail; exploratory on development seeds"},
    "H3a": {
        "definition": "Holm-adjusted log-rank tests between consecutive regimes of the regime "
                      "lookup A5, on the realized horizons",
        "units": "p-values dimensionless; horizons in steps (30 steps = 1 LT) censored at "
                 "H_max = 8 LT",
        "decision_error": "H3a cannot fail (no equivalence margin is set, DEC-0008 A3): an "
                          "adjusted p-value near 0.01, a pair not computed or fewer than 50 states "
                          "moves the verdict only between pass and inconclusive, and no outcome "
                          "refutes it; the log-rank test treats states as independent, so serial "
                          "dependence of neighbouring states could overstate significance",
        "decision": "whether regimes separate forecast horizons (RQ3, compression); it can "
                    "confirm the separation, never refute it",
        "status": _SECONDARY},
    "H3b": {
        "definition": "importances of the profile coordinates in a weight tree and a horizon "
                      "tree (8 leaves), with a bootstrap over construction states; D is the "
                      "importance of Λ̃ in the horizon tree minus the largest other importance; "
                      "the stability index (share of resamples with D > 0) is reported only",
        "units": "importances dimensionless, summing to 1 over the four coordinates; Λ̃ per 30 "
                 "steps",
        "decision_error": "a weight-tree Λ̃ upper bound within one half-width of 0.2, or a lower "
                          "bound of D within one half-width of 0; the stability index is "
                          "reported, not decided (DEC-0008 A3)",
        "decision": "whether instability sets the horizon rather than the weight (RQ3)",
        "status": _SECONDARY},
    "H3c": {
        "definition": "MSE of the regime lookup A5 over the MSE of the closed form A4 at H_ref",
        "units": "ratio dimensionless; MSE in σ_x² against the noise-free truth; H_ref = 30 steps",
        "decision_error": "an upper bound within the interval half-width of 1.05; v3 section 7 "
                          "reads \"H3c holds while excess error is flat in K\" as \"the P3 floor\"",
        "decision": "whether a few regimes cost almost nothing against the closed form (RQ3, "
                    "compression)",
        "status": _PRIMARY},
}
