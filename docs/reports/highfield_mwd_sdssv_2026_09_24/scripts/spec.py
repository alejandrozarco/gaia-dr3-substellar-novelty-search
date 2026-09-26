# Spectrum utilities for the high-field MWD lane: load SDSS-V Astra 0.8.1 mwmStar / mwmVisit, undo the per-visit XCSAO
# "rest-frame" shift (lambda_obs = lambda_grid * (1 + v/c)), robust continuum, feature metrics, trumpet-diagram plots.
import numpy as np, os
from astropy.io import fits
from scipy.interpolate import LSQUnivariateSpline
from scipy.ndimage import gaussian_filter1d
C_KMS = 299792.458
HERE = os.path.dirname(os.path.abspath(__file__))

def load_star(sid):
    h = fits.open(os.path.join(HERE, f"spec/mwmStar-0.8.1-{sid}.fits")); best = None
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        d = h[i].data[0]
        rec = dict(lam=np.array(d["wavelength"], float), flux=np.array(d["flux"], float), ivar=np.array(d["ivar"], float),
                   snr=float(d["snr"]), tel=h[i].header.get("EXTNAME"), nmf=np.array(d["nmf_rectified_model_flux"], float),
                   cont=np.array(d["continuum"], float), nmf_rchi2=float(d["nmf_rchi2"]), n_visits=int(d["n_visits"]))
        if best is None or rec["snr"] > best["snr"]: best = rec
    return best

def load_visits(sid):
    h = fits.open(os.path.join(HERE, f"spec/mwmVisit-0.8.1-{sid}.fits")); out = []
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        hd = h[i].header; lam_rest = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"]))
        for r in h[i].data:
            v = float(r["xcsao_v_rad"])
            vv = v if np.isfinite(v) and abs(v) < 1e5 else 0.0
            out.append(dict(mjd=int(r["mjd"]), v=v, snr=float(r["snr"]), in_stack=bool(r["in_stack"]), tel=hd.get("EXTNAME"),
                            lam_grid=lam_rest, lam=lam_rest * (1 + vv / C_KMS), flux=np.array(r["flux"], float), ivar=np.array(r["ivar"], float)))
    return out

def continuum(lam, flux, ivar, spacing=500.0, lo=3650.0, hi=9800.0, niter=8):
    """Robust upper-biased smoothing spline. Narrow spikes (sky residuals, cosmic rays, emission) are removed first with a
    25-pixel running median; knots every `spacing` A; pixels well below the fit (absorption) are down-weighted and pixels
    far above it (residual spikes) are rejected, so broad features up to ~spacing/2 wide are not absorbed into the continuum
    and emission spikes cannot inflate it (v2, 2026-09-24: v1 let spikes pull the spline up and faked broad troughs)."""
    from scipy.ndimage import median_filter
    m = (lam > lo) & (lam < hi) & (ivar > 0) & np.isfinite(flux)
    x = lam[m]; y = median_filter(flux[m], size=25, mode="nearest")
    w = np.ones_like(x)
    t = np.arange(x[0] + spacing / 2, x[-1] - spacing / 2, spacing)
    for k in range(niter):
        sp = LSQUnivariateSpline(x, y, t, w=w, k=3)
        r = y - sp(x); sig = 1.4826 * np.median(np.abs(r - np.median(r)))
        w = np.where(r < -1.0 * sig, 0.05, np.where(r > 3.0 * sig, 0.0, 1.0))
    c = np.full_like(lam, np.nan); c[m] = sp(x)
    return c

MASK = ((5570, 5590), (6290, 6310), (6355, 6375), (6860, 6960), (7580, 7700), (8280, 8320))   # sky lines, telluric B/A bands

def metrics(lam, flux, ivar, lo=3800.0, hi=8800.0, smooth_A=12.0):
    """Excess rms of the continuum-normalised spectrum (after subtracting the noise contribution) and a list of dips."""
    c = continuum(lam, flux, ivar)
    ok = (ivar > 0) & np.isfinite(c) & (c > 0)
    from scipy.ndimage import median_filter
    fm = median_filter(np.where(ok, flux, 0.0), size=7, mode='nearest')
    r = np.where(ok, fm / c - 1, 0.0); e = np.where(ok, 1 / np.sqrt(np.where(ivar > 0, ivar, 1)) / np.where(c > 0, c, 1), 0)
    dlam = np.median(np.diff(lam[(lam > 5000) & (lam < 6000)]))
    sp = smooth_A / dlam
    rs = gaussian_filter1d(r, sp); es = e / np.sqrt(2 * np.sqrt(np.pi) * sp)     # noise of Gaussian-smoothed white noise
    w = (lam > lo) & (lam < hi) & ok
    for a, b in MASK: w &= ~((lam > a) & (lam < b))
    rms = np.sqrt(np.mean(rs[w] ** 2)); nse = np.sqrt(np.mean(es[w] ** 2))
    excess = np.sqrt(max(rms ** 2 - nse ** 2, 0))
    # dips: local minima of the smoothed residual deeper than 5 sigma (smoothed noise) and 3 %
    dips = []
    wide = (lam > 3700) & (lam < 9000) & ok
    for a, b in MASK: wide &= ~((lam > a) & (lam < b))
    idx = np.where(wide)[0]
    for i in idx[1:-1]:
        if rs[i] < rs[i - 1] and rs[i] <= rs[i + 1] and rs[i] < -0.03 and rs[i] < -5 * es[i]:
            dips.append((float(lam[i]), float(rs[i]), float(rs[i] / es[i])))
    # merge dips closer than 15 A (keep deepest)
    merged = []
    for dd in dips:
        if merged and dd[0] - merged[-1][0] < 15:
            if dd[1] < merged[-1][1]: merged[-1] = dd
        else: merged.append(dd)
    return dict(excess=excess, rms=rms, noise=nse, dips=merged, cont=c, resid=rs)
