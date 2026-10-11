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
