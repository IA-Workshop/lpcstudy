---
name: work-unit
description: "Runs one unit of work end to end under the project's work process (LPC.PC.9): plan, implement, independent review, audit, close. Use when starting or resuming a WU-nnnn unit."
argument-hint: "[WU-id]"
arguments: unit
---

Run unit **$unit** through the work process.

1. **Open.**
   - If `docs/agent/records/work/$unit-*.md` does not exist, copy `WU-template.md` to `$unit-<slug>.md` and set the status to `in progress`.
   - Read the queue entry and every document the unit cites.
2. **Plan** (skip if the plan is already written and unchanged). Delegate to the `planner` agent. The plan's acceptance criteria and tolerances are fixed from now on (VV.3).
   - If the plan involves a derivation, a numerical method, a statistical procedure or a tolerance, have the `applied-mathematician` agent check it.
   - If it needs external facts, have the `researcher` agent find them.
   - The plan's affected checks are the blast-radius set (DEVELOPMENT_WORKFLOW.md §4.2).
3. **Implement.** Delegate to the `developer` agent with the unit file path. Large units MAY be split into sequential developer tasks.
4. **Review.** Run `/independent-review $unit`.
   - Send the findings R1…Rn back to the same developer: resume it, or send it a message, asking it to address R1…Rn.
   - The re-review covers only those findings.
   - There are at most two fix rounds; after that, run `/refer $unit`.
5. **Merge gate** (main session only). Run `LPC_GATE=merge` with the unit and integration tiers, once (DEVELOPMENT_WORKFLOW.md §4.3), then merge to `main` with a merge commit.
6. **Owner checkpoint.** If the change touches verdict or statistics code, seed or provenance code, or dependencies, mark it `needs owner review before freeze` in the queue. Do not wait: continue with other units.
7. **Audit and close.** Fill `## Audit`:
   - is the definition of done met, and with what evidence (test output, commands);
   - which defects were opened in `docs/agent/records/defects.md`.

   Set the status to `done`, update `queue.md`, and commit with `WU-nnnn` in the message.
8. **Stopping rule** (LPC.PC.10). After three attempts at one failing approach, or four hours without progress, halt and run `/refer $unit`.

Keep the main context small. Delegate exploration and long outputs to the subagents, and keep only their summaries here.
