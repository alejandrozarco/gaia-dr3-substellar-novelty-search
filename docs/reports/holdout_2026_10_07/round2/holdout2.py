"""Blind leave-one-block-out ephemeris prediction test, generalised from docs/reports/holdout_2026_10_07/holdout.py (analysis
part unchanged; data loaders extended). Usage: python holdout2.py <gaia_id>
Data (cached only): ~/claude_projects/white-dwarfs-2026/data (ATLAS forced photometry, ZTF DR light curves, Gaia DR3 epoch
photometry, TESS SPOC 2-min and TESScut FFI caches); TESS SPOC for TIC 734503308 downloaded to ./cache (MAST) on 2026-10-07.
Time systems: ATLAS MJD = exposure start (+15 s); ZTF mjd = exposure start (+exptime/2; verified: hjd - helio(mjd) = 15.00 s);
Gaia TimeG + 2455197.5 = BJD_TCB -> converted to BJD_TDB; TESS BTJD + 2457000 = BJD_TDB.
Blocks: ATLAS and ZTF per observing season (separate blocks per survey), each TESS sector group, all Gaia DR3 epochs = one block.
TESS detrending: running median over the integer number of periods >= 0.5 d (the original fixed 361 cadences = 12 h would
partially remove 3.5-7 h signals)."""
import sys, os, json, glob, numpy as np, pandas as pd, warnings
from astropy.io import fits
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.wcs import WCS
import astropy.units as u
from scipy.ndimage import median_filter
from scipy.optimize import least_squares
warnings.filterwarnings("ignore")
D = os.path.expanduser("~/claude_projects/white-dwarfs-2026/data"); OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261007)
OBJ = {  # f0 = catalogue/journal frequency (c/d); ra/dec ICRS (deg)
 "4996506979251027584": dict(name="WDJ001049.73-402029.49", G=18.328, f0=12.8313355, tic="616483543", tess_mode="spoc", tess_groups=[[103], [105]]),
 "303768056000635776": dict(name="WDJ013915.33+312419.24", G=18.016, f0=6.7555956, tic="620689181", tess_mode="spoc", tess_groups=[[85]]),
 "5467851842959399808": dict(name="WDJ103039.63-275438.60", G=18.315, f0=5.9877125, tic="874589139", tess_mode="spoc", tess_groups=[[99]]),
 "4765533842915331072": dict(name="WDJ055704.94-574404.09", G=18.35, f0=13.0390, tic="734503308", tess_mode="spoc", tess_groups=[[97, 98]]),
 "6177529630243170432": dict(name="WDJ140056.81-264218.70", G=18.301, f0=11.0730638, tic="1055802439", tess_mode="spoc", tess_groups=[[102]]),
 "2482810406432480512": dict(name="WDJ011651.58-044046.82", G=18.343, f0=3.379069, tic="610652043", tess_mode="spoc", tess_groups=[[70], [97]]),
 "6914922055508553984": dict(name="WDJ205249.27-032419.53", G=17.466, f0=14.7385119, tic="1997276088", tess_mode="spoc", tess_groups=[[55], [81]]),
 "5503429908930455808": dict(name="WDJ070106.16-534811.37", G=18.426, f0=17.6702102, tic=None, tess_mode="ffi", tess_groups=[[88, 89], [93], [96], [98]]),
 "2191618770599895296": dict(name="WDJ212738.67+593755.72", G=16.871, f0=11.0614137, tic="2019069807", tess_mode="spoc", tess_groups=[[76, 77], [83, 84]]),
 "4844023064578952320": dict(name="WDJ040444.35-395043.1", G=17.663, f0=12.2742647, tic=None, tess_mode="ffi", tess_groups=[[106], [107]]),
}
GID = sys.argv[1]; C = OBJ[GID]; C["kind"] = "sine"; NTRIAL = 1000
if len(sys.argv) > 2: C["tess_groups"] = json.loads(sys.argv[2])  # optional override, e.g. '[[106,107]]'
TAG = GID + (sys.argv[3] if len(sys.argv) > 3 else "")
IRR = pd.read_csv(f"{os.path.expanduser('~/claude_projects/white-dwarfs-2026/tables')}/irradiated_companions.csv", dtype={"gaia_dr3": str}).set_index("gaia_dr3")
if GID in IRR.index: RA, DEC = float(IRR.loc[GID, "ra_deg"]), float(IRR.loc[GID, "dec_deg"])
else:
    L0 = [l for l in open(f"{D}/atlas_forced_photometry_{GID}.txt").read().splitlines() if l.strip()]; RA, DEC = float(L0[1].split()[8]), float(L0[1].split()[9])
