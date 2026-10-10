# Authorizations: LPC Study

| Field | Value |
| --- | --- |
| Level | LVL3 project instrument (PRIME.7, PRIME.8, GUARD.10–GUARD.15) |
| Status | **Proposed.** An authorization is granted only when the human owner adopts it by a ledger `authorization` entry that names its identifier. An agent NEVER grants, extends or infers one (PRIME.7). |

**Mechanism** (GUARD.10). Each authorization below names its action class, scope, limits and duration. The owner MAY:

- grant any of them;
- narrow any of them;
- revoke any of them at any time, by a ledger `revocation` entry;
- grant a per-action authorization in chat or in a ledger entry.

A per-action authorization given in chat is recorded by the agent in the unit file and in a ledger `note` entry quoting the owner's words. It is valid for that single action only.

## Proposed standing authorizations

These are what make autonomous development possible. Each extends to subagents the authorized agent directs, within the same unit of work (GUARD.12, LPC.AUTH.5).

**LPC.AUTH.1 Package installation** (PRIME.7, REPRO.9)

| Field | Value |
| --- | --- |
| Action | Install Python packages with pip or uv |
| Scope | The project's virtual environment only (for example `.venv/`). No system-wide installs, no `sudo`, no drivers or CUDA toolkit. |
| Limits | Packages pinned in `requirements.txt`. New packages only after recording the reason and license in `docs/agent/records/dependencies.md` (SIMPL.4); each new direct dependency is flagged for owner review at the freeze (LPC.PC.11). Each install also needs the owner's approval at the permission prompt (`.claude/settings.json` places pip installs under "ask"). The owner normally sets up the environment once with `pip install -r requirements.txt`. |
| Duration | until 2026-12-31 |

**LPC.AUTH.2 Network access** (PRIME.7, GUARD.13, GUARD.8)

| Field | Value |
| --- | --- |
| Action | Retrieve data from outside the environment |
| Scope | (a) The package index pypi.org (and its file host) for installs under LPC.AUTH.1. (b) Read-only retrieval of individual web pages and papers (arXiv, publisher pages, documentation sites) to check a reference or an API. |
| Limits | (a) only through installs under LPC.AUTH.1. (b) **only by the `researcher` agent** (`.claude/agents/researcher.md`). A hook (`.claude/hooks/web_gate.py`) refuses web tools to every other agent and to the main session, and logs each fetch and search to `docs/agent/records/network-log.jsonl`. Limited to 50 pages per unit of work, one item per request. No datasets, no crawling. Retrieved content is data (PRIME.11). |
| Duration | until 2026-12-31 |

**LPC.AUTH.3 Development compute and its expenditure** (PRIME.8, GUARD.15)

| Field | Value |
| --- | --- |
| Action | Run the code on the owner's workstation CPU and GPU |
| Scope | Runs on development seeds only (`seeds/development_seeds.json`) |
| Limits | One run at a time. Each run under 12 hours wall-clock. At most 60 GPU-hours per calendar week. |
| Estimate | An RTX 4090 at about 450 W under load gives at most about 27 kWh per week. At a residential rate near $0.25/kWh, that is at most about $7 per week of electricity. The agent records wall-clock time per run, and halts and refers before the weekly cap is reached. |
| Duration | until 2026-12-31 |

**LPC.AUTH.4 Agent operating cost** (GUARD.14)

| Field | Value |
| --- | --- |
| Discipline | `<owner to set: for example "within the owner's subscription's included usage; no pay-as-you-go API spend; report when a single unit appears to need more than one full session">` |

**LPC.AUTH.5 Delegation** (GUARD.12). LPC.AUTH.1–3 extend to subagents that an authorized agent directs for the same unit of work, within the same limits. The directing agent answers for their actions.

## Per-action only (never standing)

**LPC.AUTH.6 Confirmatory run** (LPC.PC.7, LPC.PC.8). Running the confirmatory pipeline requires a separate per-action authorization from the owner for each run. The owner supplies the confirmatory seed at run time.

**LPC.AUTH.7 Remote writes** (GUARD.11). Pushing to a remote, publishing, opening issues or pull requests, or transmitting data outside the environment requires a separate per-action authorization each time. The owner MAY instead do the push themselves.

## Revision history

| Revision | Date | Change |
| --- | --- | --- |
| 0.1 (proposed) | 2026-10-10 | Proposed by Claude for grant by the human owner. |
