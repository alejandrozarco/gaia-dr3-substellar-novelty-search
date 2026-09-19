import numpy as np
from astropy.timeseries import BoxLeastSquares

def refine_period(mjd, flux, ferr, P0, durations):
    """BLS on a short-duty signal fits integer MULTIPLES of the true period. Scan
    sub-harmonics P0/n and adopt the one with MAXIMUM snr (verified on ZTF18abxnwmb:
    raw BLS gives 3x the true period, and n=3 has the highest snr of all harmonics).
    Then resolve the classic EB half-period ambiguity by comparing the dip depth at
    phase 0 against phase 0.5 - unequal depths mean the LONGER period is correct."""
    bls = BoxLeastSquares(mjd, flux, dy=ferr)
    best = None
    for n in range(1, 9):
        Pn = P0/n
        if Pn < 0.15: continue
        g = np.linspace(Pn*0.996, Pn*1.004, 600)
        r = bls.power(g, durations, objective="snr")
        k = int(np.argmax(r.power))
        cand = (float(r.power[k]), float(r.period[k]), float(r.duration[k]),
                float(r.transit_time[k]), float(r.depth[k]), n)
        if best is None or cand[0] > best[0]: best = cand
    snr, P, dur, t0, depth, n = best

    # half-period ambiguity: if doubling reveals unequal alternating depths, 2P is true
    g2 = np.linspace(2*P*0.998, 2*P*1.002, 400)
    r2 = bls.power(g2, durations, objective="snr"); k2 = int(np.argmax(r2.power))
    P2, d2, t02 = float(r2.period[k2]), float(r2.duration[k2]), float(r2.transit_time[k2])
    ph = ((mjd - t02)/P2) % 1.0
    w = (d2/P2)/2*1.2
    prim = np.abs(ph) < w; prim |= np.abs(ph-1) < w
    seco = np.abs(ph-0.5) < w
    if prim.sum() >= 4 and seco.sum() >= 4:
        dp = 1.0 - float(np.median(flux[prim])); ds = 1.0 - float(np.median(flux[seco]))
        # unequal depths (>2x) => the doubled period is the real orbital period
        if dp > 0 and ds > 0 and (dp/ds > 2.0 or ds/dp > 2.0):
            return P2, float(r2.power[k2]), n, dict(doubled=True, dprim=round(dp,5), dsec=round(ds,5))
    return P, snr, n, dict(doubled=False)