c0 = SkyCoord(RA * u.deg, DEC * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd):
    tb = Time(mjd, format="mjd", scale="utc", location=geo); return (tb.tdb + tb.light_travel_time(c0)).jd

def seasons(t_mjd):
    """observing season = years counted from solar conjunction (Sun RA = object RA), so boundaries fall in the unobservable gap"""
    t_conj = 57467.6 + RA / 360.0 * 365.2422  # MJD of 2016 March equinox + RA offset
    return np.floor((t_mjd - t_conj) / 365.2422).astype(int) + 1

def robust_clip(y, eclipse):
    med = np.median(y); s = 1.4826 * np.median(np.abs(y - med))
    return (y - med < 5 * s) & (y - med > (-2.5 if eclipse else -5 * s))

def tess_detrend(t, fl):
    P = 1 / C["f0"]; k = int(np.ceil(0.5 / P)); cad = np.median(np.diff(t)); n = int(round(k * P / cad)) | 1
    return median_filter(fl, size=n, mode="nearest")

rows = []  # t, y, e, dataset, block
def P_pre(*a): print(*a, flush=True)
Fstar = 3631e6 * 10 ** (-0.4 * C["G"])
# ---- ATLAS (exposure start + 15 s)
pA = f"{D}/atlas_forced_photometry_{GID}.txt"
if os.path.exists(pA):
    L = [l for l in open(pA).read().splitlines() if l.strip()]
    hdr = L[0].lstrip("#").split(); A = pd.DataFrame([l.split() for l in L[1:]], columns=hdr)
    for c in ("MJD", "uJy", "duJy", "err", "chi/N", "RA", "Dec", "mag5sig"): A[c] = A[c].astype(float)
    A = A[(A.duJy > 0) & (A.err == 0) & (A["chi/N"] < 10)]
    A["season"] = seasons(A.MJD.values)
    for b in ("c", "o"):
        x = A[A.F == b].copy(); x = x[x.duJy < 3 * x.duJy.median()]
        for s in np.unique(x.season):
            m = (x.season == s).values; x.loc[m, "uJy"] -= np.median(x.uJy[m])
        y = x.uJy.values / Fstar; e = x.duJy.values / Fstar; k = robust_clip(y, False)
        for tt, yy, ee, ss in zip(bjd(x.MJD.values + 15.0 / 86400)[k], y[k], e[k], x.season.values[k]): rows.append((tt, yy, ee, f"ATLAS_{b}", f"ATLAS_s{ss}"))
