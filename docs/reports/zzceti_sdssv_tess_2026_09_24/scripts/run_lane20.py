# Lane 1c (20-s): SDSS-V DR20 strip white dwarfs (same 912-star selection as lane 1) x all TESS SPOC 20-s light curves.
# Purpose: periods below the 120-s Nyquist limit (240 s; hot DAVs, short DBV modes) and a second look at every 20-s sector.
# Per light curve: PDCSAP, QUALITY == 0, normalise, 5-sigma clip, Lomb-Scargle amplitude spectrum 20-2159 c/d (df 0.001);
# S/N = peak amplitude / mean amplitude; Baluev FAP of the top peak; top 5 peaks overall and top 3 above 359 c/d.
# Downloads run 4 at a time in bounded chunks; a file is deleted after analysis unless its top peak has S/N >= 5 (disk limit).
# Output lane20_lc_results.jsonl; holes are recorded, never dropped.
import json, os, subprocess, time, numpy as np
from concurrent.futures import ThreadPoolExecutor
from astropy.io import fits
from astropy.timeseries import LombScargle
J = json.load(open("tess_coverage.json")); cov = J["coverage"]
tgt = {str(int(float(r["tic_v8_id"]))): r for r in J["targets"]}
todo = [(tic, x["sector"], x["obs_id"] + "-lc.fits") for tic, obs in cov.items() for x in obs if x["exptime"] <= 20]
done = {json.loads(l)["file"] for l in open("lane20_lc_results.jsonl")} if os.path.exists("lane20_lc_results.jsonl") else set()
todo = [x for x in todo if x[2] not in done]
if os.environ.get("LANE20_TEST"): todo = [x for x in todo if f"{x[0]}:{x[1]}" in os.environ["LANE20_TEST"].split(",")]
print("20-s light curves to fetch:", len(todo), flush=True)
os.makedirs("lc20", exist_ok=True)
def fetch(item):
    tic, sec, fn = item; path = f"lc20/{fn}"
    if os.path.exists(path) and os.path.getsize(path) > 500000: return path
    for k in range(3):
        subprocess.run(["curl", "-sL", "-m", "300", "--speed-limit", "30000", "--speed-time", "30", "-o", path, f"https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:TESS/product/{fn}"])
        if os.path.exists(path) and os.path.getsize(path) > 500000: return path
        time.sleep(5)
    if os.path.exists(path): os.remove(path)
    return None
def top_peaks(fr, amp, meanamp, k, fmin=0):
    sel = fr >= fmin; f2, a2 = fr[sel], amp[sel]; order = np.argsort(a2)[::-1]; out = []
    for i in order:
        if all(abs(f2[i] - q[0]) > 0.05 for q in out): out.append((float(f2[i]), float(a2[i] * 1e3), float(a2[i] / meanamp)))
        if len(out) == k: break
    return out
def analyse(item, path):
    tic, sec, fn = item; row = dict(tic=tic, sector=sec, file=fn, gaia=tgt[tic]["gaia_dr3_source_id"], lane=tgt[tic]["lane"], G=float(tgt[tic]["g_mag"]), teff=tgt[tic]["teff"])
    if path is None: row["status"] = "HOLE_DOWNLOAD"; return row
    try:
        h = fits.open(path); d = h[1].data; hd = h[1].header
        m = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]) & np.isfinite(d["TIME"])
        t = d["TIME"][m]; f = d["PDCSAP_FLUX"][m]
        if len(t) < 10000: row["status"] = f"FEW_POINTS_{len(t)}"; return row
        y = f / np.median(f) - 1; mad = 1.4826 * np.median(np.abs(y - np.median(y))); ok = np.abs(y - np.median(y)) < 5 * mad; t, y = t[ok], y[ok]
        fr = np.arange(20, 2159, 0.001); P = LombScargle(t, y, normalization="psd").power(fr, method="fast")
        amp = np.sqrt(4 * P / len(t)); meanamp = np.mean(amp)
        peaks = top_peaks(fr, amp, meanamp, 5); hi = top_peaks(fr, amp, meanamp, 3, fmin=359)
        pn = LombScargle(t, y).power(np.array([peaks[0][0]]))[0]
        fap = float(LombScargle(t, y).false_alarm_probability(pn, minimum_frequency=20, maximum_frequency=2159, method="baluev"))
        row.update(status="OK", n=int(len(t)), span=float(t.max() - t.min()), crowdsap=hd.get("CROWDSAP"), flfrcsap=hd.get("FLFRCSAP"), rms_ppt=float(np.std(y) * 1e3),
                   meanamp_ppt=float(meanamp * 1e3), peaks=peaks, peaks_above_359=hi, fap_top=fap, camera=h[0].header.get("CAMERA"), ccd=h[0].header.get("CCD"))
    except Exception as e:
        row["status"] = f"HOLE_READ {type(e).__name__}"
    return row
with ThreadPoolExecutor(max_workers=4) as ex, open(os.environ.get("LANE20_OUT", "lane20_lc_results.jsonl"), "a") as out:
    for c0 in range(0, len(todo), 4):
        chunk = todo[c0:c0 + 4]
        for item, path in zip(chunk, ex.map(fetch, chunk)):
            row = analyse(item, path); out.write(json.dumps(row) + "\n"); out.flush()
            if path and os.path.exists(path) and not (row.get("status") == "OK" and row["peaks"][0][2] >= 5): os.remove(path)
        if c0 % 100 == 0: print(f"{time.strftime('%H:%M:%S')} {c0}/{len(todo)} {row['status']}", flush=True)
print("LANE20_DONE", flush=True)
