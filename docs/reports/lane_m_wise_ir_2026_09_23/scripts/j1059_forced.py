# VarWISE J105943.85-274050.1 = Gaia DR3 5456743064671253632 ("J1059"): forced W1 photometry in every NEOWISE-R L1b frame
# (IRSA IBE cutouts, 200"), requested 2026-09-23 to test the "photospheric floor" (external review): with a constant M-dwarf
# photosphere W1_phot ~15.31 (VHS Ks 15.52 + Ks-W1 0.21), no minimum can be fainter than the photosphere.
# Method: per frame, fixed-position fit of two Gaussian PSFs (J1059 at its PM-propagated Gaia position; the faint REGALADE/PS1
# galaxy 3.9" to the NW) + constant background in a 9x9-pixel box; PSF sigma from the G=15.4 Gaia neighbour (per-frame fit, median
# adopted). Flux scale: MAGZP per frame, offset calibrated on the neighbour's AllWISE W1. Phases at P = 0.12097159 d (BJD_TDB).
import glob, json, numpy as np, warnings
warnings.filterwarnings("ignore")
from astropy.io import fits, ascii
from astropy.wcs import WCS
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from scipy.optimize import least_squares
from astroquery.vizier import Vizier
RA16, DE16, PMRA, PMDE = 164.93280120834928, -27.680560897461646, -49.95604041580538, -12.373514177220297
GAL = (164.93187, -27.679852)            # REGALADE 'GSC J105943.65' (PS1 source 3.96" away); static
P = 0.12097159
D = "/tmp/wise_loc/s5456743064671253632"
c0 = SkyCoord(RA16 * u.deg, DE16 * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd):
    t = Time(mjd, format="mjd", scale="utc", location=geo); return (t.tdb + t.light_travel_time(c0)).jd
# calibration star: the G=15.4 Gaia neighbour ~22" away; its AllWISE W1
v = Vizier(columns=["**"], row_limit=20); v.TIMEOUT = 300
gs = v.query_region(c0, radius=40 * u.arcsec, catalog="I/355/gaiadr3")[0]
cand = [r for r in gs if r["Gmag"] < 16.5 and SkyCoord(r["RA_ICRS"] * u.deg, r["DE_ICRS"] * u.deg).separation(c0).arcsec > 10]
cs = cand[0]; CRA, CDE = float(cs["RA_ICRS"]), float(cs["DE_ICRS"]); CPM = (float(cs["pmRA"] or 0), float(cs["pmDE"] or 0))
aw = v.query_region(SkyCoord(CRA * u.deg, CDE * u.deg), radius=3 * u.arcsec, catalog="II/328/allwise")[0][0]
W1CAL = float(aw["W1mag"]); print(f"calibration star Gaia G={float(cs['Gmag']):.2f} at {SkyCoord(CRA*u.deg, CDE*u.deg).separation(c0).arcsec:.1f}\"; AllWISE W1 {W1CAL:.3f}", flush=True)
tab = ascii.read(f"{D}/frames_neo.tbl", format="ipac")
tab = tab[(np.array(tab["qual_frame"]) > 0) & (np.array(tab["saa_sep"]) > 0)]
def pos(ra, de, pm, mjd):
    yr = 2000.0 + (mjd - 51544.5) / 365.25 - 2016.0
    return ra + pm[0] * yr / 3.6e6 / np.cos(np.radians(de)), de + pm[1] * yr / 3.6e6
