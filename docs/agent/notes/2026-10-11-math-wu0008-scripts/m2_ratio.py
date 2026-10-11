"""SE(endpoint)/half-width for a ratio of means with heavy tails (H3c-like), B in {500, 2000}."""
import numpy as np
n, block = 500, 5
L = 1 - 0.05/3; a = (1-L)/2
rng = np.random.default_rng(99)
for sigma in (1.0, 1.5, 2.0):
    for B in (500, 2000):
        fr = []
        for k in range(200):
            z = rng.standard_normal((n, 2)); z[:, 1] = 0.8*z[:, 0] + 0.6*z[:, 1]
            A, Bv = np.exp(sigma*z[:, 0]), np.exp(sigma*z[:, 1])
            SA, SB = np.convolve(A, np.ones(block), 'valid'), np.convolve(Bv, np.ones(block), 'valid')
            st = rng.integers(0, n-block+1, (B, n//block))
            v = SA[st].sum(1)/SB[st].sum(1)
            lo, hi = np.quantile(v, [a, 1-a]); hw = (hi-lo)/2
            se = []
            for q in (a, 1-a):
                d = np.sqrt(q*(1-q)/B); se.append((np.quantile(v, q+d)-np.quantile(v, q-d))/2)
            fr.append(np.array(se)/hw)
        fr = np.array(fr)
        print(f"sigma {sigma} B {B}: SE/hw lower: median {np.median(fr[:,0]):.3f} p95 {np.percentile(fr[:,0],95):.3f}; upper: median {np.median(fr[:,1]):.3f} p95 {np.percentile(fr[:,1],95):.3f}; P(max >= 0.1) {np.mean(fr.max(1) >= 0.1):.3f}")
