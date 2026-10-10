"""Seed registry and confirmatory-seed guard (LPC.PC.7, NVVUQ.18).

Development runs take their master seed from ``seeds/development_seeds.json`` by
id (``DEV-n``). A confirmatory run takes its seed and salt from the environment
and is accepted only if their SHA-256 commitment equals the latest ``CONF-1``
commitment entry of the governance ledger. Every refusal is a ``SeedRefusal``
whose message names LPC.PC.7 and never contains a seed or salt value.
"""

from __future__ import annotations

import dataclasses
import hmac
import json
import re
from collections.abc import Mapping
from pathlib import Path

from .config import StudyConfig

REGISTRY_SCHEMA = "lpcstudy.seed-registry/1"
REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "seeds" / "development_seeds.json"
LEDGER_PATH = REPO_ROOT / "docs" / "agent" / "governance" / "ledger.jsonl"
SEED_LIMIT = 2 ** 64
SEED_ID_PATTERN = re.compile(r"DEV-(0|[1-9][0-9]*)")
SEED_VARIABLE = "LPC_CONF_SEED"
SALT_VARIABLE = "LPC_CONF_SALT"


class SeedRefusal(Exception):
    """A seed request that LPC.PC.7 forbids; the message never holds a seed or salt value."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"(LPC.PC.7) {reason}")
        self.reason = reason


def load_registry(path: Path) -> dict[str, int]:
    """Load and validate the development-seed registry.

    Parameters
    ----------
    path : Path
        Registry file (``seeds/development_seeds.json``).

    Returns
    -------
    dict[str, int]
        Seed id to master seed.

    Raises
    ------
    SeedRefusal
        If the file is unreadable, has another ``schema``, has an id that is not
        ``DEV-n``, repeats an id or a value, or holds a value that is not an
        ``int`` (a ``bool`` is not) in ``[0, 2**64)``.
    """
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SeedRefusal(f"seed registry {path} is unreadable ({type(exc).__name__})") from exc
    if not isinstance(document, dict) or document.get("schema") != REGISTRY_SCHEMA:
        raise SeedRefusal(f"seed registry {path} does not have schema '{REGISTRY_SCHEMA}'")
    entries = document.get("seeds")
    if not isinstance(entries, list):
        raise SeedRefusal(f"seed registry {path} has no 'seeds' list")
    registry: dict[str, int] = {}
    owner: dict[int, str] = {}
    for entry in entries:
        seed_id = entry.get("id") if isinstance(entry, dict) else None
        value = entry.get("value") if isinstance(entry, dict) else None
        if not isinstance(seed_id, str) or not SEED_ID_PATTERN.fullmatch(seed_id):
            raise SeedRefusal("seed registry holds an id that is not of the form DEV-n")
        if seed_id in registry:
            raise SeedRefusal(f"seed registry repeats the id {seed_id}")
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < SEED_LIMIT:
            raise SeedRefusal(f"seed registry value of {seed_id} is not an integer in [0, 2**64)")
        if value in owner:
            raise SeedRefusal(f"seed registry gives {seed_id} the same value as {owner[value]}")
        registry[seed_id] = value
        owner[value] = seed_id
    return registry


def resolve_dev_seed(seed_id: str, registry: Mapping[str, int]) -> int:
    """Return the master seed registered for a development id.

    Parameters
    ----------
    seed_id : str
        Id of the form ``DEV-n``.
    registry : Mapping[str, int]
        Output of ``load_registry``.

    Returns
    -------
    int
        Master seed.

    Raises
    ------
    SeedRefusal
        If ``seed_id`` is not of the form ``DEV-n`` or is not in the registry.
    """
    if not SEED_ID_PATTERN.fullmatch(seed_id):
        shown = seed_id if re.fullmatch(r"[A-Za-z]{1,8}-[0-9]{1,4}", seed_id) else "<value>"
        raise SeedRefusal(
            f"seed id {shown} is not of the form DEV-n; a raw integer seed is never accepted "
            "(a confirmatory run takes its seed from the environment, never from an argument)")
    if seed_id not in registry:
        raise SeedRefusal(f"seed id {seed_id} is not in the development registry")
    return registry[seed_id]


def check_commitment(seed: int, salt_hex: str, ledger_path: Path,
                     seed_id: str = "CONF-1") -> None:
    """Verify a seed and salt against the latest ledger commitment.

    The ledger chain is verified first. The latest ``commitment`` entry whose
    ``data.seed_id`` equals ``seed_id`` is compared, in constant time, with
    ``make_commitment(seed, salt_hex)``.

    Parameters
    ----------
    seed : int
        Master seed to check.
    salt_hex : str
        Salt as a hexadecimal string.
    ledger_path : Path
        Ledger file (``LEDGER_PATH`` in production, a ``tmp_path`` file in tests).
    seed_id : str
        Commitment identifier in ``data.seed_id``.

    Raises
    ------
    SeedRefusal
        If the ledger is missing or its chain is broken, holds no commitment for
        ``seed_id``, or the digest differs.
    """
    try:
        from tools.ledger import verify_chain
        from tools.seal_confirmatory_seed import make_commitment
    except ImportError as exc:
        raise SeedRefusal("the commitment tools (tools/ledger.py) are not importable; run from "
                          "the repository root") from exc
    try:
        text = Path(ledger_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise SeedRefusal(f"ledger {ledger_path} is unreadable ({type(exc).__name__})") from exc
    lines = [line for line in text.splitlines() if line.strip()]
    errors = verify_chain(lines)
    if errors:
        raise SeedRefusal(f"ledger chain is broken ({len(errors)} error(s)); the commitment "
                          "cannot be trusted")
    committed = None
    for line in lines:
        entry = json.loads(line)
        data = entry.get("data")
        if entry.get("type") == "commitment" and isinstance(data, dict) \
                and data.get("seed_id") == seed_id:
            committed = data.get("sha256")
    if not isinstance(committed, str):
        raise SeedRefusal(f"the ledger has no commitment entry for {seed_id}")
    if not hmac.compare_digest(committed.encode("utf-8"),
                               make_commitment(seed, salt_hex).encode("utf-8")):
        raise SeedRefusal(f"the seed and salt do not match the ledger commitment for {seed_id}")


def confirmatory_seed(environ: Mapping[str, str], ledger_path: Path) -> int:
    """Read the confirmatory seed and salt from the environment and verify them.

    Parameters
    ----------
    environ : Mapping[str, str]
        Environment holding ``LPC_CONF_SEED`` and ``LPC_CONF_SALT``.
    ledger_path : Path
        Ledger file holding the ``CONF-1`` commitment.

    Returns
    -------
    int
        The verified master seed.

    Raises
    ------
    SeedRefusal
        If a variable is missing or malformed, or the commitment check fails.
    """
    missing = [name for name in (SEED_VARIABLE, SALT_VARIABLE) if not environ.get(name)]
    if missing:
        raise SeedRefusal("a confirmatory run needs the environment variables "
                          f"{SEED_VARIABLE} and {SALT_VARIABLE}; missing: {', '.join(missing)}")
    seed_text, salt_hex = environ[SEED_VARIABLE], environ[SALT_VARIABLE]
    if not re.fullmatch(r"[0-9]+", seed_text) or int(seed_text) >= SEED_LIMIT:
        raise SeedRefusal(f"{SEED_VARIABLE} must be a decimal integer below 2**64")
    if not re.fullmatch(r"[0-9a-f]+", salt_hex):
        raise SeedRefusal(f"{SALT_VARIABLE} must be a non-empty lowercase hexadecimal string")
    seed = int(seed_text)
    check_commitment(seed, salt_hex, ledger_path)
    return seed


def with_seed(config: StudyConfig, seed_id: str, seed: int) -> StudyConfig:
    """Return ``config`` with its seed id and master seed replaced."""
    return dataclasses.replace(config, seed_id=seed_id, seed=seed)
