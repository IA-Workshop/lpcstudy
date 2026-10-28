Readings side by side, DEV-1 / DEV-3 / DEV-4 (no pooling, no new statistic). Codes: S substantial, d needed (size not det.), s small, n negligible, L lowers, u undetermined (u* n_eff<50); B: D detected, - none, w pair fits worse. 'agree' = identical code on every seed in that cell.
| sys | row | 0.27 LT ora | 0.27 LT dep | 1.00 LT ora | 1.00 LT dep | 4.00 LT ora | 4.00 LT dep | cells agreeing |
|---|---|---|---|---|---|---|---|---|
| lorenz63 | A drop-R (MSE) | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | n/n/n = | n/n/n = | 6/6 |
| lorenz63 | A drop-O (MSE) | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | n/n/n = | n/n/n = | 6/6 |
| lorenz63 | A drop-I (MSE) | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | s/n/n | n/n/n = | 5/6 |
| lorenz63 | A drop-N (MSE) | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | n/n/n = | n/n/n = | 6/6 |
| lorenz63 | B RI (logit) | -/-/- = | -/-/- = | -/-/- = | -/-/D | -/D/- | D/-/- | 3/6 |
| lorenz63 | B OI (logit) | -/-/- = | -/-/- = | -/-/- = | -/-/- = | D/D/- | -/-/- = | 5/6 |
| lorenz63 | D constant vs F | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | n/n/n = | n/n/n = | 6/6 |
| lorenz63 | D separation vs F | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | S/d/d | d/d/d = | 5/6 |
| lorenz63 | D RO vs F | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | n/n/n = | n/n/n = | 6/6 |
| lorenz63 | D X+F vs F | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | L/n/n | n/n/n = | 5/6 |
| rossler | A drop-R (MSE) | d/d/d = | n/u*/n | S/S/S = | n/s/n | s/n/n | n/n/n = | 3/6 |
| rossler | A drop-O (MSE) | d/d/s | n/u*/n | d/d/s | n/s/n | n/n/s | n/n/n = | 1/6 |
| rossler | A drop-I (MSE) | n/n/n = | n/u*/n | n/n/n = | n/n/n = | n/n/n = | n/n/n = | 5/6 |
| rossler | A drop-N (MSE) | s/n/n | n/u*/n | n/n/n = | n/n/n = | n/n/n = | n/n/n = | 4/6 |
| rossler | B RI (logit) | -/-/- = | -/-/- = | -/-/- = | -/-/- = | -/-/- = | -/D/- | 5/6 |
| rossler | B OI (logit) | -/-/- = | -/-/D | -/-/- = | -/-/- = | -/-/- = | -/-/- = | 5/6 |
| rossler | D constant vs F | S/S/S = | n/u*/n | S/S/S = | u/u/u = | s/n/s | n/n/n = | 4/6 |
| rossler | D separation vs F | d/d/d = | d/u*/S | d/n/d | d/d/d = | u/d/d | d/d/d = | 3/6 |
| rossler | D RO vs F | s/n/s | n/u*/n | n/n/n = | n/n/n = | n/n/n = | n/n/n = | 4/6 |
| rossler | D X+F vs F | n/n/n = | L/u*/L | n/n/n = | n/n/n = | n/n/n = | n/n/n = | 5/6 |
| chua | A drop-R (MSE) | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | s/n/s | n/n/n = | 5/6 |
| chua | A drop-O (MSE) | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | n/n/n = | n/n/n = | 6/6 |
| chua | A drop-I (MSE) | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | n/n/n = | n/n/n = | 6/6 |
| chua | A drop-N (MSE) | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | n/n/n = | n/n/n = | 6/6 |
| chua | B RI (logit) | -/-/- = | -/-/- = | -/-/- = | -/-/- = | -/-/- = | -/-/- = | 6/6 |
| chua | B OI (logit) | D/-/- | -/-/- = | -/D/- | -/-/- = | -/-/- = | -/-/- = | 4/6 |
| chua | D constant vs F | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | s/s/d | n/n/n = | 5/6 |
| chua | D separation vs F | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | d/d/d = | d/d/u | 5/6 |
| chua | D RO vs F | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | n/s/n | n/n/n = | 5/6 |
| chua | D X+F vs F | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | u*/u*/u* = | n/n/n = | n/n/n = | 6/6 |

Horizon decision (one target; columns oracle / deployable)
| sys | row | oracle | deployable |
|---|---|---|---|
| lorenz63 | drop-R (pinball) | n/u/u | n/n/n = |
| lorenz63 | drop-O (pinball) | d/S/S | d/S/S |
| lorenz63 | drop-I (pinball) | S/S/S = | S/S/S = |
| lorenz63 | drop-N (pinball) | n/n/n = | n/n/L |
| lorenz63 | B RI (median ln T) | D/-/- | -/-/D |
| lorenz63 | B OI (median ln T) | D/D/D = | D/D/D = |
| lorenz63 | B RO (median ln T) | D/-/- | -/-/- = |
| rossler | drop-R (pinball) | s/n/s | n/n/n = |
| rossler | drop-O (pinball) | S/S/S = | S/S/S = |
| rossler | drop-I (pinball) | S/S/S = | S/S/S = |
| rossler | drop-N (pinball) | n/n/n = | n/n/n = |
| rossler | B RI (median ln T) | -/-/- = | -/D/D |
| rossler | B OI (median ln T) | D/D/D = | D/D/D = |
| rossler | B RO (median ln T) | D/-/D | -/D/D |
| chua | drop-R (pinball) | n/n/n = | n/n/n = |
| chua | drop-O (pinball) | d/d/S | S/d/S |
| chua | drop-I (pinball) | S/S/S = | S/S/S = |
| chua | drop-N (pinball) | n/n/n = | n/n/n = |
| chua | B RI (median ln T) | -/-/D | -/-/- = |
| chua | B OI (median ln T) | D/D/D = | D/D/D = |
| chua | B RO (median ln T) | D/D/- | -/D/- |
