import warnings; warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
c=SkyCoord(223.46949,49.94663,unit="deg")
v=Vizier(columns=["**","+_r"]); v.ROW_LIMIT=10
def show(cat,rad,keys=None,lab=""):
    try: r=v.query_region(c,radius=rad*u.arcsec,catalog=cat)
    except Exception as e: print(f"{lab or cat}: QUERY_FAILED {type(e).__name__}"); return
    if not r: print(f"{lab or cat}: NO ROW within {rad}in"); return
    for t in r:
        print(f"{lab or cat} -> {t.meta.get('name')} ({len(t)} row): {(t.meta.get('description') or '')[:70]}")
        for cn in t.colnames:
            if keys and not any(k.lower() in cn.lower() for k in keys): continue
            val=t[0][cn]
            try:
                if hasattr(val,"mask") and val.mask: continue
            except Exception: pass
            sv=str(val).strip()
            if sv and sv not in ("--","nan"): print(f"      {cn:16s} {sv[:80]}")
show("B/vsx/vsx",60,None,"VSX (60in)")
show("J/MNRAS/522/29",5,None,"Green+2023 (ALL tables)")
show("III/286",5,["_r","nvisits","vscatter","verr","vhelio","starflag","aspcapflag","teff","logg","m_h","snr","ccfwhm","autofwhm","sb2","rv_"],"APOGEE DR17")
show("J/AJ/162/184",10,None,"Kounkel+2021 APOGEE SB2 catalogue")
show("I/358",5,None,"Gaia DR3 variability (all I/358 tables)")
