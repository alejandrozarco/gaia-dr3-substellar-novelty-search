"""DESI DR1 hot white dwarfs (DR1 WD catalogue: specType DO/DAO/DOA/DAB/... or TEFF > 50 kK; S/N_B > 8; WD classes only), spectra from SPARCL
(retrieve_by_specid, DESI-DR1). EW at the UHE positions of Reindl et al. 2021 (4495, 4941, 5243, 5280, 5665, 6060 A; +-12 A; side bands 3-30 A beyond)
and at control positions 5100, 5480, 5740 A. Multiple spectra per target: each measured, and the highest-S/N one kept."""
import os, sys, numpy as np, pandas as pd, time
from sparcl.client import SparclClient
X = os.path.dirname(os.path.abspath(__file__)); POS = [4495, 4941, 5243, 5280, 5665, 6060]; CTRL = [5100, 5480, 5740]
def ew(w, f, iv, l, hw=12):
    m = (((w > l - hw - 30) & (w < l - hw - 3)) | ((w > l + hw + 3) & (w < l + hw + 30))) & (iv > 0) & np.isfinite(f); k = (np.abs(w - l) < hw) & (iv > 0) & np.isfinite(f)
    if m.sum() < 8 or k.sum() < 8: return np.nan, np.nan
    p = np.polyfit(w[m], f[m], 1, w=np.sqrt(iv[m])); c = np.polyval(p, w); dw = np.gradient(w)[k]
    if np.median(c[k]) <= 0: return np.nan, np.nan
    return float(np.sum((1 - f[k] / c[k]) * dw)), float(np.sqrt(np.sum((np.sqrt(1 / iv[k]) / c[k] * dw) ** 2)))
S = pd.read_csv(f"{X}/sample.csv", dtype={"DESIID": str, "edr3id": str}); S = S[S.DESIID.notna() & ~S.specType.isin(["STAR", "EXGAL", "CV", "WD+MS", "JUNK"])]
print(len(S), "targets", flush=True)
c = SparclClient(); rows = []; ids = S.DESIID.astype("int64").tolist()
for i in range(0, len(ids), 200):
    chunk = ids[i:i + 200]
    for k in range(5):
        try:
            r = c.retrieve_by_specid(chunk, include=["specid", "flux", "ivar", "wavelength", "mask"], dataset_list=["DESI-DR1"], limit=2000); break
        except Exception as e:
            time.sleep(20)
    else:
        print("HOLE batch", i, flush=True); continue
    for rec in r.records:
        w = np.asarray(rec.wavelength); f = np.asarray(rec.flux); iv = np.asarray(rec.ivar) * (np.asarray(rec.mask) == 0)
        d = dict(DESIID=str(rec.specid), snr=float(np.nanmedian(f[(w > 5000) & (w < 5500)] * np.sqrt(iv[(w > 5000) & (w < 5500)]))))
        for l in POS + CTRL:
            e, s = ew(w, f, iv, l); d[f"e{l}"] = e; d[f"s{l}"] = s
        rows.append(d)
    print(i + len(chunk), "retrieved;", len(rows), "spectra", flush=True)
R = pd.DataFrame(rows).sort_values("snr", ascending=False).drop_duplicates("DESIID").merge(S, on="DESIID")
R.to_csv(f"{X}/desi_uhe.csv", index=False); print("done", len(R))
