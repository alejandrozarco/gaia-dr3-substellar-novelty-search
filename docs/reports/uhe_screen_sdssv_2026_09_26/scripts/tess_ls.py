"""TESScut 11x11, 3x3 aperture, background from pixels outside 5x5, 1-d running median removed, 5-sigma clip; LS 0.05-30 c/d per sector and joint."""
import sys, numpy as np, warnings; warnings.filterwarnings("ignore")
from astroquery.mast import Tesscut
from astropy.coordinates import SkyCoord
from astropy.timeseries import LombScargle
from astropy.wcs import WCS
from scipy.ndimage import median_filter
ra, dec = float(sys.argv[1]), float(sys.argv[2]); c = SkyCoord(ra, dec, unit="deg")
secs = Tesscut.get_sectors(coordinates=c); print("sectors:", list(secs["sector"]))
T, Y = [], []
for sec in list(secs["sector"])[: int(sys.argv[3]) if len(sys.argv) > 3 else 99]:
    try:
        h = Tesscut.get_cutouts(coordinates=c, size=11, sector=int(sec))[0]
    except Exception as e:
        print(sec, "fail", str(e)[:60]); continue
    d = h[1].data; x, y = WCS(h[2].header).world_to_pixel(c); xi, yi = int(round(float(x))), int(round(float(y)))
    q = d["QUALITY"] == 0; fl = d["FLUX"][q]; t = d["TIME"][q]
    yy, xx = np.mgrid[0:fl.shape[1], 0:fl.shape[2]]; bg = np.nanmedian(fl[:, (np.abs(xx - xi) > 2) | (np.abs(yy - yi) > 2)], axis=1)
    ap = (np.abs(xx - xi) <= 1) & (np.abs(yy - yi) <= 1); lc = np.nansum(fl[:, ap], axis=1) - bg * ap.sum(); ok = np.isfinite(lc) & np.isfinite(t)
    t, lc = t[ok], lc[ok]; o = np.argsort(t); t, lc = t[o], lc[o]; r = lc / np.median(lc) - 1
    r = r - median_filter(r, size=int(1 / np.median(np.diff(t))) | 1, mode="nearest"); s = 1.4826 * np.median(np.abs(r)); m = np.abs(r) < 5 * s; t, r = t[m], r[m]
    fr = np.arange(0.05, 30, 0.001); p = LombScargle(t, r).power(fr); k = np.argsort(p)[::-1][:3]
    print(f"S{sec}: n={len(t)} top {[round(fr[i], 3) for i in k]} rms {100*np.std(r):.2f}%"); T += list(t); Y += list(r)
if T:
    T, Y = np.array(T), np.array(Y); fr = np.arange(0.05, 30, 0.0001); ls = LombScargle(T, Y); p = ls.power(fr); k = np.argsort(p)[::-1]; pk = []
    for i in k:
        if all(abs(fr[i] - q) > 0.01 for q in pk): pk.append(fr[i])
        if len(pk) == 5: break
    print("joint top peaks:", [round(x, 4) for x in pk], "FAP", f"{ls.false_alarm_probability(p.max(), minimum_frequency=0.05, maximum_frequency=30):.2g}")
    for f0 in (2.023, 1.023, 1.9826):
        X = np.vstack([np.ones_like(T), np.cos(2 * np.pi * f0 * T), np.sin(2 * np.pi * f0 * T)]).T; cc = np.linalg.lstsq(X, Y, rcond=None)[0]
        print(f"   amplitude at {f0}: {100*np.hypot(cc[1], cc[2]):.3f}% (aperture fraction), power {ls.power(f0):.4f}")
