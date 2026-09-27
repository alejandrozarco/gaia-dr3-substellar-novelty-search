"""TESS full-frame-image check of Gaia periods of 5-32 h. TESScut 11x11; 3x3 aperture on the target pixel minus the median of pixels outside
the central 5x5 (the 10th percentile when the median leaves a non-positive aperture flux); the same pixels give a background light curve. Per orbit (gaps > 0.5 d) a quadratic is removed; points > 5 sigma clipped.
Lomb-Scargle 0.2-5 c/d per sector and for all sectors combined; power and semi-amplitude (fraction of aperture flux) at the Gaia frequency.
Usage: python tess_check.py <gaia_dr3> <ra> <dec> <gaia_freq_cd> [max_sectors]"""
import sys, os, numpy as np, warnings; warnings.filterwarnings("ignore")
from astropy.io import fits; from astropy.wcs import WCS; from astropy.coordinates import SkyCoord; from astropy.timeseries import LombScargle
from astroquery.mast import Tesscut
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
gid, ra, dec, fg = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]); nmax = int(sys.argv[5]) if len(sys.argv) > 5 else 8
C = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache"); os.makedirs(C, exist_ok=True); c = SkyCoord(ra, dec, unit="deg")
secs = [int(s) for s in Tesscut.get_sectors(coordinates=c)["sector"]][:nmax]; FR = np.linspace(0.2, 5, 60000); out = []; T, Y, B = [], [], []
def clean(t, y):
    o = np.zeros_like(y) * np.nan; br = np.r_[0, np.where(np.diff(t) > 0.5)[0] + 1, len(t)]
    for a, b in zip(br[:-1], br[1:]):
        if b - a > 50: p = np.polyfit(t[a:b] - t[a], y[a:b], 2); o[a:b] = y[a:b] - np.polyval(p, t[a:b] - t[a])
    ok = np.isfinite(o); s = 1.4826 * np.nanmedian(np.abs(o[ok] - np.nanmedian(o[ok]))); return ok & (np.abs(o) < 5 * s), o
for sec in secs:
    p = os.path.join(C, f"tesscut_{gid}_s{sec}.fits")
    try:
        if not os.path.exists(p): Tesscut.get_cutouts(coordinates=c, size=11, sector=sec)[0].writeto(p, overwrite=True)
    except Exception as ex: print("sector", sec, "ERR", ex); continue
    h = fits.open(p); d = h[1].data; x, y = WCS(h[2].header).world_to_pixel(c); xi, yi = int(round(float(x))), int(round(float(y)))
    q = (d["QUALITY"] == 0) & np.isfinite(d["TIME"]); fl = d["FLUX"][q]; t = d["TIME"][q] + 2457000.0
    yy, xx = np.mgrid[0:fl.shape[1], 0:fl.shape[2]]; ap = (np.abs(xx - xi) <= 1) & (np.abs(yy - yi) <= 1); ring = (np.abs(xx - xi) > 2) | (np.abs(yy - yi) > 2)
    bk = np.nanmedian(fl[:, ring], axis=1); lc = np.nansum(fl[:, ap], axis=1) - bk * ap.sum(); med = np.nanmedian(lc)
    if not np.isfinite(med) or med <= 0: bk = np.nanpercentile(fl[:, ring], 10, axis=1); lc = np.nansum(fl[:, ap], axis=1) - bk * ap.sum(); med = np.nanmedian(lc)
    if not np.isfinite(med) or med <= 0: print("sector", sec, "non-positive aperture flux"); continue
    ok1, yv = clean(t, lc / med - 1); ok2, bv = clean(t, bk * ap.sum() / med); ok = ok1 & ok2 & np.isfinite(yv) & np.isfinite(bv)
    t, yv, bv = t[ok], yv[ok], bv[ok]
    if len(t) < 200: continue
    ls = LombScargle(t, yv); pw = ls.power(FR); k = np.argmax(pw); pb = LombScargle(t, bv).power(FR); w = np.abs(FR - fg) < 0.03
    A = np.hypot(*np.linalg.lstsq(np.vstack([np.sin(2 * np.pi * fg * t), np.cos(2 * np.pi * fg * t), np.ones_like(t)]).T, yv, rcond=None)[0][:2])
    r = dict(sector=sec, n=len(t), f_peak=round(FR[k], 4), P_peak_h=round(24 / FR[k], 3), fap_peak=float(f"{ls.false_alarm_probability(pw[k], minimum_frequency=0.2, maximum_frequency=5):.2g}"),
             pow_at_gaia=round(pw[w].max(), 4), f_at_gaia=round(FR[w][np.argmax(pw[w])], 4), bkg_pow_at_gaia=round(pb[w].max(), 4), amp_at_gaia_pct=round(100 * A, 3), med_flux=round(med, 1))
    out.append(r); print(r, flush=True); T.append(t); Y.append(yv); B.append(bv)
if T:
    t, y, b = map(np.concatenate, (T, Y, B)); ls = LombScargle(t, y); pw = ls.power(FR); k = np.argmax(pw); pb = LombScargle(t, b).power(FR)
    fa = FR[np.argmax(pw * (np.abs(FR - fg) < 0.03))]
    print("ALL", dict(n=len(t), f_peak=round(FR[k], 5), P_peak_h=round(24 / FR[k], 4), fap_peak=float(f"{ls.false_alarm_probability(pw[k], minimum_frequency=0.2, maximum_frequency=5):.2g}"),
                      f_near_gaia=round(fa, 5), pow_near_gaia=round(pw[np.argmax(pw * (np.abs(FR - fg) < 0.03))], 4), bkg_peak_f=round(FR[np.argmax(pb)], 4)))
    fig, ax = plt.subplots(1, 2, figsize=(12, 3.5)); ax[0].plot(FR, pw, "k", lw=.6, label="target"); ax[0].plot(FR, -pb, "r", lw=.6, label="background (negated)")
    ax[0].axvline(fg, color="b", ls=":", lw=1); ax[0].set_xlabel("frequency (c/d)"); ax[0].legend(fontsize=7)
    ph = (t * fa) % 1; bn = np.linspace(0, 1, 26); mb = [np.median(y[(ph >= a) & (ph < b2)]) for a, b2 in zip(bn[:-1], bn[1:])]
    ax[1].plot(ph, y, ",", color="0.7"); ax[1].plot((bn[:-1] + bn[1:]) / 2, mb, "ko"); ax[1].set_ylim(np.percentile(y, 1), np.percentile(y, 99)); ax[1].set_xlabel(f"phase (f = {fa:.5f} c/d)")
    fig.suptitle(f"Gaia DR3 {gid}, TESS FFI sectors {','.join(str(r['sector']) for r in out)}", fontsize=9); plt.tight_layout(); plt.savefig(f"tess_{gid}.png", dpi=90)
