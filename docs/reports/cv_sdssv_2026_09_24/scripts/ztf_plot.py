# Long-term ZTF light curve plot (normalized flux per field/ccd/quad/filter; catflags==0) for a list of Gaia ids.
import sys, pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
ids = sys.argv[1:]
fig, axes = plt.subplots(len(ids), 1, figsize=(13, 2.6 * len(ids)), squeeze=False)
for ax, g in zip(axes[:, 0], ids):
    try:
        d = pd.read_csv(f"/tmp/fanout/cv/ztf/{g}_clean.csv")
    except FileNotFoundError:
        ax.set_title(f"{g}: no ZTF data"); continue
    for f, c in (("zg", "g"), ("zr", "r"), ("zi", "k")):
        s = d[d.filtercode == f]
        ax.errorbar(s.bjd_tdb - 2400000.5, s.mag, s.magerr, fmt=".", ms=2, color=c, alpha=0.5, lw=0.3, label=f"{f} N={len(s)}")
    ax.invert_yaxis(); ax.set_title(f"Gaia DR3 {g}  ZTF DR (IRSA) catflags==0", fontsize=8); ax.legend(fontsize=7); ax.set_ylabel("mag")
axes[-1, 0].set_xlabel("BJD_TDB - 2400000.5")
fig.tight_layout(); fig.savefig("/tmp/fanout/cv/plots/ztf_lc_" + "_".join(i[-6:] for i in ids) + ".png", dpi=85)
print("ok")
