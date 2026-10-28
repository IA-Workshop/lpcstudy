# Phase J confirmatory round (CONF-5 to CONF-9): promoted records

These are byte-equal copies of the records of the phase J confirmatory round. The promotion itself is the owner's `promotion` entry in the ledger (`docs/agent/governance/ledger.jsonl`). The hashes are in `promoted/phase-J.sha256`.

- **Labels.** The files keep the labels their tools wrote, such as "pre-registered verdicts, UNPROMOTED" in `confirm/confirm.md` and the report. The labels are not edited, so each copy keeps the hash its source has. Whether the round is promoted is recorded in the ledger.
- **Sources.**
  - The worktree `lpcstudy-wt/run/conf-j`, detached at tag `freeze-j` (c19ad486b93a2ee96d64ce069ec42fd440428211), `runs/confirmatory/`:
    - `phasej-CONF-n/phasej/` (results.json, RESULTS.md) and `phasej-CONF-n/contrib-j/` (contrib.json, contrib.md, ce.json, ce.md), copied to `CONF-n/`;
    - `phasej-confirm/`, copied to `confirm/`;
    - `phasej-confirm-regen/`, copied to `confirm-regen/`.
  - `report.md` is `docs/agent/notes/2026-10-28-phase-j-confirmatory-report.md` at develop cbdcd97, after the audit (`docs/agent/records/audits/2026-10-28-phase-j-confirmatory.md`, zero blockers).
- **Not copied; they stay in the run worktree, with hashes in report §8:**
  - the regeneration runs' `results.json` and analyses;
  - the state dumps (`phasej/states/*.npz`, about 720 MB per run);
  - the figures;
  - the run and analysis logs.

  The per-leaf regeneration comparisons are in `docs/agent/records/phase-j-regen/`.
- **What may be said** is in report §7 (pre-registration §9). The limitations of report §6 go with every verdict. Phase J does not change, confirm or replace the CONF-1 result in `promoted/CONF-1/`.
