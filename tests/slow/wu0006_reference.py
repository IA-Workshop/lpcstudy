"""Reference numbers for the WU-0006 simulation studies, written down before the results.

The slow tests in ``tests/slow`` check how often the study's confidence intervals
and verdicts are right, by simulation. To judge a simulated count, a test needs the
value that correct code should give. This module holds those values as plain data
tables: the expected coverage (the fraction of intervals that contain the truth),
the expected error rates, and for each a range in which the simulated count must
fall. They were computed by an independent simulation and fixed before any test
result was seen (VV.3), so they cannot be tuned to make a test pass. The harness
module ``wu0006_harness.py`` and the test modules read these tables; nothing here
runs code. The detailed provenance follows.

Transcribed by script from ``docs/agent/notes/2026-10-11-math-wu0006.md`` (applied-mathematician,
2026-10-11; reference simulations with an independent implementation, scratch seed 20261011, none
a DEV or CONF seed). ``COVERAGE_REFERENCE[(case, phi)][level]`` is ``(coverage, SE of the
reference, P(the ROADMAP-bound assertion fails | correct code), (low, high) consistency range of
the count out of 1000)``; the range is the central 1 - 0.0005 interval of
``Bin(1000, p)`` mixed over the reference's own Monte Carlo error. ``A3_REFERENCE[(case, phi)]``
is ``{"pass": (rate, P(fail), range), "fail": (...)}`` at the criterion's own level
``A3_LEVEL[case]``. The ranges hold only for the generators of ``wu0006_harness``, which follow
the note's M3 (a) specification.

**Correction of 2026-10-11 (WU-0006.4, applied-mathematician; DEF-0022; made AFTER test run 2
showed the failure, VV.3).** The C7 ``"pass"`` entries were wrong: the reference took P(pass) at
the edge to be the one-sided miss P(0.1 > hi), but H2a(ii-b) passes only if the interval lies
inside the open band (-0.1, 0.1), i.e. also lo > -0.1. They are recomputed with the production
verdict rule on the same design and procedure (reference replications only, no test-run count):
R_ref = 60 000 per phi (20 000 of seed 20261011 plus 40 000 of seed 20261012, scripts
``c7_extend.py`` and ``c7_verdict_ranges.py`` next to the note), same range rule as every other
range. The C7 ``"fail"`` entries are unchanged: their definition (lo >= 0.1 or hi <= -0.1)
matches the reference exactly (hi <= -0.1 occurred in 0 of 60 000 replications per phi). No other
entry is touched. ``C7_INCONCLUSIVE_REFERENCE`` is new and is not asserted by the harness.
"""

from __future__ import annotations

COVERAGE_REFERENCE: dict[
    tuple[str, str], dict[str, tuple[float, float, float, tuple[int, int]]]
] = {
    ("C1", "0"): {
        "95": (0.9451, 0.0011, 0.02, (918, 969)),
        "98.3": (0.98, 0.0007, 0.03, (963, 994)),
    },
    ("C2", "0"): {
        "95": (0.9395, 0.0012, 0.1, (911, 964)),
        "98.3": (0.9774, 0.0007, 0.11, (959, 992)),
    },
    ("C3", "0"): {
        "95": (0.9448, 0.0016, 0.02, (917, 969)),
        "98.3": (0.9807, 0.001, 0.03, (963, 994)),
    },
    ("C4", "0"): {
        "95": (0.9402, 0.0012, 0.08, (912, 965)),
        "98.3": (0.9772, 0.0007, 0.12, (959, 992)),
    },
    ("C5", "0"): {
        "95": (0.9383, 0.0012, 0.13, (910, 963)),
        "98.3": (0.9766, 0.0008, 0.15, (958, 991)),
    },
    ("C6", "0"): {
        "95": (0.947, 0.0022, 0.01, (919, 971)),
        "98.3": (0.9794, 0.0014, 0.05, (961, 993)),
    },
    ("C7", "0"): {
        "95": (0.9443, 0.0016, 0.03, (917, 968)),
        "98.3": (0.9794, 0.001, 0.05, (962, 993)),
    },
    ("C8", "0"): {
        "95": (0.9444, 0.0011, 0.02, (917, 968)),
        "98.3": (0.9806, 0.0007, 0.03, (963, 994)),
    },
    ("C9", "0"): {
        "95": (0.9427, 0.0016, 0.04, (915, 967)),
        "98.3": (0.9782, 0.001, 0.08, (960, 993)),
    },
    ("C1", "0.3"): {
        "95": (0.9257, 0.0013, 0.67, (895, 953)),
        "98.3": (0.9695, 0.0009, 0.63, (949, 987)),
    },
    ("C2", "0.3"): {
        "95": (0.9282, 0.0013, 0.55, (898, 955)),
        "98.3": (0.9706, 0.0008, 0.55, (950, 987)),
    },
    ("C3", "0.3"): {
        "95": (0.9292, 0.0018, 0.51, (899, 956)),
        "98.3": (0.9732, 0.0011, 0.36, (953, 989)),
    },
    ("C4", "0.3"): {
        "95": (0.9265, 0.0013, 0.63, (896, 954)),
        "98.3": (0.9715, 0.0008, 0.49, (951, 988)),
    },
    ("C5", "0.3"): {
        "95": (0.9275, 0.0013, 0.59, (897, 955)),
        "98.3": (0.9691, 0.0009, 0.66, (948, 986)),
    },
    ("C6", "0.3"): {
        "95": (0.9439, 0.0023, 0.03, (915, 968)),
        "98.3": (0.98, 0.0014, 0.04, (962, 994)),
    },
    ("C7", "0.3"): {
        "95": (0.9389, 0.0017, 0.11, (910, 964)),
        "98.3": (0.9762, 0.0011, 0.17, (957, 991)),
    },
    ("C8", "0.3"): {
        "95": (0.923, 0.0013, 0.78, (892, 951)),
        "98.3": (0.9682, 0.0009, 0.72, (947, 986)),
    },
    ("C9", "0.3"): {
        "95": (0.9311, 0.0018, 0.42, (901, 958)),
        "98.3": (0.9736, 0.0011, 0.33, (954, 990)),
    },
}

