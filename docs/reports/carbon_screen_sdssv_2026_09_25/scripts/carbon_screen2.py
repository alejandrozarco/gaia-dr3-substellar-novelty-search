"""Carbon screen v2 of SDSS-V DR20 massive DA-type white dwarfs (DAQ / hidden hot and warm DQ search).
Per object: all BOSS visits from mwmVisit (XCSAO shift undone for in-stack visits), inverse-variance coadd;
depth = 1 - f/cont, cont = smoothed running 80th percentile over 25 A; Balmer cores (+-35 A), telluric bands and
sky lines masked; inverse-variance weights (capped at their 90th percentile). Weighted matched filter
z(v) = sum(w d T_v)/sqrt(sum(w T_v^2)) for Gaussian templates (FWHM 5 A) of curated C I, C II, C I+C II ('C')
and He I line lists, v = -1500..+1500 km/s. Contrast = (z - median)/(1.4826 MAD) with median/MAD from
v < -600 or v > +800 km/s; the peak is taken inside the prior window -200..+400 km/s.
Tuned on 7 known carbon white dwarfs vs 486 sample spectra (all 7 above the sample 99th percentile of 6.5).
Per-visit contrasts of the 'C' template at the coadd peak velocity are also reported. Missing files are skipped."""
import sys, os, numpy as np, pandas as pd, warnings
import carbon_screen as cs
from scipy.ndimage import percentile_filter, gaussian_filter1d
warnings.filterwarnings("ignore")
LIN = dict(cs.LINES); LIN["C"] = LIN["C I"] + LIN["C II"]
SIG = 5 / 2.3548
TT = {}
for sp, L in LIN.items():
    T = np.zeros((len(cs.vels), len(cs.grid)))
    for lam in L: T += np.exp(-0.5 * ((cs.grid[None, :] - lam * (1 + cs.vels / cs.C)[:, None]) / SIG) ** 2)
    TT[sp] = T
INW = (cs.vels >= -200) & (cs.vels <= 400); FAR = (cs.vels < -600) | (cs.vels > 800)
def prep(f, iv):
    m = np.isfinite(f) & (iv > 0)
    if m.sum() < 2000: return None
    ff = np.interp(np.arange(len(cs.grid)), np.where(m)[0], f[m])
    npix = int(round(np.log10(1 + 25 / 5000) / 6e-5))
    cont = gaussian_filter1d(percentile_filter(ff, 80, size=npix), npix / 3)
    d = 1 - ff / cont; w = iv * cont ** 2; good = m.copy()
    for a, b in cs.MASK: good &= ~((cs.grid > a) & (cs.grid < b))
    w = np.where(good, w, 0); w = np.minimum(w, np.percentile(w[good], 90)); d[~good] = 0
    return d, w
def contrast(d, w, sp):
    z = (TT[sp] @ (w * d)) / np.sqrt((TT[sp] ** 2) @ w)
    med = np.median(z[FAR]); mad = 1.4826 * np.median(np.abs(z[FAR] - med))
    return (z - med) / mad
if __name__ == "__main__":
    s = pd.read_csv(sys.argv[1], dtype={"sdss_id": str, "gaia_dr3_source_id": str}); outf = sys.argv[2]
    done = set(pd.read_csv(outf, dtype={"sdss_id": str}).sdss_id) if os.path.exists(outf) else set()
    fo = open(outf, "a")
    if not done: fo.write("sdss_id,gaia,nvis,snr_max,C,C_v,CI,CI_v,CII,CII_v,HeI,HeI_v,C_vis,status\n")
    n = 0
    for r in s.itertuples():
        if r.sdss_id in done: continue
        if not (os.path.exists(f"/tmp/fanout/exotic_atm/visit/mwmVisit-0.8.1-{r.sdss_id}.fits") or os.path.exists(f"/tmp/mwd/spec/mwmVisit-0.8.1-{r.sdss_id}.fits")): continue
        vis = cs.load(r.sdss_id)
        if not vis: fo.write(f"{r.sdss_id},{r.gaia_dr3_source_id},0,,,,,,,,,,,NOVISITS\n"); fo.flush(); continue
        num = np.nansum([v["f"] * v["iv"] for v in vis], axis=0); den = np.sum([v["iv"] for v in vis], axis=0)
        p = prep(np.where(den > 0, num / np.where(den > 0, den, 1), np.nan), den)
        if p is None: fo.write(f"{r.sdss_id},{r.gaia_dr3_source_id},{len(vis)},,,,,,,,,,,BADCOADD\n"); fo.flush(); continue
        out = {}
        for sp in ("C", "C I", "C II", "He I"):
            c = contrast(*p, sp); k = int(np.argmax(np.where(INW, c, -99))); out[sp] = (c[k], cs.vels[k])
        kC = int(np.argmin(np.abs(cs.vels - out["C"][1]))); pv = []
        for v in vis:
            pp = prep(v["f"], v["iv"])
            if pp is None: continue
            pv.append(f"{contrast(*pp, 'C')[kC]:.1f}")
        fo.write(f"{r.sdss_id},{r.gaia_dr3_source_id},{len(vis)},{max(v['snr'] for v in vis):.1f}," + ",".join(f"{out[sp][0]:.2f},{out[sp][1]:.0f}" for sp in ("C", "C I", "C II", "He I")) + f",{'/'.join(pv)},ok\n"); fo.flush(); n += 1
    print("SCREEN2_DONE", n)
