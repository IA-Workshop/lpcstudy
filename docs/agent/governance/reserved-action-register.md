# Reserved-Action Register: LPC Study

| Field | Value |
| --- | --- |
| Level | LVL3 project instrument (GUARD.4, GUARD.7, GOV.50) |
| Status | **Draft.** Adopted only by the human owner. |

Only the human owner executes a reserved action (PRIME.6). No authorization extends a reserved action to an agent. An agent that finds one necessary halts and refers (LPC.AI.12).

## Reserved classes

| Id | Class | Examples in this project | Instantiates |
| --- | --- | --- | --- |
| LPC.RAR.1 | **Irrecoverable actions:** destroying or overwriting data, records, results or source history without a verified recoverable prior state, other than an exempt class below | deleting an untracked file that is not regenerable; deleting a cited result; deleting `docs/agent/records/**` or the ledger | GUARD.5 |
| LPC.RAR.2 | **History rewrite:** any rewrite or forced overwrite of version-control history | `git commit --amend` on a committed change, `git rebase`, `git reset --hard` past a commit, `git push --force`, filter-branch | GUARD.5, PRIME.5 |
| LPC.RAR.3 | **Bulk actions:** a destructive action or remote write whose full list of targets is not enumerated and checked first, or that exceeds **1000 files or 5 GB** even when enumerated | `rm -rf runs/` without a listing; `git clean -fdx` without a dry run | GUARD.6 |
| LPC.RAR.4 | **Bulk retrieval:** downloading a dataset or collection in whole, or more than an authorization bounds | mirroring a benchmark repository; crawling a site | GUARD.8 |
| LPC.RAR.5 | **Explicit monetary transactions** | renting cloud GPUs; buying API credits; raising a spending limit | PRIME.6 |
| LPC.RAR.6 | **Hazardous actuation of physical hardware** | none in scope. The project drives no physical hardware; any attempt to connect it to hardware, for example the Chua circuit chip, is out of scope and referred. | PRIME.6, PRIME.13 |

## Exempt classes

GUARD.5 does not apply to these classes, so an agent MAY delete or overwrite them freely. Two conditions apply:

- **Enumerate first.** GUARD.6 still prevails: list the targets before deleting, and stay under the bulk threshold.
- **Never history.** No exempt class covers a rewrite of history.

| Id | Exempt class | Ground (GUARD.7) |
| --- | --- | --- |
| LPC.EXC.1 | **Temporary items:** `runs/scratch/**`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `*.egg-info/`, `build/`, `dist/`, JAX and XLA compilation caches, and files the agent created under the system temporary directory in the current session | temporary items, recorded as such by this register, that no record cites |
| LPC.EXC.2 | **Regenerable development outputs:** `runs/dev/**` whose `results.json` records its seed id, commit and configuration, provided no entry in `docs/agent/records/` or `results-manifest.md` cites it | regenerable from recorded inputs (REPRO.1) |
| LPC.EXC.3 | **Working-tree edits to tracked files** whose prior version is committed and not lost by the action | verifiably recoverable prior state |

## Revision history

| Revision | Date | Change |
| --- | --- | --- |
| 0.1 (draft) | 2026-10-10 | Proposed by Claude for adoption by the human owner. |
