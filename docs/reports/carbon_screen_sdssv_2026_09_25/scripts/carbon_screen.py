"""Carbon screen of SDSS-V DR20 massive DA-type white dwarfs (DAQ / hidden hot and warm DQ search).
Per object: all BOSS visits from mwmVisit (XCSAO shift undone for in-stack visits), inverse-variance coadd;
high-pass depth = 1 - f/cont with cont = smoothed running 80th percentile over 25 A; Balmer cores (+-35 A),
telluric bands and sky lines masked; Pearson cross-correlation with Gaussian templates (FWHM 5 A) of curated
C I, C II and He I line lists over -1500..+1500 km/s; contrast = (peak - median)/(1.4826 MAD) of the CCF at
|v - v_peak| > 400 km/s. Also per-visit C I/C II contrast at the coadd peak velocity."""
import sys, os, numpy as np, pandas as pd, warnings
from astropy.io import fits
from scipy.ndimage import percentile_filter, gaussian_filter1d
warnings.filterwarnings("ignore")
C = 299792.458
grid = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5)
LINES = {
 "C I": [4773.1, 4933.4, 5053.6, 5381.8, 6014.8, 7115.1, 7117.1, 7118.9, 8337.4, 9063.9, 9091.0, 9097.3, 9114.3],
 "C II": [3921.8, 4077.0, 4268.4, 4375.5, 4620.5, 5146.6, 6579.9, 6584.7, 7233.3, 7238.4],
 "He I": [4027.3, 4389.2, 4472.7, 4714.5, 4923.3, 5017.1, 5877.3, 6679.99, 7067.1],
}
BALMER = [3890.2, 3971.2, 4102.9, 4341.7, 4862.7, 6564.6]
MASK = [(b-35, b+35) for b in BALMER] + [(5574, 5582), (6297, 6304), (6860, 6960), (7590, 7700), (8940, 8990)]
vels = np.arange(-1500, 1501, 10.0)
def templates(lines, w):
    T = np.zeros((len(vels), len(w)))
    for lam in lines:
        mu = lam * (1 + vels / C)[:, None]
        T += np.exp(-0.5 * ((w[None, :] - mu) / 2.12) ** 2)
    T -= T.mean(axis=1, keepdims=True)
    return T / np.linalg.norm(T, axis=1, keepdims=True)
def load(sid):
    fn = f"/tmp/fanout/exotic_atm/visit/mwmVisit-0.8.1-{sid}.fits"
    if not os.path.exists(fn):
        fn2 = f"/tmp/mwd/spec/mwmVisit-0.8.1-{sid}.fits"
        if os.path.exists(fn2): fn = fn2
        else: return None
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
                vis.append(dict(mjd=int(r["mjd"]), snr=float(r["snr"]), f=np.interp(grid, w[ok], f[ok], left=np.nan, right=np.nan),
                                iv=np.interp(grid, w[ok], iv[ok], left=0, right=0)))
    return vis
def depth(f, iv):
    m = np.isfinite(f) & (iv > 0)
    if m.sum() < 2000: return None
    ff = np.interp(np.arange(len(grid)), np.where(m)[0], f[m])
    npix = int(round(np.log10(1 + 25 / 5000) / 6e-5))
    cont = gaussian_filter1d(percentile_filter(ff, 80, size=npix), npix / 3)
    d = 1 - ff / cont
    good = m.copy()
    for a, b in MASK: good &= ~((grid > a) & (grid < b))
    d[~good] = 0.0
    return d, good
TT = None
def ccf(d, good):
    out = {}
    for sp, T in TT.items():
        x = d - d[good].mean(); x[~good] = 0
        cc = (T[:, good] @ x[good]) / (np.linalg.norm(x[good]) + 1e-12)
        k = int(np.argmax(cc)); far = np.abs(vels - vels[k]) > 400
        mad = 1.4826 * np.median(np.abs(cc[far] - np.median(cc[far])))
        out[sp] = (float((cc[k] - np.median(cc[far])) / mad), float(vels[k]), float(cc[k]), cc)
    return out
if __name__ == "__main__":
    TT = {sp: templates(l, grid) for sp, l in LINES.items()}
    s = pd.read_csv(sys.argv[1], dtype={"sdss_id": str, "gaia_dr3_source_id": str})
    outf = sys.argv[2]; done = set()
    if os.path.exists(outf): done = set(pd.read_csv(outf, dtype={"sdss_id": str}).sdss_id)
    fo = open(outf, "a")
    if not done: fo.write("sdss_id,gaia,nvis,snr_max,cI_con,cI_v,cI_r,cII_con,cII_v,cII_r,heI_con,heI_v,cI_vis,cII_vis,status\n")
    for r in s.itertuples():
        if r.sdss_id in done: continue
        vis = load(r.sdss_id)
        if not vis: fo.write(f"{r.sdss_id},{r.gaia_dr3_source_id},0,,,,,,,,,,,,HOLE\n"); fo.flush(); continue
        num = np.nansum([v["f"] * v["iv"] for v in vis], axis=0); den = np.sum([v["iv"] for v in vis], axis=0)
        dd = depth(np.where(den > 0, num / np.where(den > 0, den, 1), np.nan), den)
        if dd is None: fo.write(f"{r.sdss_id},{r.gaia_dr3_source_id},{len(vis)},,,,,,,,,,,,BADCOADD\n"); fo.flush(); continue
        R = ccf(*dd)
        pv = []
        for sp in ("C I", "C II"):
            k = int(np.argmin(np.abs(vels - R[sp][1]))); vals = []
            for v in vis:
                dv = depth(v["f"], v["iv"])
                if dv is None: continue
                Rv = ccf(*dv); cc = Rv[sp][3]; far = np.abs(vels - vels[k]) > 400
                mad = 1.4826 * np.median(np.abs(cc[far] - np.median(cc[far])))
                vals.append(f"{(cc[k]-np.median(cc[far]))/mad:.1f}")
            pv.append("/".join(vals))
        fo.write(f"{r.sdss_id},{r.gaia_dr3_source_id},{len(vis)},{max(v['snr'] for v in vis):.1f},"
                 f"{R['C I'][0]:.2f},{R['C I'][1]:.0f},{R['C I'][2]:.3f},{R['C II'][0]:.2f},{R['C II'][1]:.0f},{R['C II'][2]:.3f},"
                 f"{R['He I'][0]:.2f},{R['He I'][1]:.0f},{pv[0]},{pv[1]},ok\n"); fo.flush()
    print("SCREEN_DONE")
