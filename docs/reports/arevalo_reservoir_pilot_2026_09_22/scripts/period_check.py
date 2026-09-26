"""Period ambiguity tests on the three uncatalogued EBs, per band, per-OID normalised.
Fold at P_test; measure mean depth in phase windows around 0 and 0.5 with bootstrap errors,
and count in-eclipse points on odd vs even cycles of the half period."""
import json, numpy as np
from astropy.timeseries import BoxLeastSquares
A = "/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/arev"
L = {k.strip(): v for k, v in json.load(open(f"{A}/lc_cache.json")).items()}
tests = {"AREV_747_000417_zg_c05_q1": 3.482524, "AREV_1918_000493_zg_c16_q4": 1.076991, "AREV_990_000495_zg_c14_q3": 6.381704}
rng = np.random.default_rng(1)
for sid, P in tests.items():
    rows = L[sid]
    t_all = np.array([float(x["mjd"]) for x in rows]); m_all = np.array([float(x["mag"]) for x in rows])
    o_all = np.array([x["oid"] for x in rows]); b_all = np.array([x["filtercode"] for x in rows])
    for o in set(o_all): m_all[o_all == o] -= np.median(m_all[o_all == o])
    # refine P and t0 with BLS on all bands pooled (flux), narrow grid
    fl = 10 ** (-0.4 * m_all)
    bls = BoxLeastSquares(t_all, fl)
    grid = P * (1 + np.linspace(-2e-4, 2e-4, 801))
    res = bls.power(grid, np.array([0.02, 0.04, 0.06, 0.1]) * P, objective="snr")
    k = int(np.argmax(res.power)); P1 = float(res.period[k]); t0 = float(res.transit_time[k]); dur = float(res.duration[k])
    print(f"### {sid}: P refined {P1:.6f} d (test {P:.6f}), t0 MJD {t0:.5f}, BLS duration {dur*24:.2f} h")
    for band in ("zg", "zr", "zi"):
        s = b_all == band
        if s.sum() < 30: continue
        ph = ((t_all[s] - t0) / P1 + 0.5) % 1.0 - 0.5
        w = dur / P1 / 2 * 0.8
        def depth(center):
            d = np.abs(((ph - center) + 0.5) % 1.0 - 0.5) < w
            v = m_all[s][d]
            if len(v) < 3: return (np.nan, np.nan, len(v))
            bs = [np.median(rng.choice(v, len(v))) for _ in range(400)]
            return (np.median(v), np.std(bs), len(v))
        p, sec = depth(0.0), depth(0.5)
        out = np.abs(ph) > 3 * w; out &= np.abs(np.abs(ph) - 0.5) > 3 * w
        print(f"  {band}: primary {p[0]:+.3f}±{p[1]:.3f} (n={p[2]})   phase 0.5 {sec[0]:+.3f}±{sec[1]:.3f} (n={sec[2]})   "
              f"out-of-eclipse scatter {1.4826*np.median(np.abs(m_all[s][out])):.3f} (n={out.sum()})")
    # half-period parity test: at P1/2, are eclipse points split between even and odd cycles?
    cyc = np.floor((t_all - t0) / (P1 / 2) + 0.5).astype(int)
    phh = ((t_all - t0) / (P1 / 2) + 0.5) % 1.0 - 0.5
    ine = np.abs(phh) < dur / (P1 / 2) / 2 * 0.8
    ev = ine & (cyc % 2 == 0); od = ine & (cyc % 2 == 1)
    print(f"  at P/2: points in eclipse window on even cycles {ev.sum()} (median {np.median(m_all[ev]) if ev.sum() else np.nan:+.3f}), "
          f"odd cycles {od.sum()} (median {np.median(m_all[od]) if od.sum() else np.nan:+.3f})")
    json.dump(dict(P=P1, t0_mjd=t0, dur_d=dur), open(f"{A}/eph_{sid}.json", "w"))
