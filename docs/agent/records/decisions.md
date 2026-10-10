# Decisions

Append-only record of decisions that affect a result or a contract (REPRO.7). Earlier study-design decisions, D1–D6 of 2026-10-10, are in `docs/study/decision_log_lpc.md`. A small decision MAY instead be recorded as a comment where it is implemented.

Use this format for each entry:

```
## DEC-nnnn: <title>  (YYYY-MM-DD, <actor>)
Decision:
Alternatives weighed and why rejected:
Affects:
Dissent and resolution (REPRO.8):
```

---

## DEC-0001: Development and confirmatory seeds are separated by commitment  (2026-10-10, proposed by Claude; for owner adoption with the governance)

**Decision.**

- Development runs use registered `DEV-n` master seeds.
- The confirmatory master seed is drawn by the owner at the freeze, committed by salted SHA-256 in the ledger, and supplied only at run time.

**Alternatives weighed.**

- *Reuse the pilot seed for the confirmatory run.* Rejected: its results have been seen.
- *Keep the confirmatory seed in the repository and simply promise not to use it.* Rejected: not verifiable.

**Affects:** every run; LPC.PC.7.
