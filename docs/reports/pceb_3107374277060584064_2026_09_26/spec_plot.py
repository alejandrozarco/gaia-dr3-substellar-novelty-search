"""SDSS-V visits of sdss_id 74709777 (Gaia DR3 3107374277060584064): full range and line zooms in velocity, per visit, labelled with
the ZTF photometric phase (0 = maximum light). Output spec_74709777.png"""
import os
import sys, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts"))
import sdssv
from scipy.ndimage import gaussian_filter1d
C = 299792.458
ph = pd.read_csv("visit_phase_rv.csv").set_index("mjd").phase_from_max
vs = sdssv.visits(74709777); co = sdssv.coadd(vs)
fig = plt.figure(figsize=(14, 9)); ax0 = fig.add_axes([0.05, 0.62, 0.9, 0.33])
w, f, iv = co[0], co[1], co[2]; ok = iv > 0
ax0.plot(w[ok], gaussian_filter1d(f[ok], 2), "k", lw=.6); ax0.set_xlim(3800, 9200); ax0.set_title("SDSS-V coadd (4 visits), Gaia DR3 3107374277060584064")
for l, n in ((4686, "He II"), (4862.7, "Hb"), (5008.2, "[O III]"), (6564.6, "Ha"), (8544.4, "Ca II"), (6585.3, "[N II]"), (4102.9, "Hd"), (4341.7, "Hg"), (5413, "He II 5412")):
    ax0.axvline(l, color="r", lw=.4, alpha=.5); ax0.text(l, ax0.get_ylim()[1]*0.95, n, fontsize=7, rotation=90)
lines = [("He II 4686", 4687.0), ("H-beta", 4862.7), ("[O III] 5007", 5008.2), ("H-alpha", 6564.6), ("Ca II 8544", 8544.4), ("Ca II 8665", 8664.5)]
for j, (n, l) in enumerate(lines):
    a = fig.add_axes([0.05 + j * 0.155, 0.06, 0.14, 0.48])
    for k, v in enumerate(sorted(vs, key=lambda v: v["mjd"])):
        vel = (v["wave"] / l - 1) * C; m = (np.abs(vel) < 2000) & (v["ivar"] > 0)
        if m.sum() < 20: continue
        y = v["flux"][m] / np.median(v["flux"][m]); a.plot(vel[m], gaussian_filter1d(y, 1.5) + 0.6 * k, lw=.8)
        a.text(1300, 1.0 + 0.6 * k + 0.15, f"{v['mjd']} ph {ph[v['mjd']]:.2f}", fontsize=6)
    a.axvline(0, color="grey", lw=.4); a.set_title(n, fontsize=9); a.set_xlabel("km/s", fontsize=8); a.tick_params(labelsize=7)
plt.savefig("spec_74709777.png", dpi=85)
