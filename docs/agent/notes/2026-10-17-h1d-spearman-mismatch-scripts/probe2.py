"""H1d nhat: bisect the 3 MISMATCHES. DEVELOPMENT, DEV-1 R1 dump, read-only."""
import json, math, numpy as np
from scipy import stats
R="/home/brianm/projects/physics/chaos/lpcstudy-wt/run/r1-c9bb981/runs/r1-gpu-dev1/pilot"
C=1e-2
res=json.load(open(f"{R}/results.json"))
print("floor c =", C, " ulp(c) =", np.spacing(C))
for sysname in ("lorenz63","rossler","chua"):
    z=np.load(f"{R}/states/{sysname}.npz")
    prof, N = z["core/profile"], z["core/N"]
    leaf=res["systems"][sysname]["H1d"]["rows"]["nhat"]["spearman"]
    x=prof[:,0,3]
    # other columns and rows
    others={n:(stats.spearmanr(prof[:,0,k], z[f"core/{o}"]).statistic, res["systems"][sysname]["H1d"]["rows"][n]["spearman"])
            for n,k,o in (("analog_seed",0,"eps_s"),("estimation_seed",1,"delta"),("growth",2,"Lambda_bar"))}
    print(f"== {sysname}: leaf {leaf!r}; dump column 3: {stats.spearmanr(x,N).statistic!r}; diff {stats.spearmanr(x,N).statistic-leaf:+.3e}")
    for n,(a,b) in others.items(): print(f"   {n}: dump {a!r} leaf {b!r} diff {a-b:+.1e}")
    # the tie structure of the transformed column
    lo=x.min(); tied=np.flatnonzero(x==lo)
    vals,counts=np.unique(x,return_counts=True)
    print(f"   states: {len(x)}, column-3 distinct {len(vals)}, tied groups {int((counts>1).sum())}, largest tie {counts.max()} at value {vals[counts.argmax()]!r}; log(c)={math.log(C)!r}")
    print(f"   tied-at-the-floor states: {len(tied)}; their N range [{N[tied].min():.3e}, {N[tied].max():.3e}]; raw x=exp(x)-c would be <= {np.spacing(C):.2e} (float64 resolution at c)")
    # bounds: break ties in the best and worst way (within the tied group, ranks by N)
    def rho_with_tiebreak(sign):
        key=x.copy()
        # tie-break by N within each tied group
        order=np.lexsort((sign*N, x))
        ranks=np.empty(len(x)); ranks[order]=np.arange(len(x))
        return stats.spearmanr(ranks,N).statistic
    hi, lo_r = rho_with_tiebreak(+1), rho_with_tiebreak(-1)
    print(f"   Spearman over all tie-breaks of column 3: [{lo_r:.9f}, {hi:.9f}]; leaf inside: {lo_r<=leaf<=hi}; mid-rank (dump) {stats.spearmanr(x,N).statistic:.9f}")
    # which production n and exclusion set
    print(f"   leaf n_states {res['systems'][sysname]['H1d']['rows']['nhat']['n_states']}, excluded {res['systems'][sysname]['H1d']['rows']['nhat']['n_excluded_nonfinite']}; N finite {np.isfinite(N).all()}, x finite {np.isfinite(x).all()}")
