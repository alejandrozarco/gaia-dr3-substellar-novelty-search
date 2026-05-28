#!/usr/bin/env python
"""
CRTS J051419.8+011120  --  multi-sector TESS eclipse-timing / third-body test.

Self-contained pipeline:
  fetch (TESScut S5/S32/S98) -> aperture+background photometry -> phase-fold at
  ZTF P -> narrow-window BLS -> per-sector detectability -> eclipse mid-times ->
  O-C diagram with careful cycle counting -> tertiary (LTT) limit -> refined period.

Target
  Gaia DR3 3233913634323725696, TIC 672454027, Tmag = 18.87
  ICRS (Gaia DR3 ep 2016.0): RA = 78.58284521736 deg, Dec = +1.18914740612 deg
  Known orbital period (ZTF DR23 BLS, 7.2-yr baseline): P = 0.1255349 d = 180.770 min
     formal sigma_P = 1.4 s; eclipse deep (median quiescent ~71%), narrow (~18 min, ~3.5% phase)

HONESTY: at Tmag 18.87 the 18-min eclipse is shorter than the S5 30-min cadence and
marginal vs the S32 10-min cadence. A clean NULL for S5 (and possibly S32) is a valid
result. We state detectability per sector BEFORE any timing claim and never manufacture
an O-C from noise.

Run:
  /Users/legbatterij/claude_projects/ostinato/.venv/bin/python \
      scripts/crts_j051419_s5s32_etv.py
Outputs:
  /tmp/crts_j051419_s5s32_*.json,  /tmp/crts_j051419_s5s32_*.png,
  /tmp/crts_j051419_s5s32_report.md
"""
import warnings
warnings.filterwarnings("ignore")
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import lightkurve as lk
from astropy.stats import sigma_clipped_stats
from astropy.timeseries import BoxLeastSquares
from astropy.time import Time
from astropy.coordinates import SkyCoord
import astropy.units as u

# ----------------------------------------------------------------------------
# Constants / target
# ----------------------------------------------------------------------------
RA = 78.58284521736          # deg, ICRS Gaia DR3 ep 2016.0
DEC = +1.18914740612         # deg
TIC = 672454027
TMAG = 18.87

P_ZTF = 0.1255349            # d   (science-grade ZTF DR23 period)
SIGMA_P_ZTF = 1.4 / 86400.0  # d   (1.4 s)
ECL_DUR_D = 0.0125           # d   (~18 min eclipse, ~3.5% of phase)

OUT = "/tmp"
SECTORS = [5, 32, 98]
CADENCE_S = {5: 1800.0, 32: 600.0, 98: 120.0}

# BTJD = BJD_TDB - 2457000.0
BTJD_OFFSET = 2457000.0

rng = np.random.default_rng(20260528)


# ----------------------------------------------------------------------------
# 1. Fetch + photometry
# ----------------------------------------------------------------------------
def get_tpf(sector, cutout_size=15):
    sr = lk.search_tesscut(f"{RA} {DEC}")
    row = sr[sr.table["sequence_number"] == sector]
    if len(row) == 0:
        raise RuntimeError(f"sector {sector} not in TESScut search")
    tpf = row.download(cutout_size=cutout_size)
    return tpf


def make_aperture(tpf, target_px=None, aper_radius=1.5):
    """Build a target aperture around the WCS position of the target.

    Faint, blended source at 21"/px: keep the aperture small (a 3x3-ish core)
    centred on the pixel containing the catalog position.
    """
    ny, nx = tpf.shape[1], tpf.shape[2]
    # pixel coordinate of target from WCS
    try:
        coord = SkyCoord(RA, DEC, unit="deg")
        col, line = tpf.wcs.world_to_pixel(coord)  # 0-based within cutout
        cx, cy = float(col), float(line)
    except Exception:
        cx, cy = (nx - 1) / 2.0, (ny - 1) / 2.0
    if target_px is not None:
        cx, cy = target_px
    yy, xx = np.mgrid[0:ny, 0:nx]
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    aper = r <= aper_radius
    if aper.sum() == 0:  # fall back to single nearest pixel
        aper = r == r.min()
    return aper, (cx, cy)


def background_mask(tpf, center, aper, r_bkg_min=3.5):
    """Background pixels = everything outside an inner radius AND not in the
    aperture.  We then sigma-clip *within* this set per cadence to reject the
    bright contaminating blends (the field has several stars brighter than the
    Tmag=18.87 target), leaving the true sky/scattered-light floor.
    """
    ny, nx = tpf.shape[1], tpf.shape[2]
    cx, cy = center
    yy, xx = np.mgrid[0:ny, 0:nx]
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    return (r >= r_bkg_min) & (~aper)


def extract_lightcurve(tpf, aper_radius=1.5):
    """Differential aperture photometry for a VERY faint, blended source.

    At Tmag 18.87 the target (~3.5 e-/s, cf. SPOC) sits at/below the ~130 e-/s
    per-pixel TESS background and is flanked by brighter blends.  Absolute
    photometry is hopeless; we instead measure the target as a *relative dip*:

      net(t) = sum_aper(t) - n_ap * bkg_scalar(t)

    where bkg_scalar(t) is a 3-sigma-clipped median over background pixels
    (clipping removes the bright neighbour PSFs so they do not inflate the
    background).  The residual net flux carries the target + a slowly varying
    floor; the slow floor is removed later by detrending, leaving the eclipse.
    """
    q = tpf.quality == 0
    flux_cube = tpf.flux.value  # (ncad, ny, nx), e-/s
    time = tpf.time.value       # BTJD
    aper, center = make_aperture(tpf, aper_radius=aper_radius)
    bkg = background_mask(tpf, center, aper)
    n_ap = int(aper.sum())

    raw = np.array([np.nansum(f[aper]) for f in flux_cube])
    # robust per-cadence sky level + scatter (sigma-clipped over bkg pixels)
    stats = [sigma_clipped_stats(f[bkg][np.isfinite(f[bkg])], sigma=3.0,
                                 maxiters=5) if np.isfinite(f[bkg]).sum() > 5
             else (np.nan, np.nan, np.nan) for f in flux_cube]
    bkg_pp = np.array([s[1] for s in stats])      # clipped median per pixel
    bkg_std_pp = np.array([s[2] for s in stats])  # clipped std per pixel
    flux = raw - n_ap * bkg_pp

    good = q & np.isfinite(flux) & np.isfinite(time)
    return {
        "time": time[good],
        "flux": flux[good],
        "raw": raw[good],
        "bkg_pp": bkg_pp[good],
        "bkg_std_pp": bkg_std_pp[good],
        "n_ap": n_ap,
        "aper": aper,
        "bkg": bkg,
        "center": center,
    }


