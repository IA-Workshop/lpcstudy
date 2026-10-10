---
name: dev-run
description: "Runs an lpcstudy preset on a registered development seed with provenance and the compute limits of LPC.AUTH.3. Use for smoke checks, pilot-size rehearsals, and precision estimates. Never for confirmatory runs."
argument-hint: "[preset: smoke|pilot|full] [seed id: DEV-n]"
arguments: preset seed
---

Run preset **$preset** on development seed **$seed**.

Registered development seeds:
!`python3 -c "import json; [print(s['id'], s['status'], '-', s['use']) for s in json.load(open('seeds/development_seeds.json'))['seeds']]"`

Running presets:
!`pgrep -fa "lpcstudy --preset" || echo "no preset running"`

GPU:
!`nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader 2>/dev/null || echo "no NVIDIA GPU visible"`

## Steps

1. **Check the seed.** Confirm that `$seed` is listed above. Refuse anything else, including raw integers and anything called CONF (LPC.PC.7).
2. **Check the compute limit.** `smoke` is free. For `pilot` or `full` (LPC.AUTH.3):
   - estimate the wall-clock time: the pilot took about 70 min on 2 CPU cores, and GPU runs are faster;
   - confirm it is under 12 h;
   - sum this week's GPU-hours from previous `run.log` files and confirm the total stays under 60.

   If either limit would be exceeded, stop and `/refer`.
3. **Run** with `tools/run_preset.sh $preset $seed runs/dev/$seed`. Until that wrapper exists (WU-0012):
   - **smoke** (CPU): `python -m lpcstudy --preset smoke --seed-id $seed --out runs/dev/$seed`.
   - **pilot or full** (GPU, background):

     ```
     nohup flock -n /tmp/lpcstudy-gpu.lock env JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_PREALLOCATE=false timeout 12h python -m lpcstudy --preset $preset --seed-id $seed --out runs/dev/$seed > runs/dev/$seed.log 2>&1 &
     ```

     If the lock is held, do other work. Do not wait.
   - Until WU-0001 adds `--seed-id`, only DEV-0 is possible: omit the flag, and note in the log that the v1 default seed 20261005 was used.
   - Poll with `tail -n 5 runs/dev/$seed.log` every few minutes. Never stream the log.
4. **Check the outputs.** The provenance block is present; the validation gate passes, or its failure is reported; the header label reads `DEVELOPMENT ($seed): not a hypothesis test`.
5. **Log** the command, wall-clock time and peak memory, the gate status, and the output path in the active unit file. Summarize the key numbers in at most 10 lines.

Outputs under `runs/dev/` are regenerable and MAY be deleted later (LPC.EXC.2), unless a record cites them.
