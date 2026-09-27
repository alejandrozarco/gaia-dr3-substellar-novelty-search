"""UHE line screen of hot LAMOST DR11 white-dwarf spectra (V/162/dr11wdl; Teff > 45 kK or class with O; snr_g > 8; best spectrum per Gaia source).
Spectra streamed from www.lamost.org (DR11 v1.1, else v2.0); vacuum wavelengths; ANDMASK != 0 dropped. EWs at 4495, 4941, 5280, 5665 A and
controls 5100, 5480, 5740 A (+-12 A; side bands 3-30 A beyond)."""
import os, sys, io, gzip, time, requests, threading, numpy as np, pandas as pd, warnings
from concurrent.futures import ThreadPoolExecutor
from astropy.io import fits
warnings.filterwarnings("ignore"); X = os.path.dirname(os.path.abspath(__file__)); POS = [4495, 4941, 5280, 5665]; CTRL = [5100, 5480, 5740]
def ew(w, f, iv, l, hw=12):
    m = (((w > l - hw - 30) & (w < l - hw - 3)) | ((w > l + hw + 3) & (w < l + hw + 30))) & (iv > 0) & np.isfinite(f); k = (np.abs(w - l) < hw) & (iv > 0) & np.isfinite(f)
    if m.sum() < 8 or k.sum() < 8: return np.nan, np.nan
    p = np.polyfit(w[m], f[m], 1, w=np.sqrt(iv[m])); c = np.polyval(p, w); dw = np.gradient(w)[k]
    if np.median(c[k]) <= 0: return np.nan, np.nan
    return float(np.sum((1 - f[k] / c[k]) * dw)), float(np.sqrt(np.sum((np.sqrt(1 / iv[k]) / c[k] * dw) ** 2)))
tl = threading.local()
def one(r):
    if not hasattr(tl, "s"): tl.s = requests.Session()
    raw = None
    for k in range(3):
        try:
            for rel in ("v1.1", "v2.0"):
                q = tl.s.get(f"https://www.lamost.org/dr11/{rel}/spectrum/fits/{r.ObsID}", timeout=90)
                if q.status_code == 200 and len(q.content) > 5000: raw = q.content; break
            if raw: break
        except Exception: pass
        time.sleep(2 + 3 * k)
    d = dict(ObsID=r.ObsID, GaiaDR3=r.GaiaDR3, wdClass=r.wdClass, Teff=r.Teff, snrg=r.snrg, ra=r.RAJ2000, dec=r.DEJ2000)
    if raw is None: d["status"] = "HOLE"; return d
    h = fits.open(io.BytesIO(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)); s = h[1].data[0]
    w = np.array(s["WAVELENGTH"], float); f = np.array(s["FLUX"], float); iv = np.array(s["IVAR"], float) * (s["ANDMASK"] == 0)
    for l in POS + CTRL: e, er = ew(w, f, iv, l); d[f"e{l}"] = e; d[f"s{l}"] = er
    d["status"] = "ok"; return d
S = pd.read_csv(f"{X}/sample.csv", dtype={"ObsID": str, "GaiaDR3": str})
with ThreadPoolExecutor(4) as ex: rows = list(ex.map(one, S.itertuples()))
R = pd.DataFrame(rows); R.to_csv(f"{X}/lamost_uhe.csv", index=False); print("done", len(R), R.status.value_counts().to_dict())
