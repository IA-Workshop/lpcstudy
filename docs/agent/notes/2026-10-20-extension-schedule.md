# Extension program schedule, 2026-10-20 to 2026-10-28 (phase H, DEC-0037)

**Author:** planner (claude-opus-5-5), 2026-10-20, written at about 05:40 local. **Units:** WU-0021 to WU-0026 (ROADMAP §8). All work is development work and exploratory. The sealed track (WU-0016 to WU-0018, promotion about 10-25 under D5) has priority for the main session, the reviewer and the CPU.

## 1. Resources

- **GPU.**
  - The development ensemble (WU-0026) has held the lock since 05:31: DEV-1, DEV-3 and DEV-4 in turn, about 45 min each. The GPU should be free at about **08:00 to 08:30**.
  - After that, the extension's GPU jobs queue in the order of §3.
  - Each job goes through `tools/run_preset.sh`. A job never waits on the lock; if the lock is busy, the agent does other work.
  - The GPU-hour use is small: about 2.5 h for the ensemble, about 2.5 h for WU-0021, and about 2 to 3 h for WU-0023. The weekly cap is 60 h.
- **CPU.**
  - Run-2 (WU-0016.2, sealed track, 8 threads) runs until about **this evening**.
  - Until it ends, every scratch job, unit radius and smoke runs with `LPC_THREADS=1` under `nice -n 19`.
  - The integration tier, the slow tests and any second smoke wait until run-2 ends.
  - No CPU `pilot` or `full` run is started while a GPU run is active (LPC.AUTH.3, one run at a time). Extension pilots and full runs therefore run on the GPU only.
- **Thread count of R1.** The reference smoke (WU-0021.3) and every regression smoke (WU-0021.5, WU-0023.3) use `LPC_THREADS=1`, even after run-2 ends. Bitwise equality is promised only at a fixed thread count.

## 2. Day by day

| Day | Track A (WU-0021, critical) | Other tracks | GPU | CPU |
| --- | --- | --- | --- | --- |
| **Tue 10-20** | AM: .1 researcher and .2 specification land; .3 reference smoke. PM: .4 implementation; .5 R1 regression and the plumbing smokes. Evening: .6 pilot (both systems) | F: .1 and .2 when the ensemble ends. E: .1 tool extension starts. B: .1 researcher | ensemble until about 08:00; .6 pilot at about 17:00 to 19:00 | run-2: one thread for scratch; integration tier of .4 after run-2 ends |
| **Wed 10-21** | .7 review and fix rounds; merge to `develop`; .8 full run S1, then S2, from a clean worktree at the merge | B: .2 attribution. D: .1 researcher. E: .1 done | .8: about 1 to 1.5 h | free after run-2 (sealed WU-0016.3 and .4 compare first) |
| **Thu 10-22** | **.9 development note; Track A DONE (due)** | C: .1 recommendation, O9 cap, .2 specifications. D: .2 mapping. E: .2 review of the tool | — | — |
| **Fri 10-23** | — | C: .3 implementation (one change set) and R1. E: .3 statement paragraph. D: .3 table | — | regression smoke at one thread; integration tier |
| **Sat 10-24** | — | C: .4 review, then pilots. **D done (target).** E: .4 poster outline | C pilots, about 0.5 h each, in sequence | — |
| **Sun 10-25** | buffer | C: pilots finish; gate readings. Sealed track: promotion target (D5) | C pilots | — |
| **Mon 10-26** | — | **C: .5 appendix table (target).** E: .5 build, **inputs cut off at 18:00** | free | — |
| **Tue 10-27** | — | E: .6 review of the appendix; student edits statement and outline; poster and slides | — | — |
| **Wed 10-28** | — | internal proposal | — | — |

**Critical path.**

1. WU-0021.2 (specification) → .4 → .5 (R1) → .6 (pilot, GPU) → .7 (review) → .8 (full runs, GPU) → .9: Track A, done 10-22.
2. Then WU-0023.2 → .3 → .4 (GPU pilots) → .5, done 10-26.
3. Then WU-0025.5 → .6, done 10-27.

The 10-22 date has slack of about half a day. The tightest points are the .2 specification arriving by about noon on 10-20, and the review on 10-21 (two fix rounds at most).

## 3. GPU queue (in order; each job starts only when the previous one ends)

1. Ensemble DEV-1 → DEV-3 → DEV-4 (running; WU-0026).
2. WU-0021.6 pilot, DEV-3, S1 and S2 (one run, `--systems`; about 0.5 to 1 h).
3. WU-0021.8 full run, S1, DEV-3 (about 0.6 h, at ×1.5 to 2.5 the cost of a 3-D system).
4. WU-0021.8 full run, S2, DEV-3 (about 0.4 h; the intermittency may lengthen the trajectory, risk K4).
5. WU-0021.4b, S3: smoke on the CPU, then a pilot. Only if 2 to 4 have passed by 10-21 noon.
6. WU-0023.4 pilots, one per system (about 0.3 to 0.6 h each).

## 4. When Track A fails: what moves and what is dropped first

The drop order is fixed now. Nothing is retuned to keep a date (PRIME.2).

