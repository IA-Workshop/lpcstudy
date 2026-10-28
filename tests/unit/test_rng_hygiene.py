"""Randomness hygiene of ``lpcstudy/`` (WU-0002.14, P4 and P5; DEF-0011).

Needs owner review before freeze. Every random number in the study must come
from ``make_rng(seed, *labels)``, which gives one reproducible stream per
purpose. If some code drew numbers another way (for example ``seed + 1``, or
NumPy's global generator), two parts of the study could share a stream or a run
could not be repeated. These tests scan the source code of the package for such
bypasses.

Two static scans of the package are used. Each is first tested on hand-written
source strings whose verdict is known by construction (the pattern of
``test_data.py``, ``_scan_random_state``), and then run on the repository:

* P4 (no bypass): ``default_rng(`` occurs only at the four allowlisted sites;
  no ``seed +`` arithmetic; no use of ``np.random`` other than ``Generator``
  and ``default_rng``; every ``PRNGKey(`` argument is a draw
  ``int(<generator>.integers(...))``, directly or through a name assigned from
  one in the same function.
* P5 (label hygiene): no literal label tuple of ``make_rng`` is used at two
  call sites, except the pairings that the design keeps on purpose (M4 of the
  mathematics check). Also, the crc32 of every label string of the full preset
  is distinct, because a crc collision would make two ``make_rng`` streams
  identical.

References are the allowlists written below, from the plan and its mathematics
check, and the independent ``zlib.crc32``. Tolerance: none (exact set
equalities).
"""

from __future__ import annotations

import ast
import itertools
import zlib
from pathlib import Path

import numpy as np
import pytest

from lpcstudy.analysis import H1D_REPORTED, H1D_TESTED
from lpcstudy.config import FULL
from lpcstudy.data import SPLITS, make_rng

PACKAGE = Path(__file__).resolve().parents[2] / "lpcstudy"

DEFAULT_RNG_ALLOWLIST = {
    ("data.py", "make_rng"),
    (
        "statistics.py",
        "block_resample_indices",
    ),  # the integer path, kept for fixtures
    ("validation.py", "check_cramer_rao"),  # V2 fixture, DEC-0017 Q7
    ("validation.py", "check_kaplan_meier"),  # V5 fixture, DEC-0017 Q7
}
"""The four ``default_rng(`` sites of the plan (P4)."""

PAIRINGS = {
    ("bootstrap", "H1b"): {
        ("analysis.py", "h1b_seed_amplifier"),  # CP and PLP
        ("clip_sensitivity.py", "h1b_part"),
    },  # the clip recomputation
    ("bootstrap", "H2b-noise"): {
        ("analysis.py", "h2b_knob_response"),
        ("clip_sensitivity.py", "h2b_noise_part"),
    },
    ("bootstrap", "H2c"): {
        ("analysis.py", "h2c_state_dependence")
    },  # the three differences
    ("h2a-two-part",): {
        ("analysis.py", "h2a_separation"),
        ("clip_sensitivity.py", "h2a_parts"),
        ("experiments.py", "_perturbation_scale_variant"),
    },  # H2a(ii), its variants
    ("h2b-library-change", "f'{rho:g}'"): {
        ("analysis.py", "h2b_knob_response"),
        ("clip_sensitivity.py", "h2b_library_part"),
    },
    ("bootstrap", "Q-N"): {
        ("analysis.py", "qn_noise_redundancy"),
        ("ablation.py", "profile_ablation"),
        ("contribution.py", "qn_cross_check"),
    },  # WU-0039b: the profile ablation draws Q-N's resamples (drop-N is Q-N);
    # WU-0048 test (g) recomputes those rows from the dump with the same draws
}
"""Literal label tuples that two or more ``make_rng`` sites share on purpose.

These are the pairings of M4 of the mathematics check, extended in review R1 to
the clip-sensitivity recomputation. That recomputation must draw the SAME
resamples as the verdict it re-reads, otherwise its flags measure resampling
noise. The pairings are: the H1b CP and PLP resamples; the three H2c
differences; H2a(ii) with its Lambda_fin variant and its clip recomputation;
H2b(i) and H2b(ii) with their clip recomputations; and Q-N with the profile
ablation of WU-0039b, whose drop-N row must reproduce Q-N bitwise and whose
other rows share Q-N's resamples (pre-registration draft section 7.1).

Every other pairing (H1c, Q-N, the directions across scales, the oracle pool,
the estimator and allocator streams) shares by calling ONE site more than once,
which this scan cannot see. ``test_analysis.py`` and ``test_experiments.py``
pin those (P9), and ``test_clip_sensitivity.py`` (T6) pins the recomputation:
no clipped entry gives a delta of exactly 0.0."""


def _enclosing(tree: ast.AST) -> dict[ast.AST, str]:
    """Map every syntax node to the name of the function that contains it.

    The name is ``'<module>'`` for a node outside any function.
    """
    owner: dict[ast.AST, str] = {}

    def visit(node: ast.AST, name: str) -> None:
        for child in ast.iter_child_nodes(node):
            child_name = (
                child.name
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                else name
            )
            owner[child] = child_name
            visit(child, child_name)

    owner[tree] = "<module>"
    visit(tree, "<module>")
    return owner