def gauss(X, Y, x0, y0, s): return np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) / (2 * s ** 2))
rows = []
for r in tab:
    fn = f"{D}/cut/{r['scan_id']}{int(r['frame_num']):03d}.fits"
    try:
        h = fits.open(fn); data = h[0].data.astype(float); hd = h[0].header; wc = WCS(hd)
    except Exception:
        continue
    mjd = float(r["mjd_obs"]); zp = float(hd.get("MAGZP", r["magzp"]))
    tx, ty = wc.all_world2pix(*pos(RA16, DE16, (PMRA, PMDE), mjd), 0)
    gx, gy = wc.all_world2pix(GAL[0], GAL[1], 0)
    sx, sy = wc.all_world2pix(*pos(CRA, CDE, CPM, mjd), 0)
    ny, nx = data.shape
    if not (5 < tx < nx - 6 and 5 < ty < ny - 6 and 5 < sx < nx - 6 and 5 < sy < ny - 6): continue
    good = np.isfinite(data); med = np.nanmedian(data[good]); mad = 1.4826 * np.nanmedian(np.abs(data[good] - med))
    Y, X = np.mgrid[0:ny, 0:nx]
    # calibration star: free position (+-1 px), sigma, amplitude, background in a 9x9 box
    bx = (np.abs(X - round(float(sx))) <= 4) & (np.abs(Y - round(float(sy))) <= 4) & good
    def fs(p): return (p[0] * gauss(X[bx], Y[bx], p[1], p[2], p[3]) + p[4] - data[bx])
    rs = least_squares(fs, [data[bx].max() - med, float(sx), float(sy), 0.95, med], bounds=([0, sx - 1, sy - 1, 0.5, -np.inf], [np.inf, sx + 1, sy + 1, 2.0, np.inf]))
    rows.append(dict(mjd=mjd, zp=zp, tx=float(tx), ty=float(ty), gx=float(gx), gy=float(gy), sx=float(sx), sy=float(sy), sig_star=float(rs.x[3]), noise=float(mad),
                     scan=str(r["scan_id"]), frame=int(r["frame_num"]), fn=fn))
sig = float(np.median([q["sig_star"] for q in rows])); print(f"frames {len(rows)}; adopted PSF sigma {sig:.3f} px (median of per-frame fits)", flush=True)
out = []
for q in rows:
    data = fits.getdata(q["fn"]).astype(float); ny, nx = data.shape; Y, X = np.mgrid[0:ny, 0:nx]; good = np.isfinite(data)
    def forced(x0, y0, extra=None):
        bx = (np.abs(X - round(x0)) <= 4) & (np.abs(Y - round(y0)) <= 4) & good
        cols = [np.ones(bx.sum()), gauss(X[bx], Y[bx], x0, y0, sig)]
        if extra is not None: cols.append(gauss(X[bx], Y[bx], extra[0], extra[1], sig))
        A = np.vstack(cols).T; b, *_ = np.linalg.lstsq(A, data[bx], rcond=None)
        res = data[bx] - A @ b; s2 = res @ res / max(bx.sum() - A.shape[1], 1); C = np.linalg.inv(A.T @ A) * s2
        return b[1] * 2 * np.pi * sig ** 2, np.sqrt(C[1, 1]) * 2 * np.pi * sig ** 2
    ft, eft = forced(q["tx"], q["ty"], (q["gx"], q["gy"]))
    f1, ef1 = forced(q["tx"], q["ty"])                       # J1059 alone (galaxy light included)
    # galaxy amplitude from the 2-source fit, stored for a global constant
    bx = (np.abs(X - round(q["tx"])) <= 4) & (np.abs(Y - round(q["ty"])) <= 4) & good
    A = np.vstack([np.ones(bx.sum()), gauss(X[bx], Y[bx], q["tx"], q["ty"], sig), gauss(X[bx], Y[bx], q["gx"], q["gy"], sig)]).T
    bb, *_ = np.linalg.lstsq(A, data[bx], rcond=None)
    fs_, efs = forced(q["sx"], q["sy"])
    out.append(dict(mjd=q["mjd"], zp=q["zp"], f_t=float(ft), e_t=float(eft), f_1=float(f1), e_1=float(ef1), g_amp=float(bb[2]), f_s=float(fs_), e_s=float(efs),
                    scan=q["scan"], frame=q["frame"], fn=q["fn"], tx=q["tx"], ty=q["ty"], gx=q["gx"], gy=q["gy"]))
