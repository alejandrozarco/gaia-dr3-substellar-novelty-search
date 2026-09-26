"""TESS FFI (TESScut 11x11) photometry of SDSS J1022+1611 in sectors 45, 46, 72: aperture = central 2x2 brightest pixels around
the target pixel, background = median of pixels outside a 5x5 box per cadence; quality == 0; 5-sigma clip; LS 5-30 c/d; amplitude
at f_ZTF (16.488694 c/d) in units of the aperture flux (diluted by neighbours; the target is G 17.8)."""
import numpy as np, glob
from astroquery.mast import Tesscut
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.timeseries import LombScargle
from astropy.wcs import WCS
c = SkyCoord(155.7148994, 16.1977169, unit="deg"); f0 = 16.488694
for sec in (45, 46, 72):
    try: h = Tesscut.get_cutouts(coordinates=c, size=11, sector=sec)[0]
    except Exception as ex: print(sec, "HOLE", ex); continue
    d = h[1].data; w = WCS(h[2].header); x, y = w.world_to_pixel(c); xi, yi = int(round(float(x))), int(round(float(y)))
    q = d["QUALITY"] == 0; fl = d["FLUX"][q]; t = d["TIME"][q]
    yy, xx = np.mgrid[0:11, 0:11]; bgm = (np.abs(xx - xi) > 2) | (np.abs(yy - yi) > 2)
    bg = np.nanmedian(fl[:, bgm], axis=1)
    ap = (np.abs(xx - xi) <= 1) & (np.abs(yy - yi) <= 1)
    lc = np.nansum(fl[:, ap], axis=1) - bg * ap.sum(); ok = np.isfinite(lc) & np.isfinite(t)
    t, lc = t[ok], lc[ok]; med = np.median(lc); y = lc / med - 1
    # detrend with 1-day running median
    o = np.argsort(t); t, y = t[o], y[o]; from scipy.ndimage import median_filter
    cad = np.median(np.diff(t)); y = y - median_filter(y, size=int(1 / cad) | 1, mode="nearest")
    s = 1.4826 * np.median(np.abs(y)); m = np.abs(y) < 5 * s; t, y = t[m], y[m]
    fr = np.arange(5, 30, 0.001); ls = LombScargle(t, y); P = ls.power(fr); k = np.argmax(P)
    X = np.vstack([np.ones_like(t), np.cos(2*np.pi*f0*t), np.sin(2*np.pi*f0*t)]).T; p, *_ = np.linalg.lstsq(X, y, rcond=None)
    amp = np.hypot(p[1], p[2]); err = np.std(y - X @ p) * np.sqrt(2 / len(t))
    near = np.abs(fr - f0) < 0.01; rank = int(np.sum(P > P[near].max()))
    print(f"S{sec}: n {len(t)}, cadence {cad*1440:.1f} min, aperture median {med:.1f} e/s, top {fr[k]:.4f} c/d (FAP {ls.false_alarm_probability(P[k], minimum_frequency=5, maximum_frequency=30):.1e}); "
          f"at f_ZTF: semi-amp {100*amp:.2f} +- {100*err:.2f}% of aperture flux, power rank {rank}")