SEED_NAMES = frozenset({"seed", "boot_seed", "master_seed"})
"""Names that hold a master seed or a bootstrap seed in the package."""

SEED_CONSUMERS = frozenset(
    {
        "make_rng",
        "sklearn_seed",
        "draw_starts",
        "state_oracles",
        "_h3b_trees",
        "fit_regime_tree",
        "qn_regressor",
        "make_estimator",  # WU-0048: the phase J learner, like qn_regressor
        "qn_profile_block",
        "profile_ablation_block",
        "with_seed",
        "resolve_dev_seed",
        "int",
        "isinstance",
        "type",
    }
)
"""Callees that may receive a master seed (an integer) directly.

They are the labeled-generator factory, the scikit-learn seed derivation, and
the functions whose parameter is the master seed by design (WU-0002.14).
Anything else that receives a seed-named value is a finding."""

PASS_THROUGH = frozenset(
    {
        ("analysis.py", "h2a_initial_segments"),
        ("analysis.py", "h2a_part_ii"),
        ("analysis.py", "qn_profile_block"),
        ("ablation.py", "profile_ablation_block"),
        ("contribution.py", "analyze_system"),
    }
)
"""Functions whose ``seed``/``boot_seed`` parameter is forwarded.

``contribution.analyze_system`` (WU-0048) forwards the master seed to its
``Learner`` (which only calls ``sklearn_seed``) and to
``bootstrap_generator`` (which only calls ``make_rng``).

The parameter is a Generator (or the master seed of ``qn_regressor``); callers
pass a ``make_rng(...)`` generator (checked below)."""

BOOTSTRAP_SEED_ARGUMENT = {
    "block_resample_indices": (3, "seed"),
    "bootstrap_values": (4, "seed"),
    "block_bootstrap_counted": (4, "seed"),
    "block_bootstrap_dropped": (4, "seed"),
    "block_bootstrap": (4, "seed"),
    "_boot": (3, "rng"),
    "h2a_part_ii": (None, "seed"),
    "h2a_initial_segments": (None, "seed"),
    "qn_profile_block": (None, "boot_seed"),
    "profile_ablation_block": (None, "boot_seed"),
}
"""Position and keyword of the generator argument of the bootstrap helpers.

A production caller must pass a ``make_rng(...)`` call or a generator-valued
name, never an integer or a seed-named value. The integer path of
``block_resample_indices`` has no production caller (plan, P4)."""


def _is_seed(node: ast.AST) -> bool:
    """Say whether a node is a seed.

    A seed is a seed-named variable, an attribute named ``seed``
    (``config.seed``), or ``getattr(x, "seed")``.
    """
    if (
        isinstance(node, ast.Call)
        and _callee(node) == "getattr"
        and len(node.args) >= 2
        and isinstance(node.args[1], ast.Constant)
        and node.args[1].value == "seed"
    ):
        return True
    return (isinstance(node, ast.Name) and node.id in SEED_NAMES) or (
        isinstance(node, ast.Attribute) and node.attr == "seed"
    )


def _mentions_seed(node: ast.AST, taint: frozenset = frozenset()) -> bool:
    """Say whether a seed occurs anywhere in an expression.

    A seed is a seed-named variable, or a name tainted by an assignment from a
    seed.
    """
    return any(
        _is_seed(n) or (isinstance(n, ast.Name) and n.id in taint)
        for n in ast.walk(node)
    )


def _seed_valued(node: ast.AST, taint: frozenset) -> bool:
    """Say whether the expression IS a seed (not a generator built from one).

    That means a seed, a tainted name, ``int(...)`` of one, a call of a tainted
    lambda, or a conditional with such a branch.
    """
    if _is_seed(node) or (isinstance(node, ast.Name) and node.id in taint):
        return True
    if isinstance(node, ast.Call):
        if _callee(node) == "int" and len(node.args) == 1:
            return _seed_valued(node.args[0], taint)
        return isinstance(node.func, ast.Name) and node.func.id in taint
    if isinstance(node, ast.IfExp):
        return _seed_valued(node.body, taint) or _seed_valued(
            node.orelse,
            taint,
        )
    return False


def _taints(tree: ast.AST, owner: dict) -> dict[str, frozenset]:
    """Find, per function, the names that hold a seed.

    A name is tainted if it is assigned (to a fixed point) from a seed-valued
    expression or from a lambda whose body is seed-valued. Tuple assignments are
    read pairwise.
    """
    taint: dict[str, set] = {}
    for _ in range(4):
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                continue
            targets = (
                node.targets if isinstance(node, ast.Assign) else [node.target]
            )
            value = node.value
            if value is None:
                continue
            pairs = (
                [(targets[0], value)]
                if len(targets) == 1
                else [(t, value) for t in targets]
            )
            if (
                len(targets) == 1
                and isinstance(targets[0], ast.Tuple)
                and isinstance(value, ast.Tuple)
                and len(targets[0].elts) == len(value.elts)
            ):
                pairs = list(zip(targets[0].elts, value.elts))
            scope = taint.setdefault(owner[node], set())
            frozen = frozenset(scope)
            for target, val in pairs:
                body = val.body if isinstance(val, ast.Lambda) else val
                if (
                    isinstance(target, ast.Name)
                    and _seed_valued(body, frozen)
                    and target.id not in scope
                ):
                    scope.add(target.id)
                    changed = True
        if not changed:
            break
    return {k: frozenset(v) for k, v in taint.items()}


