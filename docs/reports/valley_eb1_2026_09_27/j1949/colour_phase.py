"""WDJ194901.41+673005.59: Gaia DR3 per-transit BP-RP colour against photometric phase (TESS ephemeris from fold.py, ephem.npy;
gaia_ep.csv = VizieR I/355/epphot rows of Gaia DR3 2249098833310553728). Spearman correlation of cos(2 pi phase) with BP-RP."""
import numpy as np, pandas as pd
from scipy.stats import spearmanr
e = pd.read_csv("gaia_ep.csv"); f, tmax = np.load("ephem.npy")
m = np.isfinite(e.FBP) & np.isfinite(e.FRP) & (e.FBP > 0) & (e.FRP > 0) & (e.BPrVFlag == 0) & (e.RPrVFlag == 0)
ph = ((e.TimeBP[m].values + 2455197.5 - tmax) * f) % 1; col = -2.5 * np.log10(e.FBP[m].values / e.FRP[m].values); col -= np.median(col)
rho, p = spearmanr(np.cos(2 * np.pi * ph), col); mx = col[np.cos(2 * np.pi * ph) > 0.5]; mn = col[np.cos(2 * np.pi * ph) < -0.5]
print(f"n {m.sum()}; Spearman {rho:+.2f} (p {p:.3f}); BP-RP near max {mx.mean():+.3f} +- {mx.std()/np.sqrt(len(mx)):.3f}; near min {mn.mean():+.3f} +- {mn.std()/np.sqrt(len(mn)):.3f}")
