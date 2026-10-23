# CONF-1 promotion close-out (2026-10-23, claude-sonnet-5-5, from existing evidence)

## What was promoted
Ledger seq 40 (`promotion`, `promoted` true, `proposal_seq` 39) promotes the run-1 official CPU result. Seq 37 and 38 are the same owner note (waivers 31 and 33: risk and expiry), entered twice; harmless. Copies in `promoted/CONF-1/`, hashes in `promoted/CONF-1.sha256`:

| File | sha256 |
|---|---|
| results.json | ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe |
| RESULTS.md | ac6507e3916a4d6e869dc03109a3a5e6cfe39f0d36c7ab185b00e8df3de6fef9 |
| report.md | 194606b05b8bd60ebf31b24c4c9ec22fc1de99709fdbd654f6609090f0d3f953 |
| report.figures/F1_primary.png, F2_secondary.png, F3_crosscheck.png | bc7c803c..., 8b504a8c..., 0b87bb9e... (full values in the .sha256 file) |
| figures/ (4 files) | listed in the .sha256 file |

The `RESULTS.md` copy hash differs from the ledger's `results_md_sha256` (`2a4c1d06...4577`, the original under `runs/confirmatory/run-1/full/`, unchanged) by two lines: a `diff` shows the copy lacks the banner `**CONFIRMATORY: UNPROMOTED**` and the blank line after it. `results.json` is byte-equal to the ledger value. The promoted report keeps the stored label "CONFIRMATORY: UNPROMOTED" in its provenance row (DEC-0043). Main is synced at d75b8be.

## Ruled limitations (carried in the report text)
- Same host, environment, actor for run-2: determinism, not independence: waiver seq 31, ruling seq 34.
- Owner code review waived; results spot-checked; DEF-0001 open: waiver seq 33. Risk and expiry: note seq 37/38.
- Retroactive authorization of the official run: seq 15, ruling seq 30.
- DEF-0022 power finding, development evidence: ruling seq 32.
- NVVUQ.22 gaps G1 to G3, sealed captions, figure map: ruling seq 36.
- Q-N two readings: seq 24 (DEC-0036). DEF-0027: iterative error not estimated.

## What remains
- WU-0019 retention and the end-of-project governance review: the owner's. The waivers of seq 31 and 33 expire at the owner code review record or that review, whichever is first.
- DEF-0001 stays open. DEC-0043 (option a figures) applied through WU-0034. m8 (v3 §9 numbering) cosmetic, frozen. Open: the dotted 5.0 line of `regret_vs_regimes.png` is unexplained, not a criterion; seq 36 reading (m-1) for the owner to correct; proposals for new intervals and sizes (DEC-0041, WU-0032).

## What may be said publicly, and what stays labeled
May be said, with the limitations above attached: the pre-registered analysis of seed CONF-1 returned the stored verdict words (supported, not supported, inconclusive, per the findings document and `RESULTS.md`), for Lorenz-63, Rössler and Chua only, from one realization of the sealed run; the regeneration reproduced every compared leaf bitwise on the same host by the same actor (determinism, not independent reproduction); the code was reviewed by agents, and the owner spot-checked results but waived code review.

Stays development-labeled, not part of the promoted result: the extension attractors (phase H, WU-0021 onward), the ensemble numbers (WU-0026), the DEF-0022 projected margin, the DEV-0 LM doubling study, and any proposed new intervals or sizes. Do not describe the result as independently reproduced, owner-reviewed code, or as covering other systems.