A3_LEVEL: dict[str, str] = {
    "C2": "95",
    "C4": "98.3",
    "C5": "95",
    "C6": "95",
    "C7": "98.3",
    "C8": "98.3",
    "C9": "95",
}

A3_REFERENCE: dict[
    tuple[str, str], dict[str, tuple[float, float, tuple[int, int]]]
] = {
    ("C2", "0"): {
        "pass": (0.0308, 0.06, (14, 52)),
        "fail": (0.0296, 0.04, (13, 50)),
    },
    ("C4", "0"): {
        "pass": (0.0116, 0.08, (2, 25)),
        "fail": (0.0111, 0.06, (2, 25)),
    },
    ("C5", "0"): {
        "pass": (0.032, 0.09, (14, 53)),
        "fail": (0.0297, 0.04, (13, 50)),
    },
    ("C6", "0"): {
        "pass": (0.0268, 0.01, (10, 47)),
        "fail": (0.0262, 0.01, (10, 47)),
    },
    # 2026-10-11 correction (DEF-0022, after run 2): was 'pass': (0.01, 0.03, (1, 23)).
    ("C7", "0"): {
        "pass": (0.00103, 0.0, (0, 6)),
        "fail": (0.0106, 0.05, (1, 24)),
    },
    ("C8", "0"): {
        "pass": (0.01, 0.03, (1, 23)),
        "fail": (0.0095, 0.02, (1, 22)),
    },
    ("C9", "0"): {
        "pass": (0.0299, 0.05, (13, 51)),
        "fail": (0.0274, 0.02, (11, 48)),
    },
    ("C2", "0.3"): {
        "pass": (0.036, 0.27, (17, 58)),
        "fail": (0.0358, 0.26, (17, 58)),
    },
    ("C4", "0.3"): {
        "pass": (0.0145, 0.29, (3, 30)),
        "fail": (0.014, 0.24, (3, 29)),
    },
    ("C5", "0.3"): {
        "pass": (0.0362, 0.28, (17, 59)),
        "fail": (0.0363, 0.29, (17, 59)),
    },
    ("C6", "0.3"): {
        "pass": (0.0274, 0.02, (11, 48)),
        "fail": (0.0287, 0.03, (12, 50)),
    },
    # 2026-10-11 correction (DEF-0022, after run 2): was 'pass': (0.0126, 0.14, (2, 27)).
    ("C7", "0.3"): {
        "pass": (0.00025, 0.0, (0, 3)),
        "fail": (0.0112, 0.07, (2, 25)),
    },
    ("C8", "0.3"): {
        "pass": (0.0158, 0.41, (4, 31)),
        "fail": (0.016, 0.44, (4, 32)),
    },
    ("C9", "0.3"): {
        "pass": (0.0335, 0.15, (15, 56)),
        "fail": (0.0355, 0.24, (17, 58)),
    },
}

# 2026-10-11 (WU-0006.4, DEF-0022): C7 "inconclusive" at the edge, (rate, range of the count out of
# 1000), same rule and R_ref = 60 000 as the corrected C7 "pass". Reported for the owner; the harness
# asserts only the "pass" and "fail" ranges.
C7_INCONCLUSIVE_REFERENCE: dict[
    tuple[str, str], tuple[float, tuple[int, int]]
] = {
    ("C7", "0"): (0.98848, (975, 998)),
    ("C7", "0.3"): (0.98803, (974, 998)),
}

