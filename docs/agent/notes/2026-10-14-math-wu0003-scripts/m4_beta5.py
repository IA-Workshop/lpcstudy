"""M4: block-5 variance factor beta_5(phi) = E V*(5) / LRV for an AR(1)-type influence series, its
sensitivity to phi, the SE of the plug-in at n = 300, 500, 1000, and E V*(b)/V*(5) for b = 10, 20.
First-order coverage at nominal z: 2 Phi(z sqrt(beta_5)) - 1.
"""
import math
from statistics import NormalDist
N = NormalDist()
def vb(phi, b):
    return 1 + 2 * sum((1 - k / b) * phi ** k for k in range(1, b))
def beta(phi, b=5):
    return vb(phi, b) * (1 - phi) / (1 + phi)
z95, z983 = N.inv_cdf(0.975), N.inv_cdf(1 - 0.05 / 6)
print(" phi   beta5   cov95   cov98.3  E V10/V5  E V20/V5  dbeta/dphi  SE(beta5) n=300/500/1000")
for phi in (-0.2, -0.1, 0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5):
    b5 = beta(phi); h = 1e-5
    d = (beta(phi + h) - beta(phi - h)) / (2 * h)
    se = [abs(d) * math.sqrt((1 - phi * phi) / n) for n in (300, 500, 1000)]
    c95 = 2 * N.cdf(z95 * math.sqrt(b5)) - 1; c98 = 2 * N.cdf(z983 * math.sqrt(b5)) - 1
    print(f"{phi:5.2f}  {b5:6.4f}  {c95:6.4f}  {c98:6.4f}   {vb(phi,10)/vb(phi,5):7.4f}   {vb(phi,20)/vb(phi,5):7.4f}   {d:8.4f}    "
          + " / ".join(f"{x:.4f}" for x in se))