def _is_generator_draw(node: ast.expr) -> bool:
    """Say whether a node has the form ``int(<expr>.integers(...))``."""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "int"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Call)
        and isinstance(node.args[0].func, ast.Attribute)
        and node.args[0].func.attr == "integers"
    )


def _callee(call: ast.Call) -> str | None:
    """Return the name of the function a call invokes (or ``None``)."""
    func = call.func
    return (
        func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
    )


RANDOM_LEAVES = frozenset({"key", "wrap_key_data", "PRNGKey"})
"""``jax.random`` functions that build a key from an integer.

They are legal only inside a Generator draw."""


def _aliases(tree: ast.AST) -> dict[str, str]:
    """Find the names bound to ``numpy``, ``jax`` or their ``random`` modules.

    The binding is made by ``import ... as``. The plain names ``np``, ``numpy``
    and ``jax`` are always roots (a source may use them without importing).
    """
    roots = {"np": "numpy", "numpy": "numpy", "jax": "jax"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in ("numpy", "jax"):
                    roots[alias.asname or alias.name.split(".")[0]] = (
                        alias.name if alias.asname else alias.name.split(".")[0]
                    )
    return roots


def _resolve(node: ast.AST, roots: dict[str, str]) -> str | None:
    """Return the dotted name of an attribute chain rooted at a numpy or jax
    alias.

    The result is ``None`` if the chain has another root.
    """
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name) and node.id in roots:
        return ".".join([roots[node.id], *reversed(parts)])
    return None