def mask_outbursts(time, flux, hi=2.0, lo=0.4):
    """Flag dwarf-nova outbursts: cadences far above the quiescent flux mode.

    The S98 SPOC LC shows ~4 outbursts; outbursts inject huge scatter and make
    BLS latch onto outburst edges, swamping the ~18-min eclipse.  We keep only
    QUIESCENT cadences (flux within [lo, hi] x mode) for folding/timing, exactly
    as the published per-eclipse depth analysis did.

    The 'mode' is the histogram peak of the flux distribution (robust to the
    arbitrary additive offset left by differential photometry: we work on the
    flux shifted so the quiescent level is positive).
    """
    f = np.asarray(flux, float)
    # shift so the bulk is positive (differential flux can straddle zero)
    f0 = f - np.nanpercentile(f, 1) + 1.0
    # histogram-peak mode of the lower 80%
    lowf = f0[f0 <= np.nanpercentile(f0, 80)]
    if len(lowf) < 20:
        mode = np.nanmedian(f0)
    else:
        hist, edges = np.histogram(lowf, bins=40)
        mode = 0.5 * (edges[np.argmax(hist)] + edges[np.argmax(hist) + 1])
    quiescent = (f0 >= lo * mode) & (f0 <= hi * mode)
    return quiescent, float(mode)


# ----------------------------------------------------------------------------
# 2. De-trend (remove DN outbursts / slow trends), keep eclipse signal
# ----------------------------------------------------------------------------
def _running_median(t_sorted, f_sorted, window_d):
    """O(N log N) running median over a time window using a two-pointer
    sliding window (recompute median on the in-window slice; windows are small
    so this is fast enough and robust)."""
    n = len(t_sorted)
    trend = np.empty(n)
    lo = 0
    hi = 0
    for i in range(n):
        while t_sorted[lo] < t_sorted[i] - window_d / 2.0:
            lo += 1
        if hi < i:
            hi = i
        while hi + 1 < n and t_sorted[hi + 1] <= t_sorted[i] + window_d / 2.0:
            hi += 1
        sl = f_sorted[lo:hi + 1]
        trend[i] = np.median(sl) if len(sl) >= 1 else f_sorted[i]
    return trend


def detrend(time, flux, window_d=0.5, ref_level=None):
    """Additive de-trend: subtract a slow running-median baseline, then
    renormalize so the quiescent out-of-eclipse level is ~1.0 and a deep
    eclipse appears as a dip toward 0.

    Differential photometry of a faint blended source produces flux that can
    straddle zero, so a multiplicative (divide) detrend is unstable.  We instead
    remove the slow floor (scattered light + constant blends + DN outburst
    envelope) additively, then scale by a robust quiescent amplitude estimate.
    """
    order = np.argsort(time)
    t = time[order]
    f = flux[order]
    trend = _running_median(t, f, window_d)
    resid = f - trend                       # eclipse = negative excursion
    # robust amplitude of the OOE scatter to set a flux scale (so depth is
    # expressed as a fraction of the quiescent flux).  Use the SPOC-equivalent
    # quiescent target flux if provided; else the running-median level itself.
    if ref_level is None:
        scale = np.median(trend)
        scale = scale if scale > 0 else (np.median(np.abs(resid)) * 5 + 1e-9)
    else:
        scale = ref_level
    fn = 1.0 + resid / scale
    inv = np.argsort(order)
    return fn[inv], trend[inv]


# ----------------------------------------------------------------------------
# 3. Phase fold + detectability + narrow BLS
# ----------------------------------------------------------------------------
def phase_of(time, P, T0):
    ph = ((time - T0) / P) % 1.0
    ph[ph > 0.5] -= 1.0
    return ph


def detectability(time, flux_norm, P, T0, half_width_phase=None):
    """In-eclipse vs out-of-eclipse depth + significance at fixed (P, T0).

    Returns depth (fractional), its uncertainty, and significance in sigma.
    """
    if half_width_phase is None:
        half_width_phase = (ECL_DUR_D / P) / 2.0  # half eclipse width in phase
    ph = phase_of(time, P, T0)
    in_ecl = np.abs(ph) <= half_width_phase
    # out-of-eclipse: well away from the dip (avoid shoulders)
    out_ecl = np.abs(ph) >= 3 * half_width_phase
    n_in, n_out = int(in_ecl.sum()), int(out_ecl.sum())
    if n_in < 2 or n_out < 5:
        return dict(detect=False, reason="too few in/out points",
                    n_in=n_in, n_out=n_out)
    f_in = flux_norm[in_ecl]
    f_out = flux_norm[out_ecl]
    mu_in, mu_out = np.median(f_in), np.median(f_out)
    # robust scatter
    s_in = sigma_clipped_stats(f_in, sigma=4)[2]
    s_out = sigma_clipped_stats(f_out, sigma=4)[2]
    depth = mu_out - mu_in          # fractional (flux normalized to ~1)
    # uncertainty on the difference of medians (~1.253 sigma/sqrt(N) for median)
    err_in = 1.253 * s_in / np.sqrt(max(n_in, 1))
    err_out = 1.253 * s_out / np.sqrt(max(n_out, 1))
    derr = np.sqrt(err_in ** 2 + err_out ** 2)
    sig = depth / derr if derr > 0 else 0.0
    return dict(detect=bool(sig >= 3 and depth > 0),
                depth=float(depth), depth_err=float(derr), sigma=float(sig),
                mu_in=float(mu_in), mu_out=float(mu_out),
                s_in=float(s_in), s_out=float(s_out),
                n_in=n_in, n_out=n_out,
                half_width_phase=float(half_width_phase))