# ---- ZTF (mjd = exposure start; + exptime/2); per-oid median removed, then per-season median
pZ = f"{OUT}/ztf_{GID}_refetch.csv" if os.path.exists(f"{OUT}/ztf_{GID}_refetch.csv") else f"{D}/ztf_{GID}.csv"  # IRSA refetch 2026-10-07 (g,r,i) where the cache lacked bands
if os.path.exists(pZ):
    Z = pd.read_csv(pZ); Z = Z[(Z.catflags == 0) & (Z.magerr < 0.25)].copy()
    Z = Z[Z.groupby("oid").mjd.transform("size") >= 10].copy()
    Z["dm"] = Z.mag - Z.groupby("oid").mag.transform("median"); Z["season"] = seasons(Z.mjd.values)
    for b in ("zg", "zr", "zi"):
        x = Z[Z.filtercode == b]
        for s in np.unique(x.season):
            mm = x[x.season == s]; y = 10 ** (-0.4 * (mm.dm.values - np.median(mm.dm.values))) - 1; e = 0.921 * mm.magerr.values * (1 + y)
            k = robust_clip(y, False); tm = mm.mjd.values + mm.exptime.values / 2 / 86400
            for tt, yy, ee in zip(bjd(tm)[k], y[k], e[k]): rows.append((tt, yy, ee, f"ZTF_{b[1]}", f"ZTF_s{s}"))
# ---- Gaia DR3 epoch photometry (BJD_TCB -> BJD_TDB), G and RP, one block
pG = f"{D}/gaia_dr3_epoch_photometry_{GID}.csv"
if os.path.exists(pG):
    E_ = pd.read_csv(pG)
    for b, tc, fc, ec, fl in (("G", "TimeG", "FG", "e_FG", "GrVFlag"), ("RP", "TimeRP", "FRP", "e_FRP", "RPrVFlag")):
        m = np.isfinite(E_[tc]) & np.isfinite(E_[fc]) & (E_[fc] > 0) & (E_[fl] == 0)
        f = E_[fc][m].values; med = np.median(f); y = f / med - 1; e = E_[ec][m].values / med
        t = Time(E_[tc][m].values + 2455197.5, format="jd", scale="tcb").tdb.jd; k = robust_clip(y, False)
        for tt, yy, ee in zip(t[k], y[k], e[k]): rows.append((tt, yy, ee, f"Gaia_{b}", "Gaia_DR3"))
# ---- TESS
for grp in C["tess_groups"]:
    for sec in grp:
        if C["tess_mode"] == "spoc":
            ps = glob.glob(f"{D}/cache/**/*-s{sec:04d}-{int(C['tic']):016d}-*s_lc.fits", recursive=True) + glob.glob(f"{OUT}/cache/**/*-s{sec:04d}-{int(C['tic']):016d}-*s_lc.fits", recursive=True)
            with fits.open(ps[0]) as h:
                d = h[1].data; col = "PDCSAP_FLUX"
                q = (d["QUALITY"] == 0) & np.isfinite(d[col]) & np.isfinite(d["TIME"])
                t = d["TIME"][q].astype(float) + 2457000.0; fl = d[col][q].astype(float); er = d[col + "_ERR"][q].astype(float)
        else:
            ps = sorted(glob.glob(f"{D}/cache/tesscut_{RA:.5f}_*_s{sec}_7x7.fits"))
            with fits.open(ps[0]) as h:
                d = h[1].data; x0, y0 = WCS(h[2].header).world_to_pixel(c0); xi, yi = int(round(float(x0))), int(round(float(y0)))
                q = (d["QUALITY"] == 0) & np.isfinite(d["TIME"]); F = d["FLUX"][q]; t = d["TIME"][q].astype(float) + 2457000.0
                yy_, xx_ = np.mgrid[0:F.shape[1], 0:F.shape[2]]; ring = (np.abs(xx_ - xi) > 1) | (np.abs(yy_ - yi) > 1); ap = ~ring
                fl = np.nansum(F[:, ap], axis=1) - np.nanmedian(F[:, ring], axis=1) * ap.sum(); ok = np.isfinite(fl)
                t, fl = t[ok], fl[ok]; er = np.full(len(fl), np.nan)
        tr = tess_detrend(t, fl)
        if C["tess_mode"] == "spoc": y = fl / tr - 1; e = er / tr
        else:  # FFI: background-subtracted aperture flux of a faint star; normalise by the nominal star flux (T ~ G - 0.3), since the aperture median is background-dominated
            nrm = 15000 * 10 ** (-0.4 * (C["G"] - 0.3 - 10)); y = (fl - tr) / nrm; r_ = y - median_filter(y, 31, mode="nearest"); e = np.full(len(y), 1.4826 * np.median(np.abs(r_ - np.median(r_))))
            P_pre(f"  FFI S{sec}: median aperture flux {np.median(fl):.1f} e/s, background median {np.nanmedian(F[:, ring]):.1f} e/s/pix, n {len(y)}")
        k = robust_clip(y, False)
        for tt, yy, ee in zip(t[k], y[k], e[k]): rows.append((tt, yy, ee, f"TESS_S{sec}", "TESS_" + "+".join(f"S{s}" for s in grp)))
