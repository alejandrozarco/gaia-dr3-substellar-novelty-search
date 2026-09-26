# PG 1658+441 (TIC 115613388): per-sector amplitude/phase at a common frequency near 34.0935 c/d (120-s PDCSAP; 20-s where available),
# refined frequency from the combined 120-s data, and a coherence check (phases of each sector at the refined frequency).
import glob, numpy as np
from astropy.io import fits
from astropy.timeseries import LombScargle
T, Y, E, S = [], [], [], []
for p in sorted(glob.glob("lc/*0000000115613388*s_lc.fits")):
    h = fits.open(p); d = h[1].data; m = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]); t = d["TIME"][m]; y = d["PDCSAP_FLUX"][m] / np.nanmedian(d["PDCSAP_FLUX"][m]) - 1
    e = d["PDCSAP_FLUX_ERR"][m] / np.nanmedian(d["PDCSAP_FLUX"][m]); mad = 1.4826 * np.median(np.abs(y - np.median(y))); ok = np.abs(y - np.median(y)) < 5 * mad
    T.append(t[ok]); Y.append(y[ok]); E.append(e[ok]); S.append(h[0].header["SECTOR"])
t = np.concatenate(T); y = np.concatenate(Y); e = np.concatenate(E); s = np.concatenate([[k] * len(a) for k, a in zip(S, T)])
fr = np.arange(34.0, 34.2, 0.02 / (t.max() - t.min())); P = LombScargle(t, y, e).power(fr); f0 = fr[np.argmax(P)]
fg = np.arange(f0 - 3e-5, f0 + 3e-5, 1e-7)
def fit(tt, yy, ee, f):
    X = np.vstack([np.ones_like(tt), np.sin(2*np.pi*f*(tt-3000)), np.cos(2*np.pi*f*(tt-3000))]).T; W = 1/ee**2
    p = np.linalg.solve(X.T @ (X*W[:, None]), X.T @ (W*yy)); C = np.linalg.inv(X.T @ (X*W[:, None])); c2 = max(np.sum(W*(yy-X@p)**2)/(len(tt)-3), 1)
    return np.hypot(p[1], p[2]), np.sqrt(c2*(C[1,1]+C[2,2])/2), np.degrees(np.arctan2(p[2], p[1])) % 360, np.sum(W*(yy-X@p)**2)
chi = [fit(t, y, e, f)[3] for f in fg]; fb = fg[np.argmin(chi)]
print(f"combined 120-s: peak near {f0:.5f}, refined {fb:.7f} c/d (P = {1440/fb:.4f} min); sectors {S}")
for k, tt, yy, ee in zip(S, T, Y, E):
    a, ea, ph, _ = fit(tt, yy, ee, fb)
    fr2 = np.arange(33.5, 34.7, 0.001); amp = np.sqrt(4 * LombScargle(tt, yy, normalization="psd").power(fr2) / len(tt)); j = np.argmax(amp)
    print(f"  S{k}: amp at fb {100*a:.3f} +- {100*ea:.3f} %, phase {ph:.0f} deg; local peak 33.5-34.7: {fr2[j]:.4f} c/d amp {100*amp[j]:.3f} % (mean {100*amp.mean():.3f} %)")
a, ea, ph, _ = fit(t, y, e, fb); print(f"all: amp {100*a:.3f} +- {100*ea:.3f} %")
