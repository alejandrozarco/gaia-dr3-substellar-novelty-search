"""Emission-line screen of SDSS-V DR20 white dwarf visit spectra (gaseous debris discs and Balmer-emission white dwarfs).
Usage: python gasdisc_screen.py <sample.csv> <out.csv>   (sample needs sdss_id, gaia_dr3_source_id, classification)
Per object: mwmVisit visits (XCSAO shift undone for in-stack visits), inverse-variance coadd on a log grid (6e-5 dex).
Ca II triplet (vacuum 8500.35, 8544.44, 8664.52 A): continuum = cubic polynomial over 8380-8800 A fitted with ivar weights,
+-1100 km/s around each Ca II line and O I 8448.7 masked, 3 iterations of 3-sigma clipping; y = f/cont - 1.
Matched filter z = sum(w y T) / sqrt(sum(w T^2)), w = ivar cont^2, for emission templates summed over the three lines:
narrow single Gaussians (sigma 60, 150 km/s) and double-peaked profiles (half-separation 150, 250, 350, 500 km/s,
peak sigma max(70, 0.45 vp)), centre velocity -400..+400 km/s in 20 km/s steps. Also per-line z and the summed equivalent width.
H-alpha core: y = f / median filter (73 A) - 1, narrow Gaussian (sigma 100 km/s) matched filter over -400..+400 km/s.
O I 8448.7 narrow + broad z at the Ca II best velocity. Per-visit Ca II z for the best template.
Download holes are written as HOLE. Every object's coadd over REG and its per-visit spectra over 6400-6750 and 8250-8950 A are
stored in store/<last2>/<sdss_id>.npz for the second (template-subtraction) pass."""
import sys, os, time, shutil, threading, requests, numpy as np, pandas as pd, warnings
from concurrent.futures import ThreadPoolExecutor
from astropy.io import fits
from scipy.ndimage import median_filter
warnings.filterwarnings("ignore")
C = 299792.458
VDIR = "/tmp/fanout/exotic_atm/visit"; KEEP = "/tmp/hotdq/lane_gasdisc/keep"
SAS = "https://data.sdss.org/sas/dr20/spectro/astra/0.8.1/spectra/visit"
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5)
CAT = np.array([8500.35, 8544.44, 8664.52]); OI = 8448.7; HA = 6564.61
LO, HI = 8380, 8800
R = (GRID > LO) & (GRID < HI); WR = GRID[R]
VEL = np.arange(-400, 401, 20.0)
PROF = [("n60", 0, 60), ("n150", 0, 150)] + [(f"dp{vp}", vp, max(70, 0.45 * vp)) for vp in (150, 250, 350, 500)]
def tmpl(lines, vp, sig, wave):
    T = np.zeros((len(VEL), len(wave)))
    for lam in lines:
        for s in ((0,) if vp == 0 else (-vp, vp)):
            mu = lam * (1 + (VEL + s) / C)[:, None]; sg = lam * sig / C
            T += np.exp(-0.5 * ((wave[None, :] - mu) / sg) ** 2)
    return T
TCAT = {name: tmpl(CAT, vp, sg, WR) for name, vp, sg in PROF}
TLINE = {name: [tmpl([lam], vp, sg, WR) for lam in CAT] for name, vp, sg in PROF}
TOI = {name: tmpl([OI], vp, sg, WR) for name, vp, sg in PROF[:2] + PROF[3:4]}
HR = (GRID > 6450) & (GRID < 6680); THA = tmpl([HA], 0, 100, GRID[HR])
LMASK = np.zeros(R.sum(), bool)
for lam in list(CAT) + [OI]:
    LMASK |= np.abs(WR / lam - 1) * C < 1100