df = pd.DataFrame(rows, columns=["t", "y", "e", "ds", "blk"])
# robust per-dataset error scaling
for ds in df.ds.unique():
    m = df.ds == ds; r = (df.y[m] - np.median(df.y[m])) / df.e[m]; df.loc[m, "e"] *= max(1.4826 * np.median(np.abs(r - np.median(r))), 0.3)
df = df.sort_values("t").reset_index(drop=True)
log = open(f"{OUT}/{TAG}_log.txt", "w")
def P_(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); log.write(s + "\n"); log.flush()
P_(f"{GID} {C['name']} kind={C['kind']} N={len(df)}")
for b, g in df.groupby("blk"): P_(f"  block {b}: n {len(g)}, BJD {g.t.min():.1f}-{g.t.max():.1f}, datasets {sorted(g.ds.unique())}")

SIGW0 = 1.3 / 1440  # eclipse template sigma (d)
# ---------------- model pieces
def design(t, f, T0, sigw):
    if C["kind"] == "sine":
        th = 2 * np.pi * f * (t - T0); return np.vstack([np.ones_like(t), np.cos(th), np.cos(2 * th), np.sin(2 * th)]).T
    ph = ((t - T0) * f + 0.5) % 1 - 0.5; dt = ph / f
    return np.vstack([np.ones_like(t), -np.exp(-0.5 * (dt / sigw) ** 2), -np.cos(2 * np.pi * ph)]).T

def resid(p, sub):
    f, T0 = p[0], p[1]; sigw = p[2] if len(p) > 2 else SIGW0; out = []
    for ds, g in sub:
        X = design(g[0], f, T0, sigw) / g[2][:, None]; yy = g[1] / g[2]; c = np.linalg.lstsq(X, yy, rcond=None)[0]; out.append(yy - X @ c)
    return np.concatenate(out)

def amps(sub, f, T0, sigw):
    r = {}
    for ds, g in sub:
        X = design(g[0], f, T0, sigw) / g[2][:, None]; c, *_ = np.linalg.lstsq(X, g[1] / g[2], rcond=None); cov = np.linalg.inv(X.T @ X); r[ds] = (c[1], np.sqrt(cov[1, 1]))
    return r

def group(d):
    return [(ds, (g.t.values, g.y.values, g.e.values)) for ds, g in d.groupby("ds")]

