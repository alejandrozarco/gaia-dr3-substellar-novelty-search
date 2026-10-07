"""NED cone 8" per candidate: objects with a redshift (any flag) and type; control NGC 1068. Output: ned.txt"""
import sys, time
from astroquery.ipac.ned import Ned; import astropy.coordinates as c, astropy.units as u
def q(ra,de,r=8):
    for k in range(3):
        try:
            t=Ned.query_region(c.SkyCoord(ra*u.deg,de*u.deg),radius=r*u.arcsec); return t
        except Exception as ex: err=repr(ex)[:80]; time.sleep(5)
    return "HOLE "+err
t=q(40.6696,-0.0133,10); print("control", "HOLE" if isinstance(t,str) else [(x["Object Name"],x["Redshift"]) for x in t][:3],flush=True)
for a in sys.argv[1:]:
    n,ra,de=a.split(":"); t=q(float(ra),float(de))
    if isinstance(t,str): print(n,t,flush=True); continue
    print(n,"|", "; ".join(f'{x["Object Name"]} {x["Type"]} sep{x["Separation"]*60:.1f}" z={x["Redshift"]} {x["Redshift Flag"]}' for x in t) or "none<8\"",flush=True)
