"""WDJ2052-0324 DESI DR1: white-dwarf Balmer-core velocities (Gaussian core + linear continuum within +-W of each line; H-alpha fitted with
the emission component simultaneously) and the H-alpha emission velocity. Vacuum rest wavelengths."""
import numpy as np
from scipy.optimize import curve_fit
d = np.load("desi_dr1.npz"); w, f, iv = d["w"], d["f"], d["iv"]; ok = iv > 0; C = 299792.458
L = {"H-beta": 4862.68, "H-gamma": 4341.68, "H-delta": 4102.89}
def g1(x, a, m, s, c0, c1): return c0 + c1 * (x - m) - a * np.exp(-0.5 * ((x - m) / s) ** 2)
for n, l0 in L.items():
    for W in (12, 20):
        k = ok & (np.abs(w - l0) < W)
        try:
            p, cv = curve_fit(g1, w[k], f[k], p0=[10, l0, 4, np.median(f[k]), 0], sigma=1 / np.sqrt(iv[k]), absolute_sigma=True)
            print(f"{n} (+-{W} A): v = {(p[1]-l0)/l0*C:7.1f} +- {np.sqrt(cv[1,1])/l0*C:5.1f} km/s, sigma {p[2]:.1f} A")
        except Exception as ex: print(n, W, "fail", ex)
def g2(x, a, m, s, b, m2, s2, c0, c1): return c0 + c1 * (x - 6564.61) - a * np.exp(-0.5 * ((x - m) / s) ** 2) + b * np.exp(-0.5 * ((x - m2) / s2) ** 2)
k = ok & (np.abs(w - 6564.61) < 25)
p, cv = curve_fit(g2, w[k], f[k], p0=[4, 6564, 6, 9, 6568.7, 1.7, 21, 0], sigma=1 / np.sqrt(iv[k]), absolute_sigma=True)
e = np.sqrt(np.diag(cv))
print(f"H-alpha absorption core: v = {(p[1]-6564.61)/6564.61*C:.1f} +- {e[1]/6564.61*C:.1f} km/s (sigma {p[2]:.1f} A); emission: v = {(p[4]-6564.61)/6564.61*C:.1f} +- {e[4]/6564.61*C:.1f} km/s, sigma {p[5]:.2f} A, flux {p[3]*p[5]*np.sqrt(2*np.pi):.1f}")
