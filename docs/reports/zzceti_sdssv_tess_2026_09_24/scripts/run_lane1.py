# Lane 1 (+3): SDSS-V DR20 white dwarfs in the ZZ Ceti strip (SnowWhite DA, Teff 10-13.5 kK, log g 7.3-9.3) and the DBV strip
# (DB classes, Gentile Fusillo+2021 Teff_He 19-36 kK), G < 18, x TESS SPOC 120-s light curves from Cycles 6-8 (Sectors 70+).
# Download (4 parallel curl), then per light curve: PDCSAP, QUALITY == 0, normalise, 5-sigma clip, Lomb-Scargle amplitude
# spectrum 20-359 c/d; significance = highest peak / mean amplitude (S/N) and Baluev FAP; record the top 5 peaks per light curve.
# Output lane1_lc_results.jsonl (one row per light curve). Holes (failed downloads/reads) are recorded, never dropped.
import json, os, subprocess, sys, time, numpy as np
from concurrent.futures import ThreadPoolExecutor
from astropy.io import fits
from astropy.timeseries import LombScargle
J = json.load(open("tess_coverage.json")); cov = J["coverage"]
tgt = {str(int(float(r["tic_v8_id"]))): r for r in J["targets"]}
todo = []
for tic, obs in cov.items():
    have20 = {x["sector"] for x in obs if x["exptime"] <= 20}
    for x in obs:
        if x["exptime"] == 120 and x["sector"] >= 70: todo.append((tic, x["sector"], x["obs_id"] + "_lc.fits"))
print("light curves to fetch:", len(todo), flush=True)
os.makedirs("lc", exist_ok=True)
def fetch(item):
    tic, sec, fn = item; path = f"lc/{fn}"
    if os.path.exists(path) and os.path.getsize(path) > 100000: return path
    for k in range(3):
        subprocess.run(["curl", "-sL", "-m", "300", "-o", path, f"https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:TESS/product/{fn}"])
        if os.path.exists(path) and os.path.getsize(path) > 100000: return path
        time.sleep(5)
    return None
def analyse(item, path):
    tic, sec, fn = item; row = dict(tic=tic, sector=sec, file=fn, gaia=tgt[tic]["gaia_dr3_source_id"], lane=tgt[tic]["lane"], G=float(tgt[tic]["g_mag"]))
    if path is None: row["status"] = "HOLE_DOWNLOAD"; return row
    try:
        h = fits.open(path); d = h[1].data; hd = h[1].header
        m = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]) & np.isfinite(d["TIME"])
        t = d["TIME"][m]; f = d["PDCSAP_FLUX"][m]
        if len(t) < 2000: row["status"] = f"FEW_POINTS_{len(t)}"; return row
        y = f / np.median(f) - 1; mad = 1.4826 * np.median(np.abs(y - np.median(y))); ok = np.abs(y - np.median(y)) < 5 * mad; t, y = t[ok], y[ok]
        fr = np.arange(20, 359, 0.001); ls = LombScargle(t, y, normalization="psd"); P = ls.power(fr, method="fast")
        amp = np.sqrt(4 * P / len(t))                            # sinusoid semi-amplitude spectrum
        meanamp = np.mean(amp); order = np.argsort(amp)[::-1]; peaks = []
        for k in order:
            if all(abs(fr[k] - q[0]) > 0.05 for q in peaks): peaks.append((float(fr[k]), float(amp[k] * 1e3), float(amp[k] / meanamp)))
            if len(peaks) == 5: break
        pn = LombScargle(t, y).power(np.array([peaks[0][0]]))[0]
        fap = float(LombScargle(t, y).false_alarm_probability(pn, minimum_frequency=20, maximum_frequency=359, method="baluev"))
        row.update(status="OK", n=int(len(t)), span=float(t.max() - t.min()), crowdsap=hd.get("CROWDSAP"), flfrcsap=hd.get("FLFRCSAP"), rms_ppt=float(np.std(y) * 1e3),
                   meanamp_ppt=float(meanamp * 1e3), peaks=peaks, fap_top=fap, camera=h[0].header.get("CAMERA"), ccd=h[0].header.get("CCD"))
    except Exception as e:
        row["status"] = f"HOLE_READ {type(e).__name__}"
    return row
done = set()
if os.path.exists("lane1_lc_results.jsonl"):
    done = {json.loads(l)["file"] for l in open("lane1_lc_results.jsonl")}
todo = [x for x in todo if x[2] not in done]
with ThreadPoolExecutor(max_workers=4) as ex, open("lane1_lc_results.jsonl", "a") as out:
    for i, (item, path) in enumerate(zip(todo, ex.map(fetch, todo))):
        row = analyse(item, path); out.write(json.dumps(row) + "\n"); out.flush()
        if i % 50 == 0: print(f"{time.strftime('%H:%M:%S')} {i}/{len(todo)} {row['status']}", flush=True)
print("LANE1_DONE", flush=True)
