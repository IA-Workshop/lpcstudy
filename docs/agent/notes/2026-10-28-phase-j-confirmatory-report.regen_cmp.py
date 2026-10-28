"""Pre-registration section 5: dump arrays bitwise and claim rows, official against regeneration."""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

B = Path(sys.argv[1])
for n in range(5, 10):
    for system in ("lorenz63", "rossler", "chua"):
        a = np.load(B / f"phasej-CONF-{n}/phasej/states/{system}.npz", allow_pickle=False)
        b = np.load(B / f"phasej-CONF-{n}-regen/phasej/states/{system}.npz", allow_pickle=False)
        keys = sorted(set(a.files) | set(b.files))
        differ = []
        for k in keys:
            if k not in a.files or k not in b.files:
                differ.append((k, "one-sided", None))
                continue
            x, y = a[k], b[k]
            if x.dtype != y.dtype or x.shape != y.shape:
                differ.append((k, "shape/dtype", None)); continue
            if x.tobytes() != y.tobytes():
                ne = int(np.sum(x != y)) if x.dtype.kind in "fiub" else -1
                differ.append((k, f"{ne} of {x.size}", None))
        heads = Counter(k.split("/")[0] for k, *_ in differ)
        print(f"CONF-{n} {system}: {len(keys)} arrays, {len(differ)} differ; by group {dict(heads)}")
        for k, what, _ in differ[:400]:
            print(f"    {k}: {what}")

off = json.loads((B / "phasej-confirm/confirm.json").read_text())
reg = json.loads((B / "phasej-confirm-regen/confirm.json").read_text())
KEYS = ("claim_id", "family", "system", "profile", "horizon", "item")
def key(r):
    return tuple(r.get(k) for k in KEYS)
ro = {key(r): r for r in off["rows"]}
rr = {key(r): r for r in reg["rows"]}
assert len(ro) == len(off["rows"]) and len(rr) == len(reg["rows"])
print(f"\nrows: official {len(ro)}, regen {len(rr)}, common {len(set(ro) & set(rr))}")
ndiff = 0
for k in ro:
    a, b = ro[k], rr.get(k)
    if b is None:
        print("ROW MISSING IN REGEN", k); ndiff += 1; continue
    fields = [f for f in ("readings", "absent", "verdict") if a.get(f) != b.get(f)]
    if fields:
        ndiff += 1
        print("ROW DIFFERS", k, fields)
        for f in fields:
            print(f"    {f}: {a.get(f)} -> {b.get(f)}")
print(f"rows differing: {ndiff} of {len(ro)}")
vo = {(v["claim_id"], v["system"]): v["verdict"] for v in off["verdicts"]}
vr = {(v["claim_id"], v["system"]): v["verdict"] for v in reg["verdicts"]}
print("claim x system verdicts differing:", [(k, vo[k], vr.get(k)) for k in vo if vo[k] != vr.get(k)])
print("official row verdicts:", Counter(r["verdict"] for r in off["rows"]))
