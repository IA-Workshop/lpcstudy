import json, numpy as np
from scipy import stats
R="/home/brianm/projects/physics/chaos/lpcstudy-wt/run/r1-c9bb981/runs/r1-gpu-dev1/pilot"
res=json.load(open(f"{R}/results.json"))
for sysname in ("lorenz63","rossler","chua"):
    z=np.load(f"{R}/states/{sysname}.npz")
    prof=z["core/profile"]; N=z["core/N"]
    leaf=res["systems"][sysname]["H1d"]["rows"]["nhat"]
    x=prof[:,0,3]
    print(sysname, prof.shape, "leaf", leaf["spearman"], leaf["n_states"], leaf["n_excluded_nonfinite"])
    print("  rho from profile col3:", stats.spearmanr(x,N).statistic, " ties x:", len(x)-len(np.unique(x)), "N ties", len(N)-len(np.unique(N)))
    print("  min x", x.min(), "unique", len(np.unique(x)), "N unique", len(np.unique(N)), "N min", N.min())
