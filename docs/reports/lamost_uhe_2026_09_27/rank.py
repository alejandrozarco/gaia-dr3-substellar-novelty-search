"""Significance of the UHE windows: EW / max(robust scatter of the control windows in the same snr_g bin, formal error). Flags: (z5280 >= 3 and z5665 >= 2)
or (z5665 >= 4 and z5280 >= 1), with all control windows < 3 sigma. Known UHE stars matched within 5" to known_uhe_all.csv."""
import os, numpy as np, pandas as pd
from astropy.coordinates import SkyCoord
X = os.path.dirname(os.path.abspath(__file__))
R = pd.read_csv(f"{X}/lamost_uhe.csv", dtype={"ObsID": str, "GaiaDR3": str}); R = R[R.status == "ok"].copy()
R["bin"] = pd.cut(R.snrg, [0, 12, 16, 20, 30, 50, 1000])
mad = lambda g: 1.4826 * np.nanmedian(np.abs(np.r_[g.e5100, g.e5480, g.e5740] - np.nanmedian(np.r_[g.e5100, g.e5480, g.e5740])))
R["sig"] = R.bin.map(R.groupby("bin", observed=True).apply(mad)).astype(float)
for l in (4495, 4941, 5280, 5665): R[f"z{l}"] = R[f"e{l}"] / np.maximum(R.sig, R[f"s{l}"])
R["ctrlmax"] = R[["e5100", "e5480", "e5740"]].abs().max(axis=1) / R.sig
K = pd.read_csv(f"{X}/../uhe_screen_sdssv_2026_09_26/data/known_uhe_all.csv"); i, d, _ = SkyCoord(R.ra.values, R.dec.values, unit="deg").match_to_catalog_sky(SkyCoord(K.ra.values, K.dec.values, unit="deg"))
R["known"] = [K.name.iloc[j] if dd.arcsec < 5 else "" for j, dd in zip(i, d)]
ours = {"5671975077144346112", "4711031463842628736", "4844689579080133248", "6644780943442193664", "3597350571454888448", "4749559145849819008", "4866851575967878144", "1008280341952767232", "2120335400240968448", "303909583762954368"}
R["ours"] = R.GaiaDR3.isin(ours)
c = R[(((R.z5280 >= 3) & (R.z5665 >= 2)) | ((R.z5665 >= 4) & (R.z5280 >= 1)) | (R.known != "") | R.ours) & (R.ctrlmax < 3)].sort_values("z5665", ascending=False)
print(len(R), "measured;", len(c), "flagged/known/ours"); print(c[["GaiaDR3", "wdClass", "Teff", "snrg", "z5280", "z5665", "ctrlmax", "known"]].round(2).to_string(index=False))
R.to_csv(f"{X}/lamost_ranked.csv", index=False)
