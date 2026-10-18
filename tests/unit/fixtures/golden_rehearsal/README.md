# Golden outputs of the two rehearsal tools (WU-0003.10, plan amendment 7 G4, h1)

These files are the complete outputs (text report, `--json` file, exit code and stderr) of
`tools/rehearsal_report.py` and `tools/rehearsal_diagnostics.py` on fixed inputs, recorded **before**
`tools/rehearsal_common.py` existed. After the shared code moved into that module, the outputs are
byte-identical (`test_golden_outputs_are_byte_identical` in
`tests/unit/test_tools_rehearsal_common.py`). They are **regression guards** (the tool compared with
its own earlier output), not evidence that a number is right: correctness is tested in the two tool
test files against independent references.

## How they were produced

```
python tests/unit/golden_rehearsal.py tests/unit/fixtures/golden_rehearsal
```

with the tools as at commit `d63677d` (branch `wu/0003-rehearsal`, "Merge WU-0003.8 (.8, .8b,
.8c)"; `tools/` was unchanged in the commit that added these files, on branch `wu/0003-10-common`);
the files were later regenerated as listed under "Regenerations" at the end of this file (the
diagnostics files no longer correspond to d63677d),
development seed ids only, JAX on the CPU. Run twice: the two folders were identical (the tools are
deterministic: the diagnostics draw only through `make_rng` with its default tool seed 20261018, here
with `--resamples 100 --permutations 50`).

## The cases

| Files | Tool | Input | Exit |
| --- | --- | --- | --- |
| `report_p0_pilot`, `report_p1_pilot` | report | the committed fixtures `fixtures/rehearsal_report/p0_pilot.json`, `p1_pilot.json` (no dump) | 2 |
| `report_world` | report | the synthetic run of `test_tools_rehearsal_report.write_run` (three synthetic dumps) | 0 |
| `report_world_best_a0` | report | the same with `best_single = A0` | 0 |
| `report_world_h3c_mismatch` | report | the same with the H3c leaf off by a relative 1e-6 | 1 |
| `report_world_refused_dump` | report | the same with a dump of seed id `DEV-9` (refused, stderr only) | 2 |
| `report_world_observed` | report | the world read against `observed_file(...)` of the report tests (`--observed`) | 0 |
| `diagnostics_p0_pilot`, `diagnostics_p1_pilot` | diagnostics | the same two fixtures (no dump) | 2 |
| `diagnostics_world` | diagnostics | `build_world(rng_for("world"))` of the diagnostics tests, same stack | 2 |
| `diagnostics_world_mismatch` | diagnostics | the H3c leaf off by 1e-6 and `core/Lambda_bar` removed | 1 |
| `diagnostics_world_missing` | diagnostics | `core/E_C_A` and `core/w_star_B` removed | 2 |
| `diagnostics_world_other_stack` | diagnostics | `packages.scipy` edited and a fit leaf off by 2e-5 s | 2 |
| `diagnostics_world_no_dump` | diagnostics | the results alone, no `states/` folder | 2 |

## Normalisation (so that the files hold on another machine)

The temporary directory of a run is written `<TMP>` and the repository root `<ROOT>`. In the
diagnostics, the analysis-stack lines (python, numpy, scipy, CPU model and ISA, BLAS, SIMD,
environment) keep their status (`same`, `different`, `unusable`) and have their values replaced by
`<values>` (in the JSON, by `<value>`), because those values describe the machine. Everything else
is the tool's own text. The numbers are those of this machine's BLAS; on another stack the last
digits may differ and the golden test would then fail: that is a measured difference of the
stack, to be examined and recorded, never a reason to edit a golden file silently. A golden file
is rewritten only to record a deliberate change of output, with the reason in the unit `## Log`.

## Regenerations (append-only; each with its tool commit and reason, details in the unit `## Log`)

| Commit | Files | Tool used | What changed and why |
| --- | --- | --- | --- |
| `6b04e49` (WU-0003.8d) | `diagnostics_world.txt`, `diagnostics_world_mismatch.txt`, `diagnostics_world_missing.txt`, `diagnostics_world_other_stack.txt` (14 lines in all: 4, 2, 4, 4) | `tools/rehearsal_diagnostics.py` at `2c73b5a` (unchanged develop) | The printed H1d reproduction check line lost the clause ` = 1e-12 x max(\|leaf\|, scale ...)` (commit `53483c4`, fix round 5). Wording only: same numbers, same tolerance. The golden test went red at the develop merge `1ed9e2d` (a sibling branch added the golden test, `53483c4` changed the output) until this refresh. No `.json` file changed. |
| `dc88338` (WU-0003.8d) | the eight `diagnostics_world*` files (`.txt` and `.json`) | `tools/rehearsal_diagnostics.py` at `dc88338` | OF-3 and the block-sensitive label (owner rulings of 2026-10-17): the "D2 owner flag" wording, the new "Block-sensitive label" lines and the two new run-level lines, and the new JSON keys (`D2_any_reading_fired`, `D2_governing_reading`, `block_sensitivity`, `run_level.d2_governing`, `run_level.block_sensitive`; `D2_design_question` follows the governing reading). Everything else is byte-identical to the state after `6b04e49`. |
| WU-0003.8d fix round 1 | none | | The fix of review R1 (a point outside its interval is not computable, not a label) does not change any golden file: the golden worlds have no interval leaves, so no label row is computed there. |
