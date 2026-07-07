import numpy as np, requests, io
from astropy.table import Table

URL="https://datalab.noirlab.edu/tap/sync"

def cone(ra,dec,rad_as,label):
    r=rad_as/3600.0
    q=f"""SELECT id,ra,dec,ndet,deltamjd,rmag,gmag,imag,class_star,mjd_first,mjd_last
          FROM nsc_dr2.object
          WHERE q3c_radial_query(ra,dec,{ra},{dec},{r})"""
    resp=requests.post(URL,data={"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q},timeout=120)
    resp.raise_for_status()
    t=Table.read(io.StringIO(resp.text),format="csv")
    print(f"\n=== {label}: {len(t)} NSC objects within {rad_as}\" of ({ra},{dec}) ===")
    for row in t:
        dra=(row['ra']-ra)*3600*np.cos(np.radians(dec)); ddec=(row['dec']-dec)*3600
        sep=np.hypot(dra,ddec)
        print(f"  id={row['id']} sep={sep:.2f}\" ndet={row['ndet']} dmjd={row['deltamjd']:.1f} "
              f"r={row['rmag']:.2f} g={row['gmag']:.2f} cstar={row['class_star']:.2f} "
              f"mjd0={row['mjd_first']:.1f} mjd1={row['mjd_last']:.1f}")
    return t

cone(228.8012259,-20.8267668,5.0,"CAND1 2013 5\"")
cone(228.8012259,-20.8267668,15.0,"CAND1 2013 15\"")
cone(229.7975068,-21.0925405,5.0,"CAND2 2015 5\"")
cone(229.7975068,-21.0925405,15.0,"CAND2 2015 15\"")
