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

## DEC-0002: WU-0010 acceptance checks worded for what the tooling can run  (2026-10-10, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** Four acceptance criteria of ROADMAP.md §2 WU-0010 are checked in a different form from their literal wording, with no loosening (plan amendment in `docs/agent/records/work/WU-0010-test-tiers.md`, answers to Q1–Q4):

- *Q1.* The collect-only check names each tier directory (and `tests/test_core.py` until removed) instead of bare `tests`, which the test-gate hook blocks outside a gate. The conftest raises a UsageError for any test outside a tier directory.
- *Q2.* "Exactly 14 passed in `tests/unit`" becomes: exactly 14 collected from the seven moved files, and 14+k passed for the tier, where k is the number of marker tests that WU-0010.1 itself places in `tests/unit` (k = 5 after fix round 1).
- *Q3.* `git diff -M` cannot detect a 1-to-7 split as renames. The evidence is an `ast` source and AST comparison of each moved test and the shared helper against `main:tests/test_core.py` (stricter than the criterion), plus `--color-moved`, with `git diff -M --stat` recorded as is.
- *Q4.* "The module it imports first" is read as "the module it exercises" (the ROADMAP row's wording); each file's imports are ordered so its first import names the file.

**Alternatives weighed and why rejected.**

- *Run the bare-`tests` collection under `LPC_GATE`.* Rejected: a gate run for a collect-only check is out of proportion, and the hook exists to prevent exactly this.
- *Edit ROADMAP.md to match.* Rejected: the roadmap is adopted governance; an agent does not alter it (GOV.49).
- *Hold the unit for the owner before executing.* Rejected: the checks are equal or stricter, nothing is irreversible, and the owner can still override before merge.

**Affects:** WU-0010.1 to .3 only; no code under `lpcstudy/`. The reviewer (claude-opus-5-5) accepted each substitute check (R4 of the review). ROADMAP.md line 11 and the other text that still names `tests/test_core.py` as the live suite (`.claude/rules/test-discipline.md:18`, `.claude/skills/test-impact/SKILL.md:27`, DEVELOPMENT_WORKFLOW.md lines 89 and 138) go stale at the merge; the owner updates or adopts changes to those files.

**Dissent and resolution (REPRO.8):** none so far. Status: proposed; the merge to `main` waits for the owner to confirm or override.

- 2026-10-10, recorded by claude-sonnet-5-5 (main session) at the human owner's instruction: the human owner confirmed DEC-0002 as written, in the session chat ("I agree, confirmed as written"). Status: **confirmed**. This line records the owner's statement and is not itself a ledger `ruling`; the owner MAY append one.

## DEC-0003: WU-0011 blast-radius tool follows DEVELOPMENT_WORKFLOW §4.2 as written  (2026-10-10, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** `tools/test_impact.py` implements the §4.2 change classes as the adopted text states them. The planner's six questions (WU-0011 plan, `### Questions for the owner`) are answered so that the tool never selects fewer tests than §4.2 does:

- *Q1.* The core-module list is a designated constant, as §4.2 lists it. It cannot be derived from the import graph (`embedding`, `networks` and `estimation` reach more modules than `statistics` and `oracle` but are not core). Proposal for the owner, not implemented: say in §4.2 that the list is designated.
- *Q2.* **Not implemented; recommended for the owner.** A test file is not also selected when a module it imports directly changes. Consequence under §4.2 as written: a change to `systems` (a core module) does not select `test_dynamics.py` or `test_embedding.py`, which import `lpcstudy.systems`. The extra rule would only add tests (about 1 s of selection), so I recommend adopting it by a dated amendment to §4.2; until then the tool follows §4.2, and the gap is recorded in the WU-0011 log.
- *Q3.* A `description` field in the JSON fixture plus the comparison test's docstring satisfy "fixture docstring names it as the independent reference".
- *Q4.* "Leaf module" in criterion (a) means "not a core module" (§4.2).
- *Q5.* When a changed test file is under `tests/slow/` or `tests/gpu/`, criterion (g) wins: it is not selected without `--include-slow` or `--include-gpu`, and the tool prints an `excluded` line.
- *Q6.* `--run` delegates to `tools/run_tests.sh` when it exists (WU-0012.1) and otherwise sets the environment by hand. The skill's `2>/dev/null || echo` fallback hides the tool's errors; the owner may edit it (`.claude/` is not mine to change).

**Alternatives weighed and why rejected.** *Derive the core list from the graph:* every graph rule tried gives either a list unlike §4.2 or 11 core modules (integration run on almost every change). *Implement Q2 now:* it changes §4.2's behavior, which is adopted governance (GOV.49).

**Affects:** WU-0011 only. The risk in Q2 is under-selection, not over-selection.

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

## DEC-0004: WU-0001 plan: answers to the planner's questions  (2026-10-10, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** The WU-0001 plan amendment (`docs/agent/records/work/WU-0001-seed-provenance.md`, branch `wu/0001-seeds-provenance`) asks eight questions. Answers, none of which changes a verdict, a statistic or a fixed criterion except where stated:

- *Q1 (WU-0001.5).* The bitwise comparison with the baseline smoke reference removes `provenance`, `seconds`, `handling` **and `config.seed_id`**, and nothing else. `config.seed_id` is a necessary consequence of WU-0001.1; the criterion's "the unit adds nothing else" cannot hold literally. This is a change to how a fixed criterion is checked, not to what it protects: every number must still be bitwise identical.
- *Q2.* `--seed-id` defaults to `DEV-0` when omitted (CLAUDE.md: "until then, runs use DEV-0"), so `tests/integration/test_smoke_pipeline.py` stays valid.
- *Q3.* Development headers carry both the `DEVELOPMENT (DEV-n): not a hypothesis test` label and `UNPROMOTED` (LPC.PC.13).
- *Q4.* The sklearn seed-size defect is `DEF-0010`, to be fixed in WU-0002 after an owner ruling; not in WU-0001.
- *Q5.* Prefer **not** to change `tools/ledger.py`: tests point the ledger readers at a `tmp_path` ledger by monkeypatching the module-level ledger path. Only if that is impossible may the developer add an optional path argument, with its own test and the reviewer's explicit attention.
- *Q6.* Refusing a confirmatory run on a dirty tree or unknown commit is **not implemented** in WU-0001; recorded for the owner to decide before the freeze (WU-0004).
- *Q7.* The test file is `tests/unit/test___main__.py` (the name `tools/test_impact.py` looks for). When `tools/ledger.py` changes, add `test_seeds` by hand (the Q2 gap of DEC-0003). DEVELOPMENT_WORKFLOW §4.2's import-graph table needs rows for the new modules; that is an owner edit (adopted governance).
- *Q8.* The ledger path can be overridden only from Python, never by a flag or environment variable.

**Alternatives weighed.** *Hold WU-0001 until the owner answers:* rejected, since nothing here is irreversible and the owner can override before the owner review that the unit requires anyway.

**Affects:** WU-0001 only. Marked `needs owner review before freeze` (seed and provenance code).

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

## DEC-0005: WU-0012 plan: answers to the planner's questions  (2026-10-10, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** The WU-0012 plan (`docs/agent/records/work/WU-0012-wrappers.md`, branch `wu/0012-wrappers`) asks six questions. Answers:

- *Q1.* The smoke "same `results.json` as a direct invocation" check excludes the wall-clock `seconds` fields (and, once WU-0001.4 lands, its timing fields): the same reading as WU-0009.3, where the criterion itself removes them.
- *Q2.* "Calendar week" is the ISO week in UTC. A shared append-only tally in addition to the per-run `run.meta.json` files is **not** added in WU-0012; the risk (deleting `runs/` or a worktree loses hours from the count) is recorded for the owner.
- *Q3.* The XLA flag that caps CPU threads in jax 0.11.2 is **not set** in WU-0012 (an unknown `XLA_FLAGS` entry aborts XLA). Finding it needs a `researcher` retrieval; deferred, under the open question of the web-retrieval cap.
- *Q4.* Split the wrapper tests into three files named for the tools, so that `tools/test_impact.py` finds them under the §4.2 pattern: `tests/unit/test_tools_run_tests.py`, `test_tools_run_preset.py`, `test_tools_gpu_hours.py`. (This overrides the plan's single `test_tools_wrappers.py` file name; the criterion's radius names that file, so the log records the substitution.)
- *Q5.* `run.meta.json` does not record peak memory: its field list is fixed by the criterion, and peak RSS goes into the provenance block (WU-0001.4).
- *Q6.* CPU `pilot` and `full` runs (WU-0002.12) take the same lock as GPU runs, so that only one long run is active at a time. The GPU-hour tally counts only runs whose device is a GPU.

**Alternatives weighed.** *Keep one test file and add a mapping line to §4.2 and `test_impact.py`:* rejected, since §4.2 is adopted governance (an owner edit).

**Affects:** WU-0012 only. The seed check and `run.meta.json` need owner review before the freeze (planner's note).

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

## DEC-0006: Peak-RSS test tolerance in WU-0001 is derived, not tuned  (2026-10-10, proposed by claude-sonnet-5-5 (main session) on the applied-mathematician's analysis; for owner confirmation)

**Decision.** The fixed criterion for `peak_rss_bytes` is `> 0` (ROADMAP WU-0001.4). The extra bracket against the kernel's `VmHWM` in `tests/unit/test_provenance.py` uses the bound derived by the applied-mathematician (claude-opus-5-5; derivation, probes and assumptions in the `## Log` of `docs/agent/records/work/WU-0001-seed-provenance.md`):

- `peak % pagesize == 0`, exact (the kernel reports whole pages);
- `1024*before - 2*T <= peak <= 1024*after + 2*T`, where `T = 3 * online * (max(32, 2*online) - 1) * pagesize` is the worst-case error of the kernel's three per-CPU RSS counters (about 24.8 MB on this 32-CPU machine), with `online = os.sysconf("SC_NPROCESSORS_ONLN")`.

This replaces the developer's slack `ncpu*max(32, 2*ncpu)*pagesize` (about 8 MiB), which the applied-mathematician found not valid: it covers one counter, not three, and uses `os.cpu_count()`, which an environment variable can override. The new bracket is wider than the developer's, but narrower than nothing: the planner's zero-slack bracket was never true of the kernel. It still catches a KiB-for-bytes error (1024x), a 4096x error and any factor-2 error; it cannot catch a one-page additive error (the kernel's own noise is about a thousand pages).

**Alternatives weighed.** *The reviewer's ratio bracket 0.5x to 2x:* valid on this machine, but misses factor-2 errors and also depends on the counters. *Only `peak > 0`:* what the criterion requires, but it would not catch a unit error.

**Affects:** WU-0001.4's test only. Separate finding, not a decision: a child process inherits its parent's peak in `ru_maxrss` (a child of a 200 MB Python reported 218 MB against its own `VmHWM` of 11 MB), so a recorded `peak_rss_bytes` can reflect the launcher's peak. WU-0001 documents this limitation; whether to also record `VmHWM` is for the owner (it changes the provenance schema).

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

## DEC-0007: WU-0002.1 and .2 plan: answers to the planner's questions and work pulled forward  (2026-10-10, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** The plan amendment for WU-0002.1 and .2 (`docs/agent/records/work/WU-0002-methods-v2-changes.md`, branch `wu/0002-removals-ids`) depends on no owner ruling and decides no criterion, band, verdict rule or definition; it only removes and renames. Answers to its four questions (the plan's defaults):

- *Q1.* The v2 and v1 ids stored in `identifiers.py` and its v1-to-v3 key map are historical data, not live code symbols, for the .2 criterion "grep finds no live code symbol".
- *Q2.* Key names `gain_bound`, `regime_curve`, and a top-level `V7` until WU-0002.10.
- *Q3.* Criterion text stays v3 verbatim, including v3's own `N_lib`; library size elsewhere (config labels, report text, figure axes) reads `n_lib`. An agent does not respell criterion text.
- *Q4.* `gain_proxy` is kept for now (removing it is a separate, later change in a core module); no effect on the regression.

**Work pulled forward from later sub-tasks (the plan's reason: the item's only input is removed code, or a figure reads it):** H2d part (ii) is removed in .1 (WU-0002.8 would have done it); the v1 H3b (p_eff) statistic is removed in .2 and its regret-vs-K curve moves to `regime_curve` (WU-0002.8); the v1 H1a to `V7` key rename is done in .2 (WU-0002.10). Each follows the decision log. Consequence for the owner's ruling A2 in `docs/agent/notes/2026-10-10-rulings-for-owner.md`: after .2 a v3 `H3b` key exists (renamed from v1 H3c), so the ROADMAP's literal WU-0002.8 check "no `H3b` key exists anywhere in results" cannot pass until the owner adopts the changed wording ("no key for v1 H3b (p_eff)").

**Alternatives weighed.** *Hold .1 and .2 until the owner rules on the referral:* rejected, since nothing in them depends on a ruling. *Leave the pulled-forward items to .8 and .10:* rejected by the planner because the figure code and the key collisions (H1b to H1a, H3c to H3b, the old H2e) make sequential renames impossible.

**Affects:** WU-0002.1 and .2 only. Marked "needs owner review before freeze" (verdict code is touched by renames; `__main__` options and `tools/run_preset.sh` behind the seed refusal are touched by the removals).

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

## DEC-0008: Owner rulings of 2026-10-11 on the WU-0014 referral, the open defects and the confirmations  (2026-10-11, recorded by claude-sonnet-5-5 (main session) from the human owner's instruction in the session)

**Decision.** The human owner reviewed the rulings document (`docs/agent/notes/2026-10-10-rulings-for-owner.md`, on `develop`) and replied in the session: "I agree with and approve all recommendations. please proceed". The assistant had asked for an explicit word on A4(a) and (a2) when adopting everything; the reply is read as that word. **Every recommended ruling in that document is adopted**, with these values fixed (all values are the ones the document proposed). This entry is the record; the owner's edits to adopted text (ROADMAP.md, v3, Methods v2, DEVELOPMENT_WORKFLOW §4.2, `.claude/`) and the ledger entries remain the owner's acts (GOV.49, PRIME.1), listed in `docs/agent/notes/2026-10-11-amendments-for-owner.md`.

- **A1 Boundary convention.** One rule for every criterion: pass iff the interval lies inside the band; fail iff it misses the band entirely; otherwise inconclusive. Each band exactly as v3 §2 writes it (strict for H2a, H2b, H2c, H2e, H3a; closed for H1b to H1d, H2d, H3c); H1a's ±25% band is closed. Compare unrounded float64 values. A K-rule tie counts as inside.
- **A2 ROADMAP wording.** The WU-0002.8 check "no `H3b` key exists anywhere in results" is read as "no key for v1 H3b (p_eff)"; WU-0002.1's "v3 drops E5" is read as "v2 E5 (shift)"; the WU-0002.10 plan adds V7 slope-part and per-ρ tests (a strengthening).
- **A3 Verdicts.** A statistic that cannot be computed is "inconclusive", with the reason and count recorded. A statistic on a subset needs at least **50 states (10 blocks of 5)**, otherwise inconclusive. Failed bootstrap resamples are counted at the unfavourable tail, not dropped. **H3a:** pass as v3 writes it, otherwise inconclusive; **no equivalence margin is set, so H3a cannot fail** (a margin can be added by a later owner ruling). **H3b:** block bootstrap (blocks of 5, 2000 resamples, 95%) over construction states, refitting both trees, for the weight-tree importance of Λ̃ (band [0, 0.2)) and for D = imp_t(Λ̃) − max of the other coordinates' imp_t (bound > 0), with the stability fraction reported; trees use a **fixed leaf count of 8**.
- **A4 Definitions.** (a) H2a(ii) and Q-N use the **two-part treatment**: (ii-a) the partial correlation of 1{w\*(H_ref) = 0} with Λ̃ given the seeds over all test states; (ii-b) the partial correlation of logit w\*(H_ref) with Λ̃ given the seeds over states with 0 < w\* < 1; both intervals inside (−0.1, 0.1) to pass; fail if either lies entirely outside; counts of w\*=0 and w\*=1 reported; add a third part 1{w\*=1} if w\*=1 exceeds 5% of states; Q-N reports ΔR² for the interior logit and for the indicator. (a2) "Given both seeds" **residualizes on x, x², x₁x₂**. (b) The H2a(i) regime rule is restricted to **initial segments** ({1, 2} or {1, 2, 4} LT), medians and counts reported per span, bootstrap over all test states in time order with eligibility re-evaluated inside each resample; the complete-case {1, 2, 4} version is reported as a sensitivity. (c) `l2_regularization=1.0` documented. (d) the A5 tree criterion documented and flagged. (e) H3b trees use the fixed leaf count 8. (f) H3a uses the first evaluation draw (documented). (g) the E6 sign vector and seed documented. (h) H1a's reference is the **mean of the per-state 1/d estimates**, with a joint block bootstrap of the ratio (1/d_fit)/(1/d_LB); pass iff the ratio's interval lies inside [0.75, 1.25]. (i) H2c's better single forecaster is chosen on the calibration split.
- **A5 Silent in v3, specific in Methods v2.** The K rule is **calibration excess MSE within 5% of the minimum** (M2 §M7), tie inside. State spacing = max(5·min(τ_ac, 1 LT), 1 LT), block length 5. H1a applies at **both ρ**.
- **B Defects.** DEF-0010: option **B** (the raw seed when it is below 2³², a derived 32-bit value from `make_rng(seed, "sklearn", label)` otherwise; pinned by a test). DEF-0011: option **1** (keep `default_rng(0)` until the WU-0002.12 regression, then route through `make_rng(config.seed, "oracle-pool")` with the effect recorded) plus an audit of the other `default_rng` sites in WU-0002.11. DEF-0012: pass `LPC_THREADS` as `workers`, in a small unit.
- **C Confirmations.** DEC-0003 to DEC-0007 are confirmed as written. WU-0009.2: the direct run of `tests/test_core.py` is accepted as the stand-in for `tools/run_tests.sh unit`. Approved for the owner's action: amend §4.2 so a test file is also selected when a module it imports changes; lift the retrieval cap by ledger entry; a `note` entry for ledger entries 4 and 6; fill the blank constitution fields; the `.claude/` edits listed in the rulings document; and decide the C8 items (dirty-tree refusal for a confirmatory run; recording `VmHWM`) before the freeze, with the recommendation to decide them at the pre-freeze review.
- **Merge.** The owner authorizes merging `develop` into `main` (item 0 of the rulings document).

**Alternatives weighed.** Those in the rulings document and the applied-mathematician's note (`docs/agent/notes/2026-10-10-math-view-referral-rulings.md`).

**Affects:** WU-0002.3 to .13, WU-0005.4 and .5, WU-0003 (DEF-0010), and the v3 and Methods v2 texts, which must be amended to state these definitions before the freeze (WU-0004 checklist item). Hypothesis statistics changed by these rulings are listed as changed in the WU-0002.12 regression.

**Dissent and resolution (REPRO.8):** none. Status: **adopted by the owner** (in session, 2026-10-11).

- 2026-10-11, recorded by claude-sonnet-5-5: DEC-0002 was confirmed earlier (2026-10-10). DEC-0003, DEC-0004, DEC-0005, DEC-0006 and DEC-0007 are **confirmed** by the owner's approval above (status "proposed" in their own text is superseded by this line).

## DEC-0009: Researcher retrieval cap removed for the remainder of the season  (2026-10-11, recorded by claude-sonnet-5-5 (main session) from the human owner's statement in the session)

**Decision.** The human owner stated in the session: "Cap is hereby removed for the remainder of this season. Proceed with all recommendations." This is read as the owner removing the 50-pages-per-unit limit of LPC.AUTH.2(b) for the researcher agent for the rest of the season; the other limits of LPC.AUTH.2 (read-only retrieval of individual papers and pages, only by the `researcher` agent, no datasets, no crawling, retrieved content is data, every fetch logged to `docs/agent/records/network-log.jsonl`) are unchanged.

**Status of the instrument.** At the time of this entry the ledger (`docs/agent/governance/ledger.jsonl`, latest entry 6) holds **no** `authorization` or `amendment` entry for this change. Under PRIME.7 and GOV.36 the ledger entry is the owner's act; the command is in `docs/agent/notes/2026-10-11-amendments-for-owner.md` section 5. Until it is appended, the main session acts on the owner's direct statement (PRIME.11: an agent takes instructions from the human owner) and records that here. Two of the three retrievals started under this statement (a cited AMI delay for Lorenz-63; the jax XLA thread-cap flag) fit within the existing per-unit budget of fresh units (WU-0013 and WU-0012 follow-ups) and do not depend on it; the third (the Chua exponent, WU-0007) does.

**Alternatives weighed.** *Wait for the ledger entry before any retrieval:* rejected for the Chua retrieval because the owner's instruction is explicit and repeated, nothing in the record is hidden, and waiting blocks WU-0007.2 only; flagged so the owner can append the entry.

**Affects:** the researcher agent's retrievals for WU-0007, WU-0012 and WU-0013 follow-ups. The alphaXiv connectors are not in the researcher agent's tool list; adding them is an edit to `.claude/agents/researcher.md` by the owner.

**Dissent and resolution (REPRO.8):** none. Status: **owner instruction recorded; ledger entry pending (owner).**

## DEC-0010: WU-0007 Chua reference, AMI band and XLA thread cap: handling of the retrieval results  (2026-10-11, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** From the researcher retrievals started under DEC-0009 (notes in `docs/agent/notes/`):

- *Chua lambda_max (WU-0007.1, third row).* No published exponent was found for the code's parameter set (alpha = 15.6, beta = 28, m0 = -1.143, m1 = -0.714): the row stays `not found`, and Methods v2's 0.431 stays uncorroborated for that set. It is recorded as a **known limitation** (NVVUQ.13) for validation of Chua at those parameters. A proposed additional check, for the owner to approve at the WU-0007 plan: run the Benettin routine on the primary-source case (Matsumoto, Chua and Komuro memo UCB/ERL M84/73, alpha = 9, beta = 100/7, m0 = -8/7, m1 = -5/7; published exponent 0.23 per circuit time, about 0.33 per dimensionless time by a derived conversion with tau = 0.7 t, flagged derived) with a two-digit tolerance justified by the applied-mathematician. It verifies the routine and the field form, not the study's parameter set.
- *AMI delay (WU-0013 follow-up).* The `[3, 8]` step band of `test_regression_ami_delay_lorenz_band` is **kept** (not tightened). Deshmukh, Bradley, Garland and Meiss (arXiv:2003.06509, Sec. IV.B, Fig. 5) report a first AMI minimum of the Lorenz x-series near 0.18 time units (about 4.9 steps at the study's sampling interval), consistent with the code's 5 steps, but the minimum is a shallow shoulder, the deeper one is at 0.60 time units, and the estimator differs. The citation goes into the test docstring in a small follow-up.
- *XLA thread cap (WU-0012 follow-up).* The wrappers should export `PJRT_NPROC` and `NPROC` from `LPC_THREADS` (plain environment variables read by XLA's default thread-pool sizing; they cannot abort XLA), and must NOT use `intra_op_parallelism_threads` or other `XLA_FLAGS` entries (an unknown XLA flag aborts the process; the 2019 recipe is not a registered flag). Verification: a CPU-time versus wall-time and thread count on a float64 workload, per the research note. A small follow-up unit (WU-0012.4) changes the two wrappers and their tests.

**Alternatives weighed.** *Block the Chua row until the 1985 IEEE paper is retrieved:* the researcher found no route; recorded instead.

**Affects:** WU-0007 plan, `tests/unit/test_embedding.py` docstring, `tools/run_tests.sh`, `tools/run_preset.sh`.

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

## DEC-0011: WU-0002.7/.8 plan: answers to the planner's questions  (2026-10-11, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** The plan (`docs/agent/records/work/WU-0002.7-8-h2-h3.md`) asks four questions, answered with the applied-mathematician's confirmation (last dated entry of the same file):

- *O1.* The minimum of 50 states (DEC-0008 A3) is **not** applied to each regime in the H3a log-rank tests: the test does not need it, a small regime cannot produce a spurious pass (a pass needs p < 0.01 for every pair), and the rule would cost power with small A5 leaves. It applies to the full sample of each statistic and to subsets that feed a block bootstrap. Degenerate or missing pairs enter the Holm family at p = 1 (conservative).
- *O2.* A state where PLP's error is constant across draws is set to correlation 0 and counted, as for CP (stricter; the oracle draws and the proxy are shared across n_lib, so such a state's change is exactly 0).
- *O3.* Until WU-0002.9, results carry `pass` plus an `inconclusive_reason` and no `fail` key; WU-0002.9's plan must take over these keys.
- *O4.* H2d's `pass` stays on the point estimate until WU-0002.9.
- **Corrections taken from the confirmation (they tighten the plan):** `kind="stable"` for every `argsort`, tie order by regime index (DEF-0013); a bound is infinite iff the number of failed resamples is at least ceil(a·B), a = (1 − level)/2; failed resamples are placed outward on both sides for a two-sided band; the S3 test uses B = 40, not 20; the H3b synthetic tests draw x per state, repeat it across draws, and use dyadic targets (0.5, 0.25) with integer curvature weights so the zeros are exact; percentile (not basic) intervals for H3b.

**Alternatives weighed.** Applying the 50-state rule per regime: rejected on power grounds, with no effect on the pass error.

**Affects:** WU-0002.7 and .8 only; DEF-0013. Marked "needs owner review before freeze".

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

## DEC-0012: Shared bootstrap and verdict helpers: one contract for all WU-0002 lanes; seeding convention for new bootstraps  (2026-10-11, proposed by claude-sonnet-5-5 (main session) on the applied-mathematician's contract; for owner confirmation)

**Decision.**

- **One implementation of the DEC-0008 A1/A3 rules.** Three lanes planned overlapping helpers (WU-0002.4/.5, .6, .7/.8). The applied-mathematician's contract (Job 2, last entries of the Log in `docs/agent/records/work/WU-0002.4-5-h1.md`) governs: all helpers live in `lpcstudy/statistics.py`: `block_resample_indices`, `bootstrap_values` (vector statistics allowed), `percentile_interval(values, level) -> (lo, hi, n_failed)`, `BootstrapInterval` / `block_bootstrap_counted`, `interval_verdict(lo, hi, band, closed)`, `combine_verdicts`, `criterion_verdict` (the A3 guard order) and `MIN_STATES = 50`. Failed (non-finite) resamples are placed at -inf for the lower bound and +inf for the upper bound; a bound is infinite iff the number of failures is at least floor((B-1)·a)+1 with a = (1 - level)/2; there is no one-sided `unfavourable` argument (it would be anti-conservative for the opposite verdict). `block_bootstrap` is refactored onto `block_resample_indices` and stays **bitwise unchanged**. Result keys use `reason` and `n_failed_resamples`.
- **Implementing lane: WU-0002.4/.5**, as one commit group merged to `develop` first; the other lanes (.6, .7/.8) merge `develop` and reuse it, and do not write their own.
- **Seeding convention.** The existing bootstraps keep their `config.seed + salt` integer seeds unchanged (changing them would change numbers). New bootstraps introduced by WU-0002.4 to .8 take their randomness from `make_rng(config.seed, <label>)` (the project rule "randomness only via `make_rng`"); the helpers accept an integer or a `Generator`; when several parts of one criterion must share resample indices, pass the same integer or a fresh generator built with the same labels per part (a shared `Generator` would advance between calls). Whether to convert the existing integer-salt bootstraps is for the audit under DEF-0011.

**Alternatives weighed.** Each lane with its own helpers: rejected (divergent semantics, three names for one function). Converting all existing salts now: rejected (changes the regression numbers, and the pilot comparison is the anchor).

**Affects:** WU-0002.4 to .8, .9, .11; the shared helper semantics for the verdict logic. Marked "needs owner review before freeze" (statistics and verdict code).

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

## DEC-0013: WU-0002.3: the horizon of the K rule, and the two-stage grid in check (b)  (2026-10-11, proposed by claude-sonnet-5-5 (main session) on the WU-0002.3 review; for owner confirmation)

**Decision.** Two points of WU-0002.3 are **open questions for the owner** that DEC-0008 does not answer (the developer's log wrongly said the first was answered by DEC-0008 A5; the reviewer caught it; the log is corrected):

- *Horizon of the K rule.* DEC-0008 A5 fixes the quantity (calibration excess MSE within 5% of the minimum, tie inside) but neither v3 §5 nor Methods v2 §M7 names the horizon at which the excess is evaluated. The implementation evaluates it at the reference horizon H_ref (30 steps = 1 LT), as the code did before, locating the column by `horizons == reference_horizon`. Proposal: confirm H_ref, and have the owner state the horizon in v3 §5 (the amendments document lists it).
- *Check (b) of the ROADMAP row.* The row says the regime weight is checked against a brute-force minimizer "on the same grid" within 1e-6; one 10^4-point grid locates the minimizer only to about 5e-5, so the check cannot pass as worded. The unit uses a two-stage grid (a second grid of 10^4 points around the first minimum) with the 1e-6 tolerance kept, which the applied-mathematician approved as a strengthening of the check's form, not a loosening. Proposal: confirm, and amend the ROADMAP wording (amendments document, section 1).

**Alternatives weighed.** *Evaluate the K rule at every horizon and take the maximum:* not in either document and a different rule; rejected. *Keep the single grid and loosen the tolerance:* rejected (PRIME.2).

**Affects:** WU-0002.3 (merged to `develop` with these two points flagged); the K choice in every run. Marked "needs owner review before freeze".

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

- 2026-10-11 (claude-sonnet-5-5, main session; status of DEC-0010 itself is still **proposed**): update to DEC-0010 after the researcher's re-read of the Chua memo (`docs/agent/notes/2026-10-10-research-lyapunov.md`, 'Chua memo re-read'). The memo's quoted mu3 and sum of exponents are internally inconsistent with its own Jacobian, so they are NOT used. The memo case enters WU-0007.2 for **lambda_max only**: reference 0.23 per circuit time divided by 0.7 = 0.3286 per dimensionless time (conversion tau = 0.7 t confirmed from the memo's parameters and equation (1.3); a weak second source states 0.33), tolerance 10% (the mathematician's computation: combined sigma about 3.9%), with the orbit-boundedness guard (DEF-0015). Chua at the study's own parameters (alpha = 15.6, beta = 28) remains `not found`: a recorded known limitation.

## DEC-0014: WU-0002.6: the 50-state minimum applies to the Q-N reading  (2026-10-11, proposed by claude-sonnet-5-5 (main session) on the WU-0002.6 review R4; for owner confirmation)

**Decision.** The Q-N reading (interior logit w* and the indicator 1{w* = 0}) applies the 50-state minimum (`MIN_STATES`): a part with fewer than 50 states is inconclusive with the reason recorded. The developer chose this; the plan did not state it. It follows DEC-0008 A3 (subset statistics with fewer than 50 states are inconclusive) and DEC-0011 O1, and is the conservative side (it can only turn a verdict into inconclusive).

**Alternatives weighed.** No minimum for Q-N: rejected (DEC-0008 A3 names no exemption, and an R² on a handful of states is unstable).

**Affects:** WU-0002.6; v3 Q-N wording (add to the owner's amendment list, `docs/agent/notes/2026-10-11-amendments-for-owner.md` section 2). Marked "needs owner review before freeze" (verdict and statistics code).

**Dissent and resolution (REPRO.8):** none. Status: proposed.

- 2026-10-11 (claude-sonnet-5-5, main session; DEC-0010 still **proposed**): correction on the memo case's 10% tolerance, from the WU-0007.2 review R2. The 10% was proposed by the planner before any code value was computed (commit 431a482, 07:58). The applied-mathematician measured the code's lambda_max = 0.3235 afterwards (8e1dc9e, 08:06) and then confirmed the 10% from the error budget (combined sigma about 3.9%). So the 10% was confirmed after the value was seen; it was not changed after seeing it. The measured gap is -1.53% (0.323544 against 0.3286), well inside the bound. Also note: the memo row is in the test and in every RESULTS.md while DEC-0010 is unconfirmed (review R3); if the owner rejects it, the row is removed from both.

- 2026-10-11 (claude-sonnet-5-5, main session; DEC-0012 still **proposed**): ruling on result-key names, from the WU-0002.7/.8 review R1. DEC-0012 governs: every criterion result emits `verdict` ("pass", "fail" or "inconclusive"), `reason` (when inconclusive) and `n_failed_resamples`, plus `pass` as the boolean for the pass case, as the H1 lane (91c31f7) does. DEC-0011 O3's names (`inconclusive_reason`) are superseded for key names only; its content stands. H3a's `verdict` is only pass or inconclusive. The report reads these keys. Also (R7): ROADMAP line 115's expected `handling.zero_variance_corr` count sits in the result under `zero_variance_corr[rho][n_lib]` (a dict of counts); WU-0002.11 picks it up, and the amendments note section 1 records the wording change.

## DEC-0015: DEF-0014: V7 is a plumbing check; the smoke preset does not have to pass it  (2026-10-11, owner ruling relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The owner ruled in the session on 2026-10-11, in these words: "V7 is plumbing only and may be retired once superseded." The main session reads this as option 1 of the DEF-0014 referral (WU-0002.10 `## Referral`): V7 is a plumbing check, not a scientific criterion; `gate_pass` is false at smoke by design; V7 is judged at pilot size and above (WU-0002.12 on DEV-0, WU-0003 on DEV-1); and V7 may be retired (removed from the gate) once something supersedes it. Nothing is retired now: no superseding check exists, so V7 stays in the code and the gate.

**Consequences.**
- No threshold, band, sample size or preset changes (PRIME.2 stands).
- The smoke `gate_pass` of false is expected; regression comparisons at smoke exclude it or expect false; the report labels V7's smoke values as plumbing-size numbers (planned inside WU-0002.9, which edits the report's gate and verdict rows).
- WU-0002.12 must show that V7 passes at pilot size on DEV-0 with this code (the v1 pilot already did). If it fails there, that is a real finding to open and refer.
- 'Fully green' (the owner's condition for merging to `main`, 2026-10-11) is read as: V7 evaluated and passing at pilot size, not at smoke.
- Open for the owner: what 'superseded' means (which check retires V7) and whether a ledger `ruling` entry should state it. The ROADMAP's smoke wording ('smoke passes the gate') should become 'smoke lists V1 to V7' (amendments note section 1).

**Dissent and resolution (REPRO.8):** none. Status: ruled by the owner in conversation; recorded here pending the owner's ledger entry.

## DEC-0016: WU-0002.9: the overall verdict, H1c on PLP only, the gain-bound row, and gate_pass  (2026-10-11, proposed by claude-sonnet-5-5 (main session) on the planner's questions O1 to O4 and the applied-mathematician's answers; for owner confirmation)

**Decision.**
- **O1.** The overall verdict is "supported" only if all three v3 systems pass; it is "not supported" if any system fails; otherwise "inconclusive", with the missing systems listed. `required` is a fixed constant list of the three v3 systems (not `config.core_systems`), so a one-system smoke or development run can never read "supported". A system name outside `required` raises. Consequence: every smoke and development run reads inconclusive at best.
- **O2.** The gain bound (D-21(b) covariance screen, D-21(c) subset satisfying P1) is a gap with no ROADMAP row. The unit keeps a `pending` marker that names it. A ROADMAP row is to be opened by the owner (amendments note): "screen on the raw C >= 0 at every horizon, report the subset and the per-screen counts, no bar".
- **O3.** H1c is decided on PLP only (v3 section 2 says "(PLP)"); CP is reported without a verdict, as for H1b.
- **O4.** Verdicts are not conditioned on `gate_pass`; a gate failure marks that system's results provisional (v3 section 6 E0), which the report shows as "FAIL (results provisional)".
- **Error rate (for the owner, not a code change).** The intersection-union argument of v3 section 7 controls only the error of "supported". "Not supported" can be wrong with probability up to about 7.3% over three systems at 95% (and up to about 14% for H2c's two parts); this should be stated in v3 section 7.

**Alternatives weighed.** Treating missing systems as not counted: rejected (a one-system run would read "supported"). Deciding H1c on both forecasters: rejected (v3 says PLP).

**Affects:** WU-0002.9, the report's verdict rows, WU-0002.12's `compare_pilot` and WU-0008 (they read the verdict values, which become strings). Marked "needs owner review before freeze" (verdict code).

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

## DEC-0017: WU-0002.11: counting only, the split into lanes, and the answers to the planner's questions Q1 to Q7  (2026-10-11, proposed by claude-sonnet-5-5 (main session) on the planner's questions and the applied-mathematician's answers; for owner confirmation)

**Decision.**
- **Q1 (blocks .11c only).** A diverging Lyapunov orbit **refuses the run** (a flagged run would have a wrong time unit), with the WU-0007 bounds on |x| plus a finiteness check: Lorenz-63 40, Rössler 25, Chua 3, applied to the Benettin orbit and the three `build_context` trajectories; the cache is recomputed once and asserted bitwise equal. Lane .11c waits for the owner's ruling on DEF-0017 (seed-dependent start states change the same code).
- **Q2.** DEF-0012 (`workers=LPC_THREADS`) is a separate small unit. **Q3.** The Levenberg–Marquardt internal sites go to WU-0005.4.
- **Q4.** `regime_count_fallback` is renamed `empty_regime_fallback` (it now counts empty calibration regimes), and a count of the chosen K is added; the ROADMAP key wording is amended by the owner.
- **Q5.** This unit only counts: it excludes nothing and changes no number. Exclusions, moving dropped resamples to the A3 tail and failing on bound hits are WU-0002.9 or a later ruling.
- **Q6.** Rate counters are report-only. A nonzero counter that should be zero under the theorems, or a collapsed ν cap (more than about 1% of construction ν̂ replaced), marks results provisional; that rule is for the owner. A clip-sensitivity flag (3s against one tenth of the interval half-width) is reported next to each MSE- or weight-based verdict in .11b.
- **Q7.** The fixed seeds of the V2 (`validation.py:107`) and V5 (`:147`) checks stay as verification fixtures; the rest of the DEF-0011 conversions follow WU-0002.12 and need the owner's ruling (they change numbers). The shared stream `default_rng(config.seed)` across four consumers and the shared bootstrap indices across systems are not an inference problem (intersection–union and Holm are valid under any dependence); hygiene only.
- **Plan fixes D1 to D8** from the mathematician's review are part of the plan (the developer applies each before the commit that implements it).

**Alternatives weighed.** Flag-and-count a diverging orbit: rejected (wrong time unit). Convert all `default_rng` sites now: rejected (changes the pilot comparison anchor, DEC-0008 B).

**Affects:** WU-0002.11 (.11a to .11d), WU-0002.9 hand-off, WU-0005.4, DEF-0012. Marked "needs owner review before freeze".

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

- 2026-10-11 (claude-sonnet-5-5, main session; DEC-0017 still **proposed**): status of the clip-sensitivity flag of DEC-0017 Q6, from the WU-0002.11b review R5. The flag (3s against one tenth of the interval half-width, s the clipped share of the pooled second moment) is **deferred out of WU-0002.11b**: the share s and the scale per verdict (H2c, H2d, H3c, A2, A5) are undefined and it would add result leaves. Follow-up unit WU-0002.11e: the applied-mathematician defines s and the scale per verdict; the owner then rules whether nonzero should-be-zero counters and a collapsed nu cap mark results provisional. Listed as an open owner question (Q6).

## DEC-0018: WU-0006: the simulation studies: what is asserted, and the owner's open choice (Option C or K)  (2026-10-11, proposed by claude-sonnet-5-5 (main session) on the applied-mathematician's review of the WU-0006 plan; for owner decision)

**Finding.** The applied-mathematician's simulation of the real procedure (blocks of 5, B = 2000, an independent implementation matching production to 4e-16) shows the block-5 percentile intervals undercover even with independent states (coverage 0.938 to 0.947 at 95%, 0.977 to 0.981 at 98.3%; the log-normal cases lowest) and at lag-1 0.3 reach only 0.923 to 0.931 / 0.968 to 0.974. A correct implementation is therefore expected to fail about 16 to 17 of the 82 probabilistic assertions against the ROADMAP's bounds (about 1 to 2 at lag-1 0, about 11 at lag-1 0.3). These are real properties of the method at the pilot sample sizes, not code defects. The planner's "5 to 10% chance of one spurious failure" is replaced by this. The per-state MSE tails may be heavier than the plan's log-normal sigma = 1 (a dynamics proxy gives a log-SD of 1.7 to 2.0): at sigma = 1.5 to 2 the H2c, H2d and H3c-type intervals cover only 0.920 to 0.933 at 95% even with independent states. This bears on how much weight the study's interval-versus-band verdicts can carry (WU-0008, the owner).

**Decision (main session, proposed).**
- Implement everything the mathematician recommends as a *tightening*: integer-count bounds, corrections (N2 bound 0.045946; the H1 lag-1 standard error is sqrt((1 - phi^2)/N)), A4 (verdict equality) per replication, a pre-registered consistency range for each observed count from the reference (70 ranges, family-wise false alarm at most 3.5%; this is the defect test), the added characterization rows C2h and C4h (sigma = 1.5 and 2), the generator specifications of the note, the C7 and C6 choices.
- **The ROADMAP-bound assertions stay asserted** (Option K) behind one constant `ASSERT_ROADMAP_BOUNDS = True` until the owner rules; their outcomes are always computed and recorded in the unit Log and for WU-0008. Neither bound, level nor R is changed.
- **Open for the owner: Option C or K.** C: the ROADMAP-bound rows become labelled characterization rows (outcome reported, not asserted; the consistency ranges are the defect test); K: keep the assertions, about 13 predicted DEFs that recur at every gate. The mathematician recommends C, decided before the run. Changing the status of a ROADMAP criterion is the owner's (LPC.AI.12).
- **O5 (null delta-R2).** The interval covers the conditional gain of the two fitted models with training held fixed, so the ROADMAP criterion N1 ('interval contains 0') is predicted to fail (an estimand mismatch). N2 (false 'distinct' rate) and N3 (coverage of the conditional gain) are the right criteria. Proposed: N2 and N3 are asserted; N1 is computed and reported, and asserted only under `ASSERT_ROADMAP_BOUNDS`. The owner amends the ROADMAP row if C is chosen.
- **O1.** The spawned worker pool is approved (single-thread workers inside the LPC_THREADS = 4 budget; thread variables set to 1 in the parent environment before the pool is created; B = 500 is not an equivalent fallback). **O2.** The test files are named so that `test_impact` selects them: `test_statistics_coverage.py`, `test_analysis_coverage.py`, `test_analysis_logrank_size.py`, `test_analysis_null_delta_r2.py`. **O3.** 3000 training / 1000 test states for the delta-R2 study with the pool. **O4.** The per-state series' lag-1 autocorrelation cannot be measured from the existing development outputs (no per-state dump); a proxy gives -0.06 to +0.13, so lag-1 0.3 is very likely a stress case; add a per-state dump to the DEV-1 pilot in WU-0003.

**Alternatives weighed.** Loosening the ROADMAP bounds to pass: rejected (PRIME.2). Reducing R or B to fit the time budget: rejected (it would loosen the bounds).

**Affects:** WU-0006.1 to .4, WU-0008 (interval labels and the uncertainty budget), WU-0003 (per-state dump), and the owner's reading of every interval-versus-band verdict. Marked "needs owner review before freeze".

**Dissent and resolution (REPRO.8):** none so far. Status: proposed; the Option C or K choice is the owner's.

## DEC-0019: WU-0002.12: the fallback criterion for the DEV-0 pilot regression, the re-reference run, and the run's resources  (2026-10-11, owner approval relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The owner approved, in the session on 2026-10-11 ("All 3 are approved"), the three items put to them:
1. **The criterion.** The final fallback criterion text of the applied-mathematician's review, in `docs/agent/records/work/WU-0002.12-pilot-regression.md` (branch `wu/0002-12-pilot-regression`, section 'Proposed fallback criterion: final text for the owner (O1)', commit a3783d5): branch selection B (bitwise), N (context bitwise equal, networks differ: N1 to N5) or D (any other context difference: D1 to D3), with R1 and R4 to R7 in every branch and the divergence-locus table. The text is in force from this entry; changing it after the run's result is seen is a new owner decision.
2. **The extra run.** Branch D1: if the first run lands in branch D, run tag `v1-baseline` at the pilot preset on DEV-0 on the same machine with the same `LPC_THREADS`, on CPU under the lock (about one more CPU pilot), and apply branches B then N against that local run.
3. **Resources.** `LPC_THREADS=8`, and the wrapper may take the GPU lock for the CPU pilot run (DEC-0005 Q6).

**Conditions the main session applies (from the plan and the review):** the run starts with an empty cache directory (the cached `lyapunov.json` would hide a platform difference), from a clean detached worktree whose tree no agent writes to during the run; the order of work puts the DEF-0017 seed-dependent start states and the WU-0002.11d seed conversions strictly after this run (they change every number).

**Affects:** WU-0002.12, WU-0004.3 (the regression is its evidence). Marked "needs owner review before freeze".

**Dissent and resolution (REPRO.8):** none. Status: approved by the owner in conversation; recorded here pending the owner's ledger entry.

- 2026-10-11 (claude-sonnet-5-5, main session; DEC-0018 still **proposed**; **needs owner review before freeze**): update to DEC-0018 from the WU-0006 review R4. (1) After the delta-R2 reference was replaced (bd21e76, addendum A9: 1000 replications at the study's 3000/1000 sizes; the earlier 200-replication N2/N3 failure probabilities 0.25 and 0.42 were retracted as noise), the nominal N2 and N3 bounds (N2 <= 22/500, N3 >= 461/500) moved **under the `ASSERT_ROADMAP_BOUNDS` switch** with the A1 to A3 rows (default True, so nothing is weaker today); this supersedes the sentence of O5 that N2 and N3 are always asserted. (2) The 12 consistency ranges of A9 are the always-asserted defect test for the delta-R2 rows (family-wise false alarm at most 0.6%). (3) The A9 reference was fixed after run 2 had shown the counts (VV.3): its derivation uses reference replications only and the run-7 re-evaluation reproduced run 2's counts (same design and seeds), so its passing is a regression guard, not independent confirmation. Under Option C the always-asserted rows are therefore: the 70 + 12 consistency ranges, the exact checks (identity with the production functions, verdict equality, bitwise refit, zero failed resamples) and the log-rank and delta-R2 consistency ranges; the nominal-bound rows (A1 to A3, L, N1 to N3) become recorded characterization rows.

## DEC-0020: WU-0002.12: how the main session reads four points of the approved pilot-regression criterion (DEC-0019)  (2026-10-11, proposed by claude-sonnet-5-5 (main session) on the developer's readings and the reviewer's confirmation; for owner confirmation)

**Decision.** Where DEC-0019's text needed a reading to be implemented, the tool uses these (each confirmed by the independent review of `tools/compare_pilot.py`, WU-0002.12 `## Review`):
1. **K and `best_single` are not chain-head events** of N3, although they are discrete quantities: they change by design (WU-0002.3, WU-0002.8), so every leaf that depends on K is classified `changed`, and the dependence on `best_single` goes through the rule condition (`when`). Stricter than the literal text (it licenses fewer leaves).
2. **The `fixture` chain** (the V1, V2, V5 and V6 leaves: no trained network) counts as network-independent (compared bitwise in N1).
3. **The cache check:** `lyapunov.json` is written during the run, so the results alone cannot show whether it pre-existed; the tool takes `--cache-preexisted no` from the launch record. For the DEV-0 run started on commit a5cd75b into `runs/dev/wu0002-12/pilot`, the evidence is the directory timestamps (`runs/`, `runs/dev/`, `runs/dev/wu0002-12/` created at 13:33:52, six seconds after the commit time, in a freshly created worktree, and the wrapper refuses an existing `run.meta.json`).
4. **D1 compares through the v1-named rule table** (the local `v1-baseline` run has the v1 schema and no `provenance`).
- **Open (not decided):** D3's `SE_new` arm (the arm facing away from the pilot estimate, as implemented, or the arm facing the other estimate); relevant only with `--no-reference`; for the mathematician and the owner.
- **Limit noted:** the N5 `curvature_floor` attribution reads the core cell's sum over the three splits (no per-split counter exists); the mathematician to confirm this is acceptable for AM3 H3.

**Affects:** WU-0002.12 step 3, WU-0004.3. Marked "needs owner review before freeze".

**Dissent and resolution (REPRO.8):** none. Status: proposed.

## DEC-0021: WU-0008: defaults for the planner's questions O1 to O6 (declaration table, ninth budget row, constants, figures, secondaries, slow nodes)  (2026-10-11, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision (defaults, so the work can proceed; none is irreversible).**
- **O1.** The QoI declaration table has **14 rows** (the gain bound included, as NVVUQ.22 asks), not the ROADMAP's 13; the ROADMAP row is amended by the owner.
- **O2.** The budget has the **ninth row 'Interval procedure (coverage)'** (DEF-0020); adding it to the `uq-budget` skill is the owner's edit.
- **O3.** The WU-0006 coverage numbers are **constants with provenance** in `budget.COVERAGE_WU0006` (the run-2 analysis tables were overwritten, WU-0006 R2), with a unit test that parses the WU-0006 Log table as the independent reference.
- **O4.** **Captions only** for figures (no interval drawn; LPC.PC.1).
- **O5.** Budget tables for the secondaries and Q-N: **later** (a follow-up), the ROADMAP limits .1 to the five primaries.
- **O6.** For the endpoint-error change (.2a): the unit tiers of `statistics` and its dependants, the integration tier, and the slow `test_exact_checks` nodes for C4, C7 and C8 at both phi, once.

**Affects:** WU-0008. Marked "needs owner review before freeze". **Status:** proposed.

## DEC-0022: WU-0002.12: the local v1 re-reference becomes the new baseline; N1 kept as written; the platform record is added  (2026-10-11, owner instructions relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The owner instructed, in the session on 2026-10-11, in these words: "Redo the v1 baseline and make that the new baseline. The old platform is not available. N1 I agree with the recommendation. Explain N3. Do 4, since this is our reference platform." Recorded as:
1. **New baseline.** The v1 code (tag `v1-baseline`, commit f01360d) is re-run at the pilot preset on DEV-0 on this host (CPU, `LPC_THREADS=8`, same wrapper settings as the v3 pilot run) and its results become the regression baseline of this platform (the 'Pilot v1' row of the results manifest gets a dated line, the original pilot file is kept unmodified as the historical record). The v3 run (commit a5cd75b) is compared against it with branches B and N of DEC-0019, which also settles N1 and N3. The old platform is unavailable, so the original v1 pilot is no longer a bitwise target.
2. **N1** is kept as written (the mathematician's recommendation); any cross-host tolerance is fixed before the results it applies to exist (WU-0003.4, WU-0016.3); the 69 differing leaves are DEF-0024.
3. **N3** is explained to the owner (the licensing scope, the weakness found by the mathematician); a decision on its scope is pending the owner's reading of the explanation.
4. **Item 4 (the platform record)**: add a digest of the whitening matrices W and U to `context` and record the CPU model and the BLAS kernel in the provenance block, as a unit (WU-0001.6) with planner, mathematician, developer and independent review; marked "needs owner review before freeze" (provenance code).

**Affects:** WU-0002.12, WU-0004.3, WU-0001.6 (new), WU-0003.4, WU-0016.3. **Status:** owner instruction; recorded pending the owner's ledger entry.

## DEC-0023: WU-0001.6 (platform record): defaults for the planner's questions O1 to O3  (2026-10-11, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision (defaults).** **O1:** the provenance schema is bumped to `lpcstudy.provenance/2` (the top-level key set changes; only `test_provenance.py` pins the string; a `/2` block distinguishes a never-recorded platform, as in the a5cd75b pilot, from a failed probe). **O2:** the unit keeps the name WU-0001.6 given in DEC-0022; ROADMAP section 2 already uses WU-0001.6 for the WU-0001 review sub-task (done), so the owner appends a ROADMAP line naming this unit WU-0001.6b or renumbers (amendments note). **O3:** the local v1 re-run has no provenance block (v1 code), so the main session appends this host's probe output (CPU model, BLAS kernels, package versions) to the manifest's dated line for the new baseline. **F1** (once both sides of a comparison carry digests, DEC-0019's literal 'any context difference means branch D' would send a digest difference to D) needs an owner ruling before such a comparison exists (WU-0003.4, a cross-host regeneration).

**Affects:** WU-0001.6a/b. Marked "needs owner review before freeze" (provenance code). **Status:** proposed.

## DEC-0024: WU-0008: the budget design (M1 to M9) and two points for the owner  (2026-10-11, proposed by claude-sonnet-5-5 (main session) on the applied-mathematician's design; for owner confirmation)

**Decision.** The mathematician's design (WU-0008 Log, block 'WU-0008 mathematician design (M1-M9)', commit 28dfbd1) is accepted as the plan for WU-0008.1 and .2: its amendments are tightenings (E1 tolerance 3% to 2%; E2 replaced by 'the median over the 100 bootstraps within a factor of 1.4 of the reference SD, per endpoint', because the planned single-SE test would fail a correct helper with probability 0.13; E3 failed-resample case F = 13 gives None and F = 12 finite; the coverage constants use the WU-0006 reference rates (SE <= 0.0013) with the run-2 counts beside them; row and flag wording; two sentences under every table: results are conditional on one trajectory, library and network realization, and H3c is conditional on the fitted A4 and A5). Row decisions: oracle draws (M3) state the finite-M bias and its direction per QoI; LM row (M4) 'not estimated' even after WU-0005.4 (the residual bounds the error in observation space only, cond(J'J) about 1e7), with each primary's label stating its iterative error is unverified; round-off row (M5) 1e-4 times max(|lo|, |hi|), from the DEV-0 against v1 cross-host comparison; discretization (M6) 0 by LPC.NV.1 with V6 printed; interval procedure (M7) from WU-0006 with H2b(i) mapped to C8; proxy row (M8) 0 for H2a and H2b, 'not estimated' for H3c; the 10% rule is strict (M9).

**For the owner.**
1. **Estimator convention.** Whether to adopt a convention like LPC.NV.1 for the estimator ('PLP is the fixed 15-iteration LM'), which would make the LM row 0 by definition; otherwise an LM iteration-doubling study (15 to 30) is the way to size it.
2. **The Chua pilot H2a(i) fail is not robust to the finite-M bias bound.** The mathematician's indicative worst-case bound for the finite-M (oracle draws) bias in the H2a(i) median range is 0.86 of the V4 median half-width, i.e. 43 to 86% of the interval half-width on the DEV-0 pilot: the Chua pilot's fail does not survive it (a pass is not certified either). This is a development-run observation (DEV-0, not a hypothesis test); it bears on how many oracle draws M the full preset needs and on whether H2a(i) should be reported with that bias.

**Follow-ups proposed:** V4 signed mean deviation and a run at 1, 2 and 4 LT; a split-half check of logit-weight noise in WU-0003; the LM iteration-doubling study; a direct cross-host check of the primaries in WU-0003.4.

**Affects:** WU-0008, WU-0003 (M for the full preset). Marked "needs owner review before freeze". **Status:** proposed.

## DEC-0025: WU-0005.4: the mathematician's corrections accepted; three scope questions (D1 to D3) with defaults  (2026-10-11, proposed by claude-sonnet-5-5 (main session) on the applied-mathematician's check, commit 9b4ab35 on `wu/0005-4-lm-diagnostics`; for owner confirmation)

**Decision (accepted as the plan, before any code exists, VV.3).** The corrections of the 'Mathematics check' section: the residual is reported as c and c/rho^2 (first order chi-square with 4 degrees of freedom; RMS, if printed, is sqrt(c/(D-m))/rho); the L2 non-increase tolerance is replaced by |c_k - J(u_k)| <= eta(2 sqrt(J) + eta) with eta = 1e-12 max(1, ||X||_inf), perturbation norm 0.01, refine_steps = 15 explicit (the plan's relative 1e-12 is not a valid round-off bound as J falls to about 1e-31); M3 final residual <= D eta^2 with a test target built through the same `step` object, tau <= 5, normalized X, at least 8 states; the p95 uses `method="inverted_cdf"` (the linear quantile returns NaN when the order statistic is finite); `median_iterations` is documented as including round-off null-step accepts; the NaN stub is `lambda s: s * jnp.nan`; L4 has at least 4 rows started at u_true plus one call on the NaN-stub estimator; the trace variant is built from the same `body` closure; refine_steps = 0 has a defined diagnostics value. WU-0003.4 gets two tolerance tiers (1e-8 relative if the network weights are bitwise equal; distribution-free 99% order-statistic bands otherwise). Nothing is loosened: the replacements are tighter or correct an invalid bound.

**Scope questions, with defaults (all owner-confirmable).**
- **D1** (integer flag `lm_late_progress`: an accepted step in the last 3 iterations that lowers the cost by more than 1e-6 relative). Default: **include**, as an additive, report-only integer, with no float added to the carry; kept only if the estimates and all existing leaves stay bitwise unchanged, otherwise dropped and reported.
- **D2** (a 15-against-30 iteration study on DEV-0 smoke cells, the 'LM iteration-doubling study' of DEC-0024). Default: **not started now**; listed as a follow-up unit after the pilot regression closes (it needs CPU and a fixed protocol). Until then the LM row in WU-0008 stays 'not estimated' (DEC-0024).
- **D3** (whether the unit's O3 measures both wrong-basin and still-unconverged estimates, using c/rho^2 > 18.47, the chi-square 0.999 quantile). Default: **report it, not decide on it**: the fraction above 18.47 is printed as a diagnostic with no gate or verdict role, since v3 section 4 covers about 2% wrong-basin estimates but not estimates unconverged at the budget; whether v3 should say so is the owner's.

**Finding for the owner.** In test configurations, 2 to 13% of estimates were still moving by more than 10% of their error at iteration 15 (worst in whitened coordinates with large start errors). The production rate is unknown, and nothing in the unit measures it (the unit meets NVVUQ.10 literally, not NVVUQ.9). It bears on the estimator-convention point of DEC-0024.

**Affects:** WU-0005.4, WU-0008 (LM row), WU-0003.4. Marked "needs owner review before freeze". **Status:** proposed.

## DEC-0024 addendum A1: WU-0008 wording amendments from review round 1 (2026-10-11, recorded by claude-sonnet-5-5 (main session) from the applied-mathematician's reply; for owner confirmation)

Amends M1 (a), M7 and the row-9 text of the accepted design (DEC-0024). The mathematician's finding: decision (a) of M1, 'the finite-M variance is inside every primary interval', is false for H3c (the test-state M draws do not enter the H3c quantity; the fit-stage M-draw noise is conditioned on). It holds, with the finite-M bias outside, for the other four.

**Row 1 'Included' cells (each at most 140 characters).**
- H2a(i): `variance: yes (states resampled with their M-draw w*; eligibility redone in each resample; asymptotic for a median); finite-M bias: no`
- H2a(ii), all parts: `variance: yes in every part (target, domain and seed controls resampled with the states; asymptotic); finite-M bias: no` (caveat in the notes: whether the 'one' part is added at all is decided once on the full sample and is not resampled)
- H2b(i): `variance: yes (mean of per-state Spearman values, each from that state's own draws); finite-M bias: no`
- H2b(ii): `variance: yes (mean of per-state paired changes; same unit draws at both N_lib); finite-M clip-boundary bias: no`
- H3c: `no: test-state M draws do not enter the QoI; fit-stage M-draw noise (A4 proxies; A5 tree, leaf weights, K) is conditioned on`

**Row 9 (DEF-0020).** `DEF-0020: Option C or K (DEC-0018; owner, pending; K in force by default via ASSERT_ROADMAP_BOUNDS = True) decides only whether the WU-0006 ROADMAP-bound coverage rows stay asserted (K) or become recorded characterization rows with the consistency ranges as the defect test (C); neither changes a bound, level or R. Whether the study widens its intervals or uses another procedure (longer block, studentized, BCa) is a separate, undecided design question for the owner and the applied-mathematician.` The widening sentence cites the uq-budget rule ('widen the interval or refine') only: neither DEF-0020 nor DEC-0018 decides widening.

**M7 constants.** Reference rates: scratch seed 20261011 (`m2_coverage.py`; `m7b.py` only transcribes them); run-2 counts: seed 6006 (`make_rng(6006, "wu0006", ...)`); neither registered. R_ref (98.3% column): C1, C4, C8 at both phi: 40000; C3 and C7: 20000 (C7's pooled 60000 applies to the C7 verdict counts only; the coverage constants 0.9794 and 0.9762 are the 20000 values); C4h1.5 and C4h2 (c 0.8): 20000. The range '10^4 to 4 10^4' belongs to C6, which no QoI uses; the cases used span 2 10^4 to 4 10^4.

**Status:** proposed, with DEC-0024.

## DEC-0026: The owner ratifies the recommendations on the table; scope, what stays open, and the order of work  (2026-10-12, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling`/`adoption` entries are the owner's to append)

**Decision.** After the second merge gate (tip a74d6b0: unit 902, integration 11, `GATE-2026-10-11-develop-2.md`) and a restatement of the study's goal, the owner instructed, in the session on 2026-10-12, in these words: "Ok good, please proceed with all recommendations, which are hereby ratified". The main session reads 'all recommendations' as **every item for which a recommendation or a default is written in the records** (listed below), and nothing for which no recommendation exists; those stay open and are listed again. The ratification is recorded here, not as a ledger entry (GOV.49: ledger entries and edits to ROADMAP.md, v3, Methods v2, DEVELOPMENT_WORKFLOW.md and `.claude/` are the owner's; drafts are in the amendments note, sections 1 to 14).

**Ratified (status changes from 'proposed' to 'owner-ratified, 2026-10-12, in chat'):**
1. The defaults and answers of DEC-0002 to DEC-0014, DEC-0016 to DEC-0021, DEC-0023, DEC-0024 (design M1 to M9 and addendum A1), DEC-0025 (D1 include; D2 follow-up study; D3 diagnostic only); DEC-0015, DEC-0019, DEC-0022 were already owner decisions. DEC-0020's four readings of the regression criterion stand.
2. **DEC-0018, Option C** (the mathematician's recommendation, decided before the WU-0006 run): the ROADMAP-bound coverage rows of WU-0006 become labelled characterization rows (outcome reported, not asserted; the pre-registered consistency ranges stay asserted and are the defect test); `ASSERT_ROADMAP_BOUNDS` is set to False. N2 and N3 are the criteria of the null delta-R2 study and N1 is reported (DEF-0021; the ROADMAP row amendment is the owner's edit). No bound, level, R or B is changed (PRIME.2).
3. **DEF-0017:** seed-dependent start states (the mathematician's recommendation: start points drawn with `make_rng(seed, "start", system)` near the attractor, burn-in unchanged) and **DEC-0017 Q1:** a diverging Lyapunov orbit refuses the run (bounds Lorenz-63 40, Rössler 25, Chua 3; cache recomputed once and asserted bitwise equal). WU-0002.11c goes first; the start-state change follows as its own unit (planner, mathematician, developer, independent review) and, because it changes every number, ends with a regenerated pilot that becomes the next reference (compare against the 2026-10-11 local baseline with the DEC-0019/0020 criterion).
4. **DEC-0017 Q7 / WU-0002.11d:** the remaining `default_rng` conversions to `make_rng` are done together with the start-state change (one numbers-changing step, one new reference), not separately.
5. **DEF-0019:** the WU-0002.9b fix (H2b(i) uses the counted bootstrap) is confirmed.
6. **DEF-0025:** the robustness filter becomes `d > spec.dim`.
7. **DEF-0016:** WU-0011.5 (the direct-import rule and the scan-the-source rule in `tools/test_impact.py`, with regression tests and the fixture) is done; the stale-identifier test (`test_no_stale_identifier_in_the_package`) is amended to match whole tokens only, with cases that '20261011T165447Z' is not flagged and a standalone 'T1' still is (a false-positive fix, not a loosening: PRIME.2 checked by a case that fails on the old and new regex for a real stale id); the WU-0008 text then restores the exact log filename.
8. **WU-0002.11e (clip sensitivity):** the mathematician's recommendations OD1 (doubling the clip to 20 sigma_x as the definition), OD2 (flag when 10 |Delta_T| exceeds the half-width of the verdict's own interval, or the verdict at 20 sigma_x differs), OD3 (scope: MSE- and weight-based verdicts, with Q-N and H3b as counts only), OD4, OD5, OD6 (a fired flag never marks results provisional), OD7 (no flag on robustness variants); the unit is implemented. OD8 (a ROADMAP row) is the owner's edit.
9. **DEC-0024 point 1 (estimator convention)** is **not** ratified as a convention (no recommendation was made): the **LM iteration-doubling study (15 against 30)** is started (WU-0005.6, DEC-0025 D2) and the LM row of the budget stays 'not estimated' until it reports.
10. The next unit planned is the **WU-0003 rehearsal on DEV-1** (the recommendation of the 2026-10-11 closing report): planning first, with the per-state dump, cross-host tolerances (fixed before the results exist) and the dependency on WU-0005.5.

**Not ratified, still open (no recommendation exists):** DEF-0018 (H3a log-rank extreme p for tiny regimes); N3's licence scope and the D3 SE_new arm (DEC-0020); the estimator convention itself (DEC-0024 point 1); the Chua pilot H2a(i) reading under the finite-M bias (DEC-0024 point 2); `main` (reserved for fully green configurations: the open items and the owner's ledger entries remain; no request is made).

**Order of work.** (a) Small lanes in parallel: DEF-0025 and the test-tooling fixes; Option C switch; WU-0002.11e implementation; planning of WU-0002.11c plus the start-state unit, of WU-0005.6 and of the WU-0003 rehearsal. (b) Every lane keeps the process: planner, mathematician where mathematics, developer, independent review, at most two fix rounds, blast radius only, merge to develop. (c) Any change that moves numbers needs its own before/after comparison; a new gate on `develop` after the batch.

**Affects:** everything listed. Marked "needs owner review before freeze" where the underlying record is. **Status:** owner instruction; recorded pending the owner's ledger entry.

## DEC-0024 addendum A2: row 9 under Option C, and the predicted consequence for WU-0006 (2026-10-12, recorded by claude-sonnet-5-5 (developer, WU-0006.5) from DEC-0026 item 2; for owner confirmation of the wording)

Amends the row-9 text of addendum A1 (A1 is left as written, append-only). The sentence of A1 'Option C or K (DEC-0018; owner, pending; K in force by default via ASSERT_ROADMAP_BOUNDS = True)' is no longer true: the owner ratified Option C on 2026-10-12 (DEC-0026 item 2, recorded in this file) and WU-0006.5 sets `ASSERT_ROADMAP_BOUNDS = False`. The rest of A1 (the five row-1 cells, M7 constants, the widening sentence) stands.

**Row 9 (DEF-0020), replacing the A1 text.** `DEF-0020: Option C in force (owner-ratified 2026-10-12, DEC-0026; ASSERT_ROADMAP_BOUNDS = False): the WU-0006 ROADMAP-bound coverage rows are recorded characterization rows (outcome reported, not asserted) and the consistency ranges are the defect test; no bound, level or R is changed. Whether the study widens its intervals or uses another procedure (longer block, studentized, BCa) is a separate, undecided design question for the owner and the applied-mathematician.`

**What remains open.** The widening question: whether the study widens its intervals or uses another procedure (a longer block, studentized or BCa intervals) is still undecided and is not decided by Option C or by DEF-0020; the `uq-budget` rule ('widen the interval or refine') is the only text it cites. Option C changes what the slow tests assert, not the intervals the study reports.

**Predicted consequence for DEC-0018 and WU-0006 (recorded before any run under Option C).** With `ASSERT_ROADMAP_BOUNDS = False` the ROADMAP-bound outcomes of A1, A2, A3, L1, L2, N1, N2 and N3 stay computed, written to the `runs/tests/wu0006_*.json` tables and shown as a labelled `UserWarning` in the pytest output, but are never asserted. The about 13 nominal-bound outcomes predicted in DEC-0018 for correct code (run 2 observed 16 failed coverage and edge-rate rows and N1 in 2 delta-R2 rows, DEF-0020 and DEF-0021) therefore become **reported findings, not test failures**, and no longer recur as failing nodes at gates. The pre-registered consistency ranges (70 coverage, A3 and log-rank, and 12 delta-R2) and the exact checks stay asserted in both switch positions; a count outside a range is the defect candidate. No bound, level, R, B or seed changes (PRIME.2).

**Status:** the content is the owner's ruling (DEC-0026 item 2); this addendum's wording is proposed, with DEC-0024.

- 2026-10-12 (claude-sonnet-5-5, main session), clarification of DEC-0026 item 2 from the WU-0006.5 review R1: 'N2 and N3 are the criteria of the null delta-R2 study and N1 is reported' says which rows the ROADMAP row names as the study's criteria (DEF-0021; the amendment is the owner's edit). It does **not** say that N2 and N3 stay asserted: DEC-0018's update of 2026-10-11 (item 1 and its closing sentence) is part of the Option C that was ratified, and it makes **all** the nominal-bound rows (A1 to A3, L, N1 to N3) recorded characterization rows under C. If the owner reads it the other way, N2 and N3 (or N2 alone) come out from under `ASSERT_ROADMAP_BOUNDS`: a code change in `tests/slow/` with a mathematician's note on the N3 false-alarm rate. For owner confirmation before freeze.
- 2026-10-12 (claude-sonnet-5-5, main session), process note from the WU-0011.5 review R2: the main session authorized WU-0011.5 as a 'planner-free small lane' (the developer wrote the acceptance criteria into the unit file in a first commit before any code, and the independent review judged them adequate). DEC-0026 (b) says every lane keeps the planner step, and DEVELOPMENT_WORKFLOW 2.1 says the planner writes the plan: this is a departure by the main session, recorded here, not an agent's. For owner awareness; later small lanes keep the planner step.
- 2026-10-12 (claude-sonnet-5-5, main session): the plans for WU-0002.11c, WU-0002.14 (seed-dependent start states plus the `make_rng` conversions) and WU-0003 (plan amendment 1) were written on branches `wu/0002-11c-start-states` (d6568dd) and `wu/0003-rehearsal` (c52a5b2). Their owner questions (11c Q1, Q2; .14 O1 to O8; WU-0003 O1 to O8) are listed in the amendments note, section 14. The planners' recommendations are adopted as working defaults so that the work can proceed; they are **not** covered by the 2026-10-12 ratification (made before they existed) and need the owner's confirmation before freeze. Marked "needs owner review before freeze".

## DEC-0027: WU-0002.14 O4: the D3 criterion for a redrawn-state run uses both arms facing away; the triage order  (2026-10-13, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The main session asked the owner for a ruling on O4 of WU-0002.14 (the D3 criterion of the DEC-0019/0020 regression when every value moves because the start states are redrawn by design), with the applied-mathematician's recommendation (Mathematics check M5, WU-0002.14 unit file): "take both arms facing away from the other estimate, since the two runs are exchangeable; the current mixed rule is not symmetric under swapping them", with the proposed triage order (an excess beyond 2 z_B is a defect candidate, an excess below it is reported with the undercoverage of DEC-0018 in mind). The owner answered, in the session on 2026-10-13, in these words: "O4 take the recommendation". Recorded as: (1) `compare_pilot --redrawn-states` applies D3 with **both SE arms facing away** (`REDRAWN_D3_ARMS = "away"`; SE_new as implemented, which closes the DEC-0020 item; SE_old changes from the side of Delta to the side facing away); the options `--d3-arms half-width|delta-side` stay available only to reproduce other readings; (2) the **triage order** of M5(a) is adopted (excess beyond 2 z_B: defect candidate, referred; otherwise reported, not tuned); (3) a V4 failure at P1 (indicatively 5 to 15% for correct code) is **referred to the owner, never retuned**. The 'working default pending the owner' wording of the tool's report text is replaced by this record in a later commit of WU-0002.14 (text only).

**Affects:** WU-0002.14 (P1 may be judged), WU-0003.4. Marked "needs owner review before freeze". **Status:** owner instruction; recorded pending the owner's ledger entry.

## DEC-0028: WU-0003.6: the reproducibility tolerance declaration (same context bitwise; equal contexts by the A6 tiers; across devices by the TD statistic, away-arm form)  (2026-10-18, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Source of the wording.** ruling given through the question tool, recorded in the amendments note §29 and §33; text drafted by claude-opus-5-5 (planner). Entered by the main session on 2026-10-18 in the freeze records (WU-0004.9) with the substitutions listed in `docs/agent/notes/2026-10-18-ledger-batch-draft.md` section 2.

**Decision.** The project declares its outputs reproducible as follows (LPC.PC.18 "within the tolerance recorded in WU-0003"; REPRO.3; NVVUQ.12). The tier of a pair is selected mechanically from the context digests by `tools/compare_runs.py` (A6, B1 item 1), and the pair is judged by that tool.
1. **Same context, same device type, same host, code, seed and environment (tier T0): bitwise.** Every leaf identical (IEEE bytes), except timing (`seconds`) and the top-level `provenance` block.
2. **Equal context digests, different device, host, BLAS kernel or network weights (tiers T1 to T3): the A6/B1 tolerances as implemented in `compare_runs`.** The network-independent chain leaves (`cp`, `oracle`, `dynamics`, `fixture`) within 1e-12 relative; V1 (`delay_jacobian_rel_err`, `gain_rel_err`) within 1e-12 absolute; V2 within 1e-10 relative; LM summaries by the T1/T2 rules; QoIs and interval endpoints within 1e-4·max(|lo|, |hi|) (class a; this includes `fitted_inverse_dim` and `ci_inverse_dim[0..1]`, re-tagged under OF-7; `floor_rms` is class (g), and `ratio` and `ratio_ci` stay in the cp chain at 1e-12, see DEC-0030 item 9); other classes by the 10x rule, capped at 1e-4; every verdict identical. By OF-2 the V1 1e-12 rule applies only to these equal-context pairs.
3. **Different contexts (tier TD; GPU against CPU in practice): the TD statistic.** No per-leaf tolerance. For each of the 18 primary parts (6 per system; H2a(ii) counts two), z = |d| / sqrt(se0^2 + se1^2) with each se taken from the interval arm that faces away from the other estimate (if run 1 lies above run 0: run 0's lower arm and run 1's upper arm; the pairing of DEC-0027; OF-5), se = arm / z_level, z_level = Phi^-1(1 - 0.05/6) = 2.394 (the primary level 1 - 0.05/3). A part fails if |z_away| > 3.4 (Phi^-1(1 - 0.01/30) = 3.403; family level at most 1.2% over 18 parts). The symmetric form (se = hw / z_level) is printed as information and does not fail a part. Verdict-type leaves that differ are reported, not failed.
4. **What a TD pass does not mean.** It does not reproduce verdicts or the gate outcome. R5 against R6 passes the statistic while 52 verdict-type leaves differ and Chua's `gate_pass` differs (V6 on the GPU context 2.405e-3, a fail; on the CPU context 3.3e-4). The choice of confirmatory device is DEC-0031.

**Evidence (DEVELOPMENT; not hypothesis tests).**
- R1 against R2 (DEV-1 pilot, GPU RTX 4090, code c9bb981, repeated on the same host): tier T0, **20533 of 20533 leaves equal** (provenance and 23 timing leaves excluded). `WU-0003-R1R2.md` and `WU-0003-R1R2-compare-r1-r2.txt` on `run/r1-c9bb981`.
- R0 (smoke): DEV-0 CPU against the step-4 reference smoke: T0, 4794 leaves, 0 different (CPU bitwise). DEV-1 GPU against DEV-1 CPU: TD on all three systems; 18 of 18 parts, 0 failing, max |z| 2.53 symmetric / 2.61 away. All six V1 leaves differ across devices by 3.5e-10 to 1.5e-8 absolute (different trajectories: the reason for OF-2).
- R1 against R3 (DEV-1 pilot, GPU against CPU): TD; 18 of 18 parts, 0 failing; **max |z| 2.73 symmetric, 2.72 away** (Lorenz-63 H2a(ii) zero); 30 verdict-type leaves differ. `WU-0003-R3R6-compare-R1-R3.txt`.
- R5 against R6 (DEV-2 full, GPU against CPU): TD; 18 of 18 parts, 0 failing; **max |z| 2.32 symmetric, 2.26 away** (Rossler H2b(i)); sum z^2 16.5 / 15.8; 52 verdict-type leaves differ. `WU-0003-R3R6-compare-R5-R6.txt`.
- No rehearsal pair fell in T1 to T3 (no R4 record exists on the branches read). The T1 to T3 numbers rest on the WU-0003.9 kernel-pair evidence (WU-0002.14 S3 smoke pair, scratch copies with injected digests: declared 1e-5 for class (a), largest rel 2.94e-7; 1e-4 for (b) to (g)) and on the mathematician's notes `2026-10-14-math-wu0003.md` §M1, §M2 and `2026-10-14-math-wu0003-9-q1.md`.

**Alternatives weighed and why rejected.**
- *ROADMAP WU-0003.4's rule, "10x the GPU-to-GPU maximum relative difference, rounded up to a power of 10".* Degenerate: the GPU repeat is bitwise (10 x 0). It survives as item 1 (bitwise) and says nothing about cross-device pairs.
- *The V1 1e-12 rule across devices, as item 11 was written, or a wider replacement of about 1e-9 (OF-2 (b)).* Rejected (OF-2, §26): across devices the contexts differ, so V1 is computed on different trajectories and the comparison is not like for like.
- *A part fails on max(|z_sym|, |z_away|) > 3.4 (plan amendment 2, B1 item 5; the tool as built).* Replaced by the away-arm form (OF-5). See "Dissent".
- *Pin trajectory generation to the CPU (O4 (a)).* Not decided here (O4).

**Affects.**
- `tools/compare_runs.py`: the TD failing rule is |z_away| > 3.4 (WU-0003.9c, merged 91c93f5, independent review `WU-0003.9c-review.md`); needs owner review before freeze.
- ROADMAP WU-0003.4 (line 176) and its definition of done (line 187) do not match what was done: no "one core cell" (O8 widened it to the pilot), no differences table for w*, eps_s, delta, nu, Lambda-bar, N in the row's form, and `tests/gpu/test_reproducibility.py` does not exist. The compare_runs reports stand in. The row text is the owner's edit (or the owner requires the gpu test).
- ROADMAP WU-0003.6 (lines 178, 189): this entry is one of its two decision entries.
- WU-0016.3 (cross-host comparisons, CSQ2), WU-0004.1 (freeze checklist), LPC.PC.18.
- Not decided here: O3 (`--xla_gpu_deterministic_ops`). O4 is DEC-0031.

**Dissent and resolution (REPRO.8).** The applied-mathematician recommended the away arms and called them "not a loosening" on the sum (P0/P1: sum z^2 11.99 against 12.65; note §M1.4). Plan amendment 2 (B1 item 5) recorded that the away form alone gives a lower z on 7 of the 18 P0/P1 parts (Chua H3c 1.02 against 1.34), so, per part, away-only is looser than the as-built max-of-both rule. The owner ruled for the away form (§33, OF-5). Every rehearsal pair passes under both forms, so no rehearsal outcome changes.

**Status:** owner ruling 2026-10-18 (question tool); the ledger `ruling` entry is the owner's. Needs owner review before freeze (tolerance and verdict-comparison code).

**Record files.** `docs/agent/records/work/WU-0003-R1R2.md`; `WU-0003-R1R2-compare-r1-r2.txt`; `WU-0003-R3R6-compare-R1-R3.txt`; `WU-0003-R3R6-compare-R5-R6.txt`; `WU-0003-9c-compare-R1R3.txt`; `WU-0003-9c-compare-R5R6.txt`; `docs/agent/notes/2026-10-14-math-wu0003.md` section M1, M2; `docs/agent/notes/2026-10-14-math-wu0003-9-q1.md`.

**Amendment of 2026-10-18, owner ruling M2 of the freeze audit** (`docs/agent/records/audits/2026-10-18-freeze.md`, M2; recorded in DEC-0033). The bitwise (T0) declaration of item 1 for the official configuration (CPU, full preset, LPC_THREADS=8) is measured at smoke size (CPU, at 4 and at 8 threads) and at GPU pilot size, and is extrapolated to the full preset at LPC_THREADS=8. No CPU full-size repeat is run. If the regeneration (WU-0016.2) is not bitwise, v3 section 9 routes it to the per-quantity tolerances (tiers T1 to T3 of item 2), so no verdict is at risk.

## DEC-0029: WU-0003.6: the confirmatory sample size stays the full preset  (2026-10-18, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Source of the wording.** ruling given through the question tool, recorded in the amendments note §33; text drafted by claude-opus-5-5 (planner). Entered by the main session on 2026-10-18 in the freeze records (WU-0004.9) with the substitutions listed in `docs/agent/notes/2026-10-18-ledger-batch-draft.md` section 2.

**Decision.** The confirmatory run uses the full preset as in v3 §4 and `lpcstudy/config.py` `FULL`: construction 2000, calibration 1000, test 1000 and sweep cells 1000 states; M = 200 oracle draws and 4 evaluation draws per state; V4 at M = 50, 200, 800 on 100 states; B = 2000 bootstrap resamples. No size changes.

**These are development runs, not hypothesis-test results.** Every number below comes from DEV-1 and DEV-2. None is a verdict of the study, and none was used to choose a criterion.

**Rehearsal evidence.**
- **H3a.** At full size a pass is reachable only on Chua (R5: Holm p 0.00397; R6: same pattern). On Lorenz-63 and Rossler the full preset cannot deliver an H3a pass at these realizations. The R1 pilot projection reached it on no system (K_pilot 6, 4, 5).
- **H2e.** R6 half-widths 0.0207 (Lorenz-63), 0.0218 (Rossler, rho 0.01), 0.0241 and 0.0244 (Chua): all narrower than v3 §7's projected 0.04 (a precision gain).
- **v3 §7 precision statements.** On R6, reading (i) fires on 10 of 18 parts and reading (ii) on 10 of 18. R5 against the R1 projection: 4 reading-(ii) triggers over 69 parts (about 0.47 predicted). R6 pre-registered predictions: 11 of 12 within (outside: Lorenz-63 Q-N oracle logit, 0.0210, 0.525 of v3's 0.04, where "undetermined" was predicted). The pilot size does not support the same statements; the full preset is not oversized.
- **V4 at full size** (bar 0.05): R5 0.0263, 0.0424, 0.0299; R6 0.0290, 0.0350, 0.0230. All pass.
- **Finite-M bias.** D5 "not determined" on all three systems (R5), so budget row 1 stays "not below 10%" (PF-5). Raising M is not a lever: no admissible M (at most 399, H-M1/H-M2) brings F1 below 0.1 hw_full; that would need M of about 5,700 to 29,000 (note `2026-10-14-math-wu0003.md` §M5.1).
- **Compute against LPC.PC.22** (budget: the full preset completes within 12 h on the owner's GPU workstation). R5, GPU: 2739 s (0.76 h). R6, CPU at `LPC_THREADS=8`: 17031 s (4.73 h), peak RSS 4.75 GB; above the A1 planning bound of 4 h, below 12 h; not a clean C6 figure (other lanes may have shared the CPU). Both are within budget, so no optimization is warranted (RSRC.4).
- **Device (input to O4, not decided here).** For the same seed, the device changes the context and therefore the realization: DEV-2 Chua V6 fails on the GPU context (2.405e-3) and passes on the CPU context (3.3e-4). GPU repeats are bitwise on this host (R1/R2); a CPU sealed run would take about 4.7 h (R6, not clean) and regenerates bitwise on CPU. The official sealed run is on the CPU (DEC-0031).

**Alternatives weighed and why rejected.**
- *Pilot size.* Rejected: the projections from R1 reach fewer decisions (H3a on no system), and reading (ii) shows the pilot does not support v3 §7's statements.
- *Larger n.* Not chosen; no recommendation was made. Its effect on H3a for Lorenz-63 and Rossler is not measured, and it lengthens the CPU run.
- *Larger M.* Rejected on the M5.1 evidence above (no admissible M reaches the 10% rule).

**Affects:** WU-0003.6 (ROADMAP lines 178, 189), WU-0004.1 (freeze checklist), the pre-registration text. v3 §4 is unchanged. Whether v3 §7's precision paragraph is updated with the rehearsal figures is a separate owner edit, not decided here. The device is DEC-0031.

**Dissent and resolution (REPRO.8).** None recorded.

**Status:** owner ruling 2026-10-18 (question tool); the ledger `ruling` entry is the owner's.

**Record files.** `WU-0003-R1R2-R5-rehearsal-report-r5.txt`; `WU-0003-R1R2-R5-rehearsal-report-r1-observed-r5.txt`; `WU-0003-R3R6-report-R6.txt`; `WU-0003-R3R6.md` (all under `docs/agent/records/work/`); `docs/agent/notes/2026-10-14-math-wu0003.md` section M5.1.

## DEC-0030: Owner rulings of 2026-10-17 and 2026-10-18 on the WU-0003 rehearsal, the LM-doubling study and the comparison and diagnostics tools  (2026-10-18, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Source of the wording.** answers given through the question tool and recorded by the main session in docs/agent/notes/2026-10-11-amendments-for-owner.md §§26, 29, 30, 31, 33; text drafted by claude-opus-5-5. Entered by the main session on 2026-10-18 in the freeze records (WU-0004.9) with the substitutions listed in `docs/agent/notes/2026-10-18-ledger-batch-draft.md` section 2.

**Decision.** The note sections are the record of the wording; this entry restates them.
1. OF-2 (§26, 2026-10-17): "Equal contexts only". The V1 1e-12 rule of plan item 11 applies only to pairs whose context digests are equal (tiers T0 to T2); GPU-against-CPU pairs (TD) are judged by the TD statistic.
2. R5 and R6 (§26): authorized (full preset on DEV-2; GPU with the states dump; CPU at LPC_THREADS=8). Run on 2026-10-17.
3. DEF-0026 (§26): the offline V6/V4 check on DEV-1 to DEV-4 only. Not chosen: a pre-registered response to a sealed-run gate failure, evaluating the outcome-free gate checks first, a risk-register-only entry. A sealed-run gate failure stays a hard stop referred to the owner (DEC-0027).
4. OQ-R9 (§26): the diagnostics defaults (tool seed 20261018, 1000 permutations, 2000 resamples) are pre-registered; the first default-options report per run is the record; any other option is labelled non-default and is not the record.
5. O5, DEF-0027 (§29): report and flag only. The design value stays 15 LM iterations; the iteration-sensitivity flag is reported per part; no new reference run.
6. DEF-0028 (§29): amend tools/lm_doubling.py to the plan (structural switch, class U, before the X bullets). Done: merged f14c8fa after independent review (WU-0005.6-rule-r-order-review.md). Readings of §30: [owner: "confirmed" | "ruled otherwise: ..."]: (a) a half-width <= 0, a NaN value and an infinite point estimate with finite bounds are not structural switches; (b) an infinite lower or upper bound at any arm is.
7. OF-R2, OF-G6 (§29): keep the range. The pre-registered kappa_E range [0.7071, 1] governs; no dump change, no half-split estimator, no rerun.
8. Block length (§29, §31): keep block length 5 for all three systems (no v3 or Methods v2 amendment). OF-3: the pooled permutation reading governs the D2 verdict; the A5 rule and beta-hat-5 are printed as information. A report-only "block-sensitive" label marks a primary part whose verdict would change if the half-width were widened by sqrt(max(1, V*(10)/V*(5))); it changes no criterion. Implemented in WU-0003.8d (merged 1e3d726). Judgement calls of WU-0003.8d: [owner: (b) label rows, including "not computable" rows, never set exit 2 — "confirmed" | "count them for the exit code"]; [owner: (d) the label is per primary part, not per combined hypothesis verdict — "confirmed" | ...].
9. OF-7 (§33, 2026-10-18): re-tag the H1a fit leaves out of the cp chain under the A6 QoI rule; the 1e-12 rule stays elsewhere. As merged (WU-0003.9c, 91c93f5): fitted_inverse_dim and ci_inverse_dim[0..1] class (a), 1e-4 s; floor_rms class (g); ratio and ratio_ci stay cp 1e-12 with the OF-7 pointer. [owner: "ratio and ratio_ci are covered by OF-7 (class a)" | "they stay cp 1e-12"; note: the text ruled on said they "already" were at 1e-4 s, which stopped being true at da22cdd on 2026-10-17; under the literal reading every T2 pair fails on 18 H1a leaves with correct code.] [owner: floor_rms "class (g) as built" | "class (a) as the ruling text says".]
10. OF-1 (§33): keep strict. No licence for H2c, H2d or H3c under T1 to T3 for a fitted-coefficient change beyond 1e-6.
11. R5 of the WU-0003.9 review, O3 (§33): the declared-tolerance rule O3 is information only on T1 to T3 pairs.
12. Q7, Q8, Q9 and the handling-count scope (§33): keep the tool's strict readings; the handling-count licence is kept as written. [owner: follows_k (the K-block listing, labelled a looser reading in WU-0003.9 R17) — "confirmed" | ...]
13. OF-4 (§33): the F1 wording is corrected by DEC-0024 addendum A3.
14. OF-5 (§33): the away-arm TD form is the failing rule (|z_away| > 3.4 over 18 parts); the symmetric form is printed as information. Merged in WU-0003.9c (91c93f5). The plan text of A6 and B1 item 5 is left as written; the plan amendment for it is the planner's.
15. OF-F3 (§33): keep N = 24 diagnostic series as written (H1c not counted).
16. OF-G3 (§33): the margin band 0.0850 to 0.0933 governs the H2a(ii) comparison against v3; the hw band [0.0603, 0.135] stays printed, not governing.
17. F4 and Q6 (§33): keep both as built; Q6 is recorded as WU-0003 plan amendment 11. [owner: K2, d3 shown on scratch copies of the S3 pair — "covered by keep as built" | ...]
18. WU-0003.6 (§33): DEC-0028 (reproducibility tolerance) and DEC-0029 (sample size).

**Alternatives weighed.** As listed in the cited note sections and the mathematician's notes (2026-10-14-math-wu0003.md, 2026-10-14-math-wu0003-9-q1.md, 2026-10-14-math-wu0003-3a-kappa.md, 2026-10-17-math-block-length.md).

**Affects:** tools/compare_runs.py, tools/lm_doubling.py, tools/rehearsal_diagnostics.py, tools/rehearsal_report.py, lpcstudy/budget.py (OF-4), WU-0003, WU-0004.1, WU-0016.

**Dissent and resolution (REPRO.8):** OF-5, see DEC-0028. Otherwise none recorded.

**Status:** owner rulings (question tool); ledger rulings L12 to L17. Items 6, 8, 9, 12 and 17 carry confirmations the owner fills in above. Needs owner review before freeze (tolerance, comparison and statistics tool code).

**Note on the bracketed owner confirmations (items 6, 8, 9, 12, 17).** They are entered unfilled, as drafted. The owner fills them with a dated line appended below; until then the item is the drafted reading, not an owner-confirmed one.

## DEC-0031: The confirmatory run is on the CPU; a GPU run of the same sealed seed is a cross-check that informs only  (2026-10-18, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Source of the wording.** answer given through the question tool after the clarification of §35, recorded in docs/agent/notes/2026-10-11-amendments-for-owner.md §36; text drafted by claude-opus-5-5. Entered by the main session on 2026-10-18 in the freeze records (WU-0004.9) with the substitutions listed in `docs/agent/notes/2026-10-18-ledger-batch-draft.md` section 2.

**Decision.** Pre-declared before the freeze (WU-0003 plan amendment 1, A12 O4):
1. The official sealed run (CONF-1, full preset) runs on the CPU at LPC_THREADS=8. Device and thread count are part of the freeze configuration (LPC.PC.8; DEF-0023: the thread count changes results in the last bits).
2. A GPU run of the same sealed seed is a cross-check. It is compared with the official run by tools/compare_runs.py with the TD statistic, away-arm form, failing bound 3.4 (DEC-0028 item 3). The CPU verdicts stand. A differing verdict-type leaf, a TD failure or a GPU gate failure is reported as information and changes no verdict.
3. The GPU cross-run is a second use of the sealed seed: it needs its own per-action authorization (LPC.AUTH.6), and its outputs are released only with the official run's release decision.
4. The regeneration by another actor (WU-0016) runs on the CPU: bitwise (T0) on the same platform and LPC_THREADS, otherwise judged by the A6 tiers (DEC-0028 item 2).
5. [owner: whether R1 (GPU pilot), R3 (CPU pilot) and R6 (CPU full) satisfy LPC.PC.6 "validation gate V1-V7 passes on all three systems in the rehearsal", with R5's Chua V6 failure (GPU context) recorded under DEF-0026 — "yes" | "the rehearsal must pass at full size on the CPU (R6 did)" | ...]
6. [owner: O3 for the GPU cross-run: "XLA_FLAGS not set (R1 = R2 bitwise without it)" | "set --xla_gpu_deterministic_ops=true".]

**Evidence (DEVELOPMENT; not hypothesis tests).** R5 against R6 (DEV-2, full): tier TD, 18 of 18 parts, 0 failing, max |z_away| 2.26; 52 verdict-type leaves differ; Chua V6 fails on the GPU context (2.405e-3 against 1e-3) and passes on the CPU context (3.3e-4). R1 = R2 bitwise on the GPU (20533 leaves). CPU wall time of R6 17031 s (4.73 h; possibly shared CPU), within LPC.PC.22's 12 h. Records: WU-0003-R1R2.md, WU-0003-R3R6.md, WU-0003-R3R6-compare-R5-R6.txt, WU-0003-R3R6-gates-clips-R6.txt.

**Alternatives weighed.** Both runs on the GPU (fast; a regeneration on another GPU is only TD; the only full-size GPU rehearsal failed V6). Accepting TD for the regeneration (weakest). Pinning trajectory generation to the CPU (a numbers-changing code step after the rehearsal).

**What this does not change.** The per-seed gate risk (DEF-0026: about 4.6% for Chua V6, 11 to 25% for V4 or V6 at full size) is the same on either device. A gate failure of the official CPU run is a hard stop referred to the owner, never retuned (DEC-0027; no pre-seal response rule, §26).

**Affects:** the freeze configuration (WU-0004.7), WU-0015, WU-0016, DEC-0028 item 4, the gpu test of B10 (which tests the cross-check device only). Supersedes plan amendment 1 O4's recommendation "(b) same device type".

**Dissent and resolution (REPRO.8):** none recorded. **Status:** owner ruling 2026-10-18; ledger ruling L20.

**Note on the bracketed owner questions (items 5 and 6).** Entered unfilled, as drafted; the owner answers by a dated line appended below.

## DEC-0032: Owner rulings of 2026-10-18 on the freeze blockers B5 to B11 (B4 is DEC-0031)  (2026-10-18, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Source of the wording.** answers given through the question tool, recorded in docs/agent/notes/2026-10-11-amendments-for-owner.md §35 and §36 against docs/agent/notes/2026-10-18-freeze-blockers.md; text drafted by claude-opus-5-5. Entered by the main session on 2026-10-18 in the freeze records (WU-0004.9) with the substitutions listed in `docs/agent/notes/2026-10-18-ledger-batch-draft.md` section 2.

**Decision.**
1. B5 (where the freeze lives): develop is merged into main after the owner's code review (WU-0004.5) and a green full suite at the freeze gate; the freeze commit and tag live on main. No main request is made now.
2. B6a (DEF-0020): keep the pre-registered percentile intervals and block length 5; no widening and no other interval procedure. The measured undercoverage (DEF-0020, DEC-0018) and the report-only block-sensitive label are stated as limitations.
3. B6b (DEF-0018): keep H3a as is (no per-regime or event-count minimum; DEC-0011 O1 stands); report the event counts per regime; state the exposure (one event in a tiny regime can give an extreme log-rank p and a Holm-adjusted pass) as a limitation. To be implemented: h3a_logrank reports per-regime state counts, not event counts.
4. B7 (LM row; WU-0005.6 O4 and O6): the DEV-0 flags are quoted as development evidence with the sqrt(n_full/n_pilot) projection; the sealed report keeps "not estimated" plus a pointer; no sealed 30-iteration twin run. A text and small budget change (WU-0004b), with review and owner review.
5. B8 (DEC-0008 C): implement the refusal of a sealed run on a dirty tree or an unknown commit (code, tests, independent review, then the owner's review). VmHWM recording: [owner: "yes" | "not now"].
6. B9: ratify en bloc the working defaults and stricter readings of freeze blockers B9 [owner: "all B9 items" | "only: N2/N3 under Option C, PF-1 to PF-5, OF-H1, OF-I2, C6-R6, the R3 families of WU-0003.9b, the planner defaults of WU-0002.11c (Q1, Q2) and WU-0002.14 (O1 to O8), WU-0005.6 O1 to O3, WU-0003 plan amendment 1 O1 to O8"], except that plan amendment 1 O2 (R4, not run), O3 (GPU deterministic-ops flag, never set) and O4 (same device type; replaced by DEC-0031) are recorded as overtaken, not ratified. Ruled separately: N2 and N3 keep the code's reading (N1, N2 and N3 computed and reported, none asserted; the consistency ranges asserted); OF-I1 keeps the min anchor (H1d at 98.3% prints 0.9794). The DEV registry statuses are updated (DEV-1, DEV-2 used; DEV-3, DEV-4 used for V6 contexts only).
7. B10: write tests/gpu/test_reproducibility.py (smoke twice on the GPU against the tolerance of DEC-0028), under the GPU lock; the owner edits the ROADMAP WU-0003.4 row and definition of done to what was done.
8. B11: the sealed run keeps the states dump off; the freeze is recorded as a ledger classification entry (entry to CSQ2) plus the commitment entry written by the seed-sealing step. [owner: WU-0004.8, the governance reread (LPC.PC.25), is performed by <name>.]

**Alternatives weighed.** As in the freeze-blocker note, B5 to B11.

**Affects:** WU-0004.1 to .8, WU-0015, WU-0016, lpcstudy/analysis.py and report.py (B6b), lpcstudy/budget.py (B7), lpcstudy/__main__.py and provenance.py (B8), tests/gpu/ (B10), seeds/development_seeds.json (B9), ROADMAP.md (B10).

**Dissent and resolution (REPRO.8):** none recorded. **Status:** owner rulings 2026-10-18; ledger note L21 and ruling L22.

**Note on the bracketed owner choices (items 5, 6 and 8).** Entered unfilled, as drafted; the owner answers by a dated line appended below. The ledger references (L12 to L22) are the entries of `docs/agent/notes/2026-10-18-ledger-batch-draft.md` section 3.

## DEC-0024 addendum A3: OF-4: F1 is an indicative value, not a worst case for the median  (2026-10-18, human owner; ruling given through the question tool, recorded in the amendments note §33; text drafted by claude-opus-5-5 (planner) from the applied-mathematician's note `docs/agent/notes/2026-10-14-math-wu0003.md` §M5)

Amends point 2 of DEC-0024 and the F1 wording of WU-0008 M3 (design 28dfbd1). The earlier text is left as written.

**Correction.** F1 = (3/sqrt(pi))·h/z_0.975 is the expected range of a state whose true range is zero, with draw noise independent across the 3 horizons. It is **indicative (the bias of a zero-range state); it is not a bound on the bias of the median range.** When more than half of the eligible states have exact separation, the median of the noisy ranges lies near an upper quantile of the noise-only range, above its mean. A synthetic case (60% separated, independent noise across horizons, M = 200; `m5_d5sim.log`, seed 20261016) reaches **1.38·F1**; with noise correlation 0.5 it is 1.01·F1, with 0.9 it is 0.48·F1. The direction stands: upward, toward a fail.

**Point 2, replacement text.** "The Chua pilot H2a(i) fail is not certified against the finite-M bias. The indicative F1 for the H2a(i) median range is 0.86 of the V4 median half-width, i.e. 43 to 86% of the interval half-width on the DEV-0 pilot; a bias of that size already moves the Chua pilot's range below the 0.1 bound (0.1135 − 0.027 = 0.087), and F1 does not bound the bias, which can be larger (1.38·F1 in a synthetic case). A pass is not certified either. This is a development-run observation (DEV-0, not a hypothesis test). The number of oracle draws is not a remedy: F1/hw_full is 0.54 to 1.20 at M = 200 (0.38 to 0.85 at M = 399, the largest admissible M by H-M1/H-M2), and bringing F1 below 10% of the half-width would need M of about 5,700 to 29,000. Only a small measured bias (the D5 estimator of WU-0003) can show the row below 10%."

**WU-0008 M3, replacement wording** (appended to the WU-0008 Log as a dated correction):
- line 310: "Indicative value (the bias of a zero-range state; not a bound on the median), assuming draw noise independent across the k = 3 horizons and SD s_med at each: F1 = (3/√π)·h/z₀.₉₇₅ = 0.86362·h. Use 2/√π if k = 2."
- line 313: "The Rössler fail survives a bias of size F1 (0.211 − 0.034 = 0.177 > 0.1); F1 is not a bound, so this is an indication, not a certificate."
- line 314: "The Chua pilot fail is not certified against the finite-M bias: a bias of size F1 already gives 0.1135 − 0.027 = 0.087, and the true bias can exceed F1."
- line 315, the cell: "not estimated: finite-M bias upward (toward fail); indicative F1 = … (bias of a zero-range state, independent draw noise across horizons; not a bound on the median; V4 at H_ref only)".
- line 216, row 1, H2a(i): "bias upward; indicative F1 (not a bound)".
- line 868 (a review record; left as written): its "upper indication" is superseded by this addendum.

**Code consequence.** `lpcstudy/budget.py` prints the old wording into RESULTS.md. The docstring of `oracle_range_bound` (lines 565, 570) and the cell string at line 702 change to the wording above: a report-text change, no number changes. Radius from `/test-impact` (at least `tests/unit/test_budget.py`); needs owner review before freeze. Until it lands, every RESULTS.md, including a sealed run's, prints "indicative worst case ≤ F1".

**Affects:** WU-0008 (M3, row 1), DEC-0024 point 2 (still open per DEC-0026), `lpcstudy/budget.py`. **Status:** owner ruling 2026-10-18; the ledger entry is the owner's.

## DEC-0033: Owner rulings of 2026-10-18 on the freeze audit majors M1 to M4  (2026-10-18, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The owner ruled on the four majors of the pre-freeze audit (`docs/agent/records/audits/2026-10-18-freeze.md`, verdict "ready after the listed fixes"). Verbatim, 2026-10-18: "M1 amend / M2 extrapolate / M3 report only / M4 apply this / We are out of time." In plain words:
1. **M1 (ROADMAP row WU-0006.2): amend.** The row is amended to say that the coverage-bound rows are recorded characterization rows under DEC-0018 Option C (in force since DEC-0026 item 2; `ASSERT_ROADMAP_BOUNDS = False`), and that the consistency ranges and exact checks are the asserted criterion. The main session makes the ROADMAP edit; this entry records the decision. The intervals are not changed (DEC-0032 item 2). The ledger `amendment` entry for the ROADMAP edit is the owner's.
2. **M2 (T0 bitwise declaration at full size): extrapolate, do not repeat.** The bitwise declaration for the official configuration (CPU, full preset, LPC_THREADS=8) is measured at smoke size (CPU, at 4 and at 8 threads) and at GPU pilot size, and is extrapolated to the full preset. No CPU full-size repeat is run. The extrapolation is stated in DEC-0028 (amendment paragraph), in the freeze entry, and in the limitations of v3 section 8 (the main session edits v3). If the regeneration (WU-0016.2) is not bitwise, v3 section 9 routes it to the per-quantity tolerances, so no verdict is at risk.
3. **M3 (the gain-bound row WU-0002.15): report only, option (b) of the audit.** The row stays in the ROADMAP. It is recorded as a post-freeze change to a reported-only quantity (LPC.PC.8, second paragraph), so its results are promotable as reported. No code change is made now (`GAIN_BOUND_PENDING` stays as it is). The DEF-0005 closing line is appended (`defects.md`).
4. **M4 (the governing text): apply the audit's fix.** The freeze entry names `docs/study/proposal_and_methods_v3.md`, at its recorded SHA-256 (`2a856a4595bead58fa7de168f602ae4f250098839347aa352245b941459d0a06`, ledger entry 8), as the governing text, and states that the Claude Doc is a working copy. No re-export is made.
The owner added that time is short ("We are out of time"); the remaining audit fixes are applied as recorded and nothing further is re-litigated.

**Alternatives weighed.** As listed in the audit, M1 to M4: for M1, restoring the assertion (Option K) and accepting red rows; for M2, one CPU full-preset repeat on DEV-2 (about 4.7 h) before the seal; for M3, ruling the row out with a one-string code edit (option (a)); for M4, applying the 23 edits to the Claude Doc and re-exporting.

**Evidence.** `docs/agent/records/audits/2026-10-18-freeze.md` (M1 to M4, lines 31 to 48); DEC-0018 (Options C and K); DEC-0026 item 2 (Option C ratified); DEC-0028 (reproducibility tolerance, with its amendment of 2026-10-18); v3 section 8 (limitations) and section 9; `docs/agent/notes/2026-10-11-amendments-for-owner.md` sections 46 and 47 (the owner code review and the rulings on it); section 48 (these rulings and the records entered).

**Affects:** ROADMAP row WU-0006.2 (owner or main-session edit), v3 section 8 (main-session edit), the freeze entry (WU-0004.7), DEF-0005 and DEF-0020 status lines, WU-0002.15. **Status:** owner instruction relayed by the main session; the ledger `ruling` entry is the owner's to append.

## DEC-0033 addendum A1: the bracketed owner confirmations of DEC-0030, DEC-0031 and DEC-0032 (2026-10-18, owner answers through the question tool, recorded by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

Entries DEC-0030, DEC-0031 and DEC-0032 were entered with owner brackets unfilled (this file is append-only, so they are answered here, not edited). On 2026-10-18 the owner answered the two open questions and approved recording the rest from the answers already on record ("Yes, record them", question tool). Each bracket, in the order of the entries:

- **DEC-0030 item 6, DEF-0028 readings (a) and (b):** in force as built in `tools/lm_doubling.py classify` (a half-width <= 0, a NaN value and an infinite point estimate with finite bounds are not structural switches; an infinite lower or upper bound at any arm is). The owner's ruling of 2026-10-17 was "Amend tool to the plan"; the readings of amendments note section 30 are approved by this addendum.
- **DEC-0030 item 9, OF-7:** `ratio` and `ratio_ci` stay `cp 1e-12` (strict, as built; the owner's rulings OF-1 and "keep the tool's strict readings" of 2026-10-18). `floor_rms` is class (g) as built (`tools/compare_runs.py` RETAGS); `fitted_inverse_dim` and `ci_inverse_dim[0..1]` are class (a), 1e-4 s.
- **DEC-0030 item 12, Q7, Q8, Q9 and `follows_k`:** the strict readings are kept as built, including the K-block listing `follows_k` (owner, 2026-10-18: "keep the tool's strict readings").
- **DEC-0030 item 17, K2 of plan amendment 11 (d3 on scratch copies of the S3 pair):** covered by "keep as built" (owner, 2026-10-18: F4 and Q6 kept as built).
- **DEC-0031 item 5, LPC.PC.6 (owner, 2026-10-18):** yes. R1 (GPU pilot), R3 (CPU pilot) and R6 (CPU full) satisfy "the validation gate V1-V7 passes on all three systems in the rehearsal"; R5's Chua V6 failure on the GPU context is recorded under DEF-0026 (per-seed risk about 4.4%), not a rehearsal failure.
- **DEC-0031 item 6, O3 (owner, 2026-10-18):** `XLA_FLAGS` stays unset for the GPU cross-run (R1 = R2 bitwise without `--xla_gpu_deterministic_ops`).
- **DEC-0032 item 5, B8, VmHWM recording:** not now (the owner called it optional on 2026-10-18; not built; the refusal of a run on a dirty tree or an unknown commit is built and reviewed).
- **DEC-0032 item 6, B9:** all B9 items are ratified en bloc, with plan amendment 1 O2, O3 and O4 recorded as overtaken and N2, N3 and OF-I1 ruled as the entry states (owner, 2026-10-18, fifth round).
- **DEC-0032 item 8, B11:** the governance reread (LPC.PC.25, WU-0004.8) is performed by the human owner; the owner's name is entered in the ledger note of that entry.

**Status:** owner answers; recorded pending the owner's ledger entry (the `ruling` entry of `tools/owner_freeze_run.sh ledger` covers DEC-0028 to DEC-0033 and this addendum).

## DEC-0034: Owner lifts the compute caps for production runs (2026-10-19, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `authorization` entry is the owner's to append)

**Decision.** The owner's words, verbatim: "all caps are hereby lifted for all production runs. caps were to limit churn and resource wastage during development".

**Reading, for the owner to correct.** The caps are the limits of LPC.AUTH.3 (`authorizations.md`, row "Limits"): each run under 12 hours wall-clock, and at most 60 GPU-hours per calendar week. They no longer bind a production run: the sealed official CPU run, its GPU cross-check (WU-0015.2b), and any further run the owner designates as production. The earlier lift of the LPC.AUTH.2 page cap (DEC-0009) stands. The caps were set to limit churn and wasted resources during development, so they stay in force for development runs started through `tools/run_preset.sh` (its `timeout 12h` and the weekly check of `tools/gpu_hours.py`) until the owner says otherwise.

**What this does not change.** One GPU job at a time under the lock (it serializes the card and keeps runs comparable; it is not a cost cap). The seed rules (LPC.PC.7), the per-action authorization of every use of the sealed seed (LPC.AUTH.6), the dirty-tree and commitment refusals, and the recording of wall-clock time and GPU hours per run (the tally is a report, no longer a limit, for production runs). The acceptance line of ROADMAP WU-0015.2 ("wall-clock under 12 h") stays a measured and reported figure; a run past it is reported, not refused.

**Effect now.** Nothing in the plan is blocked by a cap: the official CPU run takes about 4.7 h, the GPU cross-check about 0.8 h, and the tally for the week is 0 GPU-hours of 60. The change matters for longer runs (a scaled-up ensemble), where the `timeout 12h` in the launch commands may be raised or left off.

**Affects:** LPC.AUTH.3, WU-0015.2, WU-0015.2b, any scaled-up ensemble. **Status:** owner instruction; recorded pending the owner's ledger entry. Suggested entry (the owner's act): `python3 tools/ledger.py append --type authorization --actor "<you>" --role "human owner" --authority "LPC.AUTH.3; DEC-0034" --summary "Compute caps of LPC.AUTH.3 (12 h per run, 60 GPU-hours per week) lifted for production runs" --data '{"ruled_on": "2026-10-19", "quote": "all caps are hereby lifted for all production runs. caps were to limit churn and resource wastage during development", "source": "decisions.md DEC-0034"}'`.

## DEC-0035: Owner rulings on the A13 ordering and on "another actor" for the regeneration (2026-10-20, owner statement relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The owner's words, verbatim: "A13 is fine, it was my inconsistency due to the complexity around human recorded ledger entries. a tool to make this easier in the future should be considered." and "Another actor is fine to be me."

**Reading, for the owner to correct.**
1. **A13.** The first commit of the sealed outputs (e754601, 2026-10-20T08:41:12Z, the owner's commit) came before the release entry (ledger seq 20, 08:43:08Z). The mechanical check of A13 as written (outputs committed after the release entry) is not met, and the owner accepts the ordering: no defect is opened, the release entry stands as the release, and the outputs were not read by any agent before it. Cause given by the owner: the number of human-recorded ledger entries made in one sitting (entries 15 to 21 were entered on 2026-10-20, some after the act they record: seq 15, the CPU-run authorization, is marked `entered_after_run`).
2. **Another actor.** For v3 section 9 item 4 and QA.9, the regeneration of the official run (WU-0016.2, run-2, ledger seq 21) may be run by the human owner, who also ran the official run. The independence the item asks for is then the second execution at the same commit from a fresh worktree (freeze-1, df8928f), with the comparison by `tools/compare_runs.py` (tier T0 expected), not a second person. The dated section 9 line of the findings document says that the owner ran both.
3. **Future tool (idea, not planned, not for the sealed run).** A helper for human-recorded ledger entries: it would take the act (authorization, release, ruling), prefill the entry from the record it cites, check order against the commits and the run provenance, warn when an entry follows the act it records, and print the sequence number for the next step. The owner asked that it be considered in the future; nothing is built.

**Affects:** WU-0015.3, WU-0015.4, WU-0016, the findings document section 9, the pre-promotion audit scope (A13 is not an open finding). **Status:** owner statements; recorded pending the owner's ledger entry.

## DEC-0036: Owner approval of the handling of review findings R1 and R4 of WU-0020.8 (2026-10-20, owner statement relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The owner's words, verbatim: "r1 is ok" and "r4 is ok", given in answer to the two questions put with fix round 1 of WU-0020.8.

**Reading, for the owner to correct.**
1. **R1 (Q-N).** The findings document shows both stored Q-N readings per system (logit part and zero-indicator part), traces both, and says that the stored overall word `verdicts.Q-N` is built from the logit part only. `lpcstudy/report.py` is not changed. The collapse is recorded here as a reporting observation of the frozen report code, not as a defect and not as a change request.
2. **R4 (DEF-0027 count).** The findings document follows the official `RESULTS.md` and the DEF-0027 correction (negligible for 5 of 18 primary parts, not shown negligible for 13: not negligible 6, not certified 7; the projection is stated and not applied). `docs/study/proposal_and_methods_v3.md` section 8 is not edited. Its wording of the count differs from RESULTS.md; the difference is recorded here and in the constant's citation in `tools/findings/design_constants.json`.

**Affects:** WU-0020.8, the findings document sections 4 and 10, the pre-promotion audit scope (the v3 section 8 wording is a known difference, not an open finding). **Status:** owner statements; recorded pending the owner's ledger entry.

## DEC-0037: Owner authorizes the extension program (additional attractors, Dysts context) and the development ensemble (2026-10-20, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The owner's words, verbatim: "for item 1, ideally we should have 2 more attractors with different properties for 10/28. higher dimensionality, or any qualitative departure from the 3 we picked is preferred. Item 2 is a strong goal, I agree. Item 3 is also a strong demonstration. Based on the research we did previously, integrate these items into the roadmap and plan so we can agressively start implmenting them. we want item 1 done by 10/22. The otehrs may be implemented concurrently. Concurrent to that, launch the ensemble study."

**Reading, for the owner to correct.**
1. **The items** (main session's list of 2026-10-20): (1) a check of the three studied systems against the Dysts database (parameters, step convention, published exponents), which the owner's wording extends to two additional attractors with different properties, due 2026-10-22; (2) the same CP / PLP / A4 comparison on further Dysts systems; (3) a descriptive comparison with the Dysts forecasting benchmark. All three are exploratory: development seeds only, labeled development, never beside the sealed result, no change to the freeze, the sealed verdict or main. A confirmatory claim on new systems would need a new sealed seed and freeze, which is the owner's decision and not part of this authorization.
2. **First two additional attractors** (chosen by the main session from the ranked catalog of docs/agent/notes/2026-10-19-math-other-attractors.md; the owner may overrule): the hyperchaotic Rössler system (four dimensions, two positive exponents, Kaplan-Yorke dimension about 3: higher dimensionality) and Lorenz-63 at r = 166.1 (type-I intermittency: a bimodal local growth exponent, a qualitative departure). Rössler observed through z (observability spanning orders of magnitude, no new equations) is a cheap third configuration if time allows. Lorenz-96 with N = 8 is a stretch candidate and is not scheduled.
3. **Constraint carried into the plan.** Code changes for new systems are additive on develop: the three frozen systems and the confirmatory path must give bitwise equal outputs (smoke preset against the freeze-1 reference); nothing is merged to main, and the promoted document is built from freeze-1.
4. **Development ensemble.** Launched 2026-10-20: full preset on the GPU for DEV-1, DEV-3 and DEV-4 in turn, from a clean detached worktree at develop 3dec086 (lpcstudy/ identical to freeze-1), through tools/run_preset.sh under the GPU lock, concurrently with the CPU regeneration run-2 (host load does not change a run's bits at fixed thread counts). Development evidence only, for the labeled development appendix.

**Affects:** ROADMAP.md (new phase), queue.md, the findings document appendix A, the research statement, the poster outline. **Status:** owner instruction; recorded pending the owner's ledger entry. Amendments to ROADMAP.md need the owner's ledger `amendment` entry (ROADMAP.md is a governed file).

## DEC-0038: Owner confirms the per-system-only verdict branch and the two further review items of the extension code (2026-10-20, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The owner's words, verbatim, in answer to three items put by the main session: "Verdict code. Still pending: option (a), the per-system-only branch in report.verdicts. Owner review needed. Add these two items to the list: data.lyapunov_record (the lyapunov_steps field) and tests/slow/test_start_states.py. Timing risk. The S1 re-specification adds roughly an hour and a re-review. The ensemble is still on the GPU, so the 10/22 target holds if the batch can start tonight. Proceed with all."

**Reading, for the owner to correct.**
1. **Option (a) is approved:** in `lpcstudy/report.py`, a run that contains any extension system skips `statistics.overall_verdict` and stores per-system verdict words with the overall word "per-system only"; the path for runs inside the three frozen systems is unchanged (checked bitwise, WU-0021 Log). It may merge to `develop` after the independent review. It never goes to `main`.
2. **The two further items stay on the owner's review list** (verdict, seed and statistics code needs owner review, LPC.PC.11): the additive field `lyapunov_steps` in `data.lyapunov_record` (default 100000: the frozen systems are unchanged) and the edit of `tests/slow/test_start_states.py` (the control row generalized to dimension 4, plus the three new cases). The owner's instruction is to proceed with implementation, review and the runs meanwhile; the owner's own read of these hunks is not claimed as done.
3. **The S1 re-specification** (RK4 step and orbit bound, review finding R1 of WU-0021.7) and its re-review proceed; the batched GPU run starts after the ensemble when the code review of the extension is approved.
4. **Retraction.** The main session's earlier ruling that accepted a "2 to 5% per seed abort hazard" for S1 rested on a wrong mechanism (an integrator instability at the production step, not an escape to infinity: review R1) and is withdrawn.

**Affects:** WU-0021, WU-0023, the extension runs. **Status:** owner instruction; recorded pending the owner's ledger entry.

### DEC-0038 addendum A1 (2026-10-20, main session; correction found by the independent re-review of WU-0021.7, finding N4)

The entry above says option (a) "is approved". The owner's words quoted there are the main session's own list of three items (including "Verdict code. Still pending: option (a)" and "Owner review needed") repeated back, followed by "Proceed with all." The words do not state an approval of the code change as such. The correct reading, which replaces item 1 and item 2 of the reading above: the owner authorized the main session to proceed with implementation, review, merging to `develop` and the development runs of the extension program, with option (a) in place; the owner's own review of these four items is **still pending** and is not claimed as done: the verdict-reporting branch in `lpcstudy/report.py` (`report.verdicts` and the added `extension_text`), the additive field `lyapunov_steps` in `data.lyapunov_record`, and `tests/slow/test_start_states.py`. The change never goes to `main` without that review. The owner may correct this reading.

### DEC-0038 addendum A2 (2026-10-21, main session; finding R2 of the WU-0023 independent review)

The owner-review list of DEC-0038 addendum A1 gains: the names in `EXTENSION_SYSTEMS` in `lpcstudy/report.py` (verdict-reporting code; the new systems S4 `hindmarsh_rose`, S5 `hyper_jha`, S6 `lorenz96_4` are added there). Status: the owner's review is pending; the change never goes to `main` without it. Separately, S6 (4-variable Lorenz-96, F = 20) needs an owner ruling because LPC.PC.1 listed Lorenz-96 as out of scope; it is not merged to `develop` until the owner rules (WU-0023 review R1).

## DEC-0039: Owner rules S6 (4-variable Lorenz-96) in scope and allows concurrent development runs (2026-10-21, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The owner's words, verbatim: "S6 i sin scope. concurrent runs are allowed."

**Reading, for the owner to correct.**
1. **S6** (`lorenz96_4`, 4-variable Lorenz-96, F = 20) is in scope as a development-only extension system under DEC-0037 (an explicit exception to the earlier Lorenz-96 line of LPC.PC.1, for development seeds, never confirmatory, never main). WU-0023 review finding R1 is resolved by this ruling; the S4 to S6 branch may merge to `develop`.
2. **Concurrent runs** are allowed for DEVELOPMENT runs: up to two at once on the GPU (a second lock slot, `LPC_GPU_LOCK=/tmp/lpcstudy-gpu-2.lock`, through the unchanged wrapper), each logged with its out-dir and start time in the work log. The one-job lock stays exclusive for the sealed run, its cross-check and any production run (DEC-0034); a production or sealed run starts only when both development slots are idle. The 12 h and GPU-hour limits of LPC.AUTH.3 stay for development runs as before.

**Affects:** WU-0023, LPC.PC.1 reading, the run wrapper use, the second extension batch. **Status:** owner instruction; recorded pending the owner's ledger entry.

## DEC-0040: Owner rulings after the pre-promotion audit of the CONF-1 findings, and agreement with the theorem items (2026-10-21, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger entries are the owner's to append)

**Decision.** The owner's words, verbatim, in answer to the audit report `docs/agent/notes/2026-10-21-audit-pre-promotion-conf1.md`: "Fix B1 and present for review. M1 point me to the review location. M2 accept. the failure was the complexity of making the ledger entry. please develop a tool that make the ledger entry a simple one command tool that I can run from the tools/ directory, then add these process instructions to the README doc. M3 because this is a small team development, it is not feasible to have more than one human actor. this may be waived for this case, and in the future, an agent session may launch. M4 propose a solution and present for review. Fix all minor items. agree with theorem items 1-3".

**Reading, for the owner to correct.**
1. **M2.** The owner accepts that the CPU run of 2026-10-19 was launched by the owner, and accepts ledger seq 15 (entered 2026-10-20, marked retroactive) as its record. The cause was the effort of making the entry; the remedy is the one-command tool (WU-0030). A ledger `ruling` entry should state this (use the tool once it is merged).
2. **M3.** The requirement of v3 section 9 item 4 and LPC.PC.6 that the regeneration be by an actor other than the producer is **waived for CONF-1** because the team has one human actor (the owner ran both runs, DEC-0035). The waiver is for this case only. For future runs an agent session may launch the regeneration. A ledger `waiver` entry should record it. The promoted report must say that run-2 shows determinism (bitwise equal, same host, same environment, same actor), not an independent reproduction.
3. **M1.** Pointer given: the owner review packet is `docs/agent/notes/2026-10-18-owner-review-packet.md`; the tiers and unit list are in `docs/agent/notes/2026-10-18-freeze-blockers.md` section B2 (recommended reading: option 2, the `lpcstudy/` pipeline first, then tools; tools not reviewed are waived by ledger `waiver`); the four extension code items of DEC-0038 and its addenda are listed separately. The owner's review itself is pending.
4. **M4 and the minor items.** M4 is a proposal for review (`2026-10-21-def0022-proposal.md`); the fixes of the minor items and of B1 are in `2026-10-21-b1-minors-report.md` (units WU-0015 to WU-0018).
5. **Theorem items 1 to 3.** (1) The branches wu/theory-verify (WU-0027) and wu/theory-dumps (WU-0028) are merged to develop; WU-0029 (dump schema /3) is added to the ROADMAP. (2) The errata of the C1.2 draft are appended to `docs/study/theorem_program_lpc_v1.md` (dated, 6 October text unchanged); the C1.3 decision is taken as option C (keep the ln 2/(2Λ̄) row with the envelope and raw-C fixes, add P1(d′) as a verification row), implemented as WU-0031 on development seeds with acceptance criteria fixed in the draft, owner review of the statistics code before any use. (3) The audit and check fixes of WU-0027 (checks that cannot fail, stronger hypotheses than named, uncounted censored skips) go into WU-0029 and WU-0031 and are counted, not silent.

**Affects:** WU-0015 to WU-0018, WU-0027 to WU-0031, the promotion path, the audit. **Status:** owner instruction; recorded pending the owner's ledger entries.

## DEC-0041: Owner accepts DEF-0022 (the H2a(ii) power finding) as a known limitation and asks for proposals to improve the quality of the interval results (2026-10-21, owner instruction relayed by claude-sonnet-5-5 (main session); the ledger `ruling` entry is the owner's to append)

**Decision.** The owner's words, verbatim, in answer to `docs/agent/notes/2026-10-21-def0022-proposal.md`: "Accept, and propose new intervals to improve the quality of the results".

**Reading, for the owner to correct.**
1. **Accepted: option 1** of the proposal (accept as a known limitation, with the full-size evidence stated; text B for the promoted report; the same wording in section 10 of the findings document; no change to any verdict, band, level or number of the sealed run). If the owner meant option 2 (a per-part interval line in the report), say so.
2. **"New intervals to improve the quality of the results"** is read as a request for **proposals** for the design of future or development work, not as a change to the sealed analysis. The pre-registered intervals, levels, bands and rules of v3 and the sealed CONF-1 verdicts are not changed: a change after the result was seen would be a post hoc criterion (PRIME.2, VV.3). Proposals go to the applied-mathematician (WU-0032), are labeled post hoc and exploratory, are evaluated on development seeds or on stored sealed intervals only as arithmetic about power, and would apply to a future pre-registered study or to the development extension, after the owner's ruling.
3. After the owner's ledger entry: the defects status line of the DEF-0022 proposal (ii) is appended by the owner, the findings document is rebuilt with the ruled wording and checked.

**Affects:** DEF-0022, WU-0017 (report limitations list), WU-0032. **Status:** owner instruction; recorded pending the owner's ledger entry.

**Ledger (appended 2026-10-22, claude-sonnet-5-5, for DEC-0040):** the owner's entries are seq 30 (`ruling`, M2, quote "M2 accept. the failure was the complexity of making the ledger entry.", 2026-10-21T08:34:06Z) and seq 31 (`waiver`, M3, scope "CONF-1 only", quote "because this is a small team development, it is not feasible to have more than one human actor. this may be waived for this case, and in the future, an agent session may launch.", 2026-10-21T08:34:06Z). Seq 29 is the `amendment` entry of the same time.

**Ledger (appended 2026-10-22, claude-sonnet-5-5, for DEC-0041):** the owner's entry is seq 32 (`ruling`, source "decisions.md DEC-0041", quote "Accept, and propose new intervals to improve the quality of the results", 2026-10-22T08:14:14Z).

## DEC-0042: Owner entries of 2026-10-22 on the audit items M1, M3, m3 and the WU-0017 figure and gap findings (2026-10-22, recorded by claude-sonnet-5-5 from ledger seq 33 to 36)

**Decision.** The owner's words, verbatim, as they stand in the ledger (all 2026-10-22):
- Seq 33, `waiver`, source "audit M1", 08:15:21Z: "results were spot checked for agreement".
- Seq 34, `ruling`, source "audit M3", 08:16:26Z: "agent-based cross-checking is ok for this project".
- Seq 35, `note`, source "audit m3", 08:17:04Z: "plan amendment approved".
- Seq 36, `ruling`, source "promotion-figure-map.md; WU-0017 NVVUQ check", 08:18:05Z: "different intervals/dataset size will be needed in subsequent runs".

**Reading, for the owner to correct.**
1. **M1 (seq 33).** The entry is a `waiver` of the owner's code review of the verdict, statistics, seed and provenance code (LPC.PC.11 second tier; WU-0004.5; freeze checklist item 3). Its quote speaks of spot-checking results for agreement, not of reading the code. So the promoted report's verification and validation status must read: **"owner code review waived (ledger seq 33); results spot-checked by the owner; code covered by independent agent reviews"**. It must not say that the owner reviewed the code. DEF-0001 is not marked resolved by this entry (see the defects status line of the same date).
2. **M3 (seq 34, with the waiver of seq 31).** The owner accepts agent-based cross-checking for this project. This does not change the facts: run-2 was by the same actor on the same host in the same environment and shows determinism (bitwise equal compared leaves), not an independent reproduction. The report says so (DEC-0040 item 2).
3. **m3 (seq 35).** "Plan amendment approved" is read as approval of the amendment of 2026-10-20 (A6: the source name `official_words` may be quoted inside the cross-check section of the findings document; WU-0020 log and `WU-0020-review.md`). If it meant another amendment, say so.
4. **WU-0017 figures and gaps (seq 36).** The quote is read as: the owner accepts the gaps G1 to G3 (no numerical-error estimate or per-QoI V&V status for the secondary rows, and the unclear status wording of the secondaries) and the figure captions as sealed output, carrying the figure map in the report text, and notes that later runs will need different intervals and sample sizes (see DEC-0041 item 2: proposals, WU-0032). It is not read as a change to the sealed analysis. The unexplained 5% criterion line of `regret_vs_regimes.png` stays open and is not repeated as a criterion.

**Affects:** WU-0017, WU-0018, WU-0020 (findings document section 10), DEF-0001, the promoted report's limitations and V&V status. **Status:** recorded from the owner's ledger entries; the reading is for the owner to correct.

## DEC-0043: Owner chooses option (a) for the findings figures of the promoted copy (2026-10-22, owner instruction relayed by claude-sonnet-5-5 (main session))

**Decision.** The owner's words, verbatim, in answer to the three options of section 9 of `docs/agent/notes/2026-10-22-promotion-proposal.md`: "option a".

**Reading, for the owner to correct.** Option (a): the three findings figures F1 to F3 are re-rendered with a promoted status title for the promoted copy (WU-0034: `findings_build.py promote`, separate output folder, preliminary figures untouched, byte-reproduction and zero-tolerance pixel check outside the title band). The `RESULTS.md` figures are copied as they are (they carry no status text). The promoted report's provenance row keeps the stored label of the sealed file. Option (c) (omit the figures) is the fallback only if promotion has to precede WU-0034.

**Affects:** WU-0033, WU-0034, WU-0018.2, WU-0018.3. **Status:** owner instruction; no ledger entry is required for this choice (a design choice for the report copy, no governed file changes); the owner may add a ledger `note` if wanted.

## DEC-0044: Promotion of the CONF-1 run-1 result (2026-10-23, recorded by claude-sonnet-5-5 from ledger seq 37 to 40)

**Decision.** The CONF-1 run-1 result (official CPU run, `ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe`; `RESULTS.md` `2a4c1d06859d07584b1633c6e7f1b5df205ffe445402509834383fb474649577`) is promoted. The owner's act is the ledger entry, not words recorded here: seq 40, type `promotion`, 2026-10-23T09:37:12+00:00, `promoted` true, `proposal_seq` 39, `reading_recorded` "WU-0017.3 dated line" (commit 03edc09). Seq 39 is the proposal (WU-0018.2; `promoted` false, rulings 30, 32, 34, 36, waivers 31, 33).

**Audits.** `docs/agent/notes/2026-10-21-audit-pre-promotion-conf1.md` and `docs/agent/notes/2026-10-22-audit-promotion-conf1.md` (zero blockers; GO for the proposal; promotion deferred to the owner-side items, now done).

**Ruled limitations carried by the promoted report.** Same host, environment and actor for run-1 and run-2: determinism, not independence (waiver seq 31, ruling seq 34, DEC-0035); owner code review waived, results spot-checked by the owner, DEF-0001 open (waiver seq 33); the risk and expiry of waivers 31 and 33 (note seq 37/38: expiry at the owner code review record or the end-of-project governance review, WU-0019.2); retroactive authorization of the official run accepted (seq 15, ruling seq 30); DEF-0022 power finding accepted as a known limitation, labeled development evidence (ruling seq 32); NVVUQ.22 gaps G1 to G3 and the four sealed figure captions with the figure map in the report text (ruling seq 36); Q-N two readings (DEC-0036, seq 24); DEF-0027 iterative error not estimated.

**Duplicate entries.** Seq 37 (2026-10-22T09:56:05Z) and seq 38 (2026-10-23T09:31:31Z) are the same owner note (waivers 31 and 33: risk accepted and expiry); it was entered twice. The wording of seq 38 is the fuller one. The duplicate is harmless: the chain is intact and both name the same waivers. No entry is altered.

**Files.** Promoted copies in `promoted/CONF-1/`, hashes in `promoted/CONF-1.sha256`; manifest line of 2026-10-23 names entry 40; originals under `runs/confirmatory/run-1/` unchanged. Main synced at d75b8be. Close-out: `docs/agent/notes/2026-10-23-promotion-closeout.md`.

**Affects:** WU-0015 to WU-0018, results manifest, what may be stated publicly. **Status:** recorded from the ledger; the owner's act is seq 40.

## DEC-0045: Development appendix A is a standalone document; recommended answers applied to the 10/28 materials (2026-10-23, main session, under the owner's instruction)

**Decision.** The owner's words, verbatim: "fix all open questions with the recommended fixes. for the purposes of this study, no further bureaucracy is needed from me. advance as quicklly as possible to the definition of done".

**Reading, for the owner to correct.**
1. **Standalone appendix.** The review of WU-0025.1 (finding R2) showed that a rendering hosted by the DEV-2 development run cannot serve as the poster handout. The main session decided, under the instruction above, that appendix A is a **standalone document** built by `tools/findings_build.py appendix` (WU-0025.7), not a section of the sealed findings document. ROADMAP WU-0025.5 and its definition of done ("with the sealed inputs", "the sealed document is rebuilt with appendix A") are superseded in practice by this decision; ROADMAP.md is a governed file and is not edited (an `amendment` would be the owner's act if wanted). The sealed findings document and the promoted copy are unchanged.
2. **Recommended answers applied** to the open questions of the research statement and poster drafts: promotion label "Confirmatory result, seed CONF-1, promoted by the owner on 2026-10-23"; appendix A includes S1 to S6 with S2 to S6 marked PROVISIONAL (stored gate V7 false); panel 12 goes on a handout or the back of the board, apart from F1 to F3; appendix A reprints no sealed value and points to section 5 of the promoted report; panel 12 says the extension's verdict-reporting code is development-only and not owner-reviewed; the student text says "a subsequent pre-registered study", not "v4".
3. **Not waived.** The owner's pending review of the extension code (DEC-0038 A1, A2) is not waived by this instruction; it requires a ledger entry. The extension code stays development-only and never goes to main.

**Affects:** WU-0025, the 10/28 materials. **Status:** owner instruction; no ledger entry required for these design choices.
