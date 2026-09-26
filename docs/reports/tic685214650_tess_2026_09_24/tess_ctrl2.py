# (1) phases at 787.4655 c/d of the target and the 12 same-CCD S87 controls (SAP flux); an instrumental additive signal would give
# a common phase; (2) SPOC aperture sizes; (3) target stamp: in-phase amplitude in pixels far (> 2.5 px) from all Gaia G < 18.5 stars.
import numpy as np, glob, json
from astropy.io import fits
f0 = 787.4655
def fit(t, y, f):
    X = np.vstack([np.ones_like(t), np.sin(2*np.pi*f*t), np.cos(2*np.pi*f*t)]).T; b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ b; s = np.sqrt(np.sum(r**2)/(len(y)-3)); C = np.linalg.inv(X.T @ X)*s**2
    return np.hypot(b[1], b[2]), np.sqrt((C[1,1]+C[2,2])/2), np.degrees(np.arctan2(b[2], b[1])) % 360
rows = []
for fn in sorted(glob.glob('mastDownload/TESS/*s0087*/*fast-lc.fits') + glob.glob('ctrl/mastDownload/TESS/*/*fast-lc.fits')):
    h = fits.open(fn); d = h[1].data; hd0 = h[0].header; apm = h[2].data
    m = (d['QUALITY'] == 0) & np.isfinite(d['SAP_FLUX']); t = d['TIME'][m]; y = d['SAP_FLUX'][m] - np.median(d['SAP_FLUX'][m])
    A, eA, ph = fit(t, y, f0); npix = int(np.sum((apm & 2) > 0))
    rows.append((hd0['TICID'], hd0['TESSMAG'], npix, A, eA, ph)); print(f"TIC {hd0['TICID']:>10} T {hd0['TESSMAG']:5.1f} aperture {npix:3d} px: A {A:.3f}+-{eA:.3f} e/s ({A/eA:4.1f} sig) phase {ph:5.0f} deg; per-pixel-normalised A/sqrt(npix) {A/np.sqrt(npix):.3f}")
ph = np.radians([r[5] for r in rows[1:] if r[1] > 12]); w = np.array([r[3]/r[4] for r in rows[1:] if r[1] > 12])
R = np.hypot(np.sum(np.cos(ph)), np.sum(np.sin(ph)))/len(ph); print(f"faint controls: mean resultant length of phases {R:.2f} (n {len(ph)}; ~{1/np.sqrt(len(ph)):.2f} expected for random phases); mean direction {np.degrees(np.arctan2(np.sum(np.sin(ph)), np.sum(np.cos(ph))))%360:.0f} deg")
