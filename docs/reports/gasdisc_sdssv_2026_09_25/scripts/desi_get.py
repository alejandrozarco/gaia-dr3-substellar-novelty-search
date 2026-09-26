"""Retrieve DESI DR1 spectra near a position via SPARCL and plot the Ca II triplet and H-alpha: python desi_get.py ra dec label"""
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sparcl.client import SparclClient
from scipy.ndimage import gaussian_filter1d
ra, dec, lab = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]; d = 3 / 3600
cl = SparclClient()
f = cl.find(outfields=["sparcl_id", "targetid", "ra", "dec", "data_release", "spectype", "redshift"], constraints={"ra": [ra - d / np.cos(np.radians(dec)), ra + d / np.cos(np.radians(dec))], "dec": [dec - d, dec + d]}, limit=20)
print([ (r["targetid"], r["data_release"], r["spectype"], round(r["redshift"] * 3e5, 1)) for r in f.records])
ids = [r["sparcl_id"] for r in f.records]
if not ids: sys.exit("no DESI spectra")
recs = cl.retrieve(uuid_list=ids, include=["flux", "ivar", "wavelength", "data_release", "targetid"]).records
C = 299792.458; CAT = [8500.35, 8544.44, 8664.52]
fig, ax = plt.subplots(1, 4, figsize=(15, 3.5))
for k, r in enumerate(recs):
    w = np.array(r["wavelength"]); fl = np.array(r["flux"]); iv = np.array(r["ivar"])
    np.savez(f"desi_{lab}_{k}.npz", w=w, f=fl, iv=iv)
    for j, l in enumerate(CAT + [6562.8]):
        m = np.abs(w / l - 1) * C < 2500; mc = m & ~(np.abs(w / l - 1) * C < 1000) & (iv > 0)
        if mc.sum() < 10: continue
        p = np.polyfit(w[mc], fl[mc], 1); y = fl[m] / np.polyval(p, w[m])
        ax[j].plot((w[m] / l - 1) * C, gaussian_filter1d(y, 2) + 0.3 * k, lw=0.8, label=f"{r['data_release']} {r['targetid']}")
for j, a in enumerate(ax): a.axvline(0, color="grey", lw=0.5); a.set_title(["Ca 8498 (air)", "Ca 8542", "Ca 8662", "H-alpha (air)"][j] + " DESI, km/s (vacuum wave)", fontsize=8)
ax[0].legend(fontsize=6); plt.tight_layout(); plt.savefig(f"desi_{lab}.png", dpi=85); print("saved")
