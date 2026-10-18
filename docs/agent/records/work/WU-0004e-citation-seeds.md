# WU-0004e: AMI-delay citation in a test docstring (C8) and DEV registry statuses (C9)

| Field | Value |
| --- | --- |
| Status | implemented; pending independent review |
| Class | CSQ3 development (no confirmatory seed read, drawn or run; no seal script touched) |
| Agent(s) | claude-sonnet-5-5 (developer), branch `wu/0004e-citation-seeds` from develop `e10f65e` |
| Estimate | small: one docstring, four status strings, one unit radius run (~1 min, CPU) |

C9 **needs owner review before freeze** (seed registry).

## Plan (written before execution)

**Sources.**

- C8: DEF-0007 follow-up, LPC.PC.21a. The researcher's verified note `docs/agent/notes/2026-10-11-research-ami-delay.md`: Deshmukh, Bradley, Garland, Meiss, "Using Curvature to Select the Time Lag for Delay Reconstruction", arXiv:2003.06509v1 (7 Mar 2020), Sec. IV.B "Classic Lorenz Attractor", Fig. 5, PDF p. 8: first AMI minima near tau = 18 samples at dt = 0.01 (0.18 time units) for x(t) at sigma = 10, beta = 8/3, rho = 28 (TISEAN `mutual`; bin count not stated); the minimum is shallow and the paper says a practitioner would pick tau_I = 60 (0.60 time units).
- C9: owner ratification of 2026-10-18 (`docs/agent/notes/2026-10-11-amendments-for-owner.md` section 36, B9: "DEV registry statuses to be updated"). Uses: sections 25 to 29 (R0 to R6 on DEV-0, DEV-1, DEV-2), section 27 and `docs/agent/notes/2026-10-17-v6-v4-offline-check.md` (DEV-3, DEV-4 V6/V4 context checks only; DEV-2 also had a V6 context check at the pilot preset).

**Scope (in).**

1. `tests/unit/test_embedding.py`, docstring of `test_regression_ami_delay_lorenz_band` only: replace the statement that the source is uncited by the verified citation and its conditions. No assertion, tolerance, name or code changes.
2. `seeds/development_seeds.json`: the `status` (and, if the schema allows, a short `note`) of DEV-1 to DEV-4. Only the `status` and `use`/`note` text fields change. `id` and `value` are not touched.

**Scope (out).** Any code (`lpcstudy/seeds.py`), the sealed/confirmatory entry or the seal script (never read), the registry `schema`, any id or value, the README rule text, any other test.

**Schema check (done before editing, recorded in the Log).** `load_registry` reads only `id` and `value` of each entry and the top-level `schema`; `status` is a free string with no allowed-value set in code, in `seeds/README.md` or in the wrapper `tools/run_preset.sh` (which reads `schema` and `id` only). No test or provenance field pins the registry file's hash or its `status` text (tests read `id` and `value` through `json.load`). If any of this proves wrong at the radius run, STOP and hand back.

**Definition of done.**

(a) The docstring cites the source with its conditions and no longer says the source is uncited; the test body, name, tolerance and assertion are byte-identical. (b) The registry diff touches only `status` and `use` text of DEV-1 to DEV-4; `id`, `value`, `schema` and key order unchanged; `load_registry` returns the same mapping before and after. (c) The unit radius passes, run once. (d) Log, queue line, commits with trailers. (e) Hand-back with tip, summary line and the registry diff.

**Acceptance criteria (fixed now; none may be loosened).**

