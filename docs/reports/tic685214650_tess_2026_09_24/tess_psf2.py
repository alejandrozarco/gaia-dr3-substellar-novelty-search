# Re-register the S87 TPF WCS on the median image with all Gaia DR3 sources (G < 19.5) inside the stamp, then repeat the
# single-source PSF test for the 787.4655 c/d in-phase amplitude map at the corrected positions.
import numpy as np, glob, json, requests
from astropy.io import fits
from astropy.wcs import WCS
from scipy.optimize import least_squares
f0 = 787.4655
th = fits.open(glob.glob("mastDownload/TESS/*s0087*/*fast-tp.fits")[0]); T = th[1].data; wcs = WCS(th[2].header)
q = (T["QUALITY"] == 0) & np.isfinite(T["TIME"]); t = T["TIME"][q]; FL = T["FLUX"][q]; good = np.all(np.isfinite(FL), axis=(1, 2)); t, FL = t[good], FL[good]
ny, nx = FL.shape[1:]; med = np.median(FL, axis=0); yy, xx = np.mgrid[0:ny, 0:nx]
ra0, de0 = wcs.all_pix2world([[nx/2-0.5, ny/2-0.5]], 0)[0]
qg = f"SELECT source_id, ra, dec, pmra, pmdec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({ra0},{de0},0.06)) AND phot_g_mean_mag < 19.5"
G = requests.get("https://gea.esac.esa.int/tap-server/tap/sync", params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=qg), timeout=120).json()["data"]
yr = 2016.0 + (2457000 + np.median(t) - 2457389.0) / 365.25
src = []
for sid, ra, de, pmra, pmde, gm in G:
    ra2 = ra + (pmra or 0) * (yr - 2016) / 3.6e6 / np.cos(np.radians(de)); de2 = de + (pmde or 0) * (yr - 2016) / 3.6e6
    px, py = wcs.all_world2pix([[ra2, de2]], 0)[0]
    if -2 < px < nx + 1 and -2 < py < ny + 1: src.append((str(sid), gm, px, py))
print(len(src), "Gaia sources (G<19.5) on/near the stamp; epoch", round(yr, 3))
def psf(x0, y0, s): return np.exp(-0.5 * ((xx - x0) ** 2 + (yy - y0) ** 2) / s ** 2)
flux0 = np.array([10 ** (-0.4 * (g - 16.0)) for _, g, _, _ in src])
def model(p):
    dx, dy, s, k, bg = p; return k * sum(f * psf(x + dx, y + dy, s) for f, (_, _, x, y) in zip(flux0, src)) + bg
r = least_squares(lambda p: (model(p) - med).ravel(), [0, 0, 1.0, med.max(), 0], bounds=([-3, -3, 0.4, 0, -np.inf], [3, 3, 3, np.inf, np.inf]))
dx, dy, s, k, bg = r.x; print(f"WCS offset fitted on the median image: dx {dx:+.2f} px, dy {dy:+.2f} px, PSF sigma {s:.2f} px; residual rms {np.std(model(r.x)-med):.1f} e/s (median image peak {med.max():.1f})")
X = np.vstack([np.ones_like(t), np.sin(2*np.pi*f0*t), np.cos(2*np.pi*f0*t)]).T; XtXi = np.linalg.inv(X.T @ X)
B = np.zeros((ny, nx, 3)); Sg = np.zeros((ny, nx))
for y in range(ny):
    for x in range(nx):
        v = FL[:, y, x] - np.median(FL[:, y, x]); b = XtXi @ (X.T @ v); B[y, x] = b; Sg[y, x] = np.sqrt(np.sum((v - X @ b) ** 2) / (len(v) - 3))
ap = th[2].data & 2 > 0; phi = np.arctan2(B[..., 2][ap].sum(), B[..., 1][ap].sum())
a = B[..., 1] * np.cos(phi) + B[..., 2] * np.sin(phi); e = Sg * np.sqrt(XtXi[1, 1])
tg = [z for z in src if z[0] == "4771958598593101184"][0]; m = np.hypot(xx - (tg[2] + dx), yy - (tg[3] + dy)) < 4
chi0 = np.sum((a[m] / e[m]) ** 2); out = []
for sid, gm, x, y in src:
    P = psf(x + dx, y + dy, s)[m]
    if P.sum() < 0.5: continue
    A = np.sum(a[m] * P / e[m] ** 2) / np.sum(P ** 2 / e[m] ** 2); eA = 1 / np.sqrt(np.sum(P ** 2 / e[m] ** 2)); chi = np.sum(((a[m] - A * P) / e[m]) ** 2)
    out.append((chi, sid, gm, A, eA, x + dx, y + dy))
print(f"no-signal chi2 {chi0:.1f} over {m.sum()} pixels; single-source fits (best first):")
for chi, sid, gm, A, eA, x, y in sorted(out)[:8]:
    print(f"  {sid} G {gm:.2f} at ({x:.2f},{y:.2f}): amp {A:.3f}+-{eA:.3f} e/s ({A/eA:.1f} sig), chi2 {chi:.1f}")
json.dump(dict(offset=[dx, dy], sigma=s, fits=[list(o) for o in sorted(out)]), open("tess_psf2.json", "w"), indent=1, default=float)
