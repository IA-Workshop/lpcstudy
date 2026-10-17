"""Extract the D2 influence series of R1 and R5 from their dumps (DEVELOPMENT, DEV-1 and DEV-2).

Uses the diagnostics tool's own builders (tools/rehearsal_diagnostics.py), so the series are the
ones D1/D2 read. Writes one npz per run: key "<system>|<name>" -> series, plus a json index.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

WT = Path(sys.argv[1])          # worktree root (tools/ and lpcstudy/)
RUNS = {"R1": Path(sys.argv[2]), "R5": Path(sys.argv[3])}
OUT = Path(sys.argv[4])
sys.path.insert(0, str(WT))
sys.path.insert(0, str(WT / "tools"))
import rehearsal_diagnostics as rd  # noqa: E402

for tag, run in RUNS.items():
    path, results, seed_id = rd.load_results(run / "results.json")
    cfg, prov = results["config"], results["provenance"]
    stack = rd.compare_stack(prov, rd.stack_record())
    arrays, index = {}, []
    for system in results["systems"]:
        rep = rd.Report()
        dump = rd.Dump.load(run / "states" / f"{system}.npz")
        try:
            ctx = rd.Context(system, dump, results["systems"][system], cfg, rep, rd.TOOL_SEED,
                             2000, 1000, stack)
            for name, builder in rd.SERIES_BUILDERS:
                for s in builder(ctx):
                    key = f"{system}|{s.name}"
                    arrays[key] = np.asarray(s.values, dtype=float)
                    index.append({"key": key, "system": system, "name": s.name,
                                  "criterion": s.criterion, "primary": bool(s.primary),
                                  "n": s.n, "n_rate": s.n_rate, "domain": s.domain})
        finally:
            dump.close()
        print(tag, system, "defects", len(rep.defects), "nc", len(rep.incomplete))
    np.savez(OUT / f"series-{tag}.npz", **arrays)
    (OUT / f"series-{tag}.json").write_text(json.dumps({"seed_id": seed_id, "series": index},
                                                       indent=1))
    print(tag, seed_id, len(index), "series,", sum(e["primary"] for e in index), "primary")
