"""T1: candidate (ii) time units, by arithmetic on stored values only.

If the Dysts maximum field were our exponent in another time unit, the ratio
R = Dysts_max / ours would be one rule applied to all three systems. Test
rules built from the stored Dysts fields (period P, dt = P/5000, sample
spacings P/100 and P/500, dt/10, log base): each must give the same factor
for Lorenz, Rossler and Chua. Values: note A.2 and the DEV-0 reference leaf.
"""
import math
ours = {"lorenz63": 0.9054940534657817, "rossler": 0.07193978510879935, "chua": 0.43113260161336364}
dmax = {"lorenz63": 0.8917098035724058, "rossler": 0.15059688939547888, "chua": 1.2301163591725595}
dspec = {"lorenz63": [1.0910931847726466, 0.02994120961308413, -14.915552395875103],
         "rossler": [0.0763301393780693, 0.007522476799147231, -5.741024338716747],
         "chua": [0.4605474829443073, 0.0022048281168492866, -4.319076735248446]}
period = {"lorenz63": 1.5008, "rossler": 5.9086, "chua": 1.4235}
ky = {"lorenz63": 2.075158758095728, "rossler": 2.0146095059018845, "chua": 2.10727056025829}
print("system    R=max/ours  R/P      R*P     max/spec0  KY(from spectrum)  KY stored")
for s in ours:
    R = dmax[s] / ours[s]
    l = dspec[s]
    kyc = 2 + (l[0] + l[1]) / abs(l[2])
    print(f"{s:9s} {R:9.4f} {R/period[s]:8.4f} {R*period[s]:8.4f} {dmax[s]/l[0]:9.4f} {kyc:12.5f} {ky[s]:12.5f}")
print("log-base factors: 1/ln2 =", round(1 / math.log(2), 4), " ln10 =", round(math.log(10), 4))
print("grid-spacing ratios available: 5 (P/100 vs P/500), 10 (dt/10), 50, 100, 500, 5000")
print("Chua coincidences (look-elsewhere: many expressions tried):")
print("   2P =", 2 * period["chua"], " vs R =", round(dmax["chua"] / ours["chua"], 4))
for nm, m0 in [("ours m0", -1.143), ("Dysts m0", -1.142857)]:
    print(f"   inner-region divergence -alpha(1+m0)-1 with {nm}:", round(-15.6 * (1 + m0) - 1, 5), " vs Dysts max", round(dmax['chua'], 5))
print("   same rule for Lorenz: divergence -(sigma+1+beta) =", round(-(10 + 1 + 8 / 3), 4), "vs Dysts max", dmax["lorenz63"])
