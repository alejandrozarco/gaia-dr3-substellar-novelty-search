"""Joins the two Chen+2020 x GF21 matches (table2 classified, table3 suspected variables) into chen_wd_all.csv with M_G, BP-RP, r/g amplitude ratio,
period in hours and g/r period agreement."""
import pandas as pd, numpy as np
a = pd.read_csv("chen_x_gf21.csv"); b = pd.read_csv("chen3_x_gf21.csv"); a["tab"] = "t2"; b["tab"] = "t3"
b["Per"] = np.where(np.isfinite(b["Per-r"]), b["Per-r"], b["Per-g"]); b["Type"] = "susp"
d = pd.concat([a, b], ignore_index=True); d["GaiaEDR3"] = d.GaiaEDR3.astype("int64").astype(str)
d["MG"] = d.Gmag + 5 * np.log10(d.Plx / 100); d["bprp"] = d.BPmag - d.RPmag; d["rg"] = d.rAmp / d.gAmp; d["P_h"] = d.Per * 24
d["pagree"] = np.abs(d["Per-g"] - d["Per-r"]) / d.Per < 0.01; d.to_csv("chen_wd_all.csv", index=False)
