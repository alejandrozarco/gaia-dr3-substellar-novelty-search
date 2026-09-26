# Which star carries the S87 787.4655 c/d signal? Per pixel, project the sinusoid onto the aperture-signal phase (signed in-phase
# amplitude a_ij with error e_ij). Model a_ij = A_k * PSF_k(ij) for a single source k at the Gaia position of each candidate
# (propagated to the S87 epoch), with a Gaussian PSF whose width is fitted to the median image around the G = 15.99 star.
# Compare chi2 between candidates (same number of free parameters -> delta chi2 is a likelihood ratio).
import numpy as np, glob, json
from astropy.io import fits
from astropy.wcs import WCS
from scipy.optimize import least_squares
f0 = 787.4655; J = json.load(open("tess_check.json"))["87"]; stars = J["pixel"]["stars"]
th = fits.open(glob.glob("mastDownload/TESS/*s0087*/*fast-tp.fits")[0]); T = th[1].data
q = (T["QUALITY"] == 0) & np.isfinite(T["TIME"]); t = T["TIME"][q]; FL = T["FLUX"][q]; good = np.all(np.isfinite(FL), axis=(1, 2)); t, FL = t[good], FL[good]
ny, nx = FL.shape[1:]; X = np.vstack([np.ones_like(t), np.sin(2*np.pi*f0*t), np.cos(2*np.pi*f0*t)]).T
XtX_inv = np.linalg.inv(X.T @ X); B = np.zeros((ny, nx, 3)); Sg = np.zeros((ny, nx))
for y in range(ny):
    for x in range(nx):
        v = FL[:, y, x] - np.median(FL[:, y, x]); b = XtX_inv @ (X.T @ v); r = v - X @ b; B[y, x] = b; Sg[y, x] = np.sqrt(np.sum(r**2)/(len(v)-3))
# reference phase from the SPOC aperture sum
ap = th[2].data & 2 > 0; bs, bc = B[..., 1][ap].sum(), B[..., 2][ap].sum(); phi = np.arctan2(bc, bs)
a = B[..., 1]*np.cos(phi) + B[..., 2]*np.sin(phi); e = Sg*np.sqrt(XtX_inv[1, 1])            # signed in-phase amplitude and error
med = np.median(FL, axis=0); yy, xx = np.mgrid[0:ny, 0:nx]
g16 = [s for s in stars if s[1] < 16.2][0]
def psf(x0, y0, sig): return np.exp(-0.5*((xx-x0)**2+(yy-y0)**2)/sig**2)
# fit PSF width (and position) to the median image near the bright star
r = least_squares(lambda p: ((p[0]*psf(p[1], p[2], p[3]) + p[4]) - med)[np.hypot(xx-g16[3], yy-g16[4]) < 2.5], [med.max(), g16[3], g16[4], 0.8, 0], bounds=([0, 0, 0, 0.3, -np.inf], [np.inf, nx, ny, 3, np.inf]))
sig = r.x[3]; print(f"PSF sigma from the G15.99 star: {sig:.2f} px; fitted centre ({r.x[1]:.2f},{r.x[2]:.2f}) vs Gaia ({g16[3]:.2f},{g16[4]:.2f})")
m = np.hypot(xx-J["pixel"]["stars"][0][3], yy-J["pixel"]["stars"][0][4]) < 4
res = []
for sid, G, sep, px, py in stars[:8]:
    P = psf(px, py, sig)[m]; A = np.sum(a[m]*P/e[m]**2)/np.sum(P**2/e[m]**2); eA = 1/np.sqrt(np.sum(P**2/e[m]**2))
    chi = np.sum(((a[m] - A*P)/e[m])**2); res.append((chi, sid, G, sep, A, eA))
chi0 = np.sum((a[m]/e[m])**2)
for chi, sid, G, sep, A, eA in sorted(res):
    print(f"  source {sid} G {G:.2f} sep {sep:5.1f}\": in-phase peak amplitude {A:.3f}+-{eA:.3f} e/s ({A/eA:.1f} sig); chi2 {chi:.1f} (no-signal chi2 {chi0:.1f}; n pix {m.sum()})")
