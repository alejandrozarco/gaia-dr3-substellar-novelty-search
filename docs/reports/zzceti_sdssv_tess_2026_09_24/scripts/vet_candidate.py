# Pixel-level vetting of a TESS periodic signal: python vet_candidate.py <gaia_dr3> <tic> <sector> <freq_c_per_d> [cadence 120|20]
# Downloads the SPOC target pixel file for that sector, re-registers the WCS on the median image with all Gaia DR3 sources
# (G < 19.5) in the stamp (Gaussian PSF), fits a sinusoid at the frequency to every pixel, forms the signed in-phase amplitude
# map (phase from the SPOC aperture sum), and fits it with a single Gaussian PSF at each Gaia source; reports chi2 per source
# (same number of parameters -> delta chi2 is a likelihood ratio). Also prints the sector light-curve amplitude at the frequency.
import sys, os, glob, json, subprocess, numpy as np, requests
from astropy.io import fits
from astropy.wcs import WCS
from scipy.optimize import least_squares
gaia, tic, sec, f0 = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]); cad = sys.argv[5] if len(sys.argv) > 5 else "120"
from astroquery.mast import Observations
obs = Observations.query_criteria(obs_collection="TESS", target_name=tic, sequence_number=sec, dataproduct_type="timeseries")
prods = Observations.get_product_list(obs)
want = "fast-tp" if cad == "20" else "_tp.fits"
tp = [p for p in prods if (want in p["productFilename"]) and ("fast" not in p["productFilename"] or cad == "20")]
if not tp: raise SystemExit("HOLE: no TPF")
fn = tp[0]["productFilename"]; path = f"tpf/{fn}"; os.makedirs("tpf", exist_ok=True)
if not os.path.exists(path):
    subprocess.run(["curl", "-sL", "-m", "900", "--speed-limit", "30000", "--speed-time", "30", "-o", path, f"https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:TESS/product/{fn}"])
th = fits.open(path); T = th[1].data; wcs = WCS(th[2].header); ap = th[2].data
q = (T["QUALITY"] == 0) & np.isfinite(T["TIME"]); t = T["TIME"][q]; FL = T["FLUX"][q]; good = np.all(np.isfinite(FL), axis=(1, 2)); t, FL = t[good], FL[good]
ny, nx = FL.shape[1:]; med = np.median(FL, axis=0); yy, xx = np.mgrid[0:ny, 0:nx]
ra0, de0 = wcs.all_pix2world([[nx / 2 - 0.5, ny / 2 - 0.5]], 0)[0]
qg = f"SELECT source_id, ra, dec, pmra, pmdec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({ra0},{de0},{0.006*max(nx,ny)})) AND phot_g_mean_mag < 19.5"
G = requests.get("https://gea.esac.esa.int/tap-server/tap/sync", params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=qg), timeout=120).json()["data"]
tg = requests.get("https://gea.esac.esa.int/tap-server/tap/sync", params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=f"SELECT source_id, ra, dec, pmra, pmdec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE source_id={gaia}"), timeout=120).json()["data"]
ids = {str(r[0]) for r in G}; G = G + [r for r in tg if str(r[0]) not in ids]
yr = 2016.0 + (2457000 + np.median(t) - 2457389.0) / 365.25; src = []
for sid, ra, de, pmra, pmde, gm in G:
    ra2 = ra + (pmra or 0) * (yr - 2016) / 3.6e6 / np.cos(np.radians(de)); de2 = de + (pmde or 0) * (yr - 2016) / 3.6e6
    px, py = wcs.all_world2pix([[ra2, de2]], 0)[0]
    if -2 < px < nx + 1 and -2 < py < ny + 1: src.append((str(sid), gm, px, py))
