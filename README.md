# lpcstudy: when should a forecaster trust the past, and when the physics?

`lpcstudy` is the research code, records and results of a study that compares an **analog forecaster (CP)**, which looks up similar situations in a library of past data, with a **physics-based forecaster (PLP)**, which uses the known equations. It tests whether four local predictability conditions decide how the two should be blended, on three chaotic systems: Lorenz-63, Rössler, and Chua's circuit.

## The result (CONF-1, promoted 2026-10-23)

The design was written down and frozen before the confirmatory run (tag `freeze-1`, `docs/study/proposal_and_methods_v3.md`). The run used a sealed random-number seed. The three primary hypotheses read:

| Hypothesis | Overall word | Lorenz-63 | Rössler | Chua |
|---|---|---|---|---|
| H2a | **not supported** | fail | fail | fail |
| H2b | **supported** | pass | pass | pass |
| H3c | **inconclusive** | inconclusive | pass | inconclusive |

"Not supported" is not "disproved", and "inconclusive" does not mean "no effect". "Supported" means that on these three systems, with an exact physics model and one measured variable, the pre-registered prediction held in this run. It does not show the same for other models, real data, higher-dimensional systems or other seeds.

**Read the promoted report:** [`promoted/CONF-1/report.md`](promoted/CONF-1/report.md) (figures in `promoted/CONF-1/report.figures/`), and the code's own report [`promoted/CONF-1/RESULTS.md`](promoted/CONF-1/RESULTS.md). All numbers are in [`promoted/CONF-1/results.json`](promoted/CONF-1/results.json).

### Limitations, as ruled

- Three low-dimensional systems, one observable, one sealed seed (one realization per system).
- The second part of H2a has low power: it can be refuted but essentially cannot pass.
- The regeneration of the run was by the same person on the same computer: it shows determinism (bitwise equal), not an independent reproduction. Results depend on thread count and the computer's linear-algebra library.
- The owner's code review was waived; the owner spot-checked the results, and the code was covered by independent AI-agent reviews.
- The secondary and reported rows carry no per-quantity numerical-error estimate or verification status.
- The four built-in report figures name no experiment or hypothesis and show no interval.
- A subsequent pre-registered study will need different intervals and sample sizes.

## How the result was checked

- A hash-chained, append-only ledger of every decision: `docs/agent/governance/ledger.jsonl` (`python3 tools/ledger.py verify`).
- The official CPU run and a regeneration at the same commit gave bitwise-equal results (20766 of 20766 leaves equal); a GPU cross-check agreed statistically. Records: `docs/agent/records/results-manifest.md`.
- Every number in the findings document is traced to a leaf of `results.json`: `docs/agent/notes/2026-10-20-prelim-findings-conf1.md` (the file keeps its pre-promotion name; `promoted/CONF-1/report.md` is the promoted copy) with its `.trace.csv` and `.sources.json`. Check with `python3 tools/findings_build.py check docs/agent/notes --stem 2026-10-20-prelim-findings-conf1`.
- Two audits: `docs/agent/notes/2026-10-21-audit-pre-promotion-conf1.md` and `docs/agent/notes/2026-10-22-audit-promotion-conf1.md`.

## Development context (not part of the result)

After the pre-registered run, six further chaotic systems and a development ensemble on other seeds were run as an exploration. These are on **development seeds only, exploratory, never confirmatory**, with per-system readings only and no overall verdict; five of the six extension systems failed a validity check and are marked PROVISIONAL. They are described in `docs/agent/notes/2026-10-23-appendix-a-standalone.md` and `docs/agent/notes/2026-10-23-extension-ensemble-summary.md`, and never appear beside the result above. The extension code lives in `lpcstudy/systems.py` and `lpcstudy/report.py` as additive entries; the three studied systems are unchanged from the frozen pipeline.

## Reproduce

```bash
pip install -r requirements.txt
python -m lpcstudy --preset smoke --out results        # plumbing check (about 1 min)
```

The full-size official run took about 4.3 hours on a CPU. The sealed seed itself is not in this repository; only its hash commitment is in the ledger.

## Where things are

| Path | Contents |
|---|---|
| `lpcstudy/` | the study code |
| `docs/study/` | the frozen design (v3), methods, pilot results |
| `promoted/CONF-1/` | the promoted result |
| `runs/confirmatory/` | the official run, the GPU cross-check and the regeneration (force-added outputs) |
| `docs/agent/` | governance, decisions, defects, notes, audits |
| `tools/` | ledger, findings builder, run wrappers |
| `tests/` | unit, integration, slow and GPU tests |

## Install and run

```bash
pip install -r requirements.txt                    # pinned (LPC.PC.17)
pytest -q tests                                   # unit tests (about 5 s)
python -m lpcstudy --preset smoke --out results   # end-to-end plumbing check (about 1 min)
python -m lpcstudy --preset pilot --out results   # pilot sample sizes (about 70 min, 2 CPU cores)
python -m lpcstudy --preset full  --out results   # study sample sizes (hours on CPU; use a GPU)
python -m lpcstudy --preset pilot --out results --report-only   # rebuild report from results.json
```

Useful options:

- `--systems lorenz63 rossler` restricts the core systems.
- `--skip-robustness` skips stage (v).

On a CUDA machine, `pip install "jax[cuda12]"`; the code runs unchanged. All computations use float64.

## Layout

| Module | Contents |
|---|---|
| `config.py` | `StudyConfig`; presets `full`, `pilot`, `smoke` |
| `systems.py` | Lorenz-63, Rössler, Chua; RK4 flow maps; Benettin λ_max |
| `embedding.py` | delay vectors; AMI delay selection; autocorrelation time |
| `data.py` | trajectories, normalization, whitening, library/construction/calibration/test splits |
| `networks.py` | MLP training (learned initial guess of ψ; error-predictor allocator) |
| `estimation.py` | ψ = learned initial guess + Levenberg–Marquardt refinement with the model |
| `dynamics.py` | batched forecasts; amplifier g_H; growth exponents; observability ν (forward formula) |
| `ensemble.py` | CP library; per-draw forecasts; oracle moments; evaluation draws with deployable features |
| `oracle.py` | oracle state quantities; w*, curvature; characteristic and realized horizons |
| `allocation.py` | rules A0–A5, A4o, A*; seed proxies; regime trees |
| `pipeline.py` | `Study` (caches, cells), rule fitting, scoring |
| `analysis.py` | statistics behind every hypothesis |
| `experiments.py` | stage orchestration; robustness |
| `validation.py` | validation gate V1–V6 |
| `statistics.py` | Kaplan–Meier, log-rank, Holm, block bootstrap, partial correlation |
| `report.py` | verdicts, `RESULTS.md`, figures |

## Outputs

`results/<preset>/` contains:

- `results.json`: all numbers.
- `RESULTS.md`: hypothesis table, rule scores, validation and robustness tables.
- `figures/*.png`
- `run.log`

## Conventions

- Time is measured in observation steps; 1 Lyapunov time = 30 steps for every system.
- Observations are in units of σ_x; latent quantities are in whitened coordinates. Seeds, ν, g_H and the profile are therefore dimensionless.
- The weight w is always the weight on CP.
- Errors are measured against the noise-free truth. Realized horizons use the noisy verifying observation.
