---
paths:
  - "docs/agent/governance/**"
  - ".claude/**"
---

# Governance and agent-configuration rules (GOV.49, PRIME.1, PRIME.5)

- **Agents do not adopt or alter governance in force.** That includes these files and the agent's own instructions in `.claude/`.
- **Proposing a change.** Write the proposed text in `docs/agent/notes/YYYY-MM-DD-proposal-<topic>.md`. Then append a `proposal` entry with `python3 tools/ledger.py append --type proposal ...`. The owner edits and adopts.
- **The ledger** (`ledger.jsonl`) is append-only, through `tools/ledger.py` only. Agents MAY append `proposal` and `note` entries. Only the human owner appends `adoption`, `authorization`, `waiver`, `ruling`, `promotion`, `classification`, `commitment` and `revocation` entries.
- **Drift.** If `python3 tools/ledger.py status` shows a file `CHANGED since adoption`, report it. Do not rely on the changed text until the owner adopts it.
