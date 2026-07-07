import numpy as np, requests, io, time
from astropy.table import Table
URL="https://datalab.noirlab.edu/tap/sync"

def cone(ra,dec,rad_as,label,tries=4):
    r=rad_as/3600.0
    q=f"""SELECT id,ra,dec,ndet,deltamjd,rmag,gmag,class_star,mjd_first,mjd_last
          FROM nsc_dr2.object WHERE q3c_radial_query(ra,dec,{ra},{dec},{r})"""
    for k in range(tries):
        try:
            resp=requests.post(URL,data={"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q},timeout=300)
            if resp.status_code==200:
                t=Table.read(io.StringIO(resp.text),format="csv")
                print(f"\n=== {label}: {len(t)} objs within {rad_as}\" ===")
                for row in t:
                    dra=(row['ra']-ra)*3600*np.cos(np.radians(dec)); ddec=(row['dec']-dec)*3600
                    sep=np.hypot(dra,ddec)
                    print(f"  id={row['id']} sep={sep:.2f}\" ndet={row['ndet']} dmjd={row['deltamjd']:.1f} r={row['rmag']:.2f} g={row['gmag']:.2f} cstar={row['class_star']:.2f} mjd0={row['mjd_first']:.1f} mjd1={row['mjd_last']:.1f}")
                return t
            else:
                print(f"  try{k} status {resp.status_code}")
        except Exception as e:
            print(f"  try{k} err {type(e).__name__}")
        time.sleep(8)
    print(f"  {label}: FAILED after {tries}")
    return None

cone(228.8012259,-20.8267668,8.0,"CAND1 2013 8\"")
cone(229.7975068,-21.0925405,8.0,"CAND2 2015 8\"")
