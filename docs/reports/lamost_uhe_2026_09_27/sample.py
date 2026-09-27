"""Sample for lamost_uhe.py: LAMOST DR11 white-dwarf catalogue (VizieR V/162/dr11wdl), Teff > 45 kK or a class containing O, snr_g > 8, best spectrum per Gaia source."""
import os, pandas as pd
from astroquery.vizier import Vizier
X = os.path.dirname(os.path.abspath(__file__)); V = Vizier(columns=["**"], row_limit=-1); V.TIMEOUT = 600
t = V.get_catalogs("V/162/dr11wdl")[0].to_pandas(); t["GaiaDR3"] = t.GaiaDR3.astype(str); t["ObsID"] = t.ObsID.astype(str)
c = t.wdClass.fillna("").str.upper(); s = t[((t.Teff > 45000) | c.str.contains("O")) & (t.snrg > 8)].sort_values("snrg", ascending=False).drop_duplicates("GaiaDR3")
s.to_csv(f"{X}/sample.csv", index=False); print(len(t), "catalogue rows;", len(s), "selected")
