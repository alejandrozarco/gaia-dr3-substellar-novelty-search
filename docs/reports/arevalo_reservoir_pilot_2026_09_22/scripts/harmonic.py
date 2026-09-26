import numpy as np
from astropy.timeseries import BoxLeastSquares

def top_peaks(periods, power, k=5, sep=0.05):
    """Top-k DISTINCT periodogram peaks. Taking only the global maximum is fragile:
    at 5,000 grid points the raw peak for our template landed on 2.5448 d, which is
    not related to the true 3.727023 d by ANY integer factor, so no harmonic scan
    could recover it. The true period is reliably among the top few peaks."""
    order = np.argsort(power)[::-1]
    out = []
    for i in order:
        P = float(periods[i])
        if all(abs(P-q)/q > sep for q in out):
            out.append(P)
        if len(out) >= k: break
    return out


def refine_period(mjd, flux, ferr, P0, durations, extra_seeds=()):
    """BLS on a short-duty signal fits integer MULTIPLES of the true period. Scan
    sub-harmonics P0/n and adopt the one with MAXIMUM snr (verified on ZTF18abxnwmb:
    raw BLS gives 3x the true period, and n=3 has the highest snr of all harmonics).
    Then resolve the classic EB half-period ambiguity by comparing the dip depth at
    phase 0 against phase 0.5 - unequal depths mean the LONGER period is correct."""
    bls = BoxLeastSquares(mjd, flux, dy=ferr)
    # BLS can lock onto EITHER a super-harmonic (integer multiple) or a sub-harmonic
    # (the half-period, when primary and secondary fold together). Scanning only P0/n
    # loses the template when the raw peak lands on P_true/2 - which is grid-dependent:
    # a 7,000-point grid gave 1.8634 d for our filed EB (true 3.727023), a 12,000-point
    # grid gave 11.1817 d. Scan BOTH directions.
    cands = []
    for seed in (P0,) + tuple(extra_seeds):
        for n in range(1, 7):
            cands.append(seed/n)
            cands.append(seed*n)
    best = None
    for Pn in sorted(set(c for c in cands if 0.15 <= c <= 60.0)):
        g = np.linspace(Pn*0.996, Pn*1.004, 600)
        r = bls.power(g, durations, objective="snr")
        k = int(np.argmax(r.power))
        cand = (float(r.power[k]), float(r.period[k]), float(r.duration[k]),
                float(r.transit_time[k]), float(r.depth[k]), Pn)
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
    if prim.sum() >= 3 and seco.sum() >= 3:
        dp = 1.0 - float(np.median(flux[prim])); ds = 1.0 - float(np.median(flux[seco]))
        scat = float(np.median(np.abs(flux - np.median(flux))))*1.4826
        ep = scat/np.sqrt(prim.sum()); es = scat/np.sqrt(seco.sum())
        sig = abs(dp-ds)/np.hypot(ep, es) if (ep > 0 and es > 0) else 0.0
        # LOGIC (verified against two known objects, 2026-09-19):
        #   true period P, one eclipse/cycle  -> folding at 2P puts ALTERNATE eclipses
        #     at phase 0 and 0.5 with EQUAL depths  => keep the SHORTER period
        #   true period 2P, distinct primary+secondary -> UNEQUAL depths => adopt 2P
        # Equal-depth twins are genuinely DEGENERATE between P and 2P; flag, do not assert.
        if ds > 3*scat and dp > 3*scat and sig > 3.0:
            return P2, float(r2.power[k2]), n, dict(doubled=True, dprim=round(dp,5),
                   dsec=round(ds,5), depth_sigma=round(float(sig),2))
        if ds > 3*scat and dp > 3*scat:
            return P, snr, n, dict(doubled=False, period_ambiguous=True,
                   P_double=round(P2,6), dprim=round(dp,5), dsec=round(ds,5),
                   depth_sigma=round(float(sig),2))
    return P, snr, n, dict(doubled=False)
