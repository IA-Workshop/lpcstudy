import json,sys,glob
fs=sys.argv[1:]
for sysn in ("lorenz63","rossler","chua"):
    print("==",sysn)
    for f in fs:
        o=json.load(open(f)); r=o[sysn]
        print(f"{o['tag']:12s} {o['core']:12s}", " ".join(f"{k}={r[k]}" for k in r if k!="kappaC"))
