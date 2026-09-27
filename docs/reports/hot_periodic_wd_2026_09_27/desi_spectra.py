import numpy as np
from sparcl.client import SparclClient
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import median_filter
c = SparclClient(connect_timeout=30, read_timeout=300)
T = {"3842377248804727168": (139.45087, 0.17820), "3230486971974872192": (69.63652, 0.52134)}
fig, ax = plt.subplots(len(T), 1, figsize=(13, 3.2 * len(T)))
for i, (gid, (ra, dec)) in enumerate(T.items()):
    f = c.find(outfields=["sparcl_id", "specid", "ra", "dec", "data_release", "spectype", "redshift"], constraints={"ra": [ra - 0.001, ra + 0.001], "dec": [dec - 0.001, dec + 0.001]}, limit=10)
    print(gid, [(r["specid"], r["data_release"], r["spectype"]) for r in f.records])
    ids = [r["sparcl_id"] for r in f.records]
    if not ids: continue
    r = c.retrieve(uuid_list=ids, include=["specid", "wavelength", "flux", "ivar", "data_release"])
    for x in r.records:
        w, fl, iv = np.array(x.wavelength), np.array(x.flux), np.array(x.ivar); np.savez(f"desi_{gid}_{x.specid}.npz", w=w, f=fl, iv=iv)
        sn = np.nanmedian(fl[(w > 4500) & (w < 5500)] * np.sqrt(iv[(w > 4500) & (w < 5500)])); print("  ", x.specid, x.data_release, "S/N", round(sn, 1))
        ax[i].plot(w, median_filter(fl, 3), lw=.5, label=f"{x.data_release} {x.specid} S/N {sn:.0f}")
    for l in (3970, 4101.7, 4340.5, 4541.6, 4685.7, 4861.3, 5411.5, 6562.8, 6560.1): ax[i].axvline(l, color="r", lw=.4, alpha=.5)
    ax[i].set_title(f"Gaia DR3 {gid}", fontsize=8); ax[i].legend(fontsize=7); ax[i].set_xlim(3600, 9800)
plt.tight_layout(); plt.savefig("desi2.png", dpi=80)