def load(fn):
    vis = []
    with fits.open(fn) as h:
        for i in (1, 2):
            if i >= len(h) or h[i].data is None or len(h[i].data) == 0: continue
            hd = h[i].header; wg = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"]))
            for r in h[i].data:
                v = float(r["xcsao_v_rad"]); ins = bool(r["in_stack"])
                w = wg * (1 + v / C) if (ins and np.isfinite(v)) else wg
                f = np.array(r["flux"], float); iv = np.array(r["ivar"], float); ok = (iv > 0) & np.isfinite(f)
                if ok.sum() < 1000: continue
                vis.append(dict(mjd=int(r["mjd"]), snr=float(r["snr"]), f=np.interp(GRID, w[ok], f[ok], left=np.nan, right=np.nan),
                                iv=np.interp(GRID, w[ok], iv[ok], left=0, right=0)))
    return vis

REG = [(3880, 4000), (4780, 4940), (4990, 5200), (5820, 5940), (6400, 6750), (7740, 7810), (8250, 8950)]
VREG = [(6400, 6750), (8250, 8950)]
STORE = "/tmp/hotdq/lane_gasdisc/store"
def save(sid, vis, f, iv):
    d = {}
    for a, b in REG:
        m = (GRID > a) & (GRID < b); d[f"f_{a}"] = f[m].astype(np.float32); d[f"iv_{a}"] = iv[m].astype(np.float32)
    for a, b in VREG:
        m = (GRID > a) & (GRID < b)
        d[f"vf_{a}"] = np.array([v["f"][m] for v in vis], np.float32); d[f"viv_{a}"] = np.array([v["iv"][m] for v in vis], np.float32)
    d["mjd"] = np.array([v["mjd"] for v in vis]); d["vsnr"] = np.array([v["snr"] for v in vis], np.float32)
    os.makedirs(f"{STORE}/{sid[-2:]}", exist_ok=True); np.savez_compressed(f"{STORE}/{sid[-2:]}/{sid}.npz", **d)

def cat_prep(f, iv):
    f = f[R]; iv = iv[R]; ok = np.isfinite(f) & (iv > 0)
    if ok.sum() < 300: return None
    x = (WR - 8590) / 210; use = ok & ~LMASK
    for _ in range(3):
        if use.sum() < 100: return None
        p = np.polyfit(x[use], f[use], 3, w=np.sqrt(iv[use])); cont = np.polyval(p, x)
        res = (f - cont) * np.sqrt(iv); use = use & (np.abs(res) < 3)
    if np.nanmedian(cont) <= 0: return None
    y = np.where(ok, f / cont - 1, 0.0); w = np.where(ok, iv * cont ** 2, 0.0)
    return y, w

def zscore(T, y, w):
    den = np.sqrt((T ** 2) @ w); den[den == 0] = np.inf
    return (T @ (w * y)) / den

def analyse(vis, sid=None):
    num = np.nansum([v["f"] * v["iv"] for v in vis], axis=0); den = np.sum([v["iv"] for v in vis], axis=0)
    f = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)
    if sid is not None: save(sid, vis, f, den)
    out = {}
    p = cat_prep(f, den)
    if p is None: out["status"] = "BADCAT"; return out
    y, w = p; best = (-99, None, 0)
    for name in TCAT:
        z = zscore(TCAT[name], y, w); k = int(np.argmax(z)); out[f"z_{name}"] = round(float(z[k]), 2)
        if z[k] > best[0]: best = (float(z[k]), name, k)
    zb, nb, kb = best; out.update(z_cat=round(zb, 2), cat_tmpl=nb, cat_v=int(VEL[kb]))
    out["z_lines"] = "/".join(f"{zscore(T[kb:kb+1], y, w)[0]:.1f}" for T in TLINE[nb])
    dl = np.gradient(WR); win = np.zeros(len(WR), bool)
    for lam in CAT: win |= np.abs(WR / (lam * (1 + VEL[kb] / C)) - 1) * C < 700
    out["ew_cat"] = round(float(np.sum((y * dl)[win & (w > 0)])), 2)
    out["z_oi"] = round(float(max(zscore(TOI[n][kb:kb+1], y, w)[0] for n in TOI)), 2)
    per = []
    for v in vis:
        pv = cat_prep(v["f"], v["iv"])
        if pv is not None: per.append(f"{zscore(TCAT[nb][kb:kb+1], *pv)[0]:.1f}")
    out["z_cat_visits"] = "/".join(per)
    fh = f[HR]; ivh = den[HR]; okh = np.isfinite(fh) & (ivh > 0)
    if okh.sum() > 100:
        ff = np.interp(np.arange(len(fh)), np.where(okh)[0], fh[okh]); cont = median_filter(ff, 121, mode="nearest")
        yh = np.where(okh, ff / cont - 1, 0); wh = np.where(okh, ivh * cont ** 2, 0)
        zh = zscore(THA, yh, wh); k = int(np.argmax(zh)); out.update(z_ha=round(float(zh[k]), 2), ha_v=int(VEL[k]))
    out["status"] = "OK"
    return out

