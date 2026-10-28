# Phase J confirmatory round: presentation figures

**PHASE J CONFIRMATORY (CONF-5 to CONF-9): presentation figures of the stored, pre-registered results. Made after the freeze; not part of the pre-registered analysis; no new finding.** Main session (claude-opus-5-5), 2026-10-28, at the owner's request ("this is just an interpretive presentation of that, not a new finding").

- **Source.** `tools/phasej_figures.py promoted/phase-J --out docs/agent/notes/2026-10-28-phase-j-figures`, run on the promoted records, which are unchanged (`promoted/phase-J.sha256` verifies).
- **What the script does.**
  - It computes no statistic. Each point, interval and level is read from the node that stores the reading. Each claim row is found with the frozen lookup of `tools/lpc_confirm.py`.
  - All 48 plotted readings are checked against `confirm/confirm.json`, and the script refuses to plot on a mismatch.
  - A rebuild is byte-identical.
- **Seeds are never pooled.** Each seed is one colored point with its own interval, offset sideways inside its group.
- **Marker fill.**
  - Filled: that seed's stored reading implies the claim.
  - Hollow: it does not.
  - In rows that carry no claim, which are faded and shown only for context, hollow means the stored reading is "undetermined".
- **Bars** are each row's stored interval at its stored level, which the panel title states. The levels are the pre-registered Holm/Bonferroni levels, so they differ between rows.
- **Lines.** A solid line marks no change (ratio 1, difference 0). A dashed line marks the 5% margin of a claim, or J-C2's 10% target.
- **Report.** The limitations in §6 of the report (`promoted/phase-J/report.md`) apply to every figure. Report §7 states what may and may not be said.

## The figures

| file | shows |
|---|---|
| `F1_horizon_ablation.png` | **Ablation of the horizon forecast.** For each system and profile: the loss of predicting the forecast horizon with one condition removed, divided by the loss with all four. Above 1, the model predicts the horizon worse without that condition. Across the 30 seed × system × profile cells, dropping I (instability) raises the loss by 21 to 29% (ratio 1.209 to 1.288) and dropping O (separation) by 5 to 13% (1.050 to 1.130) (J-H1, J-H2). Dropping N (noise) leaves the ratio between 0.992 and 1.014 (J-H3). Dropping R (recurrence) is not a claim and is shown faded. |
| `F2_allocation_ablation.png` | **Ablation of the allocation at 1 LT.** The same layout for the error of the CP–PLP blend. Only Rössler oracle drop R is a claim (J-A1), and it sits above the 5% line on all five seeds. The faded rows are context. On Lorenz-63 and Chua most readings are undetermined at this horizon (pre-registration §8 item 3), which shows as hollow points with wide intervals. |
| `F3_horizon_claims.png` | **J-H4, J-H5, J-H6 at the horizon T_c.** J-H4: the O and I interaction Δ (loss of an additive O, I model minus the loss of a model with their interaction), above 0 on every seed. J-H5: the Lyapunov rank's loss divided by the profile's, from 1.365 to 2.056. J-H6: adding the raw delay vector to the profile lowers the loss, with every ratio below 1. |
| `F4_allocation_claims.png` | **J-A2, J-A3, J-A4, J-I1, J-C2.** One panel per claim, with the claim's statement and level in its title. J-A4 is the one row not confirmed: three seeds imply the claim. On CONF-5 and CONF-7 the pre-registered guard (effective sample size under 50) makes the reading "undetermined" whatever the interval; CONF-7's interval lies entirely below 1. |
| `F5_reading_grid.png` | **Every claim row's stored reading on every seed,** with the words exactly as stored. Green means the reading implies the claim; gray means it does not. The right column is the row verdict. |

## What these figures may not be used for (pre-registration §9)

- An overall verdict, or a count of claims as a finding.
- Pooling across seeds. The groups are five separate realizations.
- A causal reading. A condition that "helps" predicts the horizon or the weight better. It does not make the system more predictable.
- Reading "not confirmed" (J-A4) as "no effect".
- Any comparison with CONF-1's numbers.

## Hashes (sha256)

```
110bea223bdd4ae69e1d4d8ddd2dc09bf735f63e5a50210ac32c0fbad4772614  F1_horizon_ablation.png
4859b72cbb3b120f7a4c8313f0656a94d24e519e68c9358ea190546f0a940c83  F2_allocation_ablation.png
1606b806cc507e16b4a351bba1f98fdf226346db3a83b978c0f3fe9e28d8a40f  F3_horizon_claims.png
70399cfb2ba3a565518be632f0029857215e250137c8c0034d9e80e0edc47d41  F4_allocation_claims.png
f121c28f43de3ef593138ef096fdb3c1c14d90d162e487fa3cf437400c65707b  F5_reading_grid.png
95104734b9170677ba598be91aa684735bcf5c02388afad3ec6f20274da81ada  tools/phasej_figures.py
```
