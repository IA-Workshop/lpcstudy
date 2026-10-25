# LPC Study (`lpcstudy`)

`lpcstudy` is the research code for a science-fair mathematics study. It compares an analog forecaster (CP) with a physics-based forecaster (PLP) on Lorenz-63, Rössler and Chua, and tests whether four local predictability conditions decide how to blend them.

- **Consequence class:** CSQ2. Development work on DEV seeds is CSQ3.
- **Governance:** `docs/agent/governance/`.
- **Profile:** numerical VVUQ, `LVL1-profile-NVVUQ.md`.

## Start every session

Run `/start-session`. If governance is not adopted, or the ledger chain is broken, take only free actions and tell the owner (LPC.AI.1).

## IMPORTANT

- **Development seeds only.** Never draw, read or run the confirmatory seed, and never use `--confirmatory` (LPC.PC.7).
- **Web access is reserved to the `researcher` agent.** A hook blocks it everywhere else. Use `/verify-citation` or dispatch `researcher`.
- **Never rewrite history.** No amend, rebase, force or reset --hard: make a new commit. Records and the ledger are append-only (PRIME.5).
- **Blast radius only.** Never run the full test suite outside a gate, and never rerun a test without a code change. Use `/test-impact` first (`.claude/rules/test-discipline.md`).
- **GPU slots.** Development runs use at most two GPU slots, each under its own lock (`LPC_GPU_LOCK=/tmp/lpcstudy-gpu.lock` or `/tmp/lpcstudy-gpu-2.lock`; DEC-0039). A sealed run takes the GPU alone. Everything else runs on CPU (the default in settings).
- **Never loosen a test, tolerance or criterion to pass** (PRIME.2). Never clip, replace or skip silently: count it and report it (PRIME.4).

## Commands

```
/test-impact                                           # compute and run the blast-radius tests (never the whole suite)
python -m lpcstudy --preset smoke --out runs/dev       # plumbing check (~1 min)
/dev-run pilot DEV-1                                   # GPU, background, under the lock (LPC.AUTH.3)
python3 tools/ledger.py verify && python3 tools/ledger.py status
```

- Runs take `--seed-id DEV-n` from `seeds/development_seeds.json`.
- On the GPU workstation, use `jax[cuda12]==0.11.2`.
- The owner sets up `.venv` once with `pip install -r requirements.txt`. Further installs prompt.

## How work flows

- **Plan and status.** `ROADMAP.md` is the plan. CONF-1 (phases A–G) is promoted (ledger seq 40). The current work is phase I, the follow-on extension study and ablations: it has no deadline and runs until done.
- **Minimal formality** (ledger seq 42). Do the work directly with one agent per task, fix accuracy problems found, and move on. Review rounds, audits, unit-file logs, decision and incident records and manifest bookkeeping are not required unless the owner asks. Acceptance criteria are still fixed before results are seen.
- **What stays.** The sealed seed and its script are the owner's; the ledger chain; verdict words and labels exactly as stored; development numbers never beside a sealed result; merges to `main` only with the owner's authorization.
- **Ledger.** The main session appends entries that record statements the owner approved in chat, quoting the approving words (ledger seq 41).
- **Commits.** Commit often on unit branches and `develop`. Messages name the unit and end with `Agent: <model id>`.

## Code conventions

- **Python 3.13, NumPy-style docstrings, type annotations,** descriptive names of at most three words.
- **float64 throughout.** Randomness only via `lpcstudy.data.make_rng(seed, *labels)`.
- **Units and conventions.** Time is in steps (1 Lyapunov time = 30 steps). Noise ρ is a fraction of σ_x. Latent states are whitened. Errors are measured against the noise-free truth.
- **Tests** name an independent reference and justify their tolerance (skill `numerical-test`).

## Design documents

These are in `docs/study/`:

- the governing design: proposal and methods v3 (export from the Claude Doc if absent);
- Methods v2: amendment log and code-change list;
- the decision log, which maps hypothesis identifiers between v2 and v3;
- the pilot results.

Code follows the documents.

## When compacting

Preserve:

- the active unit id and its plan;
- the list of modified files;
- the test commands run, with their results (the last test set and its summary line, so it is not rerun);
- any pending referral.
