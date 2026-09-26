"""Ca II triplet profiles (GE.norm normalisation, velocity space) of every cached ESO spectrum for three timeline variables.
Output prof_check.png"""
import sys, glob, os, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import gas_disc_epochs as GE
sys.path.insert(0, "/tmp/hotdq/lane_gastime"); import gas_disc_timeline as TL
from scipy.ndimage import gaussian_filter1d
t = pd.read_csv("timeline_clean.csv", dtype={"gaia": str})
stars = ["WD J2133+2428", "SDSS J0738+1835", "Gaia J0611-6931"]
fig, ax = plt.subplots(3, 3, figsize=(13, 12))
pos = TL.gaia_pos(t[t.name.isin(stars)].gaia.unique().tolist())
for i, n in enumerate(stars):
    g = t[t.name == n].gaia.iloc[0]; ra, dec = float(pos.loc[g].ra), float(pos.loc[g].dec)
    sp = [s for s in TL.eso(ra, dec) if "hole" not in s]
    sp = sorted(sp, key=lambda s: s["mjd"])
    for k, s in enumerate(sp):
        nn, v = GE.norm(s["w"], s["f"], s["iv"]); ok = (v > 0) & np.isfinite(nn)
        if ok.sum() < 100: continue
        ew = t[(t.identifier == s["identifier"])].ew_A
        for j, l in enumerate(GE.CAT):
            vel = (GE.W / l - 1) * GE.C; m = ok & (np.abs(vel) < 2000)
            ax[i, j].plot(vel[m], gaussian_filter1d(nn[m], 1) + 0.3 * k, lw=.7)
            if j == 2: ax[i, j].text(1100, 1.05 + 0.3 * k, f"{s['date']} EW {ew.iloc[0] if len(ew) else float('nan'):.1f}", fontsize=6)
        for j in range(3): ax[i, j].set_title(f"{n} Ca II {GE.CAT[j]:.0f}", fontsize=8); ax[i, j].axvline(0, color="grey", lw=.4)
plt.tight_layout(); plt.savefig("prof_check.png", dpi=80)