1. **S3 goes first.** It starts only if S1 and S2 pass R1 and the pilot by 10-21 noon. Otherwise it is not done before 10-28.
2. **If R1 (the bitwise regression) fails** and one fix round does not restore it, the extension code is not merged. No extension number appears in the 10/28 materials. Appendix A then shows only the ensemble (WU-0026) and the Dysts context (WU-0022, WU-0024). Those two do not depend on extension code.
3. **If WU-0021 is not done by 10-22 end of day,** WU-0023 starts only after it, and its set shrinks to what can be piloted by 10-25 18:00: first to two systems, then to none. The full runs of WU-0021.8 can fall back to the pilot (.6) in the appendix, labeled "pilot preset".
4. **A gate failure is not a Track A failure.** A system that fails V1 to V7 is reported as provisional with its gate statistics. That is a result.
5. **The cutoff for 10/28** is 10-26 18:00. An input not reviewed by then is not in appendix A. It may appear in the research statement only as a number-free sentence of future work.
6. **The sealed track is not delayed** by any of this.

## 5. Risks and owner decisions

**Risks.**

| Id | Risk | Mitigation |
| --- | --- | --- |
| K1 | Extension code changes the frozen pipeline silently | R1: a bitwise three-system smoke (DEV-0, CPU, one thread) against the WU-0021.3 reference made from code equal to `freeze-1`, repeated after every fix round. R2: additivity of the `lpcstudy/` diff (no deleted line except named ones). R3: pins of the frozen specs and presets. The confirmatory path itself is never run (LPC.PC.7); `__main__.py`, `seeds.py` and `provenance.py` are out of the diff. |
| K2 | A sealed-track document is built from extension code | WU-0017 and WU-0018 run `--report-only` and the findings build from a worktree at `freeze-1`, or after checking `git diff --quiet freeze-1 -- lpcstudy/`. The extended findings tool must reproduce the committed sealed document byte for byte (WU-0025 E1). The main session adds this check to the WU-0017.1 log. |
| K3 | Constitution scope (LPC.PC.1 lists new systems as out of scope) | The owner's ruling, O1. Until it is recorded, the developer may start WU-0021.3 and .4 on a branch (development work), but nothing merges and no pilot or full run starts. |
| K4 | S2's laminar phases lengthen the autocorrelation time, the spacing and the trajectory; λ converges slowly (SE about 8% at 60 000 steps, math note) | A per-system Lyapunov run length (R2 exception (i)); the pilot measures wall clock and memory before the full run; the 12 h cap of the wrapper. If the SE stays above 1%, it is reported as uncertainty in the time unit. |
| K5 | S1 with D = 7 may not embed (d_KY about 3.0; Embedology needs d_box < 3.5) | V2 and V7 decide. A failure is provisional and is reported, never retuned to D = 9. Changing D would be a new specification and an owner decision. |
| K6 | CPU contention with run-2 slows the unit radius and the smokes | One thread, niced. The integration tier is deferred to the evening and logged as deferred (§4.8). |
| K7 | Reviewer and main-session time are shared with the sealed track | The sealed track first. WU-0025.5 is the only extension step the main session must do before 10-28. |
| K8 | Extension numbers drift into the main body or the poster's main panels | D4. WU-0025 E4 (`check` refuses development sources outside appendix A), E7 (labels) and the honesty checklist. |

**Owner decisions.** Each has a planner default, applied unless the owner rules otherwise.

| Id | Decision | Planner default (recommendation) |
| --- | --- | --- |
| O1 | Scope route under LPC.PC.1 | A spin-off (constitution wording), recorded in the DEC-0037 ledger `ruling`. Lorenz-96 and the misspecified arm stay out. Alternative: an amendment of LPC.PC.1. |
| O2 | Where the extension code lives | **`develop`, never merged to `main`** (main stays reserved for fully green configurations). R1 to R3 protect the frozen pipeline, and K2 protects the sealed builds. A long-lived branch would avoid any trace on `develop`, but it costs repeated merges of develop's tool fixes and a second integration surface. Not recommended. |
| O3 | Seed for the extension runs | DEV-3 for every pilot and full run of WU-0021 and WU-0023 (math note §C.3). No seed-to-seed replicate of the new systems before 10-28. |
| O4 | Dysts as a dependency | Not installed (LPC.PC.17). Values are transcribed by hand with a citation and the data-file version. |
| O5 | Development numbers in the 10/28 materials | Only in the labeled appendix (D4). The research statement stays number-free. |
| O6 | Compute concurrency | Extension pilots and full runs on the GPU only, behind the lock. CPU smokes at one thread while run-2 is active. No CPU pilot during a GPU run. |
| O7 | Seed-to-seed spread of the ensemble | Stored values side by side. No mean, standard deviation or range is computed. |
| O8 | S3 (Rössler observed through z) | Optional, and only after S1 and S2 pass. Its one-line change to the orbit-guard check (DEF-0015) needs the owner's glance. |
| O9 | The number of further Dysts systems (WU-0023) | At most 4, chosen by the selection rules of WU-0023 |

**Ledger entries the owner appends.** These are not appended by agents.

- The DEC-0037 `ruling`, with O1 and the restatement of what stays out of scope.
- The `amendment` for ROADMAP.md §8, with the new SHA-256.
- Optionally, one entry that adopts O2 to O9 as defaults.