def grid_power(sub, freqs, tref):
    """returns best total delta-chi2 and best phase reference time for each f"""
    best = np.zeros(len(freqs)); bestT = np.zeros(len(freqs))
    if C["kind"] == "sine":
        PH = np.linspace(0, 2 * np.pi, 720, endpoint=False); cph, sph = np.cos(PH), np.sin(PH)
        for i0 in range(0, len(freqs), 100):
            F = freqs[i0:i0 + 100]; tot = np.zeros((len(F), len(PH)))
            for ds, (t, y, e) in sub:
                w = 1 / e ** 2; y = y - np.sum(w * y) / np.sum(w); th = 2 * np.pi * np.outer(F, t - tref); co, si = np.cos(th), np.sin(th)
                N11 = (co ** 2) @ w; N22 = (si ** 2) @ w; N12 = (co * si) @ w; v1 = co @ (w * y); v2 = si @ (w * y)
                num = np.outer(v1, cph) + np.outer(v2, sph); den = np.outer(N11, cph ** 2) + np.outer(2 * N12, cph * sph) + np.outer(N22, sph ** 2)
                tot += np.where(num > 0, num ** 2 / den, 0)
            k = np.argmax(tot, 1); best[i0:i0 + 100] = tot[np.arange(len(F)), k]; bestT[i0:i0 + 100] = tref + PH[k] / (2 * np.pi) / F
        return best, bestT
    B = 4096; bc = (np.arange(B) + 0.5) / B; off = (bc + 0.5) % 1 - 0.5
    for i, f in enumerate(freqs):
        g = np.exp(-0.5 * (off / f / SIGW0) ** 2); G1, G2 = np.conj(np.fft.rfft(g)), np.conj(np.fft.rfft(g ** 2)); tot = np.zeros(B)
        for ds, (t, y, e) in sub:
            w = 1 / e ** 2; y = y - np.sum(w * y) / np.sum(w); bi = (((t - tref) * f) % 1 * B).astype(int)
            r = np.bincount(bi, w * y, B); W = np.bincount(bi, w, B)
            num = np.fft.irfft(np.fft.rfft(r) * G1, B); den = np.fft.irfft(np.fft.rfft(W) * G2, B)
            tot += np.where((num < 0) & (den > 0), num ** 2 / np.maximum(den, 1e-30), 0)
        k = np.argmax(tot); best[i] = tot[k]; bestT[i] = tref + (k + 0.5) / B / f  # dip centred at bin k (circular correlation shift)
    return best, bestT

def fit_ephem(d, label):
    sub = group(d); t = d.t.values; w = 1 / d.e.values ** 2; tc = np.sum(w * t) / np.sum(w); span = t.max() - t.min()
    step = 0.1 / span; res = {}
    for k, fc in (("0", C["f0"]), ("-1", C["f0"] - 1.0014), ("+1", C["f0"] + 1.0014)):
        fr = np.arange(fc - 0.012, fc + 0.012, step); pw, bt = grid_power(sub, fr, tc); res[k] = (fr, pw, bt)
    fr, pw, bt = res["0"]; i = np.argmax(pw); fb, Tb = fr[i], bt[i]
    excl = np.abs(fr - fb) < 0.5 / span; j = np.argmax(np.where(excl, -1, pw))
    alias_main = dict(f_alias=float(fr[j]), dchi2_alias=float(pw[i] - pw[j]))
    alias_day = {k: float(pw[i] - res[k][1].max()) for k in ("-1", "+1")}
    # move T to cycle nearest the weighted centre
    Tb = Tb + np.round((tc - Tb) * fb) / fb
    p0 = [fb, Tb] + ([SIGW0] if C["kind"] == "eclipse" else [])
    sc = [1e-6, 1e-4] + ([1e-4] if C["kind"] == "eclipse" else [])
    ls = least_squares(resid, p0, args=(sub,), x_scale=sc, diff_step=[1e-10, 1e-11] + ([1e-3] if C["kind"] == "eclipse" else []))
    chi2 = np.sum(ls.fun ** 2); dof = len(ls.fun) - len(ls.x) - sum(design(g[0][:3], 1, 0, SIGW0).shape[1] for _, g in sub)
    cov = np.linalg.inv(ls.jac.T @ ls.jac) * max(chi2 / dof, 1.0)
    f, T0 = ls.x[0], ls.x[1]; sigw = ls.x[2] if C["kind"] == "eclipse" else SIGW0
    A_ = amps(sub, f, T0, sigw)
    P_(f"  [{label}] grid f {fb:.6f}; fit f {f:.7f} +- {np.sqrt(cov[0,0]):.2g}, T0 {T0:.6f} +- {np.sqrt(cov[1,1])*1440:.3f} min, chi2r {chi2/dof:.3f}; "
       f"next alias f {alias_main['f_alias']:.6f} dchi2 {alias_main['dchi2_alias']:.1f}; daily aliases dchi2 {alias_day}" + (f"; sigw {sigw*1440:.2f} min" if C['kind']=='eclipse' else ""))
    return dict(f=f, T0=T0, cov=cov[:2, :2], sigw=sigw, chi2r=chi2 / dof, amps=A_, span=span, tmin=t.min(), tmax=t.max(), **alias_main, dchi2_day_m1=alias_day["-1"], dchi2_day_p1=alias_day["+1"])

