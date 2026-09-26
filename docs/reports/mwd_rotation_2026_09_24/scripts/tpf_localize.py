# Pixel-level localisation of a TESS periodic signal: per-pixel sinusoid fit at f0 (after a 1.5-d running-median high-pass per pixel),
# signed-amplitude map, and a Gaussian-PRF fit of that map with the source fixed at the Gaia position of the target or of each neighbour.
# Usage: python tpf_localize.py tpf_file target_sid f0 [radius_arcsec_for_neighbours]
import sys, os, json, math, csv, io
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
import requests
from scipy.optimize import least_squares
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.chdir("/tmp/fanout/rotation")
fn, sid, f0 = sys.argv[1], sys.argv[2], float(sys.argv[3])
R = float(sys.argv[4]) if len(sys.argv) > 4 else 90.0
TAP = "https://gea.esac.esa.int/tap-server/tap/sync"

h = fits.open(fn)
d = h[1].data
t = np.array(d["TIME"], float); q = np.array(d["QUALITY"], int); F = np.array(d["FLUX"], float)
ap = h[2].data; wcs = WCS(h[2].header)
ok = np.isfinite(t) & (q == 0) & np.all(np.isfinite(F.reshape(len(t), -1)), axis=1)
t, F = t[ok], F[ok]
ny, nx = F.shape[1:]
sector = h[0].header.get("SECTOR"); obs_year = Time(np.median(t) + 2457000, format="jd").jyear


def hp(tt, y, win=1.5):
    g = np.arange(tt.min(), tt.max() + 0.1, 0.1)
    med = np.array([np.median(y[np.abs(tt - x) < win / 2]) if np.sum(np.abs(tt - x) < win / 2) > 20 else np.nan for x in g])
    okm = np.isfinite(med)
    return y - np.interp(tt, g[okm], med[okm])


X = np.vstack([np.ones_like(t), np.sin(2 * np.pi * f0 * t), np.cos(2 * np.pi * f0 * t)]).T
S = np.zeros((ny, nx)); C = np.zeros((ny, nx)); E = np.zeros((ny, nx)); MED = np.zeros((ny, nx))
for j in range(ny):
    for i in range(nx):
        y = F[:, j, i]; MED[j, i] = np.median(y)
        yh = hp(t, y)
        b, *_ = np.linalg.lstsq(X, yh, rcond=None)
        res = yh - X @ b; sig = 1.4826 * np.median(np.abs(res - np.median(res)))
        S[j, i], C[j, i] = b[1], b[2]; E[j, i] = sig * math.sqrt(2 / len(t))
# signed amplitude: project each pixel's (S,C) onto the phase of the brightest-amplitude pixels
A = np.hypot(S, C)
k = np.argsort(A.ravel())[::-1][:4]
ph0 = math.atan2(np.sum(C.ravel()[k]), np.sum(S.ravel()[k]))
SA = S * math.cos(ph0) + C * math.sin(ph0)          # signed amplitude (e-/s)
snr = SA / E

# Gaia sources in the stamp (propagated to the sector epoch)
ra0, de0 = wcs.pixel_to_world_values((nx - 1) / 2, (ny - 1) / 2)
rad = max(nx, ny) * 21 / 2 * 1.5
qry = (f"SELECT source_id, ra, dec, pmra, pmdec, phot_g_mean_mag, phot_rp_mean_mag FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT(ra,dec), "
       f"CIRCLE({ra0},{de0},{rad/3600})) AND phot_g_mean_mag < 19.5")
rr = requests.post(TAP, data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=qry), timeout=300)
if rr.status_code != 200: print("HOLE Gaia", rr.status_code); sys.exit(2)
G = list(csv.DictReader(io.StringIO(rr.text)))
srcs = []
for g in G:
    dt = obs_year - 2016.0
    ra = float(g["ra"]) + (float(g["pmra"] or 0) * dt / 3.6e6) / math.cos(math.radians(float(g["dec"])))
    de = float(g["dec"]) + float(g["pmdec"] or 0) * dt / 3.6e6
    px, py = wcs.world_to_pixel_values(ra, de)
    if -1 <= px <= nx and -1 <= py <= ny:
        srcs.append(dict(source_id=g["source_id"], G=float(g["phot_g_mean_mag"]), RP=float(g["phot_rp_mean_mag"]) if g["phot_rp_mean_mag"] else None,
                         px=float(px), py=float(py)))
tgt = next(s for s in srcs if s["source_id"] == sid)
for s in srcs:
    s["sep_px"] = math.hypot(s["px"] - tgt["px"], s["py"] - tgt["py"]); s["sep_as"] = s["sep_px"] * 21.0

# PRF-like model: 2D Gaussian (sigma free, common) centred on a fixed source position; amplitude + constant free
yy, xx = np.mgrid[0:ny, 0:nx]
w = 1 / np.maximum(E, 1e-9)


