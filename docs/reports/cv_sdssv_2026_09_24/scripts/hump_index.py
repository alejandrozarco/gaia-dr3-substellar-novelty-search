# Hump index per visit for all 605 objects: mean flux in 6200-6700 A divided by the linear interpolation between the
# median flux in 5600-5900 A and 7000-7400 A (barycentric frame). Used to test whether broad 6200-6700 A humps (possible
# cyclotron humps) are common in BOSS visits of faint targets, i.e. an instrumental artefact near the dichroic split.
import numpy as np, pandas as pd, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/fanout/cv")
from cvspec import load_visits
m = pd.read_csv("master.csv")
rows = []
for sid, g, gm in zip(m.sdss_id, m.gaia_dr3_source_id, m.g_mag):
    for v in load_visits(int(sid)):
        lam, fl, iv = v["lam"], v["flux"], v["ivar"]; ok = (iv > 0) & np.isfinite(fl)
        def med(a, b):
            s = ok & (lam > a) & (lam < b); return np.nanmedian(fl[s]) if s.sum() > 20 else np.nan
        f1, f2, fh = med(5600, 5900), med(7000, 7400), med(6200, 6700)
        interp = f1 + (f2 - f1) * ((6450 - 5750) / (7200 - 5750))
        s = ok & (lam > 6200) & (lam < 6700)
        err = np.sqrt(1 / np.nansum(iv[s])) if s.sum() else np.nan
        rows.append(dict(sdss_id=sid, gaia=g, g_mag=gm, mjd=v["mjd"], fieldid=v["fieldid"], ext=v["ext"], snr=v["snr"], hump=fh / interp if interp > 0 else np.nan,
                         hump_excess=fh - interp, err=err))
h = pd.DataFrame(rows); h.to_csv("hump_index_visits.csv", index=False)
print(len(h), "visits")
print(h.hump.describe())
big = h[(h.hump > 1.3) & (h.snr > 3)]
print("visits with hump index > 1.3 and S/N>3:", len(big), "of", (h.snr > 3).sum())
print(big.sort_values("hump", ascending=False).head(40).to_string())
