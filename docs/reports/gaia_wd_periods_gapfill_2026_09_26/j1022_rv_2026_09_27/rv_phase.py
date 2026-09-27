"""Velocities against the photometric ephemeris (ZTF: f = 16.4886946 +- 8.1e-6 c/d, t_max = BJD_TDB 2458000.04931 +- 0.6 min).
Exposure mid-times (TAI MJD) are converted to BJD_TDB at the star's position (Apache Point). Reflection-effect expectation: at maximum light the
companion is at superior conjunction, so the white dwarf's RV crosses zero from negative to positive: v = gamma + K sin(2 pi phase)."""
import numpy as np
from astropy.time import Time; from astropy.coordinates import SkyCoord, EarthLocation; import astropy.units as u
f0, ef, t0 = 16.4886946, 8.1e-6, 2458000.04931
c = SkyCoord(155.7148994, 16.1977169, unit="deg"); apo = EarthLocation.of_site("apo")
rows = [("SDSS2007", 54174.20249, -2.2, 5.0), ("SDSS2007", 54174.21483, 3.7, 11.2), ("SDSS2007", 54174.22715, -6.9, 5.0),
        ("BOSS2012", 55987.25704, 10.6, 7.6), ("BOSS2012", 55987.26841, 33.6, 11.8), ("BOSS2012", 55987.27977, -3.9, 6.2),
        ("BOSS2012", 55987.29115, -25.6, 8.8), ("BOSS2012", 55987.30252, -6.6, 21.4), ("BOSS2012", 55987.31388, -6.2, 7.0)]
ph, V, E, G = [], [], [], []
for vis, mjd, v, e in rows:
    t = Time(mjd, format="mjd", scale="tai", location=apo); bjd = (t.tdb + t.light_travel_time(c)).jd
    n = (bjd - t0) * f0; p = n % 1; ph.append(p); V.append(v); E.append(e); G.append(vis)
    print(f"{vis} BJD {bjd:.5f} cycles {n:.2f} phase {p:.3f} (+-{abs(bjd - t0) * ef:.3f}) v {v:+.1f}")
ph, V, E, G = map(np.array, (ph, V, E, G))
def chi_for(K, off):
    m = K * np.sin(2 * np.pi * (ph - off)); c2 = 0
    for g in set(G):
        k = G == g; w = 1 / E[k] ** 2; gam = np.sum(w * (V[k] - m[k])) / w.sum(); c2 += np.sum(((V[k] - m[k] - gam) / E[k]) ** 2)
    return c2
Ks = np.arange(0, 101, 0.5); offs = np.linspace(0, 1, 400, endpoint=False)
grid = np.array([[chi_for(K, o) for o in offs] for K in Ks]); i, j = np.unravel_index(np.argmin(grid), grid.shape)
print(f"free phase: K = {Ks[i]:.1f} km/s, zero-crossing (neg->pos) at photometric phase {offs[j]:.2f}, chi2 {grid[i, j]:.1f}; chi2(K=0) {grid[0, 0]:.1f}")
pro = grid[:, 0]  # offset 0 = reflection expectation
k0 = np.argmin(pro); print(f"phase fixed by reflection expectation (offset 0): K = {Ks[k0]:.1f} km/s, chi2 {pro[k0]:.1f}, delta chi2 vs K=0 {pro[0] - pro[k0]:.1f}; K range (dchi2<4) {Ks[pro <= pro[k0] + 4].min():.1f}-{Ks[pro <= pro[k0] + 4].max():.1f}")
pro5 = grid[:, 200]; k5 = np.argmin(pro5); print(f"opposite phase (offset 0.5): best K {Ks[k5]:.1f}, chi2 {pro5[k5]:.1f}")