def predict(E, t):
    """predicted reference time (max light / mid-eclipse) of the cycle nearest t, and its sigma (d)"""
    n = np.round((t - E["T0"]) * E["f"]); P = 1 / E["f"]; c = E["cov"]
    sP = np.sqrt(c[0, 0]) / E["f"] ** 2; cTP = -c[0, 1] / E["f"] ** 2
    sT = np.sqrt(c[1, 1] + n ** 2 * sP ** 2 + 2 * n * cTP); return E["T0"] + n * P, sT, n

def stat_Z(sub, f, Tref, sigw):
    num = 0.0; den = 0.0
    for ds, (t, y, e) in sub:
        X = design(t, f, Tref, sigw)[:, :2] if C["kind"] == "sine" else design(t, f, Tref, sigw)
        Xw = X / e[:, None]; c, *_ = np.linalg.lstsq(Xw, y / e, rcond=None); cov = np.linalg.inv(Xw.T @ Xw)
        a, s = c[1], np.sqrt(cov[1, 1]); num += a / s ** 2; den += 1 / s ** 2
    return num / np.sqrt(den), num / den, 1 / np.sqrt(den)

def free_phase(sub, f, Tpred, sigw, halfwin, nstep=1201):
    """scan a time shift; return best shift (d), 1-sigma (d), and the delta-chi2 curve"""
    sh = np.linspace(-halfwin, halfwin, nstep); chi = np.zeros(len(sh))
    for i, s in enumerate(sh):
        tot = 0.0
        for ds, (t, y, e) in sub:
            X = design(t, f, Tpred + s, sigw)[:, :2] if C["kind"] == "sine" else design(t, f, Tpred + s, sigw)
            Xw = X / e[:, None]; c, *_ = np.linalg.lstsq(Xw, y / e, rcond=None)
            if c[1] < 0: c = np.linalg.lstsq(Xw[:, [0] + list(range(2, Xw.shape[1]))], y / e, rcond=None)[0]; tot += np.sum((y / e - Xw[:, [0] + list(range(2, Xw.shape[1]))] @ c) ** 2)
            else: tot += np.sum((y / e - Xw @ c) ** 2)
        chi[i] = tot
    k = np.argmin(chi); ok = chi <= chi[k] + 1.0
    # contiguous 1-sigma interval around the minimum
    lo = k
    while lo > 0 and ok[lo - 1]: lo -= 1
    hi = k
    while hi < len(sh) - 1 and ok[hi + 1]: hi += 1
    sig = max((sh[hi] - sh[lo]) / 2, sh[1] - sh[0])
    return sh[k], sig, chi

