"""Scratch (WU-0001.6 M1-M5): digest every stage of the whitening chain
{stats, state_mean, centred X, C = np.cov, eigh(C), W, U} under the current BLAS kernel,
plus cross-stage runs on the reference C (saved by the default-kernel run) to localize."""
import hashlib, json, os, sys, ctypes
from pathlib import Path
import numpy as np
d = Path(sys.argv[1]); tag = sys.argv[2]; save_ref = len(sys.argv) > 3 and sys.argv[3] == "ref"
def H(a): return hashlib.sha256(np.ascontiguousarray(a, dtype="<f8").tobytes()).hexdigest()[:12]
def ulps(a, b):
    a = np.asarray(a, "<f8").ravel(); b = np.asarray(b, "<f8").ravel()
    ia = a.view("<i8").astype(object); ib = b.view("<i8").astype(object)
    # same-sign entries assumed (checked)
    assert np.all(np.sign(a) == np.sign(b))
    return int(max(abs(x - y) for x, y in zip(ia, ib)))
def corename():
    for line in open("/proc/self/maps"):
        if "libscipy_openblas64_" in line and "numpy.libs" in line:
            lib = ctypes.CDLL(line.split()[-1], mode=os.RTLD_NOLOAD)
            f = lib.scipy_openblas_get_corename64_; f.restype = ctypes.c_char_p
            return f().decode()
from lpcstudy.data import _symmetric_root
out = {"tag": tag, "core": corename()}
for system in ("lorenz63", "rossler", "chua"):
    stats = np.load(d / f"stats_{system}.npy")
    state_mean = stats.mean(axis=0)
    X = np.array(stats.T, ndmin=2, dtype=np.float64)   # as np.cov does
    Xc = X - X.mean(axis=1)[:, None]
    C = np.cov(stats.T)
    eigval, eigvec = np.linalg.eigh(C)
    W, U = _symmetric_root(C)
    r = {"stats": H(stats), "mean": H(state_mean), "Xc": H(Xc), "C": H(C),
         "eigval": H(eigval), "eigvec": H(eigvec), "W": H(W), "U": H(U),
         "kappaC": float(np.linalg.cond(C))}
    if save_ref:
        np.savez(d / f"ref_{system}.npz", C=C, eigval=eigval, eigvec=eigvec, W=W, U=U, mean=state_mean)
    else:
        ref = np.load(d / f"ref_{system}.npz")
        Wx, Ux = _symmetric_root(ref["C"])           # this kernel's eigh+products on reference C
        ev, evec = np.linalg.eigh(ref["C"])
        E = ref["eigvec"]                            # reference eigh, this kernel's products only
        Wp = E @ np.diag(1.0 / np.sqrt(ref["eigval"])) @ E.T
        Up = E @ np.diag(np.sqrt(ref["eigval"])) @ E.T
        r.update({"ulp_C": ulps(C, ref["C"]), "ulp_W": ulps(W, ref["W"]), "ulp_U": ulps(U, ref["U"]),
                  "ulp_mean": ulps(state_mean, ref["mean"]),
                  "refC_eigval_eq": bool(np.array_equal(ev, ref["eigval"])),
                  "refC_eigvec_eq": bool(np.array_equal(evec, ref["eigvec"])),
                  "refC_W_eq": bool(np.array_equal(Wx, ref["W"])), "refC_U_eq": bool(np.array_equal(Ux, ref["U"])),
                  "refEig_W_eq": bool(np.array_equal(Wp, ref["W"])), "refEig_U_eq": bool(np.array_equal(Up, ref["U"]))})
    out[system] = r
print(json.dumps(out))