mjd = np.array([o["mjd"] for o in out]); zp = np.array([o["zp"] for o in out])
ft = np.array([o["f_t"] for o in out]); et = np.array([o["e_t"] for o in out]); fsr = np.array([o["f_s"] for o in out])
# calibration: star's forced magnitude vs AllWISE W1
mst = zp - 2.5 * np.log10(np.clip(fsr, 1e-3, None)); C = np.median(W1CAL - mst); sC = 1.4826 * np.median(np.abs(W1CAL - mst - C)) / np.sqrt(len(mst))
print(f"calibration offset {C:+.3f} mag (star scatter per frame {1.4826*np.median(np.abs(W1CAL - mst - C)):.3f} mag; offset error {sC:.3f})", flush=True)
# J1059 fluxes in mJy: three variants
k = 309.54e3 * 10 ** (-0.4 * (zp + C))       # mJy per DN
gal = np.array([o["g_amp"] for o in out]) * 2 * np.pi * sig ** 2 * k           # galaxy flux (mJy) from free 2-source fits
Gfix = float(np.median(gal)); print(f"galaxy flux from free 2-source fits: median {Gfix:.3f} mJy, 16-84% {np.percentile(gal,16):.3f}-{np.percentile(gal,84):.3f}", flush=True)
ffix, efix = [], []
for o_ in out:
    data = fits.getdata(o_["fn"]).astype(float); ny, nx = data.shape; Y, X = np.mgrid[0:ny, 0:nx]; good = np.isfinite(data)
    kk = 309.54e3 * 10 ** (-0.4 * (o_["zp"] + C))
    bx = (np.abs(X - round(o_["tx"])) <= 4) & (np.abs(Y - round(o_["ty"])) <= 4) & good
    gal_img = (Gfix / kk) / (2 * np.pi * sig ** 2) * gauss(X[bx], Y[bx], o_["gx"], o_["gy"], sig)
    A = np.vstack([np.ones(bx.sum()), gauss(X[bx], Y[bx], o_["tx"], o_["ty"], sig)]).T
    bb, *_ = np.linalg.lstsq(A, data[bx] - gal_img, rcond=None); res = data[bx] - gal_img - A @ bb
    s2 = res @ res / max(bx.sum() - 2, 1); Cc = np.linalg.inv(A.T @ A) * s2
    ffix.append(bb[1] * 2 * np.pi * sig ** 2 * kk); efix.append(np.sqrt(Cc[1, 1]) * 2 * np.pi * sig ** 2 * kk)
F1 = np.array([o["f_1"] for o in out]) * k; eF1 = np.array([o["e_1"] for o in out]) * k
VARIANT = __import__("os").environ.get("VARIANT", "fixed")
if VARIANT == "single": F, eF = F1, eF1
elif VARIANT == "free": F, eF = ft * k, et * k
else: F, eF = np.array(ffix), np.array(efix)
print(f"VARIANT = {VARIANT}", flush=True)
Fphot = 309.54e3 * 10 ** (-0.4 * 15.31)
# check against the catalogue detections (detected frames): compare forced vs w1mpro
det = np.genfromtxt("../data/j1059_neowise_lc.csv", delimiter=",", skip_header=1, names=True)
mt = []
for d_ in det:
    j = np.argmin(np.abs(mjd - d_["mjd"]))
    if abs(mjd[j] - d_["mjd"]) < 2e-4 and F[j] > 0: mt.append((d_["w1mpro"], -2.5 * np.log10(F[j] / 309.54e3)))
