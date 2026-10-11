"""Scratch (WU-0001.6 M5): build_context(system, smoke) as a run does; digest ctx arrays as built."""
import hashlib, json, sys, tempfile, time
from pathlib import Path
import numpy as np
from lpcstudy.config import PRESETS
from lpcstudy.data import build_context
lam = {'lorenz63': 0.9054940534657817, 'rossler': 0.07193978510879935, 'chua': 0.43113260161336364}
cache = Path(tempfile.mkdtemp(dir=sys.argv[1])); (cache / "lyapunov.json").write_text(json.dumps(lam))
out = {}
for s in sys.argv[2:]:
    t = time.time(); ctx = build_context(s, PRESETS["smoke"], cache)
    H = lambda a: hashlib.sha256(a.tobytes()).hexdigest()[:12]
    out[s] = {"s": round(time.time() - t, 1), "W": H(ctx.whiten), "U": H(ctx.unwhiten), "mean": H(ctx.state_mean),
              "types": [type(a).__name__ + str(a.dtype) + str(a.dtype.byteorder) + ("C" if a.flags.c_contiguous else "-")
                        + ("own" if a.flags.owndata else "view") for a in (ctx.whiten, ctx.unwhiten, ctx.state_mean)],
              "W_sym_bitwise": bool(np.array_equal(ctx.whiten, ctx.whiten.T)),
              "U_sym_bitwise": bool(np.array_equal(ctx.unwhiten, ctx.unwhiten.T))}
print(json.dumps(out))
