"""Robust per-exposure velocities (median over the Balmer lines; error = 1.2533 * robust scatter / sqrt(n), floor 5 km/s) and a sinusoid fit at the
photometric period (87.33 min = 16.48871 c/d) with free K, phase and one systemic velocity per visit; constant-velocity chi2; K upper limit from
the chi2 profile."""
import numpy as np
P = 1 / 16.48871
data = {  # exposure mid-times (MJD) and per-line velocities (Ha, Hb, Hg, Hd, He) from exp_rv_sdss.py
 "SDSS2007": [(54174.20249, [7.1, -11.2, 1.5, -4.6, -2.2]), (54174.21483, [2.3, 17.2, 24.9, 3.7, -37.4]), (54174.22715, [-4.7, -6.9, -7.9, -11.6, 9.7])],
 "BOSS2012": [(55987.25704, [10.6, 21.8, 1.5, 15.6, -2.7]), (55987.26841, [39.0, 158.6, 33.6, 19.4, 7.4]), (55987.27977, [-3.9, -11.2, 18.2, 38.8, -11.4]),
              (55987.29115, [12.1, -25.6, -19.6, -45.1, -36.2]), (55987.30252, [-207.8, -27.8, -6.6, 21.9, 19.2]), (55987.31388, [-37.0, -2.3, 2.2, -6.2, -31.4])]}
T, V, E, G = [], [], [], []
for gi, (vis, rows) in enumerate(data.items()):
    for t, vs in rows:
        v = np.array(vs); med = np.median(v); mad = 1.4826 * np.median(np.abs(v - med)); err = max(1.2533 * mad / np.sqrt(len(v)), 5.0)
        T.append(t); V.append(med); E.append(err); G.append(gi); print(f"{vis} MJD {t:.5f}: {med:+6.1f} ± {err:4.1f} km/s")
T, V, E, G = map(np.array, (T, V, E, G))
chi_const = sum(np.sum(((V[G == g] - np.average(V[G == g], weights=1 / E[G == g] ** 2)) / E[G == g]) ** 2) for g in (0, 1)); dof = len(V) - 2
print(f"constant (per visit): chi2 = {chi_const:.1f} for {dof} dof")
best = (np.inf, None); Ks = np.arange(0, 151, 1.0); prof = []
for K in Ks:
    cb = np.inf
    for ph in np.linspace(0, 1, 200, endpoint=False):
        m = K * np.sin(2 * np.pi * (T / P + ph)); c = 0
        for g in (0, 1):
            k = G == g; w = 1 / E[k] ** 2; gam = np.sum(w * (V[k] - m[k])) / w.sum(); c += np.sum(((V[k] - m[k] - gam) / E[k]) ** 2)
        cb = min(cb, c)
    prof.append(cb)
prof = np.array(prof); kb = Ks[np.argmin(prof)]
print(f"best K = {kb:.0f} km/s, chi2 = {prof.min():.1f} (dof {len(V) - 4}); delta chi2 vs K=0: {prof[0] - prof.min():.1f}")
ul = Ks[(prof <= prof.min() + 4) ].max(); print(f"K range with delta chi2 < 4 (about 2 sigma): 0-{ul:.0f} km/s" if prof[0] <= prof.min() + 4 else f"K range (delta chi2 < 4): {Ks[prof <= prof.min() + 4].min():.0f}-{ul:.0f} km/s")
for K in (35, 50, 70, 100): print(f"  K = {K}: delta chi2 = {prof[int(K)] - prof.min():.1f}")