mt = np.array(mt); print(f"forced vs catalogue w1mpro for {len(mt)} detected frames: median (forced - catalogue) {np.median(mt[:,1]-mt[:,0]):+.3f} mag, scatter {1.4826*np.median(np.abs(mt[:,1]-mt[:,0]-np.median(mt[:,1]-mt[:,0]))):.3f}", flush=True)
print(f"frames with a catalogue detection: {len(mt)} of {len(F)}; forced fluxes available in all", flush=True)
ph = (bjd(mjd) / P) % 1
o = np.argsort(mjd); vis = np.empty(len(mjd), int); vis[o] = np.cumsum(np.r_[0, np.diff(mjd[o]) > 60])
print(f"\nphotosphere W1 15.31 = {Fphot:.3f} mJy (VHS Ks + Ks-W1 0.21)\n per visit: year, n, mean mJy, semi-amp mJy, model minimum mJy (min/photosphere), lowest 3 forced fluxes")
per = []
for vv in np.unique(vis):
    m = vis == vv
    if m.sum() < 8: continue
    X_ = np.vstack([np.ones(m.sum()), np.cos(2 * np.pi * ph[m]), np.sin(2 * np.pi * ph[m])]).T; w = 1 / eF[m]
    b, *_ = np.linalg.lstsq(X_ * w[:, None], F[m] * w, rcond=None); Cv = np.linalg.inv((X_ * w[:, None]).T @ (X_ * w[:, None]))
    res = (F[m] - X_ @ b) * w; s = np.sqrt(max(res @ res / max(m.sum() - 3, 1), 1))
    A = np.hypot(b[1], b[2]); eA = np.sqrt((b[1] ** 2 * Cv[1, 1] + b[2] ** 2 * Cv[2, 2]) / max(A ** 2, 1e-12)) * s
    mn = b[0] - A; emn = np.sqrt(Cv[0, 0] * s ** 2 + eA ** 2)
    yr = 2000 + (np.mean(mjd[m]) - 51544.5) / 365.25
    per.append(dict(year=round(float(yr), 2), n=int(m.sum()), mean=float(b[0]), emean=float(np.sqrt(Cv[0, 0]) * s), semi=float(A), esemi=float(eA), minimum=float(mn), eminimum=float(emn)))
    print(f"  {yr:.2f} n={m.sum():2d} mean {b[0]:.3f}+-{np.sqrt(Cv[0,0])*s:.3f} semi {A:.3f}+-{eA:.3f} min {mn:.3f}+-{emn:.3f} ({mn/Fphot:.2f}x phot)  lowest {np.sort(F[m])[:3].round(3)}")
# phase-binned, early vs late
res = {"per_visit": per, "Fphot_mJy": Fphot, "psf_sigma_px": sig, "cal_offset_mag": float(C)}
for lab, sel in (("2014-2018", mjd < 58500), ("2019-2020.9", (mjd >= 58500) & (mjd < 59215)), ("2021-2024", mjd >= 59215)):
    if sel.sum() < 20: continue
    edges = np.linspace(0, 1, 11); med = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        s_ = sel & (ph >= lo) & (ph < hi)
        med.append((float(np.median(F[s_])), float(1.2533 * np.std(F[s_]) / np.sqrt(max(s_.sum(), 1))), int(s_.sum())) if s_.sum() >= 3 else (np.nan, np.nan, int(s_.sum())))
    mins = min(med, key=lambda x: x[0] if np.isfinite(x[0]) else 9)
    res[f"binned_{lab}"] = med
    print(f"\n {lab}: phase-binned median flux (mJy): " + " ".join(f"{m_[0]:.3f}" for m_ in med) + f"\n   faintest bin {mins[0]:.3f} +- {mins[1]:.3f} mJy = {mins[0]/Fphot:.2f}x photosphere (n={mins[2]}); brightest {max(m_[0] for m_ in med if np.isfinite(m_[0])):.3f}")
json.dump(res, open(f"j1059_forced_{VARIANT}.json", "w"), indent=1, default=float)
np.savetxt(f"j1059_forced_lc_{VARIANT}.csv", np.vstack([mjd, bjd(mjd), F, eF, ph]).T, delimiter=",", fmt="%.7f",
           header="VarWISE J105943.85-274050.1 = Gaia DR3 5456743064671253632; NEOWISE-R W1 forced PSF photometry (2-source fixed-position fit), flux in mJy; phase at P = 0.12097159 d\nmjd_utc,bjd_tdb,f_mjy,e_mjy,phase")