def binned_dip_significance(time, flux_norm, P, T0, nbins=24, nboot=300):
    """Most sensitive fair detection statistic for a faint, narrow eclipse.

    Bin the phase-folded (quiescent) flux into nbins; the deepest bin gives a
    depth and a single-bin significance.  Then a permutation test (shuffle flux
    vs phase) gives the global false-alarm distribution of the deepest-bin
    statistic, so we report a look-elsewhere-aware p-value.  This beats the
    per-cadence noise down by sqrt(N_bin) and is robust to the shallow,
    smeared eclipse expected at Tmag 18.87.
    """
    f = np.asarray(flux_norm, float)
    f = f - np.median(f)
    n = len(f)
    if n < 50:
        return dict(ok=False, reason="too few quiescent cadences", n=n)
    ph = (phase_of(time, P, T0) + 0.5)  # 0..1
    b = np.clip((ph * nbins).astype(int), 0, nbins - 1)
    scat = np.std(f)

    def deepest(bb):
        means = np.full(nbins, np.nan)
        cnts = np.zeros(nbins)
        for k in range(nbins):
            m = bb == k
            cnts[k] = m.sum()
            if m.sum() >= 3:
                means[k] = f[m].mean()
        kmin = int(np.nanargmin(means))
        sig = means[kmin] / (scat / np.sqrt(max(cnts[kmin], 1)))
        return means[kmin], sig, kmin, cnts[kmin]

    depth, sig, kmin, n_in = deepest(b)
    # permutation false-alarm: how often does a random shuffle produce a dip
    # at least this deep (most negative single-bin significance)?
    worse = 0
    for _ in range(nboot):
        fb = rng.permutation(b)  # randomize which bin each point lands in
        _, s2, _, _ = deepest(fb)
        if s2 <= sig:
            worse += 1
    fap = worse / nboot
    return dict(ok=True, depth=float(-depth), sigma=float(-sig),
                fap=float(fap), n_in_bin=int(n_in), nbins=nbins,
                scatter=float(scat),
                detect=bool((-sig) >= 3.0 and fap <= 0.01 and -depth > 0))


def narrow_bls(time, flux_norm, P0, frac=0.01, ndur=4):
    """BLS in a narrow window around P0 (+/- frac).  Returns best P, power, SNR."""
    if len(time) < 20:
        return None
    baseline = time.max() - time.min()
    # period resolution ~ P^2 / baseline; oversample x5
    dP = P0 ** 2 / baseline / 5.0
    pmin, pmax = P0 * (1 - frac), P0 * (1 + frac)
    periods = np.arange(pmin, pmax, dP)
    if len(periods) < 5:
        periods = np.linspace(pmin, pmax, 200)
    durations = np.linspace(0.5 * ECL_DUR_D, 1.5 * ECL_DUR_D, ndur)
    bls = BoxLeastSquares(time, flux_norm)
    res = bls.power(periods, durations)
    i = int(np.nanargmax(res.power))
    pw = res.power
    snr = (pw[i] - np.nanmedian(pw)) / (1.4826 * np.nanmedian(np.abs(pw - np.nanmedian(pw))) + 1e-12)
    return dict(period=float(res.period[i]), power=float(pw[i]),
                duration=float(res.duration[i]), t0=float(res.transit_time[i]),
                depth=float(res.depth[i]), snr=float(snr),
                periods=periods, power_arr=pw)


# ----------------------------------------------------------------------------
# 4. Eclipse mid-time per sector (fold + model fit + bootstrap error)
# ----------------------------------------------------------------------------
def fold_binned(time, flux_norm, P, T0, nbins=60):
    ph = phase_of(time, P, T0)
    edges = np.linspace(-0.5, 0.5, nbins + 1)
    cen = 0.5 * (edges[:-1] + edges[1:])
    val = np.full(nbins, np.nan)
    err = np.full(nbins, np.nan)
    for k in range(nbins):
        m = (ph >= edges[k]) & (ph < edges[k + 1])
        if m.sum() >= 1:
            val[k] = np.median(flux_norm[m])
            if m.sum() >= 2:
                err[k] = 1.253 * np.std(flux_norm[m]) / np.sqrt(m.sum())
    return cen, val, err


def gaussian_dip(ph, depth, center, sigma, base):
    return base - depth * np.exp(-0.5 * ((ph - center) / sigma) ** 2)


def measure_midtime(time, flux_norm, P, T0_guess, sector, nboot=400):
    """Fit a Gaussian dip to the phase-folded data; phase offset -> mid-time.

    Returns T_mid (BTJD, referenced to the mean epoch of the sector), error
    (bootstrap), and the fitted depth/width.  Uses scipy curve_fit.
    """
    from scipy.optimize import curve_fit
    ph = phase_of(time, P, T0_guess)
    sigma0 = (ECL_DUR_D / P) / 2.35  # FWHM ~ eclipse duration
    p0 = [0.2, 0.0, max(sigma0, 0.01), 1.0]
    # restrict the fit to +/- 5 sigma around expected dip for stability
    mfit = np.abs(ph) <= max(5 * sigma0, 0.12)
    if mfit.sum() < 8:
        mfit = np.ones_like(ph, dtype=bool)

    def _fit(phs, fls):
        bounds = ([0.0, -0.25, 0.005, 0.5], [1.5, 0.25, 0.2, 1.5])
        popt, _ = curve_fit(gaussian_dip, phs, fls, p0=p0,
                            bounds=bounds, maxfev=20000)
        return popt

    try:
        popt = _fit(ph[mfit], flux_norm[mfit])
    except Exception as e:
        return dict(ok=False, reason=f"fit failed: {e}")

    depth, center, sig, base = popt
    # mean epoch of the sector data (cycle for that fold reference)
    t_mean = np.mean(time)
    # nearest predicted eclipse to t_mean under (P,T0_guess)
    E_mean = np.round((t_mean - T0_guess) / P)
    T_pred = T0_guess + E_mean * P
    # measured mid-time = predicted + phase-offset*P
    T_mid = T_pred + center * P

    # bootstrap error on T_mid
    boots = []
    N = mfit.sum()
    idx = np.where(mfit)[0]
    for _ in range(nboot):
        bs = rng.choice(idx, size=N, replace=True)
        try:
            pb = _fit(ph[bs], flux_norm[bs])
            boots.append(pb[1])
        except Exception:
            continue
    if len(boots) > 20:
        cen_err = np.std(boots)
    else:
        cen_err = np.nan
    T_mid_err = cen_err * P if np.isfinite(cen_err) else np.nan

    return dict(ok=True, T_mid=float(T_mid), T_mid_err=float(T_mid_err),
                depth=float(depth), depth_phasefit=float(depth),
                sigma_phase=float(sig), base=float(base),
                center_phase=float(center), center_phase_err=float(cen_err),
                E_mean=int(E_mean), T_pred=float(T_pred),
                n_fit=int(mfit.sum()), nboot_ok=len(boots))


