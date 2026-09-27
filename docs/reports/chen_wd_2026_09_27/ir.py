"""Short-period (< 6 h), red-rising (r/g > 1.4) white dwarfs from Chen+2020 x GF21: CatWISE2020 W1/W2 excess against Montreal pure-H G3-W1/G3-W2
at the GF21 Teff/log g, plus UKIDSS LAS / VHS / 2MASS Ks where available."""
import pandas as pd, numpy as np, astropy.units as u, warnings; warnings.filterwarnings("ignore")
from astroquery.xmatch import XMatch; from astropy.table import Table
d = pd.read_csv("chen_wd_all.csv", dtype={"GaiaEDR3": str})
k = d[(d.Pwd > 0.75) & (d.P_h < 6) & (d.rg > 1.4) & (d.Gmag < 19.5)].copy().drop_duplicates("GaiaEDR3"); k["tid"] = k.GaiaEDR3
T = Table.from_pandas(k[["tid", "RA_ICRS", "DE_ICRS"]])
def xm(cat, r, cols):
    x = XMatch.query(cat1=T, cat2=cat, max_distance=r * u.arcsec, colRA1="RA_ICRS", colDec1="DE_ICRS").to_pandas(); x["tid"] = x.tid.astype(str)
    return x.sort_values("angDist").drop_duplicates("tid")[["tid"] + cols]
w = xm("vizier:II/365/catwise", 3, ["W1mproPM", "W2mproPM", "e_W1mproPM", "e_W2mproPM"])
out = k.merge(w, on="tid", how="left")
for cat, col, nm in [("vizier:II/319/las9", "Kmag1", "K_ukidss"), ("vizier:II/367/vhs_dr5", "Kspmag", "Ks_vhs"), ("vizier:II/246/out", "Kmag", "K_2mass")]:
    try: out = out.merge(xm(cat, 2, [col]).rename(columns={col: nm}), on="tid", how="left")
    except Exception as ex: print("HOLE", cat, ex); out[nm] = np.nan
L = open("Table_DA.txt").readlines(); hdr = L[1].replace("log g", "logg").split()
D = np.array([[float(x) for x in l.split()] for l in L[2:] if len(l.split()) == len(hdr)]); iG, iW1, iW2, iK = hdr.index("G3"), hdr.index("W1"), hdr.index("W2"), hdr.index("Ks")
def pred(te, lg, c):
    if not (np.isfinite(te) and np.isfinite(lg)): return np.nan
    lg = min(max(lg, 7.0), 9.0); lo = np.floor(lg * 2) / 2; hi = min(lo + 0.5, 9.0); v = []
    for l in (lo, hi):
        q = D[np.isclose(D[:, 1], l)]; q = q[np.argsort(q[:, 0])]; v.append(np.interp(te, q[:, 0], q[:, iG] - q[:, c]))
    return np.interp(lg, [lo, hi], v) if hi > lo else v[0]
for nm, c, obs in [("dW1", iW1, "W1mproPM"), ("dW2", iW2, "W2mproPM")]:
    out[nm] = [(g - o) - pred(t, l, c) for g, o, t, l in zip(out.Gmag, out[obs], out.TeffH, out.loggH)]
kk = out.K_ukidss.fillna(out.Ks_vhs).fillna(out.K_2mass); out["Kbest"] = kk
out["dK"] = [(g - o) - pred(t, l, iK) for g, o, t, l in zip(out.Gmag, kk, out.TeffH, out.loggH)]
out.to_csv("short_red_ir.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(out.sort_values("P_h")[["GaiaEDR3", "WDJname", "Type", "Gmag", "MG", "TeffH", "MassH", "P_h", "gAmp", "rAmp", "rg", "W1mproPM", "dW1", "dW2", "Kbest", "dK"]].round(2).to_string(index=False))
