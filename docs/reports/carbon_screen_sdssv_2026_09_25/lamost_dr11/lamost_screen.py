"""Carbon screen (carbon_screen2 method) of LAMOST DR11 v1.1 LRS white-dwarf spectra (V/162/dr11wdl; best spectrum per Gaia source,
snr_g > 8). Spectra are streamed from www.lamost.org (DR11 v1.1, falling back to v2.0 when v1.1 returns Not Found; not stored). Wavelengths vacuum, heliocentric; ANDMASK != 0 pixels dropped."""
import sys, os, io, gzip, time, requests, threading, numpy as np, pandas as pd, warnings
from concurrent.futures import ThreadPoolExecutor
from astropy.io import fits
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/hotdq/lane_daq"); import carbon_screen as cs, carbon_screen2 as c2
s = pd.read_csv(sys.argv[1], dtype={"GaiaDR3": str, "ObsID": str}); outf = sys.argv[2]
done = set(pd.read_csv(outf, dtype={"obsid": str}).obsid) if os.path.exists(outf) else set()
todo = [(r.ObsID, r.GaiaDR3, r.wdClass, r.snrg) for r in s.itertuples() if r.ObsID not in done]
tl = threading.local()
def fetch(item):
    if not hasattr(tl, "s"): tl.s = requests.Session()
    for k in range(3):
        try:
            for rel in ("v1.1", "v2.0"):
                r = tl.s.get(f"https://www.lamost.org/dr11/{rel}/spectrum/fits/{item[0]}", timeout=90)
                if r.status_code == 200 and len(r.content) > 5000: return item, r.content
        except Exception: pass
        time.sleep(2 + 3 * k)
    return item, None
fo = open(outf, "a")
if not done: fo.write("obsid,gaia,wdclass,snrg,C,C_v,CI,CI_v,CII,CII_v,HeI,HeI_v,status\n")
n = 0
with ThreadPoolExecutor(6) as ex:
    for (ob, g, wc, sn), raw in ex.map(fetch, todo):
        if raw is None: fo.write(f"{ob},{g},{wc},{sn},,,,,,,,,HOLE\n"); continue
        try:
            h = fits.open(io.BytesIO(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)); d = h[1].data[0]
            w = np.array(d["WAVELENGTH"], float); f = np.array(d["FLUX"], float); iv = np.array(d["IVAR"], float); ok = (iv > 0) & np.isfinite(f) & (d["ANDMASK"] == 0)
            if ok.sum() < 1000: fo.write(f"{ob},{g},{wc},{sn},,,,,,,,,BADSPEC\n"); continue
            p = c2.prep(np.interp(cs.grid, w[ok], f[ok], left=np.nan, right=np.nan), np.interp(cs.grid, w[ok], iv[ok], left=0, right=0))
            if p is None: fo.write(f"{ob},{g},{wc},{sn},,,,,,,,,BADSPEC\n"); continue
            out = {}
            for sp in ("C", "C I", "C II", "He I"):
                cc = c2.contrast(*p, sp); k = int(np.argmax(np.where(c2.INW, cc, -99))); out[sp] = (cc[k], cs.vels[k])
            fo.write(f"{ob},{g},{wc},{sn}," + ",".join(f"{out[sp][0]:.2f},{out[sp][1]:.0f}" for sp in ("C", "C I", "C II", "He I")) + ",ok\n")
        except Exception as e:
            fo.write(f"{ob},{g},{wc},{sn},,,,,,,,,ERROR {type(e).__name__}\n")
        n += 1
        if n % 500 == 0: fo.flush(); print(n, len(todo), flush=True)
fo.close(); print("LAMOST_DONE", n, flush=True)
