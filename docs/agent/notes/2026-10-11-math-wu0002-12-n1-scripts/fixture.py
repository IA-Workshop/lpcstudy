"""Scratch (WU-0002.12 N1 analysis): rebuild a system context on this machine with the run's
lambda, then evaluate V1 and V2 exactly as experiments.py does, plus digests of the oracle
gains. Prints JSON. Read-only use of lpcstudy; writes only into a scratch cache dir."""
import hashlib, json, sys, tempfile, time
from pathlib import Path
import numpy as np

system = sys.argv[1]
what = sys.argv[2] if len(sys.argv) > 2 else "all"
RUN = "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/pilot-dev0/runs/dev/wu0002-12/pilot/results.json"
new = json.load(open(RUN))["systems"][system]
lam = new["context"]["lambda_max"]

from lpcstudy.config import PRESETS
from lpcstudy.data import build_context
from lpcstudy.validation import check_jacobians, check_cramer_rao
from lpcstudy.oracle import state_oracles

cache = Path(tempfile.mkdtemp())
(cache / "lyapunov.json").write_text(json.dumps({system: lam}))
t0 = time.time()
ctx = build_context(system, PRESETS["pilot"], cache)
out = {"system": system, "build_s": round(time.time() - t0, 1),
       "obs_scale_equal_run": ctx.obs_scale == new["context"]["obs_scale"],
       "interval_equal_run": ctx.interval == new["context"]["interval"],
       "whiten_sha": hashlib.sha256(ctx.whiten.tobytes()).hexdigest()[:12],
       "unwhiten_sha": hashlib.sha256(ctx.unwhiten.tobytes()).hexdigest()[:12]}
if what in ("all", "v"):
    out.update({k: repr(v) for k, v in check_jacobians(ctx).items()})
    out.update({k: repr(v) for k, v in check_cramer_rao(ctx).items()})
if what in ("all", "o"):
    o = state_oracles(ctx, "test", PRESETS["pilot"].steps_per_lyapunov)
    np.save(cache / "gains.npy", o.gains); np.save(cache / "growth.npy", o.growth)
    out["gains_sha"] = hashlib.sha256(o.gains.tobytes()).hexdigest()[:12]
    out["growth_sha"] = hashlib.sha256(o.growth.tobytes()).hexdigest()[:12]
    out["nu_sha"] = hashlib.sha256(o.nu.tobytes()).hexdigest()[:12]
    out["oracle_dir"] = str(cache)
print(json.dumps(out))