def fit_at(px, py):
    def resid(p):
        amp, sig, c0 = p
        m = amp * np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (2 * sig ** 2)) / (2 * np.pi * sig ** 2) + c0
        return ((SA - m) * w).ravel()
    best = None
    for s0 in (0.6, 0.9, 1.3):
        r = least_squares(resid, [SA.max() * 2 * np.pi * s0 ** 2, s0, 0.0], bounds=([-np.inf, 0.3, -np.inf], [np.inf, 3.0, np.inf]))
        if best is None or r.cost < best.cost: best = r
    return float(2 * best.cost), best.x


# free-position fit (where is the signal?)
def resid_free(p):
    amp, sig, c0, px, py = p
    m = amp * np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (2 * sig ** 2)) / (2 * np.pi * sig ** 2) + c0
    return ((SA - m) * w).ravel()
pos = np.clip(snr, 0, None) ** 2
cx, cy = float(np.sum(pos * xx) / np.sum(pos)), float(np.sum(pos * yy) / np.sum(pos))
rf = None
for sx, sy in ((cx, cy), (tgt["px"], tgt["py"])):
    r_ = least_squares(resid_free, [SA.max() * 2 * np.pi, 0.9, 0.0, sx, sy], bounds=([-np.inf, 0.5, -np.inf, 0, 0], [np.inf, 3.0, np.inf, nx - 1, ny - 1]))
    if rf is None or r_.cost < rf.cost: rf = r_
fx, fy = rf.x[3], rf.x[4]
res = dict(tpf=fn, sector=sector, f0=f0, n_cad=len(t), stamp=[ny, nx], snr_centroid=[cx, cy], free_fit=dict(px=float(fx), py=float(fy), sigma=float(rf.x[1]), chi2=float(2 * rf.cost)),
           target=dict(px=tgt["px"], py=tgt["py"]), sources=[])
for s in sorted(srcs, key=lambda z: z["sep_px"]):
    if s["sep_px"] > R / 21.0 and s["source_id"] != sid: continue
    chi2, p = fit_at(s["px"], s["py"])
    s.update(chi2=chi2, amp=float(p[0]), sigma=float(p[1]), dist_to_free_px=float(math.hypot(s["px"] - fx, s["py"] - fy)))
    res["sources"].append(s)
best = min(res["sources"], key=lambda z: z["chi2"])
res["best_source"] = best["source_id"]
res["dchi2_target_minus_best"] = float(next(s["chi2"] for s in res["sources"] if s["source_id"] == sid) - best["chi2"])
json.dump(res, open(f"cand/tpfloc_{sid}_S{sector}_{f0:.4f}.json", "w"), indent=1)
print(f"{sid} S{sector} f0={f0} ncad={len(t)} stamp={ny}x{nx}; free-position fit: px={fx:.2f} py={fy:.2f} sigma={rf.x[1]:.2f} chi2={2*rf.cost:.1f}; "
      f"target at px={tgt['px']:.2f} py={tgt['py']:.2f} (dist {math.hypot(tgt['px']-fx, tgt['py']-fy):.2f} px); S/N^2-weighted centroid ({cx:.2f},{cy:.2f})")
for s in res["sources"]:
    print(f"   {s['source_id']:>20s} G={s['G']:5.2f} sep={s['sep_as']:5.1f}\" px=({s['px']:.2f},{s['py']:.2f}) dist_to_free={s['dist_to_free_px']:.2f}px "
          f"chi2(fixed here)={s['chi2']:.1f} {'<- TARGET' if s['source_id']==sid else ''}{' <- BEST' if s['source_id']==best['source_id'] else ''}")
print(f"   chi2(target) - chi2(best) = {res['dchi2_target_minus_best']:.1f}; max |pixel S/N| = {np.max(np.abs(snr)):.1f}")
# figure
fig, ax = plt.subplots(1, 3, figsize=(15, 4.8))
im = ax[0].imshow(np.log10(np.maximum(MED, 1)), origin="lower", cmap="gray"); ax[0].set_title(f"median flux (log) S{sector}")
im2 = ax[1].imshow(SA, origin="lower", cmap="RdBu_r", vmin=-np.max(np.abs(SA)), vmax=np.max(np.abs(SA))); ax[1].set_title(f"signed amplitude at {f0:.4f} c/d (e-/s)")
plt.colorbar(im2, ax=ax[1])
im3 = ax[2].imshow(snr, origin="lower", cmap="RdBu_r", vmin=-np.max(np.abs(snr)), vmax=np.max(np.abs(snr))); ax[2].set_title("per-pixel S/N"); plt.colorbar(im3, ax=ax[2])
for a in ax:
    a.contour(ap & 2, levels=[0.5], colors="y", linewidths=1)
    for s in srcs:
        col = "lime" if s["source_id"] == sid else "orange"
        a.plot(s["px"], s["py"], "x" if s["source_id"] == sid else "+", color=col, ms=10 if s["source_id"] == sid else 5 + max(0, 18 - s["G"]))
    a.plot(fx, fy, "o", mfc="none", mec="m", ms=14)
fig.suptitle(f"{sid} TESS S{sector}: x = target (lime), + = Gaia G<19.5 (size ~ brightness), magenta o = free-fit signal position, yellow = SPOC aperture")
fig.tight_layout(); fig.savefig(f"cand/tpfloc_{sid}_S{sector}_{f0:.4f}.png", dpi=85)