def test_block(dtr, dho, label):
    E = fit_ephem(dtr, f"train w/o {label}")
    sub = group(dho); t = dho.t.values; tc = np.median(t); f, sigw = E["f"], E["sigw"]
    Tp, sT, n = predict(E, tc); P = 1 / f
    # gap in cycles from nearest training data
    tt = dtr.t.values; gap_cyc = np.min(np.abs(tt - tc)) * f
    Zobs, Aobs, sA = stat_Z(sub, f, Tp, sigw)
    # nulls
    Zsh = np.zeros(NTRIAL); Zph = np.zeros(NTRIAL); Zfr = np.zeros(NTRIAL)
    for k in range(NTRIAL):
        s2 = [(ds, (tt_, yy[p_], ee[p_])) for ds, (tt_, yy, ee) in sub for p_ in [rng.permutation(len(yy))]]
        Zsh[k] = stat_Z(s2, f, Tp, sigw)[0]
        Zph[k] = stat_Z(sub, f, Tp + rng.uniform(0, P), sigw)[0]
        while True:
            fr_ = rng.uniform(f - 3, f + 3)
            if all(abs(fr_ - x) > 0.05 for x in (f, f - 1, f + 1, f - 2, f + 2, f - 1.0027, f + 1.0027)): break
        Zfr[k] = stat_Z(sub, fr_, Tp + rng.uniform(0, 1 / fr_), sigw)[0]
    p = lambda Z: (1 + np.sum(Z >= Zobs)) / (NTRIAL + 1)
    halfwin = min(0.5 * P, max(5 * sT, (20 if C["kind"] == "eclipse" else 0.25 * P * 1440) / 1440))
    if C["kind"] == "sine": halfwin = 0.5 * P
    dsh, sobs, _ = free_phase(sub, f, Tp, sigw, halfwin)
    sboot = np.nan
    if C["kind"] == "eclipse":  # bootstrap the free shift (Gaussian template is only an approximation to the eclipse shape)
        nb = 200 if len(dho) < 5000 else 40; bs = []
        for _ in range(nb):
            s2 = [(ds, (tt_[p_], yy[p_], ee[p_])) for ds, (tt_, yy, ee) in sub for p_ in [rng.integers(0, len(yy), len(yy))]]
            bs.append(free_phase(s2, f, Tp + dsh, sigw, 1.5 / 1440, 301)[0])
        sboot = 1.4826 * np.median(np.abs(np.array(bs) - np.median(bs))); sobs = max(sobs, sboot)
    stot = np.hypot(sobs, sT); off_sig = abs(dsh) / stot
    # expected Z from training amplitudes
    num = 0; den = 0
    for ds, (t_, y_, e_) in sub:
        key = ds if ds in E["amps"] else next((k for k in E["amps"] if k.split("_")[0] == ds.split("_")[0]), None)
        if key is None: continue
        X = design(t_, f, Tp, sigw); Xw = X / e_[:, None]; s = np.sqrt(np.linalg.inv(Xw.T @ Xw)[1, 1]); num += E["amps"][key][0] / s ** 2; den += 1 / s ** 2
    Zexp = num / np.sqrt(den) if den else np.nan
    pmain = max(p(Zsh), p(Zfr))
    verdict = ("PASS" if (pmain < 0.01 and off_sig < 3) else ("UNDERPOWERED" if Zexp < 3 and pmain >= 0.01 else "FAIL"))
    r = dict(block=label, n=len(dho), bjd_mid=round(tc, 2), cycles_from_train=int(round(gap_cyc)), n_cycles_from_T0=int(n),
             f_train=f, P_train_d=1 / f, sigma_P_train_d=np.sqrt(E["cov"][0, 0]) / f ** 2, T0_train=E["T0"], sigma_T0_train_min=np.sqrt(E["cov"][1, 1]) * 1440,
             pred_sigma_min=sT * 1440, pred_sigma_cycles=sT * f, Z_obs=Zobs, amp_at_pred=Aobs, amp_err=sA, Z_expected=Zexp,
             p_shuffle=p(Zsh), p_randfreq=p(Zfr), p_randphase=p(Zph), free_shift_min=dsh * 1440, free_shift_err_min=sobs * 1440, free_shift_boot_err_min=sboot * 1440,
             offset_sigma=off_sig, offset_cycles=dsh * f, train_next_alias_f=E["f_alias"], train_dchi2_next_alias=E["dchi2_alias"],
             train_dchi2_daily_m1=E["dchi2_day_m1"], train_dchi2_daily_p1=E["dchi2_day_p1"], verdict=verdict)
    P_(f"  HOLDOUT {label}: n {len(dho)}, Z {Zobs:.2f} (exp {Zexp:.1f}), p_shuf {r['p_shuffle']:.4f} p_rfreq {r['p_randfreq']:.4f} p_rphase {r['p_randphase']:.4f}; "
       f"pred sigma {sT*1440:.2f} min ({sT*f:.4f} cyc); free shift {dsh*1440:+.2f} +- {sobs*1440:.2f} min -> {off_sig:.2f} sigma; {verdict}")
    return r

