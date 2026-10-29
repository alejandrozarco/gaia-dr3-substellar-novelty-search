"""TOI-905: DR4 detectability using only the TESS-only acceleration floor (2026-10-30).
For a circular orbit the peak line-of-sight acceleration is (2 pi / Pc)^2 a1 sin i, so the TESS-only value
|dv/dt| = 188 m/s/yr (lower 2-sigma 132) sets a1 sin i >= |dv/dt| (Pc / 2 pi)^2. Same rough DR4 simulation as
dr4_detectability.py (70 AL epochs 2014.57-2020.05, sigma_AL 0.10 mas, random scan angles, isotropic i, random node/phase)."""
import numpy as np
rng = np.random.default_rng(20261030)
AUYR = 4.740470  # km/s per au/yr
PLX = 6.3626
N, SIG = 70, 0.10
print('accel_m/s/yr  Pc_yr  a1sini_floor_mas  P(dchi2_acc>25)  P(dchi2_acc>25 or uwe_lin>1.4)')
for acc in (188., 132.):
    for Pc in (5, 6.25, 8, 10, 15, 20, 30, 50, 100):
        a1s = acc / 1000. / AUYR * (Pc / (2 * np.pi))**2 * PLX
        hit_a = hit_any = 0
        for _ in range(2000):
            t = np.sort(rng.uniform(2014.57, 2020.05, N)); th = rng.uniform(0, np.pi, N)
            cosi = rng.uniform(0, 1); sini = np.sqrt(1 - cosi**2)
            a1 = a1s / max(sini, 1e-3); Om = rng.uniform(0, 2*np.pi); ph = rng.uniform(0, 2*np.pi)
            u = 2*np.pi*(t - 2017.3)/Pc + ph
            x, y = a1*np.cos(u), a1*np.sin(u)*cosi
            X = x*np.cos(Om) - y*np.sin(Om); Y = x*np.sin(Om) + y*np.cos(Om)
            al = X*np.sin(th) + Y*np.cos(th) + SIG*rng.standard_normal(N)
            dt = t - 2017.3
            A4 = np.c_[np.sin(th), np.cos(th), dt*np.sin(th), dt*np.cos(th)]
            A6 = np.c_[A4, .5*dt**2*np.sin(th), .5*dt**2*np.cos(th)]
            r4 = al - A4 @ np.linalg.lstsq(A4, al, rcond=None)[0]; r6 = al - A6 @ np.linalg.lstsq(A6, al, rcond=None)[0]
            c4, c6 = (r4**2).sum()/SIG**2, (r6**2).sum()/SIG**2
            a = (c4 - c6) > 25; hit_a += a; hit_any += a or np.sqrt(c4/(N-4)) > 1.4
        print('%8.0f %8.2f %12.3f %16.3f %16.3f' % (acc, Pc, a1s, hit_a/2000, hit_any/2000))