# --- Log-rank (note M5; production h3a_logrank; 600 states, 3 terciles of 200; R_ref = 40 000) ---
# (row, phi) -> {"fwer": (rate, range of the count out of 2000) or None, "pass": (rate, range),
#                "inflation": mean chi-square of the null pair(s), "p_fail": P(ROADMAP bound fails)}
LOGRANK_REFERENCE: dict[tuple[str, str], dict[str, object]] = {
    ("L1", "0"): {
        "fwer": (0.0105, (7, 39)),
        "pass": (0.0010, (0, 9)),
        "inflation": 1.009,
        "p_fail": 0.006,
    },
    ("L1", "0.3"): {
        "fwer": (0.0134, (11, 47)),
        "pass": (0.0013, (0, 10)),
        "inflation": 1.079,
        "p_fail": 0.105,
    },
    ("L2", "0"): {
        "fwer": None,
        "pass": (0.0115, (8, 42)),
        "inflation": 1.012,
        "p_fail": 0.021,
    },
    ("L2", "0.3"): {
        "fwer": None,
        "pass": (0.0122, (9, 44)),
        "inflation": 1.046,
        "p_fail": 0.041,
    },
}

# --- Characterization rows (note M2, R_ref = 20 000; phi = 0 except C1s): (95%, 98.3%) coverage ---
CHARACTERIZATION_REFERENCE: dict[str, tuple[float, float]] = {
    "C1s0.1": (0.9398, 0.9794),
    "C1s0.2": (0.9328, 0.9740),
    "C2h1.5": (0.9298, 0.9734),
    "C2h2": (0.9214, 0.9695),
    "C4h1.5": (0.9331, 0.9744),
    "C4h2": (0.9227, 0.9669),
}
CHARACTERIZATION_R_REF = 20_000

# --- Null delta R^2 (addendum A9; production qn_profile_block; 3000 / 1000 states) ---
# 2026-10-11 replacement (applied-mathematician, addendum A9; a documented correction made AFTER test
# run 2, VV.3; the derivation does not use the run-2 counts). The first version of this table was the
# R_ref = 200 run of the review's M4 (phi = 0 only, seed 20261011, indicative), kept here:
#   logit_w_interior: mean_gain -0.0023, sd 0.0024, P(gain > 0) 0.15, half_width 0.0155,
#                     N1 0.925, N2 0.020, N3 0.960, P("reduces") 0.980
#   w_zero_indicator: mean_gain -0.0035, sd 0.0043, P(gain > 0) 0.21, half_width 0.0253,
#                     N1 0.890, N2 0.035, N3 0.925, P("reduces") 0.960
# Its failure probabilities (N2 0.25, N3 0.42 for the indicator) came from tail draws of that small
# run and are retracted (A9).
# New table: R_ref = 1000 per phi (scratch seed 20261014, 8 single-thread workers). For each
# (phi, target): the reference rates of the three rows with their standard errors, the probability
# that the slow test's bound fails at R = 500 (N1 and N3 >= 461, N2 <= 22) for correct code, and
# the consistency range of the count out of 500 (central 1 - 0.0005 of Bin(500, p) mixed over the
# reference's error; the always-asserted defect test).
DELTA_R2_REFERENCE_R = 1000
DELTA_R2_REFERENCE: dict[tuple[str, str], dict[str, object]] = {
    ("0", "logit_w_interior"): {
        "mean_gain": -0.0024,
        "p_gain_positive": 0.169,
        "half_width": 0.0156,
        "n1": (0.919, 0.009, 0.54, (431, 483)),
        "n2": (0.016, 0.004, 0.000, (0, 23)),
        "n3": (0.941, 0.007, 0.066, (446, 490)),
    },
    ("0", "w_zero_indicator"): {
        "mean_gain": -0.0032,
        "p_gain_positive": 0.218,
        "half_width": 0.0251,
        "n1": (0.933, 0.008, 0.19, (440, 487)),
        "n2": (0.019, 0.004, 0.001, (0, 25)),
        "n3": (0.945, 0.007, 0.033, (448, 491)),
    },
    ("0.3", "logit_w_interior"): {
        "mean_gain": -0.0025,
        "p_gain_positive": 0.125,
        "half_width": 0.0155,
        "n1": (0.924, 0.008, 0.41, (434, 484)),
        "n2": (0.009, 0.003, 0.000, (0, 16)),
        "n3": (0.946, 0.007, 0.028, (449, 491)),
    },
    ("0.3", "w_zero_indicator"): {
        "mean_gain": -0.0034,
        "p_gain_positive": 0.203,
        "half_width": 0.0251,
        "n1": (0.926, 0.008, 0.35, (436, 485)),
        "n2": (0.014, 0.004, 0.000, (0, 21)),
        "n3": (0.945, 0.007, 0.033, (448, 491)),
    },
}