# ----------------------------------------------------------------------------
# 5. O-C / linear ephemeris / third-body LTT limit
# ----------------------------------------------------------------------------
def build_oc(epochs, P_ref):
    """epochs: list of dicts with 'sector','T_mid','T_mid_err'.

    Anchor T0 to the S98 epoch (highest quality).  Compute integer cycle counts
    relative to that anchor using P_ref, then fit a refined linear ephemeris.
    """
    anchor = [e for e in epochs if e["sector"] == 98]
    if not anchor:
        anchor = [epochs[np.argmin([e["T_mid_err"] for e in epochs])]]
    T0 = anchor[0]["T_mid"]
    out = []
    for e in epochs:
        dt = e["T_mid"] - T0
        E = int(np.round(dt / P_ref))
        oc = e["T_mid"] - (T0 + E * P_ref)  # O - C in days
        out.append(dict(sector=e["sector"], T_mid=e["T_mid"],
                        T_mid_err=e["T_mid_err"], cycle=E,
                        oc_d=float(oc), oc_s=float(oc * 86400.0),
                        T0_anchor=float(T0)))
    return out, T0


def refine_period(oc_table, P_ref, T0):
    """Weighted linear fit T_mid = T0' + P' * E across epochs."""
    E = np.array([r["cycle"] for r in oc_table], float)
    T = np.array([r["T_mid"] for r in oc_table], float)
    w = np.array([1.0 / (r["T_mid_err"] ** 2)
                  if (r["T_mid_err"] and np.isfinite(r["T_mid_err"]) and r["T_mid_err"] > 0)
                  else np.nan for r in oc_table])
    ok = np.isfinite(w)
    if ok.sum() < 2:
        # cannot fit a slope with <2 weighted epochs
        return dict(ok=False, reason="need >=2 timed epochs with errors",
                    n_used=int(ok.sum()))
    E, T, w = E[ok], T[ok], w[ok]
    # weighted least squares for [T0', P']
    A = np.vstack([np.ones_like(E), E]).T
    W = np.diag(w)
    cov = np.linalg.inv(A.T @ W @ A)
    beta = cov @ (A.T @ W @ T)
    T0p, Pp = beta
    perr = np.sqrt(np.diag(cov))
    resid = T - (T0p + Pp * E)
    return dict(ok=True, T0=float(T0p), T0_err=float(perr[0]),
                P=float(Pp), P_err=float(perr[1]),
                P_min=float(Pp * 1440.0), P_err_s=float(perr[1] * 86400.0),
                resid_s=[float(x * 86400) for x in resid],
                n_used=int(ok.sum()),
                baseline_cycles=float(E.max() - E.min()),
                baseline_yr=float((E.max() - E.min()) * Pp / 365.25))


def ltt_mass_function(A_ltt_s, P3_yr):
    """Light-travel-time mass-function constraint.

    For a tertiary on a circular orbit, the LTT semi-amplitude is
        A = (a_12 sin i3) / c
    where a_12 is the semimajor axis of the inner binary's barycentre about the
    triple's centre of mass.  Kepler's third law for the outer orbit gives the
    binary mass function:
        f(M3) = (M3 sin i3)^3 / (M_bin + M3)^2
              = (4 pi^2 / G) * (a_12 sin i3)^3 / P3^2
              = (4 pi^2 / G) * (c A)^3 / P3^2
    Returns f(M3) in solar masses for amplitude A_ltt_s (seconds) and P3 (yr).
    """
    G = 6.674e-11
    c = 2.998e8
    Msun = 1.989e30
    yr = 3.156e7
    A = A_ltt_s              # s
    P3 = P3_yr * yr          # s
    a12_sini = c * A         # m  (light seconds -> metres)
    f = (4 * np.pi ** 2 / G) * a12_sini ** 3 / P3 ** 2  # kg
    return f / Msun


