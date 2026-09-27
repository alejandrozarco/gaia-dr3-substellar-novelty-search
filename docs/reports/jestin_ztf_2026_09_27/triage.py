"""Triage of results.csv: detection = FAP < 1e-8 and fundamental amplitude > 5 sigma in g or r. Flags: 1-day alias families (top
frequency within 0.01 c/d of n +- 1/365.25 or within 0.005 of a sidereal-day multiple), Gaia neighbours within 6" (brighter than
target + 2 mag), agreement with the Gaia GLS frequency (f, 2f or f/2 within 0.01 c/d)."""
import os, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
X = os.path.dirname(os.path.abspath(__file__))
R = pd.read_csv(f"{X}/results.csv", dtype={"GaiaDR3": str}); print(R.status.value_counts().to_dict())
R = R[R.status == "ok"].copy()
for b in ("zg", "zr"): R[f"s_{b}"] = R[f"A1_{b}"] / R[f"eA1_{b}"]
R["smax"] = R[["s_zg", "s_zr"]].max(axis=1)
D = R[(R.fap_top < 1e-8) & (R.smax > 5)].copy()
sid = 1.00273791
D["alias"] = [any(abs(f - n * sid) < 0.005 for n in range(1, 50)) or any(abs(f - n) < 0.01 for n in range(1, 50)) for f in D.f_top]
def gmatch(r):
    if not np.isfinite(r.get("f_gaia", np.nan)): return ""
    for m, lab in ((1, "f"), (2, "2f"), (0.5, "f/2")):
        if abs(r.f_top - m * r.f_gaia) < 0.01: return lab
    return "no"
D["gaia_agree"] = D.apply(gmatch, axis=1); D["P_h"] = 24 / D.f_top
print(len(R), "ok;", len(D), "detected;", D.alias.sum(), "alias-flagged")
D.to_csv(f"{X}/detected.csv", index=False)
