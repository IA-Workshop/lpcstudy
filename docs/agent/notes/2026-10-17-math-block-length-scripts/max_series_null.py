"""Selection-adjusted null for the most extreme single series (DEVELOPMENT, DEV-1/DEV-2).

Per run: statistic T = max over the 24 primary series of log V*(20)/V*(5) and of acf(1); null by
the same per-system permutations as block_curve.py (2000; make_rng(20261017, "block-length-note",
"max", run, system)). Prints the observed max, which series, and P(null max >= observed).
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, sys.argv[1])
from lpcstudy.data import make_rng
DIR = Path(sys.argv[2]); NP = 2000
def bv(m, b):
    x = m - m.mean(axis=-1, keepdims=True)
    c = np.concatenate([np.zeros(x.shape[:-1] + (1,)), np.cumsum(x, axis=-1)], axis=-1)
    return b * ((c[..., b:] - c[..., :-b]) / b).var(axis=-1)
def a1(m):
    x = m - m.mean(axis=-1, keepdims=True)
    return (x[..., :-1] * x[..., 1:]).sum(-1) / (x * x).sum(-1)
for tag in ("R1", "R5"):
    z = np.load(DIR / f"series-{tag}.npz"); meta = json.loads((DIR / f"series-{tag}.json").read_text())
    prim = [e for e in meta["series"] if e["primary"]]
    obs_r, obs_a, null_r, null_a = {}, {}, [], []
    for system in ("lorenz63", "rossler", "chua"):
        ser = [e for e in prim if e["system"] == system]
        keys = make_rng(20261017, "block-length-note", "max", tag, system).random((NP, max(e["n"] for e in ser)))
        for e in ser:
            x = z[e["key"]]
            obs_r[e["key"]] = np.log(bv(x[None], 20)[0] / bv(x[None], 5)[0]); obs_a[e["key"]] = a1(x[None])[0]
            p = x[np.argsort(keys[:, :x.size], axis=1)]
            null_r.append(np.log(bv(p, 20) / bv(p, 5))); null_a.append(a1(p))
    null_r, null_a = np.max(null_r, axis=0), np.max(null_a, axis=0)
    kr = max(obs_r, key=obs_r.get); ka = max(obs_a, key=obs_a.get)
    print(f"{tag}: max V*(20)/V*(5) {np.exp(obs_r[kr]):.3f} ({kr}); P(null max >=) {(1+np.sum(null_r>=obs_r[kr]))/(1+NP):.3f}")
    print(f"{tag}: max acf(1) {obs_a[ka]:+.3f} ({ka}); P(null max >=) {(1+np.sum(null_a>=obs_a[ka]))/(1+NP):.3f}")
