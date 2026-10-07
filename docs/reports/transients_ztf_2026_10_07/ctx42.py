"""PS1 DR2 + Gaia DR3 within 3" (VizieR) and LS DR10 tractor+photo-z within 6" for the stationary screen1 objects (2026-10-07). Output: ctx42.txt"""
import pandas as pd, requests, io, numpy as np
from astroquery.vizier import Vizier; import astropy.units as u, astropy.coordinates as c
S=pd.read_csv("screen1.csv"); S=S[(S.rms_as<0.6)&(S.rate_ash<0.3)&(S.span_h>0.5)]
viz=Vizier(columns=["**"],row_limit=5)
def ls(ra,de,r=6):
    s=f"""SELECT t.ra,t.dec,t.type,t.flux_g,t.flux_r,t.flux_z,t.shape_r,p.z_phot_median,p.z_phot_l68,p.z_phot_u68,p.z_spec FROM ls_dr10.tractor AS t LEFT JOIN ls_dr10.photo_z AS p ON t.ls_id=p.ls_id WHERE 't'=q3c_radial_query(t.ra,t.dec,{ra},{de},{r/3600})"""
    try:
        x=requests.post("https://datalab.noirlab.edu/tap/sync",data=dict(REQUEST="doQuery",LANG="ADQL",FORMAT="csv",QUERY=s),timeout=120)
        d=pd.read_csv(io.StringIO(x.text))
        if "flux_g" not in d.columns: return "HOLE"
        if not len(d): return "none<6\""
        d["sep"]=np.hypot((d.ra-ra)*np.cos(np.radians(de)),d.dec-de)*3600
        for b in "grz": d[b]=(22.5-2.5*np.log10(d[f"flux_{b}"].where(d[f"flux_{b}"]>0))).round(2)
        return "; ".join(f"{x.sep:.1f}\" {x.type} r{x.r} rhalf{x.shape_r:.1f} zp{x.z_phot_median:.3f}[{x.z_phot_l68:.2f},{x.z_phot_u68:.2f}] zs{x.z_spec}" for x in d.sort_values("sep").head(3).itertuples())
    except Exception as ex: return "HOLE "+repr(ex)[:60]
out=[]
for r in S.itertuples():
    sc=c.SkyCoord(r.ra*u.deg,r.dec*u.deg); L=[f"#### {r.oid} {r.ra:.5f} {r.dec:.5f} b={sc.galactic.b.deg:.1f} distnr={r.distnr_med:.1f}"]
    for cat,cols in (("II/349/ps1",["gmag","rmag","imag"]),("I/355/gaiadr3",["Gmag","BP-RP","Plx","e_Plx","pmRA","pmDE"])):
        try:
            t=viz.query_region(sc,radius=3*u.arcsec,catalog=cat)
            L.append(cat+": "+("; ".join(f"r={x['_r']:.2f} "+" ".join(f"{k}={x[k]}" for k in cols) for x in t[0]) if len(t) else "none<3\""))
        except Exception as ex: L.append(cat+" HOLE")
    L.append("LS DR10: "+ls(r.ra,r.dec)); out.append("\n".join(L)); print(out[-1],flush=True)
open("ctx42.txt","w").write("\n".join(out)+"\n")