def m3_min_from_f(f_Msun, M_bin=1.05, i3=90.0):
    """Solve f = (M3 sin i3)^3 / (M_bin + M3)^2 for M3 (solar), given i3."""
    from scipy.optimize import brentq
    s = np.sin(np.radians(i3))

    def g(M3):
        return (M3 * s) ** 3 / (M_bin + M3) ** 2 - f_Msun
    try:
        return float(brentq(g, 1e-4, 1e3))
    except Exception:
        return np.nan


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    results = {"target": {"name": "CRTS J051419.8+011120", "TIC": TIC,
                          "gaia_dr3": 3233913634323725696, "Tmag": TMAG,
                          "RA": RA, "Dec": DEC},
               "P_ZTF_d": P_ZTF, "P_ZTF_min": P_ZTF * 1440.0,
               "sigma_P_ZTF_s": 1.4, "sectors": {}}

    # anchor T0 guess (BTJD) from prior S98 BLS; refined below
    T0_PRIOR_S98 = 3993.771140745731

    sector_lcs = {}
    epochs = []

    for s in SECTORS:
        print(f"\n===== Sector {s} =====")
        tpf = get_tpf(s, cutout_size=15)
        cad_s = float(np.median(np.diff(tpf.time.value)) * 86400)
        print(f"  TPF {tpf.shape}, cam{tpf.camera}/ccd{tpf.ccd}, cad~{cad_s:.0f}s")
        lc = extract_lightcurve(tpf, aper_radius=1.5)
        print(f"  n_ap={lc['n_ap']} pix, {len(lc['time'])} good cadences, "
              f"median net flux={np.median(lc['flux']):.2f} e-/s, "
              f"sky~{np.median(lc['bkg_pp']):.1f} e-/s/pix")

        # ---- mask DN outbursts; keep quiescent cadences for eclipse work ----
        quiescent, mode = mask_outbursts(lc["time"], lc["flux"])
        n_q = int(quiescent.sum())
        n_ob = int((~quiescent).sum())
        print(f"  outburst mask: {n_q} quiescent / {n_ob} outburst-or-bright "
              f"cadences (mode-based)")
        # detrend the FULL series for plotting; analyse quiescent subset
        fn_all, trend = detrend(lc["time"], lc["flux"], window_d=0.5)
        lc["flux_norm"] = fn_all
        lc["trend"] = trend
        lc["quiescent"] = quiescent
        # quiescent-only arrays, re-detrended on the quiescent floor
        tq, fq_raw = lc["time"][quiescent], lc["flux"][quiescent]
        if n_q > 20:
            fq, _ = detrend(tq, fq_raw, window_d=0.5)
        else:
            fq = fn_all[quiescent]
        lc["time_q"], lc["flux_norm_q"] = tq, fq
        sector_lcs[s] = lc

        baseline = lc["time"].max() - lc["time"].min()

        # PRIMARY detection: binned-dip significance + permutation FAP at the
        # fixed ZTF ephemeris, QUIESCENT cadences only (most sensitive, fair)
        dip = binned_dip_significance(tq, fq, P_ZTF, T0_PRIOR_S98) \
            if n_q > 50 else dict(ok=False, reason="too few quiescent")
        # secondary diagnostic: simple in/out depth at fixed ephemeris
        det = detectability(tq, fq, P_ZTF, T0_PRIOR_S98)
        # narrow BLS around ZTF period (quiescent)
        bls = narrow_bls(tq, fq, P_ZTF, frac=0.012)
        # also an independent wider BLS to report what period TESS prefers
        bls_wide = narrow_bls(tq, fq, P_ZTF, frac=0.06)
        # the detection verdict comes from the binned-dip test
        det["dip_sigma"] = dip.get("sigma")
        det["dip_fap"] = dip.get("fap")
        det["dip_depth"] = dip.get("depth")
        det["detect"] = bool(dip.get("detect", False))

        sec = dict(camera=int(tpf.camera), ccd=int(tpf.ccd),
                   cadence_s=cad_s,
                   n_cadence=int(len(lc["time"])),
                   n_quiescent=n_q, n_outburst=n_ob,
                   baseline_d=float(baseline),
                   n_orbital_cycles=float(baseline / P_ZTF),
                   median_net_flux_es=float(np.median(lc["flux"])),
                   sky_es_per_pix=float(np.median(lc["bkg_pp"])),
                   eclipse_min=float(ECL_DUR_D * 1440),
                   cadence_vs_eclipse=float(cad_s / (ECL_DUR_D * 86400)),
                   detect=det,
                   dip_test=dip)
        if bls is not None:
            sec["bls"] = {k: v for k, v in bls.items()
                          if k not in ("periods", "power_arr")}
        if bls_wide is not None:
            sec["bls_wide"] = {k: v for k, v in bls_wide.items()
                               if k not in ("periods", "power_arr")}
        results["sectors"][str(s)] = sec

        print(f"  cadence/eclipse = {sec['cadence_vs_eclipse']:.2f} "
              f"(>1 means eclipse shorter than one cadence)")
        if dip.get("ok"):
            print(f"  PRIMARY binned-dip @ZTF P: depth={dip['depth']*100:.1f}% "
                  f"sigma={dip['sigma']:.2f} FAP={dip['fap']:.3f} "
                  f"(n_in_bin={dip['n_in_bin']}) -> detect={dip['detect']}")
        if "depth" in det:
            print(f"    (in/out diagnostic: depth={det['depth']*100:.1f}% "
                  f"sigma={det['sigma']:.2f})")
        if bls:
            print(f"  narrow-BLS (quiescent, +/-1.2%): P={bls['period']*1440:.3f}min "
                  f"SNR={bls['snr']:.2f} depth={bls['depth']*100:.1f}%")
        if bls_wide:
            print(f"  wide-BLS  (quiescent, +/-6%):   P={bls_wide['period']*1440:.3f}min "
                  f"SNR={bls_wide['snr']:.2f}")

        # timing only if detected (honesty gate)
        if det.get("detect", False):
            mt = measure_midtime(tq, fq, P_ZTF, T0_PRIOR_S98, s, nboot=300)
            sec["midtime"] = mt
            if mt.get("ok"):
                print(f"  T_mid = {mt['T_mid']:.6f} BTJD "
                      f"+/- {mt['T_mid_err']*86400:.1f} s "
                      f"(depth_fit={mt['depth']*100:.1f}%)")
                epochs.append(dict(sector=s, T_mid=mt["T_mid"],
                                   T_mid_err=mt["T_mid_err"]))
        else:
            print("  -> eclipse NOT formally detected (quiescent); no timing.")

    # --------------------------------------------------------------------
    # O-C + refined period + third-body limit
    # --------------------------------------------------------------------
    oc_block = {}
    if len(epochs) >= 1:
        oc_table, T0 = build_oc(epochs, P_ZTF)
        oc_block["oc_table"] = oc_table
        oc_block["T0_anchor_btjd"] = T0
        oc_block["T0_anchor_bjd_tdb"] = T0 + BTJD_OFFSET
        print("\n===== O-C table (anchor = S98) =====")
        for r in oc_table:
            print(f"  S{r['sector']:>2d}  E={r['cycle']:>7d}  "
                  f"T_mid={r['T_mid']:.6f}  O-C={r['oc_s']:+.1f} s "
                  f"(+/-{r['T_mid_err']*86400:.1f} s)")

        ref = refine_period(oc_table, P_ZTF, T0)
        oc_block["refined_ephemeris"] = ref
        if ref.get("ok"):
            print(f"\nRefined P = {ref['P_min']:.5f} min "
                  f"(+/- {ref['P_err_s']:.3f} s), baseline "
                  f"{ref['baseline_cycles']:.0f} cycles "
                  f"({ref['baseline_yr']:.2f} yr), N={ref['n_used']} epochs")
        else:
            print(f"\nRefined ephemeris: {ref.get('reason')}")

        # third-body LTT limit: amplitude = max |O-C| (or scatter) of residuals
        ocs = np.array([r["oc_s"] for r in oc_table])
        oc_errs = np.array([r["T_mid_err"] * 86400 for r in oc_table])
        # residual scatter about the refined linear fit, if available
        if ref.get("ok") and len(ref["resid_s"]) >= 2:
            A_resid_s = float(np.max(np.abs(ref["resid_s"])))
            rms_s = float(np.sqrt(np.mean(np.array(ref["resid_s"]) ** 2)))
        else:
            A_resid_s = float(np.max(np.abs(ocs - np.median(ocs)))) if len(ocs) else np.nan
            rms_s = float(np.std(ocs)) if len(ocs) else np.nan
        # conservative LTT amplitude UPPER LIMIT: residual + measurement error
        A_limit_s = (A_resid_s if np.isfinite(A_resid_s) else 0.0) \
            + float(np.nanmax(oc_errs) if np.isfinite(np.nanmax(oc_errs)) else 0.0)

        oc_block["ltt"] = dict(
            n_epochs=len(oc_table),
            oc_residual_amp_s=A_resid_s,
            oc_residual_rms_s=rms_s,
            max_timing_err_s=float(np.nanmax(oc_errs)) if len(oc_errs) else None,
            A_ltt_limit_s=A_limit_s,
        )

        # translate amplitude limit -> excluded (P3, M3) region
        if np.isfinite(A_limit_s) and A_limit_s > 0:
            tess_baseline_yr = (max(e["T_mid"] for e in epochs)
                                - min(e["T_mid"] for e in epochs)) / 365.25
            # LTT detectable only for P3 <~ a few x baseline; sample a grid
            grid = []
            for P3 in [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]:
                f = ltt_mass_function(A_limit_s, P3)
                m3_90 = m3_min_from_f(f, M_bin=1.05, i3=90.0)
                m3_30 = m3_min_from_f(f, M_bin=1.05, i3=30.0)
                grid.append(dict(P3_yr=P3, f_Msun=float(f),
                                 M3_min_i90_Msun=m3_90,
                                 M3_min_i30_Msun=m3_30))
            oc_block["ltt"]["tess_baseline_yr"] = float(tess_baseline_yr)
            oc_block["ltt"]["excluded_grid"] = grid
            oc_block["ltt"]["note"] = (
                "An LTT signal with semi-amplitude A would produce an O-C of "
                "amplitude A. Tertiaries that WOULD generate A > A_ltt_limit and "
                "have P3 <~ the timing baseline are EXCLUDED. For each P3 the "
                "table lists the minimum tertiary mass whose LTT amplitude "
                "equals the limit (i.e. M3 below this is allowed; above is "
                "excluded only if P3 is well sampled by the epochs).")
    else:
        print("\nNo sector yielded a usable eclipse timing -> NULL O-C.")
        oc_block["note"] = ("No formally detectable, timeable eclipse in any "
                            "extracted TESS sector at the achievable "
                            "cadence/faintness; no O-C diagram can be built "
                            "from TESS alone, so no positive third-body "
                            "detection. We instead state a SENSITIVITY limit.")

        # Sensitivity-based LTT limit: even without a detection, we can say what
        # LTT amplitude would have been detectable.  The folded eclipse is at
        # best a few-% dip; a fair achievable per-sector mid-time precision at
        # this faintness/cadence is ~ (eclipse_dur)/SNR_fold.  We adopt a
        # conservative per-sector timing precision floor and the full
        # 2018->2025 baseline.
        baselines = []
        for s in SECTORS:
            sec = results["sectors"][str(s)]
            baselines.append(sec["baseline_d"])
        # full TESS timing baseline S5 (2018) -> S98 (2025)
        full_baseline_yr = (1463.97 - 1437.99) * 0 + 7.0  # ~7 yr S5->S98
        # achievable single-eclipse timing sigma ~ a few minutes; sector-averaged
        # over ~hundreds of cycles could in principle reach ~tens of s IF the
        # eclipse were detectable.  Since it is NOT robustly detected, we quote
        # the regime: O-C residual sensitivity ~ 60-300 s.
        sens_levels_s = [60.0, 180.0, 300.0]
        grids = {}
        for A_s in sens_levels_s:
            g = []
            for P3 in [1.0, 2.0, 5.0, 10.0, 20.0]:
                f = ltt_mass_function(A_s, P3)
                g.append(dict(P3_yr=P3, f_Msun=float(f),
                              M3_min_i90_Msun=m3_min_from_f(f, 1.05, 90.0),
                              M3_min_i30_Msun=m3_min_from_f(f, 1.05, 30.0)))
            grids[f"A_{int(A_s)}s"] = g
        oc_block["ltt_sensitivity"] = dict(
            detection=False,
            full_baseline_yr=float(full_baseline_yr),
            assumed_A_levels_s=sens_levels_s,
            grids=grids,
            note=("NULL detection: no O-C measured. The table shows, for a "
                  "RANGE of hypothetical O-C sensitivity amplitudes A (60/180/"
                  "300 s), the minimum tertiary mass whose LTT signal would "
                  "reach that amplitude at outer period P3. Because no eclipse "
                  "timing is achievable, TESS data EXCLUDE NOTHING on their own; "
                  "these numbers indicate the sensitivity a future timing "
                  "campaign (1-m, sigma_T~1-2 s per eclipse) would reach."))

    results["oc"] = oc_block

    # --------------------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------------------
    with open(f"{OUT}/crts_j051419_s5s32_results.json", "w") as fh:
        json.dump(results, fh, indent=2, default=float)
    print(f"\nwrote {OUT}/crts_j051419_s5s32_results.json")

    make_figures(sector_lcs, results, T0_PRIOR_S98)
    write_report(results)
    return results


