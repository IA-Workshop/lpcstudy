---
name: refer
description: "Halts a line of work and writes the findings and justification statement for the owner (PRIME.14, LPC.AI.12–13). Use when a reserved action, missing authorization, governance conflict, unclear permission, or the stopping rule blocks progress."
argument-hint: "[WU-id] [one-line question]"
---

Halt the blocked line of work: $ARGUMENTS

1. **Make it safe.** Leave the work in a safe, recoverable state: commit or clearly mark work in progress. Take no further action on the blocked line (GUARD.3).
2. **Write the statement.** Append to the unit file:

```
## Referral: <one-line question>
Unit: WU-nnnn     Raised by: <model id>     Date: <YYYY-MM-DD>
What I was doing:  <one or two sentences>
What stopped me:   <the provision, e.g. PRIME.7, and the specific action>
Findings:          <facts, with file paths, commands and outputs>
Options:           1. <option> - effect, risk, cost
                   2. <option> - effect, risk, cost
Recommendation:    <option n, and why>
To verify the outcome: <what the owner can check afterward>
State left in:     <branch/commit; what is done and undone>
```

3. **Tell the owner and move on.** Set the unit's status to `halted` in `queue.md`. Tell the owner in at most three lines what is needed. Then continue with another queued unit that does not depend on this one (LPC.PC.24).

Never resolve the matter yourself by an equivalent route (PRIME.12, PRIME.14).