def psf(x0, y0, s): return np.exp(-0.5 * ((xx - x0) ** 2 + (yy - y0) ** 2) / s ** 2)
fl0 = np.array([10 ** (-0.4 * (g - 16.0)) for _, g, _, _ in src])
def model(p):
    dx, dy, s, k, bg = p; return k * sum(f * psf(x + dx, y + dy, s) for f, (_, _, x, y) in zip(fl0, src)) + bg
r = least_squares(lambda p: (model(p) - med).ravel(), [0, 0, 1.0, med.max(), 0], bounds=([-3, -3, 0.4, 0, -np.inf], [3, 3, 3, np.inf, np.inf]))
dx, dy, s = r.x[:3]
X = np.vstack([np.ones_like(t), np.sin(2 * np.pi * f0 * t), np.cos(2 * np.pi * f0 * t)]).T; XtXi = np.linalg.inv(X.T @ X)
B = np.zeros((ny, nx, 3)); Sg = np.zeros((ny, nx))
for y in range(ny):
    for x in range(nx):
        v = FL[:, y, x] - np.median(FL[:, y, x]); b = XtXi @ (X.T @ v); B[y, x] = b; Sg[y, x] = np.sqrt(np.sum((v - X @ b) ** 2) / (len(v) - 3))
apm = ap & 2 > 0; phi = np.arctan2(B[..., 2][apm].sum(), B[..., 1][apm].sum())
a = B[..., 1] * np.cos(phi) + B[..., 2] * np.sin(phi); e = Sg * np.sqrt(XtXi[1, 1])
A_ap = np.hypot(B[..., 1][apm].sum(), B[..., 2][apm].sum()); e_ap = np.sqrt(np.sum(e[apm] ** 2))
tsrc = [z for z in src if z[0] == gaia]
if not tsrc: raise SystemExit("target not in stamp")
tg0 = tsrc[0]; m = np.hypot(xx - (tg0[2] + dx), yy - (tg0[3] + dy)) < 4
chi0 = np.sum((a[m] / e[m]) ** 2); out = []
for sid, gm, x, y in src:
    P = psf(x + dx, y + dy, s)[m]
    if P.sum() < 0.3: continue
    A = np.sum(a[m] * P / e[m] ** 2) / np.sum(P ** 2 / e[m] ** 2); eA = 1 / np.sqrt(np.sum(P ** 2 / e[m] ** 2)); chi = np.sum(((a[m] - A * P) / e[m]) ** 2)
    out.append((float(chi), sid, float(gm), float(A), float(eA), float(np.hypot(x - tg0[2], y - tg0[3]) * 21)))
out.sort()
print(f"{gaia} TIC {tic} S{sec} f {f0:.4f} c/d ({86400/f0:.1f} s): aperture amplitude {A_ap:.3f}+-{e_ap:.3f} e/s ({A_ap/e_ap:.1f} sig); WCS offset ({dx:+.2f},{dy:+.2f}) px, PSF sigma {s:.2f}; "
      f"no-signal chi2 {chi0:.1f} over {m.sum()} px")
for chi, sid, gm, A, eA, sep in out[:6]:
    print(f"   {'TARGET ' if sid == gaia else '       '}{sid} G {gm:.2f} sep {sep:5.1f}\": amp {A:.3f}+-{eA:.3f} e/s ({A/eA:.1f} sig) chi2 {chi:.1f}")
best = out[0]; tchi = [o for o in out if o[1] == gaia][0][0]
verdict = "ON_TARGET" if best[1] == gaia and (len(out) < 2 or out[1][0] - best[0] > 4) else ("TARGET_PREFERRED_WEAKLY" if best[1] == gaia else f"OFF_TARGET ({best[1]}, delta chi2 {tchi - best[0]:.1f})")
print("   verdict:", verdict)
json.dump(dict(gaia=gaia, tic=tic, sector=sec, freq=f0, aperture_amp=A_ap, aperture_err=e_ap, chi0=chi0, fits=out, verdict=verdict), open(f"vet_{gaia}_S{sec}.json", "w"), indent=1)