def scan_bypass(
    sources: dict[str, str],
) -> tuple[set[tuple[str, str]], list[str]]:
    """Find the ``default_rng`` sites and the other bypasses of ``make_rng``.

    Findings (the second element of the result):

    * seed arithmetic of any shape and depth (``seed + 1``, ``seed * 2 + 1``,
      ``config.seed - 1``);
    * a seed passed as an argument to a callee outside ``SEED_CONSUMERS`` (a
      pass-through function of ``PASS_THROUGH`` excepted), also when it reaches
      the call through an intermediate name (``base = config.seed``), a lambda
      (``g = lambda: config.seed``) or ``getattr(config, "seed")``;
    * an integer constant or a seed in the generator position of a bootstrap
      helper, or a helper without one (so the integer path of
      ``block_resample_indices`` has no production caller);
    * ``numpy.random`` attributes other than ``Generator`` and ``default_rng``
      under any alias of ``numpy`` (``import numpy as xp``);
    * a ``numpy.random`` or ``jax.random`` module, or
      ``jax.random.key``/``wrap_key_data``/``PRNGKey``, bound to a name (``r =
      np.random``, ``P = jax.random.PRNGKey``);
    * ``getattr`` on a numpy or jax name or with the attribute
      ``seed``/``random``/``default_rng``/``key``;
    * ``import random``, ``import numpy.random``, ``from numpy.random import``,
      ``from numpy import random``, ``from jax import random``, ``from
      jax.random
      import``;
    * ``jax.random.key`` (also through ``import jax.random as jr``);
    * ``PRNGKey`` arguments that are not Generator draws;
    * a ``random_state=`` that is not a ``sklearn_seed`` call.

    Modules named ``seeds.py`` (the seed registry) are exempt from the
    seed-argument and arithmetic rules.

    Parameters
    ----------
    sources : dict[str, str]
        Module name to source text.

    Returns
    -------
    tuple[set[tuple[str, str]], list[str]]
        The set of ``(module, function)`` that call ``default_rng``, and the
        findings.
    """
    sites: set[tuple[str, str]] = set()
    problems: list[str] = []
    for module, source in sources.items():
        tree = ast.parse(source)
        owner = _enclosing(tree)
        registry = module == "seeds.py"
        roots = _aliases(tree)
        taints = _taints(tree, owner)
        parent: dict[ast.AST, ast.AST] = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parent[child] = node
        draws: dict[tuple[str, str], bool] = (
            {}
        )  # (function, name) -> assigned only from draws
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
            ):
                key = (owner[node], node.targets[0].id)
                draws[key] = draws.get(key, True) and _is_generator_draw(
                    node.value
                )
        for node in ast.walk(tree):
            where = f"{module}:{getattr(node, 'lineno', '?')}"
            taint = taints.get(owner.get(node, "<module>"), frozenset())
            if isinstance(node, ast.Call):
                callee = _callee(node)
                here = (module, owner[node])
                if callee == "default_rng":
                    sites.add(here)
                if (
                    callee == "getattr"
                    and node.args
                    and (
                        any(
                            isinstance(n, ast.Name) and n.id in roots
                            for n in ast.walk(node.args[0])
                        )
                        or (
                            len(node.args) > 1
                            and isinstance(node.args[1], ast.Constant)
                            and node.args[1].value
                            in (
                                {"seed", "random", "default_rng"}
                                | RANDOM_LEAVES
                            )
                        )
                    )
                ):
                    problems.append(
                        f"{where} getattr on a random module or on a seed"
                    )
                if callee == "PRNGKey":
                    arg = (
                        node.args[0]
                        if len(node.args) == 1 and not node.keywords
                        else None
                    )
                    ok = arg is not None and (
                        _is_generator_draw(arg)
                        or (
                            isinstance(arg, ast.Name)
                            and draws.get((owner[node], arg.id), False)
                        )
                    )
                    if not ok:
                        problems.append(
                            f"{where} PRNGKey argument is not a Generator draw"
                        )
                for kw in node.keywords:
                    if kw.arg == "random_state" and not (
                        isinstance(kw.value, ast.Call)
                        and _callee(kw.value) == "sklearn_seed"
                    ):
                        problems.append(
                            f"{where} random_state is not a sklearn_seed call"
                        )
                if not registry:
                    direct = [a for a in node.args] + [
                        k.value for k in node.keywords
                    ]
                    for arg in direct:
                        if (
                            _seed_valued(arg, taint)
                            and callee not in SEED_CONSUMERS
                            and here not in PASS_THROUGH
                            and not (
                                callee == "default_rng"
                                and here in DEFAULT_RNG_ALLOWLIST
                            )
                            and module != "statistics.py"
                        ):
                            problems.append(f"{where} seed passed to {callee}")
                    position, keyword = BOOTSTRAP_SEED_ARGUMENT.get(
                        callee,
                        (None, None),
                    )
                    given = [k.value for k in node.keywords if k.arg == keyword]
                    if position is not None and len(node.args) > position:
                        given.append(node.args[position])
                    elif callee in BOOTSTRAP_SEED_ARGUMENT and not given:
                        problems.append(
                            f"{where} {callee} without a generator argument"
                        )
                    for arg in given:
                        integer = isinstance(arg, ast.Constant) and isinstance(
                            arg.value,
                            int,
                        )
                        if (
                            integer
                            or (
                                _mentions_seed(arg, taint)
                                and not (
                                    isinstance(arg, ast.Call)
                                    and _callee(arg) == "make_rng"
                                )
                            )
                            and module != "statistics.py"
                            and here not in PASS_THROUGH
                        ):
                            problems.append(
                                f"{where} integer or seed-named generator "
                                f"argument "
                                f"of {callee}"
                            )
            elif (
                (
                    isinstance(node, ast.BinOp)
                    or (
                        isinstance(node, ast.UnaryOp)
                        and isinstance(
                            node.op,
                            (ast.USub, ast.UAdd, ast.Invert),
                        )
                    )
                )
                and not registry
                and _mentions_seed(node, taint)
            ):
                problems.append(f"{where} seed arithmetic")
            elif isinstance(node, ast.Attribute):
                dotted = _resolve(node, roots)
                up = parent.get(node)
                is_link = isinstance(up, ast.Attribute) and up.value is node
                if dotted is None or is_link:
                    pass
                elif dotted.startswith("numpy.random.") and dotted.rsplit(
                    ".",
                    1,
                )[1] not in ("Generator", "default_rng"):
                    problems.append(f"{where} {dotted}")
                elif dotted in ("numpy.random", "jax.random"):
                    problems.append(
                        f"{where} {dotted} used as a value (bound to a name)"
                    )
                elif (
                    dotted.startswith("jax.random.")
                    and dotted.rsplit(".", 1)[1] in RANDOM_LEAVES
                ):
                    called = isinstance(up, ast.Call) and up.func is node
                    if dotted.endswith(("key", "wrap_key_data")):
                        problems.append(f"{where} {dotted}")
                    elif not called:
                        problems.append(f"{where} {dotted} bound to a name")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "random" or alias.name.startswith(
                        ("random.", "numpy.random")
                    ):
                        problems.append(f"{where} import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and (
                    node.module == "random"
                    or node.module.startswith(
                        ("numpy.random", "random.", "jax.random")
                    )
                ):
                    problems.append(f"{where} from {node.module} import")
                elif node.module in ("numpy", "jax") and any(
                    a.name == "random" for a in node.names
                ):
                    problems.append(f"{where} from {node.module} import random")
    return sites, problems


