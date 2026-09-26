# Infrared photometry of 6021870154194477312 vs neighbours: VHS DR5, CatWISE2020, unWISE, 2MASS, SkyMapper DR4, within 3".
import warnings; warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
import astropy.units as u
from astropy.coordinates import SkyCoord
c = SkyCoord(244.7254259862617, -35.90743853686, unit="deg")  # epoch 2016; PM 27.7 mas/yr -> <0.3" offset for any epoch 2006-2026
V = Vizier(columns=["**", "_r"], row_limit=50)
for cat in ["II/367/vhs_dr5", "II/365/catwise", "II/363/unwise", "II/328/allwise", "II/246/out", "II/379/smssdr4", "II/335/galex_ais", "B/denis/denis"]:
    t = V.query_region(c, radius=3 * u.arcsec, catalog=cat)
    if not t: print(f"{cat}: none within 3\""); continue
    for x in t:
        keep = [k for k in x.colnames if any(s in k for s in ["_r", "mag", "Jap", "Ksap", "Hap", "Yap", "Zap", "W1", "W2", "FUV", "NUV", "Jpet", "Kspet", "FW1", "FW2", "e_"])][:40]
        print(f"== {cat}"); print(x[keep])
