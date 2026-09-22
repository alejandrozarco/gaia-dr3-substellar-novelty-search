import warnings; warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
c=SkyCoord(223.46949,49.94663,unit="deg")
v=Vizier(columns=["**","+_r"]); v.ROW_LIMIT=5
for cat in ("III/286/allvis","III/286/catalog"):
    r=v.query_region(c,radius=5*u.arcsec,catalog=cat)
    if not r: print(cat,"none"); continue
    t=r[0]; print(f"=== {cat} ({len(t)} row) ===")
    for cn in t.colnames:
        val=t[0][cn]
        try:
            if hasattr(val,"mask") and val.mask: continue
        except Exception: pass
        sv=str(val).strip()
        if sv and sv not in ("--","nan") and any(k in cn.lower() for k in ("apogee","field","tele","plate","mjd","fiber","jd","file","vhelio","snr","starflag","vscatter","nvis","loc","id","rv","ccf")):
            print(f"   {cn:16s} {sv}")
