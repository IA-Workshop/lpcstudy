"""H1d nhat: why the transform loses the order, and how large each effect is. Read-only, DEV-1 R1 dump."""
import json, math, numpy as np
from scipy import stats
R="/home/brianm/projects/physics/chaos/lpcstudy-wt/run/r1-c9bb981/runs/r1-gpu-dev1/pilot"
C=1e-2
for sysname in ("lorenz63","rossler","chua"):
    z=np.load(f"{R}/states/{sysname}.npz")
    prof=z["core/profile"]
    ties=[len(prof[:,0,k])-len(np.unique(prof[:,0,k])) for k in range(4)]
    x=prof[:,0,3]
    r=np.exp(x)-C   # the raw N-hat the profile column can still tell (resolution ~ 1e-17 absolute)
    small=np.sum(r<1e-12)
    print(f"{sysname}: ties per profile column (draw 1): {ties}; states with raw N-hat below ~1e-12: {int(small)} of {len(x)} "
          f"(float64 resolution of log(x + c) in x: ulp(c)={np.spacing(C):.1e} and ulp(log c)*c={np.spacing(abs(math.log(C)))*C:.1e})")
    # states in tied groups
    vals,counts=np.unique(x,return_counts=True)
    inties=int(counts[counts>1].sum())
    print(f"   states inside a tied group: {inties}; groups {int((counts>1).sum())}")