if __name__ == "__main__":
    if os.environ.get("DRY"): sys.exit(0)
    cnt = df.blk.value_counts(); blocks = sorted(b for b in df.blk.unique() if cnt[b] >= 30)
    P_(f"  blocks with < 30 points kept in training only (not tested): {sorted(set(df.blk) - set(blocks))}"); fold_file = f"{OUT}/{TAG}_folds.csv"
    done = pd.read_csv(fold_file) if os.path.exists(fold_file) else pd.DataFrame()
    for b in blocks:
        if len(done) and b in set(done.block): P_(f"  skip {b} (done)"); continue
        r = test_block(df[df.blk != b], df[df.blk == b], b)
        done = pd.concat([done, pd.DataFrame([r])], ignore_index=True); done.to_csv(fold_file, index=False)
    # final combined ephemeris
    E = fit_ephem(df, "ALL")
    f, T0, cov = E["f"], E["T0"], E["cov"]; P = 1 / f; sP = np.sqrt(cov[0, 0]) / f ** 2; sT0 = np.sqrt(cov[1, 1]); cTP = -cov[0, 1] / f ** 2
    t1, t2 = Time("2026-11-01T00:00:00", scale="utc").tdb.jd, Time("2027-04-01T00:00:00", scale="utc").tdb.jd
    n = np.arange(np.ceil((t1 - T0) / P), np.floor((t2 - T0) / P) + 1); tp = T0 + n * P; st = np.sqrt(sT0 ** 2 + n ** 2 * sP ** 2 + 2 * n * cTP)
    ev = "mid_eclipse" if C["kind"] == "eclipse" else "max_light_fundamental"
    pr = pd.DataFrame(dict(cycle=n.astype(int), bjd_tdb=np.round(tp, 6), sigma_min=np.round(st * 1440, 3),
                           utc_iso=Time(tp, format="jd", scale="tdb").utc.isot, event=ev))
    with open(f"{OUT}/{TAG}_predictions.csv", "w") as fh:
        fh.write(f"# Gaia DR3 {GID} ({C['name']}); predicted {ev} times 2026-11-01 to 2027-03-31; ephemeris BJD_TDB = {T0:.6f} + {P:.9f} E "
                 f"(sigma T0 {sT0*1440:.3f} min, sigma P {sP:.2g} d, cov(T0,P) {cTP:.3g} d^2); utc_iso is geocentric-barycentric uncorrected label only (BJD is authoritative)\n")
        pr.to_csv(fh, index=False)
    summ = dict(gaia=GID, name=C["name"], kind=C["kind"], T0_bjd_tdb=T0, sigma_T0_d=sT0, P_d=P, sigma_P_d=sP, cov_T0_P=cTP, f_cd=f,
                chi2r=E["chi2r"], next_alias_f=E["f_alias"], dchi2_next_alias=E["dchi2_alias"], dchi2_daily=[E["dchi2_day_m1"], E["dchi2_day_p1"]],
                amps={k: [float(a), float(s)] for k, (a, s) in E["amps"].items()}, sigw_min=E["sigw"] * 1440, n_predictions=len(pr),
                pred_sigma_min_range=[float(st.min() * 1440), float(st.max() * 1440)])
    json.dump(summ, open(f"{OUT}/{TAG}_summary.json", "w"), indent=1, default=float)
    P_(json.dumps(summ, default=float)); P_(pr.head(3).to_string()); P_(pr.tail(3).to_string())
