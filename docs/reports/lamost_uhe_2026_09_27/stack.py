"""Median stack of normalised LAMOST spectra (5150-5800 A) of the screened hot WDs, to test whether the 5280 A window is biased for all stars."""
import os, io, gzip, time, requests, threading, numpy as np, pandas as pd, warnings
from concurrent.futures import ThreadPoolExecutor
from astropy.io import fits; from scipy.ndimage import median_filter
warnings.filterwarnings("ignore"); X = os.path.dirname(os.path.abspath(__file__))
R = pd.read_csv(f"{X}/lamost_ranked.csv", dtype={"ObsID": str, "GaiaDR3": str}); R = R[R.status == "ok"]
G = np.arange(5150, 5800, 1.0); tl = threading.local()
def one(r):
    if not hasattr(tl, "s"): tl.s = requests.Session()
    for k in range(3):
        try:
            for rel in ("v1.1", "v2.0"):
                q = tl.s.get(f"https://www.lamost.org/dr11/{rel}/spectrum/fits/{r.ObsID}", timeout=90)
                if q.status_code == 200 and len(q.content) > 5000:
                    raw = q.content; d = fits.open(io.BytesIO(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw))[1].data[0]
                    w = np.array(d["WAVELENGTH"], float); f = np.array(d["FLUX"], float); ok = (np.array(d["IVAR"]) > 0) & (d["ANDMASK"] == 0)
                    w, f = w[ok], f[ok]; k2 = (w > 4900) & (w < 6100)
                    if k2.sum() < 200: return r.ObsID, None
                    c = median_filter(f[k2], 301, mode="nearest"); return r.ObsID, np.interp(G, w[k2], f[k2] / c, left=np.nan, right=np.nan)
        except Exception: pass
        time.sleep(2 + 3 * k)
    return r.ObsID, None
with ThreadPoolExecutor(4) as ex: out = dict(ex.map(one, R.itertuples()))
ids = [o for o in R.ObsID if out.get(o) is not None]; A = np.array([out[o] for o in ids])
np.save(f"{X}/stack_flux.npy", A); pd.Series(ids).to_csv(f"{X}/stack_ids.csv", index=False); print("stacked", len(ids), "holes", len(R) - len(ids))
