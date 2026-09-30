"""Select radial-velocity-variable white dwarfs from rv_fit_pairs.csv (2026-09-30).
Per pair, the lines with a fit (H-alpha, H-beta, H-gamma) are combined: errors are multiplied by that line's robust z scale
(1.26, 1.20, 1.33 from the full sample), weighted mean dv and its error; consistency chi^2 between lines. A pair is flagged when
>= 2 lines agree (consistency p > 0.001), |dv| > 60 km/s, and |dv| / err > 6. Output: results/rv_candidates.csv (flagged pairs, best
per star) and the number of flagged stars."""
import os, numpy as np, pandas as pd
from scipy.stats import chi2
H = os.path.dirname(os.path.abspath(__file__)); P = pd.read_csv(os.path.join(H, "results", "rv_fit_pairs.csv"), dtype={"gaia": str})
SC = {"Ha": 1.26, "Hb": 1.20, "Hg": 1.33}; V = np.vstack([P[f"vc_{k}"] for k in SC]).T; E = np.vstack([P[f"e_{k}"] * s for k, s in SC.items()]).T
ok = np.isfinite(V) & np.isfinite(E) & (E > 0); w = np.where(ok, 1 / np.where(ok, E, 1)**2, 0)
P["nl"] = ok.sum(1); P["dv"] = np.where(P.nl > 0, (w * np.nan_to_num(V)).sum(1) / np.where(w.sum(1) > 0, w.sum(1), 1), np.nan); P["edv"] = 1 / np.sqrt(np.where(w.sum(1) > 0, w.sum(1), np.nan))
P["chi_cons"] = (w * (np.nan_to_num(V) - P.dv.values[:, None])**2).sum(1); P["p_cons"] = chi2.sf(P.chi_cons, np.clip(P.nl - 1, 1, None))
P["zdv"] = P.dv / P.edv
F = P[(P.nl >= 2) & (P.p_cons > 0.001) & (P.dv.abs() > 60) & (P.zdv.abs() > 6)].sort_values("zdv", key=abs, ascending=False)
print("pairs with >= 2 lines:", int((P.nl >= 2).sum()), "; flagged pairs:", len(F), "; stars:", F.gaia.nunique())
F.drop_duplicates("gaia").to_csv(os.path.join(H, "results", "rv_candidates.csv"), index=False)
pd.set_option("display.width", 250); print(F.drop_duplicates("gaia")[["gaia", "a", "b", "sn_a", "sn_b", "nl", "dv", "edv", "zdv", "p_cons", "vc_Ha", "vc_Hb", "vc_Hg"]].head(60).to_string())