tl = threading.local()
def fetch(sid):
    fn = f"{VDIR}/mwmVisit-0.8.1-{sid}.fits"
    if os.path.exists(fn) and os.path.getsize(fn) > 10000: return fn, False
    kf = f"{KEEP}/mwmVisit-0.8.1-{sid}.fits"
    if os.path.exists(kf): return kf, False
    if not hasattr(tl, "s"): tl.s = requests.Session()
    for k in range(4):
        try:
            r = tl.s.get(f"{SAS}/{sid[-4:-2]}/{sid[-2:]}/mwmVisit-0.8.1-{sid}.fits", timeout=120)
            if r.status_code == 200 and len(r.content) > 10000 and r.content[:6] == b"SIMPLE":
                open(fn + ".part", "wb").write(r.content); os.replace(fn + ".part", fn); return fn, True
            if r.status_code == 404: return None, False
        except Exception: pass
        time.sleep(2 + 4 * k)
    return None, False

COLS = ["sdss_id", "gaia", "cls", "snr", "nvis", "z_cat", "cat_tmpl", "cat_v", "z_lines", "ew_cat", "z_oi", "z_ha", "ha_v",
        "z_n60", "z_n150", "z_dp150", "z_dp250", "z_dp350", "z_dp500", "z_cat_visits", "status"]
if __name__ == "__main__":
    os.makedirs(KEEP, exist_ok=True)
    s = pd.read_csv(sys.argv[1], dtype=str); outf = sys.argv[2]
    done = set(pd.read_csv(outf, dtype={"sdss_id": str}).sdss_id) if os.path.exists(outf) else set()
    todo = [r for r in s.itertuples() if r.sdss_id not in done]; print("to do", len(todo), flush=True)
    fo = open(outf, "a")
    if not done: fo.write(",".join(COLS) + "\n")
    t0 = time.time()
    with ThreadPoolExecutor(4) as ex:
        for i, (r, (fn, fresh)) in enumerate(zip(todo, ex.map(lambda r: fetch(r.sdss_id), todo))):
            row = dict(sdss_id=r.sdss_id, gaia=r.gaia_dr3_source_id, cls=r.classification, snr=r.snr)
            if fn is None: row["status"] = "HOLE"
            else:
                try:
                    vis = load(fn); row["nvis"] = len(vis)
                    row.update(analyse(vis, r.sdss_id) if vis else {"status": "NOVIS"})
                except Exception as e: row["status"] = f"ERR_{type(e).__name__}"
                if fresh: os.remove(fn)
            fo.write(",".join(str(row.get(c, "")) for c in COLS) + "\n"); fo.flush()
            if i % 500 == 0: print(f"{time.strftime('%H:%M:%S')} {i}/{len(todo)} {row['status']} {time.time()-t0:.0f}s", flush=True)
    print("GASDISC_DONE", flush=True)
