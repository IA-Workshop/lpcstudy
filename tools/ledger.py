"""Append-only, hash-chained governance ledger (GOV.36).

The ledger is ``docs/agent/governance/ledger.jsonl``: one JSON object per
line. Each entry stores the SHA-256 of the previous line, so editing,
reordering or removing an earlier entry breaks the chain and ``verify``
reports it. Entries are only ever appended (PRIME.5).

Commands
--------
append   add a transaction (adoption, authorization, waiver, ruling,
         promotion, classification, commitment, amendment, proposal, note)
verify   check the hash chain
status   compare the current SHA-256 of each governed file with the hash
         recorded at its latest adoption, and list pending proposals

This tool holds no authority of its own (GOV.38). Who may append which
transaction type is set by the project constitution, not by this code:
adoption, authorization, waiver, ruling, promotion, classification and
commitment entries are the human owner's acts (PRIME.1, GOV.50).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "agent" / "governance" / "ledger.jsonl"
TYPES = ("adoption", "authorization", "waiver", "ruling", "promotion", "classification",
         "commitment", "amendment", "proposal", "revocation", "note")
GENESIS = "0" * 64


def sha256_text(text: str) -> str:
    """Return the hexadecimal SHA-256 of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the hexadecimal SHA-256 of a file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_lines() -> list[str]:
    """Return the ledger's non-empty lines, oldest first."""
    if not LEDGER.exists():
        return []
    return [ln for ln in LEDGER.read_text(encoding="utf-8").splitlines() if ln.strip()]


def verify_chain(lines: list[str]) -> list[str]:
    """Return a list of chain errors (empty when the chain is intact).

    Parameters
    ----------
    lines : list[str]
        Ledger lines, oldest first.

    Returns
    -------
    list[str]
        One message per broken link or malformed entry.
    """
    errors, previous = [], GENESIS
    for number, line in enumerate(lines, start=1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"entry {number}: not valid JSON ({exc})")
            previous = sha256_text(line)
            continue
        if entry.get("prev_sha256") != previous:
            errors.append(f"entry {number}: prev_sha256 does not match entry {number - 1}")
        if entry.get("seq") != number:
            errors.append(f"entry {number}: seq is {entry.get('seq')}, expected {number}")
        previous = sha256_text(line)
    return errors


def append_entry(args: argparse.Namespace) -> None:
    """Append one transaction after checking the existing chain."""
    lines = read_lines()
    errors = verify_chain(lines)
    if errors:
        sys.exit("ledger chain is broken; refusing to append:\n  " + "\n  ".join(errors))
    files = {}
    for name in args.files or []:
        path = (ROOT / name).resolve()
        if not path.is_file():
            sys.exit(f"governed file not found: {name}")
        files[name] = sha256_file(path)
    entry = {
        "seq": len(lines) + 1,
        "prev_sha256": sha256_text(lines[-1]) if lines else GENESIS,
        "utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "type": args.type,
        "actor": args.actor,
        "role": args.role,
        "authority": args.authority,
        "summary": args.summary,
        "files": files,
        "data": json.loads(args.data) if args.data else {},
    }
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"appended entry {entry['seq']} ({args.type})")


def show_status() -> None:
    """Report drift of governed files from their latest adopted hash."""
    latest: dict[str, tuple[int, str]] = {}
    proposed: dict[str, int] = {}
    for line in read_lines():
        entry = json.loads(line)
        for name, digest in entry.get("files", {}).items():
            if entry["type"] in ("adoption", "amendment"):
                latest[name] = (entry["seq"], digest)
            elif entry["type"] == "proposal":
                proposed[name] = entry["seq"]
    for name in sorted(set(latest) | set(proposed)):
        path = ROOT / name
        current = sha256_file(path) if path.is_file() else "missing"
        if name in latest:
            seq, digest = latest[name]
            state = "adopted, unchanged" if current == digest else "CHANGED since adoption"
            print(f"{name}: {state} (entry {seq})")
        else:
            print(f"{name}: proposed (entry {proposed[name]}), NOT ADOPTED")


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("append", help="append a transaction")
    add.add_argument("--type", required=True, choices=TYPES)
    add.add_argument("--actor", required=True, help="person or agent (with model id)")
    add.add_argument("--role", required=True, help="e.g. human owner, agent")
    add.add_argument("--authority", default="", help="provision or ruling relied on")
    add.add_argument("--summary", required=True)
    add.add_argument("--files", nargs="*", help="governed files to hash, relative to repo root")
    add.add_argument("--data", default="", help="JSON object with transaction details")
    sub.add_parser("verify", help="check the hash chain")
    sub.add_parser("status", help="report adoption state and drift of governed files")
    args = parser.parse_args()
    if args.command == "append":
        append_entry(args)
    elif args.command == "verify":
        errors = verify_chain(read_lines())
        print("ledger chain intact" if not errors else "\n".join(errors))
        sys.exit(1 if errors else 0)
    else:
        show_status()


if __name__ == "__main__":
    main()
