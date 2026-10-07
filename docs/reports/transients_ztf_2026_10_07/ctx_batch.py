"""Batch context for survivors (2026-10-05): ALeRCE detections (pos/neg, drb), last non-detection before first det + deepest
limit, ndethist; VizieR PS1 DR2 and Gaia DR3 within 3"; Lasair Sherlock class. Output: ctx.txt"""
import requests, json, pandas as pd, numpy as np
from concurrent.futures import ThreadPoolExecutor
from astroquery.vizier import Vizier; import astropy.units as u, astropy.coordinates as c
A="https://api.alerce.online/ztf/v1"; F={1:"g",2:"r",3:"i"}
V=pd.read_csv("survivors.csv"); V=V[V.tns_lasair.isna()]
J=json.load(open("fresh_all.json")); L={x["objectId"]:x for x in J["all"]}
viz=Vizier(columns=["**"],row_limit=5)
def one(r):
    o=r.oid; out=[f"#### {o} {r.ra:.5f} {r.dec:.5f} cls={r.cls}"]
    try:
        ob=requests.get(f"{A}/objects/{o}",timeout=60).json(); d=pd.DataFrame(requests.get(f"{A}/objects/{o}/detections",timeout=60).json()).sort_values("mjd")
        n=pd.DataFrame(requests.get(f"{A}/objects/{o}/non_detections",timeout=60).json())
        out.append(f"ndethist {ob.get('ndethist')} ncovhist {ob.get('ncovhist')} starthist {ob.get('mjdstarthist'):.2f} alerce class {ob.get('class')} {ob.get('probability')}")
        out.append(" | ".join(f"{x.mjd:.3f}{F[int(x.fid)]}{'+' if str(x.isdiffpos) in ('1','t','True') else '-'}{x.magpsf:.2f}±{x.sigmapsf:.2f} drb{x.drb:.2f} dnr{x.distnr:.1f}" for x in d.itertuples()))
        if len(n):
            b=n[n.mjd<d.mjd.min()].sort_values("mjd")
            out.append("pre-nondet: "+(" ".join(f"{x.mjd:.2f}{F[int(x.fid)]}>{x.diffmaglim:.1f}" for x in b.tail(5).itertuples()) if len(b) else "none")+f" | n_nondet_total {len(n)}")
    except Exception as ex: out.append("ALeRCE HOLE "+repr(ex)[:80])
    l=L.get(o); out.append("Lasair: "+(f"{l['classification']} sep {l['separationArcsec']} {l['catalogue_table_name']} {l['catalogue_object_id']} z {l['z']} photoz {l['photoZ']}" if l else "not in Lasair fresh list"))
    sc=c.SkyCoord(r.ra*u.deg,r.dec*u.deg)
    for cat,cols in (("II/349/ps1",["gmag","rmag","imag"]),("I/355/gaiadr3",["Gmag","BP-RP","Plx","pmRA","pmDE"])):
        try:
            t=viz.query_region(sc,radius=3*u.arcsec,catalog=cat)
            out.append(cat+": "+("; ".join(f"r={x['_r']:.2f} "+" ".join(f"{k}={x[k]}" for k in cols if k in t[0].colnames) for x in t[0]) if len(t) else "none<3\""))
        except Exception as ex: out.append(cat+" HOLE")
    return "\n".join(out)
with ThreadPoolExecutor(4) as ex: R=list(ex.map(one,V.itertuples()))
open("ctx.txt","w").write("\n".join(R)+"\n"); print("\n".join(R))
