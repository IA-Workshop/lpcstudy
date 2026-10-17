import numpy as np
R="/home/brianm/projects/physics/chaos/lpcstudy-wt/run/r1-c9bb981/runs/r1-gpu-dev1/pilot"
z=np.load(f"{R}/states/lorenz63.npz"); x=z["core/profile"][:,0,3]; N=z["core/N"]
vals,counts=np.unique(x,return_counts=True)
print("tied groups (x value -> raw N-hat ~ exp(x) - c, from the dump) and the oracle N of the group:")
for v,c in zip(vals[counts>1][:8],counts[counts>1][:8]):
    idx=np.flatnonzero(x==v)
    print(f"  x={v!r}: {c} states, raw ~ {np.expm1(v-np.log(1e-2))*1e-2:.3e}, N {np.sort(N[idx])}")
print("sorted raw N-hat estimates (smallest 15):", np.sort(np.expm1(x-np.log(1e-2))*1e-2)[:15])