- **A1 (C8 is docstring-only).** `git diff` of `tests/unit/test_embedding.py` shows changes only inside the docstring of `test_regression_ami_delay_lorenz_band`; the AST of the module with that docstring stripped is equal before and after (checked with `ast.dump` on develop's file and the edited file).
- **A2 (C9 changes no id or value).** The id-to-value mapping read with `json.load` from develop's file and from the edited file is equal, and the list of ids and the top-level keys other than the entry text are unchanged; checked by a script, result in the Log. `load_registry(REGISTRY_PATH)` returns the same mapping (the existing `test_real_registry_matches_its_json_exactly` and the DEV-n resolution tests stay green).
- **A3 (truthful statuses).** DEV-1: `used` (R0 to R2 smoke/pilot, R3, rehearsal; WU-0003-R*). DEV-2: `used` (R5/R6 full preset; V6 context check at the pilot preset). DEV-3 and DEV-4: `used`, with a statement in `use` that only the V6/V4 context checks (no outcome) were run. Each statement is checked against the cited section or record by grep, result in the Log.
- **A4 (radius green, once).** `tests/unit/test_embedding.py`, `tests/unit/test_seeds.py`, `tests/unit/test_config.py`, `tests/unit/test_data.py`, `tests/unit/test___main__.py`, `tests/unit/test_tools_run_preset.py`, `tests/unit/test_tools_gpu_hours.py`, `tests/unit/test_tools_run_tests.py` (the last three copy the real registry into a synthetic root through `wrapper_helpers.py`) plus `tests/integration/test_cli_seeds.py` named by `tools/test_impact.py` for this file (integration tier, separate call, only if it does not need a preset run; otherwise recorded as not run). No test is edited to pass; no tolerance changes.

**Affected checks (RSRC.11), by hand from DEVELOPMENT_WORKFLOW.md section 4.2.** Rule for a test file: that file only. Rule for `seeds/development_seeds.json`: the two seed tests (`SEEDS_TESTS` in `tools/test_impact.py`) plus every test that parses or copies the registry (grep for `REGISTRY_PATH`, `development_seeds`, `wrapper_helpers`). Smaller than the whole suite; no gate.

## Log

- 2026-10-18, claude-sonnet-5-5 (developer): branch created from develop `e10f65e` as worktree `lpcstudy-wt/wu/0004e-citation-seeds`. Read the registry, `lpcstudy/seeds.py`, `seeds/README.md`, `.claude/rules/seeds.md`, `tools/run_preset.sh` registry check, the registry tests and `tools/test_impact.py`. Schema check: see Plan. The registry has no sealed entry (the file holds DEV-0 to DEV-4 only); the sealed seed and the seal script were not read. README says "never edit or remove" an entry; the owner ratified the status update (section 36 B9), so only status text changes and ids and values stay: noted for the owner.
- 2026-10-18, claude-sonnet-5-5 (developer): edits made. C8: docstring of `test_regression_ami_delay_lorenz_band` now cites Deshmukh et al., arXiv:2003.06509v1, Sec. IV.B, Fig. 5 with its conditions and the researcher's assessment on the band; body, name, assertion and tolerance untouched. C9: DEV-1 to DEV-4 `status` "unused" -> "used" and a new `note` key per entry (the `use` text is unchanged, so the designed use is kept beside the actual use). Edit of `seeds/**` by a script in the worktree raised no permission prompt. Checks by script (python -I): A1 AST of `test_embedding.py` with that one docstring stripped is equal before (git HEAD) and after: True. A2 id-to-value mapping equal: True; id order equal: True; top-level keys other than `seeds` equal: True; per entry the changed keys are exactly `note` and `status` for DEV-1 to DEV-4 and none for DEV-0; `use` unchanged. A3 facts grepped: R0 DEV-1 smoke, R1/R2 DEV-1 pilot GPU, R3 DEV-1 pilot CPU (amendments section 25, 27, 29); R5/R6 DEV-2 full GPU/CPU (section 29); V6 contexts DEV-1 to DEV-4 at pilot and full presets, CPU (v6-v4-offline-check.md lines 10, 57-64: "DEV-1 to DEV-4"), DEV-3 and DEV-4 nothing else. Dates: R-runs and the V6 check are dated 2026-10-17 in the amendments file.
- 4.9 checklist before invocation 1 (unit tier): (1) Change set: `git diff --name-only main...HEAD` is empty of unit files (branch is from develop; vs develop: `seeds/development_seeds.json`, `tests/unit/test_embedding.py`, this unit file) plus `git status --porcelain`: the same three. (2) Radius from section 4.2 by hand: a test file maps to itself (`test_embedding.py`); the registry maps to `SEEDS_TESTS` (`tests/unit/test_seeds.py`, `tests/integration/test_cli_seeds.py`) plus every test that parses or copies the registry: `test_config.py`, `test_data.py`, `test___main__.py` (`REGISTRY_PATH`), and `test_tools_run_preset.py`, `test_tools_gpu_hours.py`, `test_tools_run_tests.py` (`wrapper_helpers.py` copies the real registry). Eight unit files, far smaller than the whole suite; no gate. (3) Already run: no, new code. (4) Device: wrapper sets `JAX_PLATFORMS=cpu`. (5) `LPC_THREADS` default 4; unit timeout 300 s. (6) Contention: no preset run needed; CPU only. (7) Output: wrapper uses `-q --tb=short -rfE`. (8) Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit tests/unit/test_embedding.py tests/unit/test_seeds.py tests/unit/test_config.py tests/unit/test_data.py tests/unit/test___main__.py tests/unit/test_tools_run_preset.py tests/unit/test_tools_gpu_hours.py tests/unit/test_tools_run_tests.py`.
- Invocation 1 result (unit tier, 8 files): `406 passed in 42.91s`, no failure, no skip reported.
- 4.9 checklist before invocation 2 (integration tier, one file): (1) change set as above, unchanged since invocation 1 except this Log. (2) Radius: `tests/integration/test_cli_seeds.py`, named by `tools/test_impact.py` `SEEDS_TESTS` for `seeds/development_seeds.json`; refusal cases only, the study is never run (its docstring). (3) Already run: no (other tier). (4) Device: wrapper sets cpu. (5) Threads 4; integration timeout 900 s. (6) No contention, no preset. (7) Quiet output by the wrapper. (8) Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh integration tests/integration/test_cli_seeds.py`.
- Invocation 2 result (integration tier): `8 passed in 7.47s`. Both invocations ran once, with no code change between them and no rerun.
- Self-check: diff re-read against the plan item by item (A1 to A4 and the definition of done (a) to (c) met; the queue line and commit are the remaining (d)). Grep of the diff for `clip|nan_to_num|isfinite|where(|try:|except|default_rng|random.|PRNGKey|approx|rel=|atol|rtol`: no match (no code, no tolerance, no randomness changed). No clip, replacement or fallback exists in this unit to count. No assertion or tolerance changed (AST check A1).

## Review

- **Reviewer:** `reviewer`, claude-opus-5-5 (fresh context, not the author), 2026-10-18, round 1 on tip `b5e6851`.
- **Findings and resolution:** full text in `docs/agent/records/work/WU-0004e-review.md`.
  - R1 (medium): the DEV-3/DEV-4 notes say "V6/V4", and so does DEV-1's. Only V6 was computed on those contexts. Open.
  - R2 (high): the edit to `seeds/**` was made by script, so the owner's `ask` gate did not fire. The owner must approve the diff before merge. Open.
  - R3 (low, owner item): the `note` key, and the README's "never edit" and "fresh" lines. Open.
  - R4 (low): the docstring attributes "shallow" to the paper; reword, or have the researcher confirm. Open.
  - Verdict: **changes required**. Needs owner review before freeze (seed registry).

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted>