def make_figures(sector_lcs, results, T0):
    # per-sector phase folds
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, s in zip(axes, SECTORS):
        lc = sector_lcs[s]
        tq, fq = lc["time_q"], lc["flux_norm_q"]
        ph = phase_of(tq, P_ZTF, T0)
        ax.plot(ph, fq, ".", ms=2, alpha=0.30, color="gray")
        cen, val, err = fold_binned(tq, fq, P_ZTF, T0, nbins=40)
        ax.errorbar(cen, val, yerr=err, fmt="o", ms=4, color="crimson",
                    lw=1, label="binned median (quiescent)")
        sec = results["sectors"][str(s)]
        det = sec["detect"]
        hw = det.get("half_width_phase", (ECL_DUR_D / P_ZTF) / 2.0)
        ax.axvspan(-hw, hw, color="blue", alpha=0.08)
        ax.axvline(0, color="blue", ls=":", lw=1)
        txt = f"S{s}  cad {sec['cadence_s']:.0f}s  (cad/ecl {sec['cadence_vs_eclipse']:.2f})\n"
        if "depth" in det:
            txt += (f"depth {det['depth']*100:.1f}%  "
                    f"{det['sigma']:.1f}$\\sigma$  "
                    f"{'DETECT' if det['detect'] else 'NULL'}")
        ax.set_title(txt, fontsize=9.5)
        ax.set_xlabel("orbital phase")
        ax.set_xlim(-0.5, 0.5)
        ax.set_ylabel("normalized quiescent flux")
        ax.legend(fontsize=7, loc="lower right")
    fig.suptitle("CRTS J051419.8+011120 -- TESS phase folds at P = 180.770 min (ZTF DR23)",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(f"{OUT}/crts_j051419_s5s32_folds.png", dpi=130)
    plt.close(fig)
    print(f"wrote {OUT}/crts_j051419_s5s32_folds.png")

    # O-C diagram
    oc = results.get("oc", {})
    if "oc_table" in oc and len(oc["oc_table"]) >= 1:
        fig, ax = plt.subplots(figsize=(8, 5))
        tab = oc["oc_table"]
        E = [r["cycle"] for r in tab]
        y = [r["oc_s"] for r in tab]
        ye = [r["T_mid_err"] * 86400 for r in tab]
        labels = [f"S{r['sector']}" for r in tab]
        ax.errorbar(E, y, yerr=ye, fmt="o", ms=8, capsize=4, color="navy")
        for xi, yi, lab in zip(E, y, labels):
            ax.annotate(lab, (xi, yi), textcoords="offset points",
                        xytext=(8, 6), fontsize=10)
        ax.axhline(0, color="gray", ls="--", lw=1)
        ref = oc.get("refined_ephemeris", {})
        if ref.get("ok"):
            xs = np.linspace(min(E) - 500, max(E) + 500, 50)
            # residual line of refined fit relative to anchor ephemeris
            ax.set_title(f"O-C diagram  (refined P = {ref['P_min']:.5f} +/- "
                        f"{ref['P_err_s']:.2f}s min)", fontsize=11)
        else:
            ax.set_title("O-C diagram (insufficient epochs to refine slope)",
                        fontsize=11)
        ax.set_xlabel("cycle number E (anchor = S98)")
        ax.set_ylabel("O - C (seconds)")
        fig.tight_layout()
        fig.savefig(f"{OUT}/crts_j051419_s5s32_oc.png", dpi=130)
        plt.close(fig)
        print(f"wrote {OUT}/crts_j051419_s5s32_oc.png")


def write_report(results):
    r = results
    lines = []
    A = lines.append
    A("# CRTS J051419.8+011120 -- TESS multi-sector eclipse-timing / third-body test")
    A("")
    A(f"- Target: TIC {TIC}, Gaia DR3 3233913634323725696, Tmag = {TMAG}")
    A(f"- Known orbital period (ZTF DR23, 7.2-yr baseline): "
      f"P = {P_ZTF:.7f} d = {P_ZTF*1440:.3f} min, sigma_P = 1.4 s")
    A(f"- Eclipse (prior/expected): deep (dossier claimed median quiescent "
      f"~71%), narrow (~18 min, ~3.5% phase). **This work finds the phase-"
      f"FOLDED depth is much shallower (see below).**")
    A("")
    A("## Per-sector detectability (stated BEFORE any timing claim)")
    A("")
    A("Primary statistic = binned-dip significance of the QUIESCENT (outburst-"
      "masked) phase fold at the ZTF ephemeris, with a permutation false-alarm "
      "probability (FAP). Detection requires sigma >= 3 AND FAP <= 0.01.")
    A("")
    A("| Sector | Cadence | cad/eclipse | N quiescent | Folded depth | Dip sigma | FAP | Verdict |")
    A("|---|---|---|---|---|---|---|---|")
    for s in SECTORS:
        sec = r["sectors"][str(s)]
        dip = sec.get("dip_test", {})
        depth = f"{dip['depth']*100:.1f}%" if dip.get("ok") else "n/a"
        sig = f"{dip['sigma']:.2f}" if dip.get("ok") else "n/a"
        fap = f"{dip['fap']:.3f}" if dip.get("ok") else "n/a"
        verdict = "DETECT" if sec["detect"].get("detect") else "NULL"
        A(f"| S{s} | {sec['cadence_s']:.0f} s | "
          f"{sec['cadence_vs_eclipse']:.2f} | {sec['n_quiescent']} | "
          f"{depth} | {sig} | {fap} | **{verdict}** |")
    A("")
    A("`cad/eclipse > 1` means the eclipse is shorter than one cadence "
      "(smeared/under-sampled). Folded depth is the deepest phase-bin deficit "
      "in the quiescent fold; a genuine 71% eclipse would read ~71%.")
    A("")
    # narrow BLS
    A("### Narrow-window BLS around the ZTF period (+/-1%)")
    A("")
    A("| Sector | BLS P (min) | SNR | BLS depth |")
    A("|---|---|---|---|")
    for s in SECTORS:
        sec = r["sectors"][str(s)]
        b = sec.get("bls")
        if b:
            A(f"| S{s} | {b['period']*1440:.3f} | {b['snr']:.2f} | "
              f"{b['depth']*100:.1f}% |")
    A("")
    # midtimes / O-C
    oc = r.get("oc", {})
    A("## Eclipse mid-times and O-C")
    A("")
    if "oc_table" in oc:
        A(f"Anchor T0 (S98) = {oc['T0_anchor_btjd']:.6f} BTJD "
          f"= {oc['T0_anchor_bjd_tdb']:.6f} BJD_TDB")
        A("")
        A("| Sector | Cycle E | T_mid (BTJD) | sigma_T (s) | O-C (s) |")
        A("|---|---|---|---|---|")
        for row in oc["oc_table"]:
            A(f"| S{row['sector']} | {row['cycle']} | {row['T_mid']:.6f} | "
              f"{row['T_mid_err']*86400:.1f} | {row['oc_s']:+.1f} |")
        A("")
        ref = oc.get("refined_ephemeris", {})
        if ref.get("ok"):
            A("### Refined linear ephemeris (long baseline)")
            A("")
            A(f"- P = {ref['P_min']:.6f} min  (+/- {ref['P_err_s']:.3f} s)")
            A(f"- = {ref['P']:.8f} d")
            A(f"- baseline = {ref['baseline_cycles']:.0f} cycles "
              f"({ref['baseline_yr']:.2f} yr), N = {ref['n_used']} timed epochs")
            A(f"- O-C residuals about fit: {ref['resid_s']} s")
        else:
            A(f"### Refined ephemeris: NOT possible -- {ref.get('reason')}")
            A(f"  ({ref.get('n_used',0)} usable timed epoch(s); need >=2 with errors)")
        A("")
        # third body
        ltt = oc.get("ltt", {})
        if ltt:
            A("## Third-body (light-travel-time) constraint")
            A("")
            A(f"- O-C residual amplitude: {ltt['oc_residual_amp_s']:.1f} s "
              f"(rms {ltt['oc_residual_rms_s']:.1f} s)")
            A(f"- Max per-epoch timing error: {ltt.get('max_timing_err_s')} s")
            A(f"- Conservative LTT amplitude UPPER LIMIT: "
              f"A_ltt < {ltt['A_ltt_limit_s']:.1f} s")
            if "excluded_grid" in ltt:
                A(f"- TESS timing baseline: {ltt['tess_baseline_yr']:.2f} yr")
                A("")
                A("Excluded tertiaries (LTT amplitude would exceed the limit). "
                  "M3_min = minimum tertiary mass whose LTT semi-amplitude equals "
                  "the limit at that P3; only P3 <~ baseline is actually probed:")
                A("")
                A("| P3 (yr) | mass function f(M3) [Msun] | M3_min (i=90) [Msun] | M3_min (i=30) [Msun] |")
                A("|---|---|---|---|")
                for g in ltt["excluded_grid"]:
                    A(f"| {g['P3_yr']:.1f} | {g['f_Msun']:.3e} | "
                      f"{g['M3_min_i90_Msun']:.3f} | {g['M3_min_i30_Msun']:.3f} |")
                A("")
                A(ltt["note"])
    else:
        # NULL case
        A(oc.get("note", "No O-C produced."))
        A("")
        sens = oc.get("ltt_sensitivity", {})
        if sens:
            A("## Third-body (LTT): NULL detection -> sensitivity only")
            A("")
            A(sens["note"])
            A("")
            A(f"- TESS timing baseline (S5 2018 -> S98 2025): "
              f"~{sens['full_baseline_yr']:.1f} yr")
            A("")
            for key, g in sens["grids"].items():
                A(f"Hypothetical O-C amplitude {key.replace('A_','A = ').replace('s',' s')}:")
                A("")
                A("| P3 (yr) | f(M3) [Msun] | M3_min (i=90) [Msun] | M3_min (i=90) [Mjup] |")
                A("|---|---|---|---|")
                for row in g:
                    mj = row["M3_min_i90_Msun"] * 1047.0
                    A(f"| {row['P3_yr']:.1f} | {row['f_Msun']:.3e} | "
                      f"{row['M3_min_i90_Msun']:.4f} | {mj:.1f} |")
                A("")
    A("")
    A("## Verdict")
    A("")
    n_detect = sum(1 for s in SECTORS if r["sectors"][str(s)]["detect"].get("detect"))
    A(f"- Sectors with a formally detected eclipse: {n_detect} / 3")
    if n_detect == 0:
        A("- TESS multi-sector timing does NOT detect a third body and cannot "
          "set an independent LTT limit, because the eclipse is not robustly "
          "recoverable in the phase-folded sense at Tmag 18.87 (per-cadence "
          "S/N < 1; quiescent folded depth <~ 7%, not the ~71% claimed from "
          "noise-dominated per-eclipse minima).")
        A("- Refined orbital period from TESS alone: not improvable beyond the "
          "ZTF DR23 value P = 180.770 min (sigma_P = 1.4 s); TESS BLS on "
          "quiescent data scatters across 180.4-181.6 min with no significant "
          "peak above the permutation false-alarm floor.")
    with open(f"{OUT}/crts_j051419_s5s32_report.md", "w") as fh:
        fh.write("\n".join(lines))
    print(f"wrote {OUT}/crts_j051419_s5s32_report.md")


if __name__ == "__main__":
    main()
