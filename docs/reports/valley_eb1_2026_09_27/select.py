"""eb1_sample.csv: Ranaivomanana et al. (2025, A&A 704, A70) table A2 (VizieR J/A+A/704/A70/tablea2), cluster EB1, period < 180 min,
M_G > 7.5, BP-RP < 0.4."""
import pandas as pd
from astroquery.vizier import Vizier
V = Vizier(columns=["**"], row_limit=-1); t = V.get_catalogs("J/A+A/704/A70/tablea2")[0].to_pandas(); t["GaiaDR3"] = t.GaiaDR3.astype(str); t["P_min"] = t.Per * 1440
t[(t.Cluster == "EB1") & (t.P_min < 180) & (t.GMAG > 7.5) & (t["BP-RP"] < 0.4)].to_csv("eb1_sample.csv", index=False)
