# lpcstudy — v1 research code

> **Development bundle (2026-10-10).** This is the v1 code as run for the pilot, plus governance (`docs/agent/governance/`), work records (`docs/agent/records/`), seeds (`seeds/`) and study documents (`docs/study/`). Start with `.claude/CLAUDE.md` (Claude Code reads it automatically). The study design is now v3. The hypothesis identifiers below are the v1 ones, which WU-0002 updates.


This is the working prototype for the pilot study **"State-dependent allocation between an analog (CP) and a physics-based (PLP) forecaster via local predictability conditions"**.

It runs proposal stages (i)–(v) end to end:

- (i) system generation;
- (ii) mechanism validation;
- (iii) allocation and horizon testing;
- (iv) state abstraction and benchmarking;
- (v) robustness and cross-system transfer.

It then evaluates every pre-registered hypothesis (H1a–H3d, T1) and writes a results report.

The Methods document (`methods_experimental_procedures_v1.md`) is the specification. Every constant lives in `lpcstudy/config.py`.

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
- `--skip-transfer` and `--skip-robustness` skip stage (v).

On a CUDA machine, `pip install "jax[cuda12]"`; the code runs unchanged. All computations use float64.

## Layout

| Module | Contents |
|---|---|
| `config.py` | `StudyConfig`; presets `full`, `pilot`, `smoke` |
| `systems.py` | Lorenz-63, Rössler, Chua, Lorenz-96; RK4 flow maps; Benettin λ_max |
| `embedding.py` | delay vectors; AMI delay selection; autocorrelation time |
| `data.py` | trajectories, normalization, whitening, library/construction/calibration/test splits |
| `networks.py` | MLP training (learned initial guess of ψ; error-predictor allocator) |
| `estimation.py` | ψ = learned initial guess + Levenberg–Marquardt refinement with the model |
| `dynamics.py` | batched forecasts; amplifier g_H; growth exponents; observability ν (forward formula) |
| `ensemble.py` | CP library; per-draw forecasts; oracle moments; evaluation draws with deployable features |
| `oracle.py` | oracle state quantities; w*, curvature; characteristic and realized horizons |
| `allocation.py` | rules A0–A5, A4f, A4o, A*; seed proxies; regime trees |
| `pipeline.py` | `Study` (caches, cells), rule fitting, scoring |
| `analysis.py` | statistics behind every hypothesis |
| `experiments.py` | stage orchestration; transfer; robustness |
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
