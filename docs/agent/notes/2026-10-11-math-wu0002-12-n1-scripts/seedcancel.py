"""Scratch: analog_seed-like distances in whitened coordinates (cancellation) under the
whitening matrix of this process's OpenBLAS kernel; saves them for comparison across kernels."""
import json, sys, tempfile
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from lpcstudy.config import PRESETS
from lpcstudy.data import build_context
system, out = sys.argv[1], sys.argv[2]
RUN = "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/pilot-dev0/runs/dev/wu0002-12/pilot/results.json"
lam = json.load(open(RUN))["systems"][system]["context"]["lambda_max"]
cache = Path(tempfile.mkdtemp(dir=Path(out).parent)); (cache / "lyapunov.json").write_text(json.dumps({system: lam}))
ctx = build_context(system, PRESETS["pilot"], cache)
truth = ctx.eval_states[ctx.split_indices["test"]]
lib = ctx.library_states[:100_000]
_, idx = cKDTree(lib).query(truth, 10)            # 10 nearest library states (state space)
analog = lib[idx].mean(axis=1)                     # mean of the 10, as the CP analog mean
seed = np.sqrt(np.sum((ctx.whiten_states(analog) - ctx.whiten_states(truth))**2, axis=1))
np.save(out, seed)
print(system, "median analog seed (whitened)", float(np.median(seed)))
