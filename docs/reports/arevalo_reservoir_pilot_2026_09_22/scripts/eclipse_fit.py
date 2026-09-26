"""HJD ephemeris + trapezoid eclipse fits (per band) for the three uncatalogued EBs.
Duration = trapezoid T14 (first to last contact), so it is a fitted width, not a span of points."""
import json, numpy as np
from scipy import optimize
from astropy.timeseries import BoxLeastSquares
A = "/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/arev"
L = {k.strip(): v for k, v in json.load(open(f"{A}/lc_cache.json")).items()}
rng = np.random.default_rng(3)
def load(sid):
    rows = L[sid]
    t = np.array([float(x["hjd"]) for x in rows]); m = np.array([float(x["mag"]) for x in rows])
    e = np.array([float(x["magerr"]) for x in rows]); o = np.array([x["oid"] for x in rows]); b = np.array([x["filtercode"] for x in rows])
    for q in set(o): m[o == q] -= np.median(m[o == q])
    return t, m, e, b
def trap(ph, c, d, T14, f):
    """flux model in phase units: depth d, total width T14, flat-bottom fraction f of T14"""
    x = np.abs(ph - c); T23 = f * T14; y = np.ones_like(ph)
    full = x <= T23 / 2; part = (x > T23 / 2) & (x < T14 / 2)
    y[full] = 1 - d
    y[part] = 1 - d * (T14 / 2 - x[part]) / max(1e-9, (T14 - T23) / 2)
    return y
def fit_band(ph, flux, center, T14_0):
    sel = np.abs(((ph - center) + 0.5) % 1.0 - 0.5) < 0.25
    p = ((ph[sel] - center + 0.5) % 1.0 - 0.5); y = flux[sel]
    def resid(q): return trap(p, q[0], q[1], q[2], q[3]) - y
    best = None
    for f0 in (0.0, 0.3, 0.6):
        try:
            r = optimize.least_squares(resid, [0.0, 0.2, T14_0, f0], bounds=([-0.02, 0.0, 0.003, 0.0], [0.02, 0.9, 0.2, 0.95]))
            if best is None or r.cost < best.cost: best = r
        except Exception:
            pass
    return best.x, p, y
out = {}
for sid, P0, T0 in (("AREV_747_000417_zg_c05_q1", 3.482501, 0.02), ("AREV_1918_000493_zg_c16_q4", 1.076986, 0.04),
                    ("AREV_990_000495_zg_c14_q3", 6.381774, 0.02)):
    t, m, e, b = load(sid); fl = 10 ** (-0.4 * m)
    bls = BoxLeastSquares(t, fl); grid = P0 * (1 + np.linspace(-1.5e-4, 1.5e-4, 1201))
    res = bls.power(grid, np.array([0.5, 1, 2]) * T0 * P0, objective="snr"); k = int(np.argmax(res.power))
    P = float(res.period[k]); t0 = float(res.transit_time[k])
    # move t0 to the middle of the data span (smallest ephemeris covariance)
    n_mid = np.round((np.median(t) - t0) / P); t0 += n_mid * P
    rec = dict(P=P, T0_HJD=t0, bands={})
    print(f"### {sid}: P = {P:.6f} d, T0 = HJD {t0:.5f} (data {t.min()-2400000:.1f}-{t.max()-2400000:.1f})")
    for band in ("zr", "zg", "zi"):
        s = b == band
        if s.sum() < 40: continue
        ph = ((t[s] - t0) / P) % 1.0
        x, p, y = fit_band(ph, fl[s], 0.0, T0)
        boots = []
        for _ in range(150):
            j = rng.integers(0, s.sum(), s.sum())
            try: xb, _, _ = fit_band(ph[j], fl[s][j], 0.0, T0); boots.append(xb)
            except Exception: pass
        boots = np.array(boots)
        dmag = -2.5 * np.log10(1 - x[1])
        rec["bands"][band] = dict(depth_mag=dmag, depth_err=float(np.std(-2.5 * np.log10(1 - boots[:, 1]))),
                                  T14_frac=x[2], T14_err=float(np.std(boots[:, 2])), flat=x[3], n=int(s.sum()),
                                  n_in=int((np.abs(p - x[0]) < x[2] / 2).sum()))
        bb = rec["bands"][band]
        line = (f"  {band}: primary depth {dmag:.3f}±{bb['depth_err']:.3f} mag, T14 = {x[2]*100:.2f}±{bb['T14_err']*100:.2f}% of P "
                f"({x[2]*P*24:.2f} h), flat fraction {x[3]:.2f}, {bb['n_in']} points inside T14")
        # secondary at 0.5 (same width), and for 747 the 2P parity test
        x2, p2, y2 = fit_band(ph, fl[s], 0.5, x[2])
        bb["sec_depth_mag"] = float(-2.5 * np.log10(1 - x2[1])); bb["sec_T14_frac"] = float(x2[2])
        line += f" | phase-0.5 depth {bb['sec_depth_mag']:.3f} mag"
        print(line)
    if sid.startswith("AREV_747"):
        for band in ("zr", "zg"):
            s = b == band; ph2 = ((t[s] - t0) / (2 * P)) % 1.0
            a, _, _ = fit_band(ph2, fl[s], 0.0, rec["bands"][band]["T14_frac"] / 2)
            c, _, _ = fit_band(ph2, fl[s], 0.5, rec["bands"][band]["T14_frac"] / 2)
            print(f"  2P = {2*P:.6f} d test, {band}: eclipse at 0.0 depth {-2.5*np.log10(1-a[1]):.3f}, at 0.5 depth {-2.5*np.log10(1-c[1]):.3f}")
    out[sid] = rec
json.dump(out, open(f"{A}/eclipse_fit.json", "w"), indent=1)
