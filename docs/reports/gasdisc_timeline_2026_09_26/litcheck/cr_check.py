"""EW of the Ca II triplet (GE.measure) after a 5-pixel running median of the normalised spectrum (removes single-pixel spikes such
as cosmic rays), for the ESO spectra of WD J2133+2428 and Gaia J0611-6931. Compare with the unfiltered EW."""
import os
import sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import gas_disc_epochs as GE
sys.path.insert(0, "/tmp/hotdq/lane_gastime"); import gas_disc_timeline as TL
from scipy.ndimage import median_filter
t = pd.read_csv("timeline_clean.csv", dtype={"gaia": str})
for n in ["WD J2133+2428", "Gaia J0611-6931"]:
    g = t[t.name == n].gaia.iloc[0]; p = TL.gaia_pos([g]).loc[g]
    for s in sorted([s for s in TL.eso(float(p.ra), float(p.dec)) if "hole" not in s], key=lambda s: s["mjd"]):
        nn, v = GE.norm(s["w"], s["f"], s["iv"]); ok = (v > 0) & np.isfinite(nn)
        e0, er0, _, _ = GE.measure(nn, v, np.zeros(len(GE.W)))
        nm = nn.copy(); nm[ok] = median_filter(nn[ok], size=5)
        e1, er1, _, _ = GE.measure(nm, v, np.zeros(len(GE.W)))
        print(f"{n} {s['date']} {s['identifier']}: EW raw {e0:.2f} +- {er0:.2f}, median-5 {e1:.2f}")
