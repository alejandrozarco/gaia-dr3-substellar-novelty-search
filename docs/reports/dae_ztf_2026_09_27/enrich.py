"""Adds GF21 photometric TeffH/loggH/MassH, Gaia DR3 vari_spurious_signals GLS (local), Chen+2020 ZTF periodic (J/ApJS/249/18/table2),
VSX, and a W1/W2 excess: observed G - W1 (Vega) against Montreal pure-H G3 - W1 at the GF21 Teff/log g (log g clipped to 7.0-9.0)."""
import pandas as pd, numpy as np, astropy.units as u, warnings; warnings.filterwarnings("ignore")
from astroquery.xmatch import XMatch; from astropy.table import Table
s = pd.read_csv("dae_sample.csv", dtype={"targetid": str, "gaia": str}); T = Table.from_pandas(s[["targetid", "ra", "dec"]])
def xm(cat, r, cols):
    x = XMatch.query(cat1=T, cat2=cat, max_distance=r * u.arcsec, colRA1="ra", colDec1="dec").to_pandas(); x["targetid"] = x.targetid.astype(str)
    return x.sort_values("angDist").drop_duplicates("targetid")[["targetid"] + cols]
gf = xm("vizier:J/MNRAS/508/3877/maincat", 1.5, ["TeffH", "loggH", "MassH", "Pwd"])
ch = xm("vizier:J/ApJS/249/18/table2", 2, ["Per", "Type", "gAmp", "rAmp"]).rename(columns={"Per": "P_chen", "Type": "type_chen", "gAmp": "gAmp_chen", "rAmp": "rAmp_chen"})
vs = xm("vizier:B/vsx/vsx", 5, ["Name", "Type", "Period"]).rename(columns={"Name": "vsx_name", "Type": "vsx_type", "Period": "P_vsx"})
v = pd.read_csv("docs/reports/gaia_wd_periods_2026_09_24/data/wd_vspur_gf21.csv", dtype={"source_id": str}, usecols=["source_id", "gls_freq_g_fov", "gls_freq_fap_g_fov"]).rename(columns={"source_id": "gaia", "gls_freq_g_fov": "f_gaia", "gls_freq_fap_g_fov": "fap_gaia"})
s = s.merge(gf, on="targetid", how="left").merge(ch, on="targetid", how="left").merge(vs, on="targetid", how="left").merge(v, on="gaia", how="left")
L = open("../j2052/Table_DA.txt").readlines(); hdr = L[1].replace("log g", "logg").split()
D = np.array([[float(x) for x in l.split()] for l in L[2:] if len(l.split()) == len(hdr)]); iT, iL, iG, iW1, iW2 = 0, 1, hdr.index("G3"), hdr.index("W1"), hdr.index("W2")
def pred(te, lg):
    if not (np.isfinite(te) and np.isfinite(lg)): return np.nan, np.nan
    lg = min(max(lg, 7.0), 9.0); lo = np.floor(lg * 2) / 2; hi = min(lo + 0.5, 9.0); out = []
    for c in (iW1, iW2):
        v = []
        for l in (lo, hi):
            q = D[np.isclose(D[:, iL], l)]; q = q[np.argsort(q[:, 0])]; v.append(np.interp(te, q[:, 0], q[:, iG] - q[:, c]))
        out.append(np.interp(lg, [lo, hi], v) if hi > lo else v[0])
    return out
p = np.array([pred(a, b) for a, b in zip(s.TeffH, s.loggH)]); s["GW1_model"], s["GW2_model"] = p[:, 0], p[:, 1]
s["dW1"] = (s.Gmag - s.W1mproPM) - s.GW1_model; s["dW2"] = (s.Gmag - s.W2mproPM) - s.GW2_model   # > 0 = infrared excess (mag)
s.to_csv("dae_enriched.csv", index=False)
print(len(s), "Gaia GLS:", s.f_gaia.notna().sum(), "Chen:", s.P_chen.notna().sum(), "VSX:", s.vsx_name.notna().sum(), "W1:", s.W1mproPM.notna().sum(), "W1 excess > 0.75:", (s.dW1 > 0.75).sum())