def label_templates(
    sources: dict[str, str],
) -> list[tuple[str, str, int, list[ast.expr]]]:
    """List every ``make_rng`` call and every ``_paired_change`` label tuple.

    Each entry is ``(module, function, line, label expressions)``. The label
    expressions after the seed are AST nodes. A ``*labels`` call is skipped (its
    callers are read).
    """
    out = []
    for module, source in sources.items():
        tree = ast.parse(source)
        owner = _enclosing(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            callee = _callee(node)
            if callee == "make_rng" and not any(
                isinstance(a, ast.Starred) for a in node.args[1:]
            ):
                out.append(
                    (module, owner[node], node.lineno, list(node.args[1:]))
                )
            elif callee == "_paired_change":
                tup = next(
                    (a.elts for a in node.args if isinstance(a, ast.Tuple)),
                    None,
                )
                if tup is not None:
                    out.append((module, owner[node], node.lineno, list(tup)))
    return out


def scan_labels(
    sources: dict[str, str],
) -> list[tuple[str, str, int, tuple[str, ...]]]:
    """List ``(module, function, line, literal labels)`` of every ``make_rng``
    call.

    The literal labels are the string constants (and the source of f-strings)
    among the arguments after the seed. A call with a ``*labels`` argument is
    not listed; its callers are. The tuple argument of ``_paired_change`` is
    read as the labels of that call.
    """
    found = []
    for module, function, line, parts in label_templates(sources):
        literal = tuple(
            (
                p.value
                if isinstance(p, ast.Constant) and isinstance(p.value, str)
                else ast.unparse(p)
            )
            for p in parts
            if (isinstance(p, ast.Constant) and isinstance(p.value, str))
            or isinstance(p, ast.JoinedStr)
        )
        found.append((module, function, line, literal))
    return found


def shared_labels(
    found: list[tuple[str, str, int, tuple[str, ...]]],
) -> dict[tuple[str, ...], set[tuple[str, str]]]:
    """Find literal label tuples used at two or more call sites.

    Returns each such tuple with its ``(module, function)`` sites.
    """
    by_key: dict[tuple[str, ...], list] = {}
    for module, function, line, literal in found:
        by_key.setdefault(literal, []).append((module, function, line))
    return {
        key: {(m, f) for m, f, _ in sites}
        for key, sites in by_key.items()
        if len(sites) > 1 and key
    }


def _package_sources() -> dict[str, str]:
    """Read the source text of every module of the package, by file name."""
    return {
        path.name: path.read_text() for path in sorted(PACKAGE.glob("*.py"))
    }


def test_bypass_scan_flags_every_bypass_and_passes_the_good_forms() -> None:
    """The scanner flags what it should on hand-written sources (P4 scanner
    check, review R2).

    Reference: source strings with a known verdict, one per form.

    Flagged:

    * seed arithmetic of any shape (``seed + 1``, ``config.seed + 5``, ``seed *
      2
      + 1``, ``config.seed - 1``, a seed deep in an expression, ``-seed``);
    * ``np.random.seed``, ``numpy.random.rand``, ``getattr(np.random, ...)``;
    * ``import random``, ``import numpy.random``, ``from numpy.random import
      ...``, ``from numpy import random``, ``from jax import random``;
    * ``jax.random.key`` and ``wrap_key_data``;
    * ``PRNGKey(seed)``, ``PRNGKey(7)``, ``PRNGKey(x)``, a name that is not
      always
      a draw;
    * an integer or seed-named value in the generator position of a bootstrap
      helper (positional or keyword), a bootstrap helper without one, a seed
      passed to any other callee;
    * ``random_state=0`` and ``random_state=config.seed``.

    Passed: ``PRNGKey(int(rng.integers(...)))`` and a name assigned only from
    such a draw; ``make_rng(config.seed, ...)``, ``sklearn_seed``, ``not
    isinstance(seed, int)``, a bootstrap helper given a ``make_rng`` call or a
    generator name; the annotation ``np.random.Generator``. ``default_rng`` is
    reported with its enclosing function.
    """
    bad = {
        "plus": "x = seed + 1",
        "plus_attr": "x = config.seed + 5",
        "np_seed": "import numpy as np\nnp.random.seed(0)",
        "np_rand": "import numpy\nnumpy.random.rand(3)",
        "stdlib": "import random",
        "key_seed": "k = PRNGKey(seed)",
        "key_const": "k = PRNGKey(7)",
        "key_name": "def f(x):\n    return PRNGKey(x)",
        "mixed": (
            "def f(rng):\n    a = int(rng.integers(0, 4))\n    a = 3\n"
            "    return PRNGKey(a)"
        ),
        # review R2 (WU-0002.14): forms the first version of the scan let
        # through
        "int_seed_to_bootstrap": (
            "def f(c):\n    return block_bootstrap_counted(s, 5, 10, 5, "
            "c.seed, .95)"
        ),
        "int_literal_to_bootstrap": (
            "def f():\n    return bootstrap_values(s, 5, 10, 5, 7)"
        ),
        "int_literal_keyword": (
            "def f():\n    return block_bootstrap(s, 5, 10, 5, seed=7)"
        ),
        "seed_keyword_h2a": (
            "def f(c):\n    return h2a_part_ii(w, g, x, n_resamples=1, "
            "block=5, seed=c.seed)"
        ),
        "boot_seed_keyword": (
            "def f(c):\n    return qn_profile_block(x, boot_seed=c.seed)"
        ),
        "no_generator_argument": (
            "def f():\n    return block_bootstrap(s, 5, 10, 5)"
        ),
        "seed_to_other_callee": "def f(c):\n    return helper(c.seed)",
        "seed_keyword_other": "def f(c):\n    return helper(x=seed)",
        "jax_key": "import jax\nk = jax.random.key(0)",
        "wrap_key_data": "import jax\nk = jax.random.wrap_key_data(d)",
        "from_numpy_random": "from numpy.random import default_rng as dr",
        "from_numpy_random_generator": (
            "from numpy.random import Generator, PCG64"
        ),
        "from_numpy_import_random": "from numpy import random as npr",
        "import_numpy_random": "import numpy.random",
        "from_jax_import_random": "from jax import random",
        "getattr_random": "import numpy as np\nf = getattr(np.random, 'seed')",
        "seed_times_two": "x = seed * 2 + 1",
        "seed_minus_one": "x = config.seed - 1",
        "seed_deep": "x = (3 + (config.seed ^ 5)) % 7",
        "seed_negated": "x = -seed",
        "random_state_const": "M(random_state=0)",
        "random_state_seed": "M(random_state=config.seed)",
        # re-review R9: indirect forms
        "seed_via_name": (
            "def f(c):\n    base = c.seed\n"
            "    return block_bootstrap_counted(s, 5, 10, 5, "
            "base, .95)"
        ),
        "seed_via_name_other_callee": (
            "def f(c):\n    base = c.seed\n    return helper(base)"
        ),
        "seed_via_int_name": (
            "def f(c):\n    base = int(c.seed)\n"
            "    return bootstrap_values(s, 5, 10, 5, base)"
        ),
        "seed_via_two_names": (
            "def f(c):\n    a = c.seed\n    b = a\n    return helper(b)"
        ),
        "seed_via_lambda": (
            "def f(c):\n    g = lambda: c.seed\n    return helper(g())"
        ),
        "seed_via_tuple": (
            "def f(c):\n    a, b = c.seed, 1\n    return helper(a)"
        ),
        "seed_via_conditional": (
            "def f(c, k):\n    a = c.seed if k else 0\n    return " "helper(a)"
        ),
        "seed_arithmetic_via_name": (
            "def f(c):\n    a = c.seed\n    return a * 2"
        ),
        "getattr_seed": "def f(c):\n    return helper(getattr(c, 'seed'))",
        "numpy_alias": "import numpy as xp\nxp.random.seed(0)",
        "numpy_alias_rand": "import numpy as xp\nx = xp.random.rand(3)",
        "random_bound": "import numpy as np\nr = np.random\nr.seed(0)",
        "jax_random_bound": "import jax\nr = jax.random\nk = r.key(0)",
        "jax_random_alias": "import jax.random as jr\nk = jr.key(0)",
        "jax_random_alias_wrap": (
            "import jax.random as jr\nk = jr.wrap_key_data(d)"
        ),
        "from_jax_random_key": "from jax.random import key as K\nk = K(0)",
        "from_jax_random_prng": "from jax.random import PRNGKey as K\nk = K(0)",
        "prng_bound": "import jax\nP = jax.random.PRNGKey\nk = P(0)",
        "nested_getattr": (
            "import numpy as np\n"
            "g = getattr(getattr(np, 'random'), "
            "'default_rng')(0)"
        ),
        "getattr_random_name": (
            "def f(m):\n    return getattr(m, 'default_rng')(0)"
        ),
    }
    for name, source in bad.items():
        assert scan_bypass({name: source})[1], f"{name} was not flagged"
    good = (
        "import numpy as np\n"
        "def train(rng: np.random.Generator):\n"
        "    a = int(rng.integers(0, 2**32))\n"
        "    k = PRNGKey(a)\n"
        "    return PRNGKey(int(rng.integers(0, 2**32)))\n"
        "def make():\n    return np.random.default_rng(1)\n"
        # forms that must stay legal
        "def legal(config, seed, system):\n"
        "    rng = make_rng(config.seed, system, 'x')\n"
        "    ok = not isinstance(seed, int)\n"
        "    s = sklearn_seed(seed, 'a')\n"
        "    M(random_state=sklearn_seed(config.seed, 'b'))\n"
        "    return block_bootstrap_counted(f, 5, 10, 5, "
        "make_rng(config.seed, system, 'y'), .95)\n"
        "def legal_name(rng):\n    return bootstrap_values(f, 5, 10, 5, "
        "rng)\n"
        "def legal_indirect(config, system):\n"
        "    base = make_rng(config.seed, system, 'z')\n"
        "    n = int(config.n)\n"
        "    return bootstrap_values(f, n, 10, 5, base)\n"
        "def legal_alias(key):\n"
        "    import jax.random as jr\n"
        "    return jr.split(key)\n"
        "def legal_xp():\n    import numpy as xp\n    return "
        "xp.random.Generator\n"
    )
    sites, problems = scan_bypass({"good.py": good})
    assert problems == [] and sites == {("good.py", "make")}


def test_no_bypass_of_make_rng_in_the_package() -> None:
    """P4: ``default_rng(`` occurs only at the four allowed sites, and nothing
    else bypasses ``make_rng``.

    Also: no seed arithmetic, and every key is a draw.

    Reference: the exact allowlist of the plan (``make_rng``, the integer path
    of ``block_resample_indices``, and the two ``validation.py`` fixtures of
    DEC-0017 Q7), read from the ``ast`` of the package. Tolerance: none (set
    equality, so a new site and a lost site both fail). At least one ``PRNGKey``
    is scanned, so the key check cannot pass vacuously.
    """
    sources = _package_sources()
    sites, problems = scan_bypass(sources)
    assert sites == DEFAULT_RNG_ALLOWLIST, sites ^ DEFAULT_RNG_ALLOWLIST
    assert problems == [], problems
    assert "PRNGKey(" in sources["networks.py"]


def test_label_scan_reads_make_rng_and_paired_change_calls() -> None:
    """The label scanner lists literal labels and groups the sites that share
    them (P5 scanner).

    Reference: hand-written sources. A shared tuple is reported with both sites;
    a call with different labels is not; the tuple of ``_paired_change`` is read
    as a label; a call with a ``*labels`` argument is not listed (its callers
    are).
    """
    source = (
        "def a(s):\n    return make_rng(s, 'sys', 'x', 'y')\n"
        "def a2(s):\n    return make_rng(s, 'sys', 'x', 'y')\n"
        "def c(s):\n    return make_rng(s, 'sys', 'z')\n"
        "def d(s, labels):\n    return make_rng(s, *labels)\n"
        "def e(s):\n    return _paired_change(1, 2, s, 0.9, ('sys', 'p', "
        "f'{s:g}'), 'n')\n"
        "def f(s):\n    return _paired_change(*u, s, 0.9, ('sys', 'p', "
        "f'{s:g}'), 'n')\n"
    )
    found = scan_labels({"m.py": source})
    assert [f[1] for f in found] == ["a", "a2", "c", "e", "f"]
    assert shared_labels(found) == {
        ("sys", "x", "y"): {("m.py", "a"), ("m.py", "a2")},
        ("sys", "p", "f'{s:g}'"): {("m.py", "e"), ("m.py", "f")},
    }


def test_labels_are_shared_only_by_the_documented_pairings() -> None:
    """P5: only the documented pairings share a literal label tuple between two
    ``make_rng`` sites.

    Reference: the pairing list ``PAIRINGS`` (M4 of the mathematics check),
    written above. The observed shared tuples must equal the list exactly, with
    the same sites, so adding a pairing and losing one both fail. Tolerance:
    none.
    """
    found = scan_labels(_package_sources())
    assert len(found) >= 30, len(
        found
    )  # the scan must see the package's call sites
    assert shared_labels(found) == PAIRINGS


def _label(*keys: object) -> str:
    """Build the string that ``make_rng`` hashes (written again here,
    independent of the code).
    """
    return "|".join(str(k) for k in keys)


def string_arguments(
    sources: dict[str, str],
    callee: str,
    index: int,
) -> set[str]:
    """Collect the string literals at argument ``index`` of every call of
    ``callee``.
    """
    found = set()
    for source in sources.values():
        for node in ast.walk(ast.parse(source)):
            if (
                isinstance(node, ast.Call)
                and _callee(node) == callee
                and len(node.args) > index
            ):
                arg = node.args[index]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    found.add(arg.value)
    return found


def label_domains(sources: dict[str, str]) -> dict[str, list]:
    """Give the values each variable part of a label takes in a full-preset run.

    The values come from the configuration and from the literals at the call
    sites (the purposes of ``unit_noise`` and the labels of ``sklearn_seed``).
    """
    cfg = FULL
    rhos = sorted(
        {*cfg.noise_levels, *cfg.library_sweep_noises, cfg.core_noise}
    )
    return {
        "system": list(cfg.core_systems),
        "embed_dim": sorted({cfg.embedding_dim, *cfg.robustness_dims}),
        "delay": list(range(1, cfg.steps_per_lyapunov + 1)),
        "split": list(SPLITS),
        "purpose": sorted(string_arguments(sources, "unit_noise", 2)),
        "width": list(cfg.estimator_widths),
        "name": [*H1D_TESTED, *H1D_REPORTED],
        "rho": rhos,
        "sklearn": sorted(string_arguments(sources, "sklearn_seed", 1)),
    }


def _domain_of(expr: ast.expr, domains: dict[str, list]) -> list:
    """Return the domain of one label expression.

    An unknown expression is an error (never skipped).
    """
    text = ast.unparse(expr)
    if isinstance(expr, ast.Constant):
        return [expr.value]
    if isinstance(expr, ast.JoinedStr):
        raise TypeError("f-strings are expanded by _expand")
    if text.endswith("embed_dim"):
        return domains["embed_dim"]
    if text.endswith(".delay"):
        return domains["delay"]
    if text == "label":
        return domains["sklearn"]
    if text in domains:
        return domains[text]
    if text.endswith(("system", "spec.name")):
        return domains["system"]
    raise KeyError(
        f"no domain for the label part {text!r}: add it to label_domains "
        "(a new purpose must not be left out of the crc32 check)"
    )


F_STRING_FIELDS = {"rho": "rho", "other": "rho", "noise": "rho"}
"""The f-string fields of the label calls and the domain of each.

All are noise levels, formatted with ``:g``."""


def _expand(parts: list[ast.expr], domains: dict[str, list]) -> list[str]:
    """Return all label strings of one call site.

    They are the product of the domains of its parts.
    """
    choices = []
    for part in parts:
        if isinstance(part, ast.JoinedStr):
            variants = [""]
            for piece in part.values:
                if isinstance(piece, ast.Constant):
                    variants = [v + piece.value for v in variants]
                # A FormattedValue: only a noise level formatted with :g is
                # known.
                else:
                    assert isinstance(piece, ast.FormattedValue), ast.dump(
                        piece
                    )
                    field = ast.unparse(piece.value)
                    spec = (
                        "".join(
                            v.value if isinstance(v, ast.Constant) else "?"
                            for v in piece.format_spec.values
                        )
                        if piece.format_spec
                        else ""
                    )
                    if field not in F_STRING_FIELDS or spec != "g":
                        raise KeyError(
                            f"no domain for the f-string field "
                            f"{{{field}:{spec}}}: map it "
                            "in F_STRING_FIELDS (an unknown field "
                            "must not be expanded "
                            "over the wrong domain)"
                        )
                    values = domains[F_STRING_FIELDS[field]]
                    variants = [
                        v + format(x, "g") for v in variants for x in values
                    ]
            choices.append(variants)
        else:
            choices.append(_domain_of(part, domains))
    return [_label(*combo) for combo in itertools.product(*choices)]


def _full_preset_labels() -> list[str]:
    """List every label string that the call sites can produce in a full-preset
    run.

    The list is derived from the scan of the sources (review R3), not from a
    hand list.
    """
    sources = _package_sources()
    domains = label_domains(sources)
    labels: set[str] = set()
    for _, _, _, parts in label_templates(sources):
        labels.update(_expand(parts, domains))
    return sorted(labels)


def test_crc32_of_every_full_preset_label_is_distinct() -> None:
    """P5 (tightened by the mathematics check, review R3): distinct labels give
    distinct crc32.

    Why: a crc32 collision would give two ``make_rng`` calls the same stream
    (the seed enters the generator key next to the crc).

    Reference: ``zlib.crc32`` on the strings (independent of ``make_rng``). The
    strings come from the AST scan of every ``make_rng`` call (and
    ``_paired_change`` label tuple) of the package, each variable part expanded
    over its domain in the full preset (systems, embedding dimensions {5, 7,
    10}, delays 1 to 30, splits, widths, noise levels, the H1d names), the
    purposes of ``unit_noise`` and the ``sklearn_seed`` labels read from the
    call sites. So a new purpose, label or site is included by construction, and
    an expression with no domain fails the test. With about 2500 strings in a
    space of 2^32 the chance of a collision is about 7e-4, so a failure would be
    a real finding.
    Tolerance: none.
    """
    labels = _full_preset_labels()
    assert len(labels) > 2400, len(labels)
    for expected in (
        "lorenz63|7|construction|noise-sensitivity",
        "sklearn|regime-tree",
        "start|rossler",
        "lorenz63|oracle-pool",
        "chua|10|30|estimator|0.05|128",
        "rossler|bootstrap|V7|efficiency-0.005",
    ):
        assert expected in labels, expected
    crcs = [zlib.crc32(label.encode()) for label in labels]
    assert len(set(crcs)) == len(crcs), [
        (a, b)
        for a, b in itertools.combinations(labels, 2)
        if zlib.crc32(a.encode()) == zlib.crc32(b.encode())
    ][:3]
    seed = 20261005
    mine = make_rng(seed, "lorenz63", 7, 5, "estimator", "0.01", 64).random(4)
    ref = np.random.default_rng(
        [seed, zlib.crc32(b"lorenz63|7|5|estimator|0.01|64")]
    ).random(4)
    assert np.array_equal(mine, ref)


def test_label_expansion_flags_an_unknown_part_and_expands_f_strings() -> None:
    """The label enumeration fails loudly on an unknown part and expands
    f-strings.

    It never skips a part it has no domain for, and it expands a ``{rho:g}``
    f-string over the noise levels. Reference: hand-written calls.
    """
    sources = {
        "m.py": (
            "def f(s, ctx):\n    return make_rng(s, ctx.spec.name, 'x', "
            "mystery)\n"
        )
    }
    domains = label_domains(_package_sources())
    ((_, _, _, parts),) = label_templates(sources)
    with pytest.raises(KeyError, match="mystery"):
        _expand(parts, domains)
    ((_, _, _, parts),) = label_templates(
        {
            "m.py": (
                "def f(s, system):\n    return make_rng(s, system, "
                "f'efficiency-{rho:g}')\n"
            )
        }
    )
    for bad_field in ("f'w-{width}'", "f'w-{rho}'", "f'w-{rho:.2f}'"):
        ((_, _, _, parts_bad),) = label_templates(
            {
                "m.py": (
                    "def f(s, system):\n"
                    f"    return make_rng(s, system, {bad_field})\n"
                )
            }
        )
        with pytest.raises(KeyError, match="f-string field"):
            _expand(parts_bad, domains)
    assert sorted(_expand(parts, domains)) == sorted(
        f"{sys}|efficiency-{rho:g}"
        for sys in FULL.core_systems
        for rho in sorted(
            {*FULL.noise_levels, *FULL.library_sweep_noises, FULL.core_noise}
        )
    )


def test_the_start_label_belongs_to_draw_starts_alone() -> None:
    """The label ``"start"`` is used by ``draw_starts`` only, so no other stream
    shares it.

    Reference: the ``make_rng`` call sites found by the scanner (tested above on
    hand sources). Tolerance: none (exact list).
    """
    sites = [
        (m, f)
        for m, f, _, literal in scan_labels(_package_sources())
        if "start" in literal
    ]
    assert sites == [("data.py", "draw_starts")]
