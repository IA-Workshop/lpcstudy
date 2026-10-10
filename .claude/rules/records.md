---
paths:
  - "docs/agent/records/**"
---

# Records rules (PRIME.5, REPRO.5, REPRO.7)

- **Append-only.** Defects, decisions, incidents, results manifest, network log, audits and work-unit logs are append-only. Change a status by adding a dated line, never by editing or deleting an earlier entry.
- **Unit files.** Before execution, a unit file's `## Plan` changes only by an appended dated amendment that keeps the original, and after the first result is seen, only by a recorded decision (VV.3).
- **Attribution.** Every entry carries a date and its author: a person, or an agent with its model id.
- **Results.** `results-manifest.md` lists every reported or cited result, with its seed id, commit, configuration and environment.
