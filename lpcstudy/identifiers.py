"""The identifier table of the study: v3 hypothesis ids, roles and criterion texts.

One table, used by ``analysis`` (result keys), ``experiments`` (result keys) and ``report``
(verdicts, the Markdown table and figure keys), so that no module spells an identifier of its
own. The rows are the 14 rows of the identifier map in ``docs/study/decision_log_lpc.md``
("v3 ID | v2 ID | Role"); the ``criterion`` text is the statistic and the pass rule of the
hypothesis tables of ``docs/study/proposal_and_methods_v3.md`` section 2, verbatim with the
Markdown escapes removed (for the gain bound, the sentence after the RQ3 table).

This module defines no statistic, band, level or verdict rule: it names things. The v2 ids and
the v1 keys that appear below are historical data of the map, not live identifiers of the code.

WU-0002.2. WU-0002.9 and WU-0002.10 will consume ``role`` and ``pending``.
"""

from dataclasses import dataclass


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
        ROADMAP sub-tasks whose row names this id and may change the statistic computed under
        ``key``. While non-empty, the report marks the row as computed with the v1 statistic.
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
        "of the independently estimated 1/d", ("WU-0002.4",)),
    Hypothesis(
        "H1b", "H1c", "H1b", "secondary",
        "Slope of log r.m.s. PLP error on log(g_H δ/√m) at H_ref; pass if in [0.8, 1.2]",
        ("WU-0002.4",)),
    Hypothesis(
        "H1c", "H1d", "H1c", "secondary",
        "Median of Λ̄ × dT/d ln θ (PLP); pass if in [0.8, 1.25]"),
    Hypothesis(
        "H1d", "H1e", "H1d", "secondary",
        "Spearman correlation, each; pass if ≥ 0.7", ("WU-0002.5",)),
    Hypothesis(
        "Q-N", "Q-N", "Q-N", "estimate",
        "Out-of-sample gain in R² (ΔR²) for predicting logit w*, with exact (oracle) values; "
        "pass if read by the table in §7", ("WU-0002.6",)),
    Hypothesis(
        "H2a", "H2a", "H2a", "primary",
        "(i) median range of w* over 1, 2, 4 LT in the small-error regime; (ii) partial "
        "correlation of logit w* with Λ̃ given both seeds; pass if (i) interval below 0.1 and "
        "(ii) interval inside (−0.1, 0.1)"),
    Hypothesis(
        "H2b", "H2b", "H2b", "primary",
        "(i) mean per-state rank correlation of w* with ρ; (ii) mean paired change in w* from "
        "N_lib = 10³ to 10⁴ at ρ = 1%; pass if both lower bounds > 0", ("WU-0002.7",)),
    Hypothesis(
        "H2c", "H2c", "H2c", "secondary",
        "Paired MSE differences at H_ref; pass if both upper bounds < 0"),
    Hypothesis(
        "H2d", "H2d", "H2d", "secondary",
        "MSE ratio minus 1 at H_ref; pass if upper bound ≤ 0.10", ("WU-0002.8",)),
    Hypothesis(
        "H2e", "H2f", "H2e", "secondary",
        "Median per-state change in error correlation, N_lib 10³ → 10⁵; pass if lower bound > 0 "
        "at ρ = 1% and 2%", ("WU-0002.7",)),
    Hypothesis(
        "(reported)", "H2e", "gain_bound", "reported",
        "The hybrid's horizon gain over the better forecaster is reported against the P1 bound, "
        "without a pass/fail bar."),
    Hypothesis(
        "H3a", "H3a", "H3a", "secondary",
        "Holm-adjusted log-rank tests between consecutive regimes; pass if all p < 0.01",
        ("WU-0002.8",)),
    Hypothesis(
        "H3b", "H3c", "H3b", "secondary",
        "Importances in a weight tree and a horizon tree; pass if weight tree: Λ̃ < 0.2; "
        "horizon tree: Λ̃ highest"),
    Hypothesis(
        "H3c", "H3d", "H3c", "primary",
        "MSE ratio, regimes / closed form, at H_ref; pass if upper bound ≤ 1.05",
        ("WU-0002.8",)),
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
