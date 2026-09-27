"""TESS 2-min (SPOC PDCSAP) periodogram sweep of GF21 white dwarfs observed in sectors 70-106. SEL=hot (default): TeffH > 12 kK and G < 17.5; SEL=rest: the complement. dip_sigma: depth of the lowest ~30-min median bin in units of the bin scatter (eclipse indicator).
Sample: 2-min target lists S70-S106 x Gentile Fusillo+2021 (Pwd > 0.75, 10" XMatch, then < 2" after propagating GF21 positions to 2000);
subset TeffH > 12 kK and G < 17.5 (wd_2min_S70_S106.csv). Light curves: MAST bulk-download URLs (tesscurl_sector_N_lc.sh), streamed,
analysed and deleted. Per light curve: QUALITY == 0, finite PDCSAP, 5-sigma clip about the median; Lomb-Scargle 0.2-72 c/d (grid 0.1/T);
three highest peaks (separated by > 3/T) with Baluev FAP and semi-amplitude; CROWDSAP; power of a 1-day-median-detrended copy at the top
frequency (tests for slow systematics). Output appended to sweep.csv (resumable). Usage: python stream_ls.py [nthreads]"""
import os, sys, re, glob, time, subprocess, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from astropy.io import fits; from astropy.timeseries import LombScargle
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); TMP = os.path.join(H, "lc_tmp"); os.makedirs(TMP, exist_ok=True)
OUT = os.path.join(H, "sweep.csv" if os.environ.get("SEL", "hot") == "hot" else "sweep_rest.csv")
W = pd.read_csv(os.path.join(H, "wd_2min_S70_S106.csv"), dtype={"GaiaEDR3": str})
SEL = os.environ.get("SEL", "hot")
W = W[(W.TeffH > 12000) & (W.Gmag < 17.5)] if SEL == "hot" else W[~((W.TeffH > 12000) & (W.Gmag < 17.5))]
URL = {}
for f in glob.glob(os.path.join(H, "curl", "tesscurl_sector_*_lc.sh")):
    for l in open(f):
        m = re.search(r"(https://\S+s(\d{4})-(\d{16})-\d{4}-s_lc\.fits)", l)
        if m: URL[(int(m.group(2)), int(m.group(3)))] = m.group(1)
jobs = [(int(r.TICID), int(s), r.GaiaEDR3) for _, r in W.iterrows() for s in r.sectors.split()]
done = set()
if os.path.exists(OUT):
    d = pd.read_csv(OUT); done = set(zip(d.tic, d.sector))
jobs = [j for j in jobs if (j[0], j[1]) not in done and (j[1], j[0]) in URL][:int(os.environ.get("LIMIT", "10000000"))]
print(len(jobs), "light curves to process;", sum((j[1], j[0]) not in URL for j in [(int(r.TICID), int(s), r.GaiaEDR3) for _, r in W.iterrows() for s in r.sectors.split()]), "without a URL", flush=True)
def fetch(j):
    tic, sec, gid = j; p = os.path.join(TMP, f"{tic}_{sec}.fits")
    for k in range(3):
        r = subprocess.run(["curl", "-s", "-f", "-L", "-m", "300", "-o", p, URL[(sec, tic)]])
        if r.returncode == 0 and os.path.getsize(p) > 10000: return j, p
        time.sleep(5)
    return j, None
def analyse(j, p):
    tic, sec, gid = j; row = dict(tic=tic, sector=sec, gaia=gid)
    try:
        h = fits.open(p); d = h[1].data; row["crowdsap"] = h[1].header.get("CROWDSAP"); q = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]) & np.isfinite(d["TIME"])
        t = d["TIME"][q]; f = d["PDCSAP_FLUX"][q]; y = f / np.nanmedian(f) - 1; s = 1.4826 * np.median(np.abs(y)); k = np.abs(y) < 5 * s; t, y = t[k], y[k]
        row.update(n=len(t), rms=round(float(np.std(y)), 4))
        if len(t) < 500: row["status"] = "short"; return row
        T = t.max() - t.min(); fr = np.arange(0.2, 72, 0.1 / T); ls = LombScargle(t, y); pw = ls.power(fr, method="fast")
        idx = []; o = np.argsort(pw)[::-1]
        for i in o:
            if all(abs(fr[i] - fr[k2]) > 3 / T for k2 in idx): idx.append(i)
            if len(idx) == 3: break
        for n, i in enumerate(idx, 1):
            X = np.vstack([np.sin(2 * np.pi * fr[i] * t), np.cos(2 * np.pi * fr[i] * t), np.ones_like(t)]).T; c = np.linalg.lstsq(X, y, rcond=None)[0]
            row.update({f"f{n}": round(float(fr[i]), 5), f"pow{n}": round(float(pw[i]), 5), f"fap{n}": float(f"{ls.false_alarm_probability(pw[i], minimum_frequency=0.2, maximum_frequency=72, method='baluev'):.2g}"), f"amp{n}": round(float(np.hypot(c[0], c[1])), 5)})
        from scipy.ndimage import median_filter
        w = max(int(1.0 / np.median(np.diff(t))) | 1, 3); yd = y - median_filter(y, w, mode="nearest"); row["pow1_detrended"] = round(float(LombScargle(t, yd).power(np.array([row["f1"]]))[0]), 5)
        nb = max(len(t) // 15, 8); tb = np.array_split(np.argsort(t), nb); bm = np.array([np.median(y[i]) for i in tb]); bs = np.std(bm)
        row["dip_sigma"] = round(float((np.median(bm) - bm.min()) / bs), 2) if bs > 0 else 0.0; row["status"] = "ok"
    except Exception as ex: row["status"] = f"ERR {ex}"[:60]
    return row
nth = int(sys.argv[1]) if len(sys.argv) > 1 else 4; buf = []; t0 = time.time()
with ThreadPoolExecutor(nth) as ex:
    for n, (j, p) in enumerate(ex.map(fetch, jobs), 1):
        row = analyse(j, p) if p else dict(tic=j[0], sector=j[1], gaia=j[2], status="DOWNLOAD_FAILED")
        buf.append(row)
        if p and os.path.exists(p): os.remove(p)
        if len(buf) >= 25 or n == len(jobs):
            pd.DataFrame(buf).to_csv(OUT, mode="a", header=not os.path.exists(OUT), index=False); buf = []
            print(n, "done", round(time.time() - t0), "s", flush=True)
