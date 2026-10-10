---
name: freeze-checklist
description: "Prepares, but does not perform, the freeze package for the owner (LPC.PC.8). Owner-invoked only."
disable-model-invocation: true
---

Prepare the freeze checklist. The freeze itself is the owner's ledger transaction (LPC.PC.8); you only prepare it.

Open blocking defects:
!`grep -n -A2 "Blocking:\*\* yes" docs/agent/records/defects.md || echo "none"`

Queue:
!`cat docs/agent/records/work/queue.md`

Write `docs/agent/notes/<today>-freeze-checklist.md`, with each item marked done or not done and its evidence:

- [ ] All blocking defects resolved (`defects.md`).
- [ ] WU-0001 to WU-0003 and WU-0005 to WU-0008 done, or their gaps recorded as known limitations.
- [ ] Owner has reviewed the verdict and statistics code, the seed and provenance code, and new dependencies (LPC.PC.11).
- [ ] Full test suite passes. Paste the output.
- [ ] Validation gate V1–V7 passes on all three systems in the development rehearsal.
- [ ] Reproducibility tolerance declared (WU-0003).
- [ ] Precision report and sample-size decision recorded (WU-0003).
- [ ] Proposal and methods v3 exported to `docs/study/`, with its SHA-256 computed.
- [ ] `requirements.txt` pins reviewed (LPC.PC.17).
- [ ] Audit by the critical-elite-auditor with no open blockers (`/audit freeze`).

Then give the owner the commands for the freeze transaction:

- the commit hash;
- the SHA-256 of the v3 export;
- the configuration;
- the dependency lock;
- the confirmatory-seed commitment, which the owner draws with `tools/seal_confirmatory_seed.py`.

Never run `seal_confirmatory_seed.py` and never append the freeze entry yourself.
