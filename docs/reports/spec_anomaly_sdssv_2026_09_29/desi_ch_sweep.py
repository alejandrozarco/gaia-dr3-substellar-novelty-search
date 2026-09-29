"""CH G-band index across 4,708 cool (<8000 K) DESI DR1 DA white dwarfs (DESI_CLASS_FINAL.txt, Pwd > 0.8).
Index = 1 - mean flux 4285-4316 A / median continuum (4235-4262, 4322-4332 A); per-target error from ivar.
Spectra with index z > 5 are saved for inspection. Failed batches are listed as holes. Output: desi_ch_sweep.csv."""
import numpy as np, pandas as pd, time, os
from sparcl.client import SparclClient
c = SparclClient(connect_timeout=30, read_timeout=600)
C = pd.read_csv("anomdesi/desi_cool_da.csv"); ids = [int(x) for x in C.DESIID]; out = []; holes = []
def idx(w, f, iv):
    band = (w > 4285) & (w < 4316); cm = ((w > 4235) & (w < 4262)) | ((w > 4322) & (w < 4332)); cont = np.nanmedian(f[cm])
    if not np.isfinite(cont) or cont <= 0: return np.nan, np.nan
    e = 1 / np.sqrt(np.where(iv[band] > 0, iv[band], np.nan)) / cont
    return 1 - np.nanmean(f[band] / cont), np.sqrt(np.nansum(e**2)) / max(np.isfinite(e).sum(), 1)
for k in range(0, len(ids), 150):
    ch = ids[k:k + 150]
    for a in range(3):
        try:
            f = c.find(outfields=["sparcl_id", "targetid"], constraints={"targetid": ch, "data_release": ["DESI-DR1"]}, limit=1000)
            uu = {}; [uu.setdefault(r["targetid"], r["sparcl_id"]) for r in f.records]
            R = c.retrieve(uuid_list=list(uu.values()), include=["targetid", "wavelength", "flux", "ivar"], limit=1000)
            for x in R.records:
                w, fl, iv = np.array(x.wavelength), np.array(x.flux), np.array(x.ivar); i, e = idx(w, fl, iv)
                k2 = (w > 4500) & (w < 5500); sn = float(np.nanmedian(fl[k2] * np.sqrt(iv[k2])))
                z = i / e if e and e > 0 else np.nan
                out.append(dict(targetid=x.targetid, ch=i, e=e, z=z, snr=sn))
                if np.isfinite(z) and z > 5: np.savez(f"anomdesi/desi_ch_{x.targetid}.npz", w=w, f=fl, iv=iv)
            break
        except Exception as ex: time.sleep(20 * (a + 1))
    else: holes.append(k)
    if (k // 150) % 5 == 0: print(k, len(out), flush=True); pd.DataFrame(out).to_csv("anomdesi/desi_ch_sweep.csv", index=False)
O = pd.DataFrame(out).merge(C.rename(columns={"DESIID": "targetid"}), on="targetid", how="left"); O.to_csv("anomdesi/desi_ch_sweep.csv", index=False)
print("ALL-DONE", len(O), "spectra; holes", holes, flush=True)
