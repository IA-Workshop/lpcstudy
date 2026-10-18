"""Scratch (WU-0001.6 M5): full SHA-256 of state_mean, C, W, U (float64 '<f8', C order) per system."""
import hashlib, sys, numpy as np
from lpcstudy.data import _symmetric_root
for s in ("lorenz63", "rossler", "chua"):
    st = np.load(f"{sys.argv[1]}/stats_{s}.npy"); C = np.cov(st.T); W, U = _symmetric_root(C)
    for k, a in (("state_mean", st.mean(axis=0)), ("cov", C), ("whiten", W), ("unwhiten", U)):
        print(sys.argv[2], s, k, hashlib.sha256(np.asarray(a, "<f8").tobytes(order="C")).hexdigest())
