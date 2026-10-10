# Governance: LPC Study

This folder is the project's governance corpus (GOV.35). The files are plain Markdown and the ledger is JSON lines; both are readable without special software.

| File | What it is | Identifiers |
| --- | --- | --- |
| `LVL0-constitution.md` | Placeholder for the ratified LVL0 constitution r1.5 (the owner pastes it in) | PRIN, PRIME, GUARD, VV, REPRO, INTPR, DSGN, SIMPL, RSRC, QA, GOV |
| `project-constitution.md` | LVL3 project constitution: scope, classification (CSQ2), proportionality, and every mechanism GOV.21 requires | LPC.PC.1–25 |
| `agent-instructions.md` | How agents work here: free, authorized and forbidden actions; the referral form | LPC.AI.1–14 |
| `reserved-action-register.md` | Reserved classes and exempt classes | LPC.RAR.1–6, LPC.EXC.1–3 |
| `authorizations.md` | Proposed standing and per-action authorizations | LPC.AUTH.1–7 |
| `threat-model.md` | What is protected, from what; what is not | LPC.TM.1–6 |
| `LVL1-profile-NVVUQ.md` | Proposed LVL1 profile for numerical verification, validation and uncertainty quantification; adopted by the custodians | NVVUQ.1–23 |
| `NVVUQ-instantiation-LPC.md` | How this project meets NVVUQ, with gaps mapped to units WU-0005 to WU-0008 | LPC.NV.1–2 |
| `ledger.jsonl` | Append-only, hash-chained record of governance transactions (GOV.36); tool: `tools/ledger.py` | entry `seq` |

**Agent configuration.** `.claude/` holds the operational form of the agent instructions:

- `CLAUDE.md`;
- `settings.json`: permission rules and the web-access hook;
- `agents/`: researcher, planner, developer, applied-mathematician, reviewer, critical-elite-auditor;
- `skills/`;
- `rules/`.

These files implement LPC.AI and LPC.AUTH and hold no authority of their own (GOV.38). Where they differ from the governance files, the governance files govern. Adopt them with the governance by adding `.claude/CLAUDE.md`, `.claude/settings.json` and the files under `.claude/agents/` to the `--files` list in step 3.

## Where each required mechanism is defined (GOV.21)

| Mechanism | Defined in |
| --- | --- |
| Work process | LPC.PC.9 |
| Stopping rule | LPC.PC.10 |
| Defect tracking | LPC.PC.14 |
| Review | LPC.PC.11 |
| Correction propagation | LPC.PC.15 |
| Incidents | LPC.PC.16 |
| Dependency management | LPC.PC.17 |
| Retention | LPC.PC.19 |
| Classification and consequence class | LPC.PC.3–6 |
| Working-notes workspace | LPC.PC.20 |
| Threat model | `threat-model.md` |
| Reserved-action register | `reserved-action-register.md` |
| Authorization mechanism | `authorizations.md` |
| Agent instructions | `agent-instructions.md` |

## Status and adoption (human owner only)

Every file here is a **draft**, proposed by Claude on 2026-10-10 (ledger entries 1 and 2). None is in force until you adopt it (GOV.41, GOV.49). Adoption takes about ten minutes:

1. **Fill the blanks:**
   - your name in `project-constitution.md`;
   - the operating-cost discipline in LPC.PC.23 and LPC.AUTH.4;
   - any LVL1 profile you select (LPC.PC.4). If you are also acting as custodian, adopt `LVL1-profile-NVVUQ.md` with its own `adoption` entry (GOV.28), and add `"profiles":["NVVUQ"]` to the classification in step 4.

   Edit anything you want to change first. Drafts are yours to amend.
2. **Paste the LVL0 r1.5 text** into `LVL0-constitution.md`.
3. **Adopt the instruments** (this records their SHA-256, so later edits show as drift in `ledger.py status`):

   ```
   python tools/ledger.py append --type adoption --actor "<your name>" --role "human owner" \
     --authority "GOV.41, GOV.50" --summary "Adopt LPC project governance r0.1" \
     --files docs/agent/governance/LVL0-constitution.md docs/agent/governance/project-constitution.md \
             docs/agent/governance/agent-instructions.md docs/agent/governance/reserved-action-register.md \
             docs/agent/governance/threat-model.md docs/agent/governance/authorizations.md \
             docs/agent/governance/NVVUQ-instantiation-LPC.md \
             .claude/CLAUDE.md .claude/settings.json .claude/agents/*.md \
             .claude/rules/*.md .claude/skills/*/SKILL.md .claude/hooks/*.py \
             ROADMAP.md DEVELOPMENT_WORKFLOW.md
   ```
4. **Record the classification:**

   ```
   python tools/ledger.py append --type classification --actor "<your name>" --role "human owner" \
     --authority "GOV.13, GOV.24" --summary "Project CSQ2; development work CSQ3; confirmatory pipeline CSQ2" \
     --data '{"project":"CSQ2","components":{"development":"CSQ3","confirmatory":"CSQ2"},"profiles":[]}'
   ```
5. **Grant the standing authorizations** you accept:

   ```
   python tools/ledger.py append --type authorization --actor "<your name>" --role "human owner" \
     --authority "PRIME.7, GUARD.10, GUARD.11" --summary "Grant LPC.AUTH.1, 2, 3, 5 until 2026-12-31" \
     --data '{"granted":["LPC.AUTH.1","LPC.AUTH.2","LPC.AUTH.3","LPC.AUTH.5"],"until":"2026-12-31"}'
   ```
6. **Commit, and check the result:**

   ```
   git add -A && git commit -m "Adopt governance r0.1"
   python tools/ledger.py status
   ```

To change an instrument later, edit it, then append an `amendment` entry with `--files` naming it.
