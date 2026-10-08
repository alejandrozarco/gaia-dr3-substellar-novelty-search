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
pZ = f"{D}/ztf_{GID}.csv"
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
                fl = np.nansum(F[:, ap], axis=1) - np.nanmedian(F[:, ring], axis=1) * ap.sum(); ok = np.isfinite(fl) & (fl > 0)
                t, fl = t[ok], fl[ok]; er = np.full(len(fl), np.nan)
        tr = tess_detrend(t, fl); y = fl / tr - 1
        if not np.all(np.isfinite(er)): r_ = y - median_filter(y, 31, mode="nearest"); er = np.full(len(y), 1.4826 * np.median(np.abs(r_ - np.median(r_)))) * tr
        e = er / tr; k = robust_clip(y, False)
        for tt, yy, ee in zip(t[k], y[k], e[k]): rows.append((tt, yy, ee, f"TESS_S{sec}", "TESS_" + "+".join(f"S{s}" for s in grp)))
