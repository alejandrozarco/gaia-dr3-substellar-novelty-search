import numpy as np, requests, io, time
from astropy.table import Table
URL="https://datalab.noirlab.edu/tap/sync"

def raw(ra,dec,rad_as):
    r=rad_as/3600.0
    q=f"SELECT id,ra,dec,ndet,deltamjd,rmag,gmag,class_star,mjd_first,mjd_last FROM nsc_dr2.object WHERE q3c_radial_query(ra,dec,{ra},{dec},{r})"
    resp=requests.post(URL,data={"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q},timeout=300)
    print("status",resp.status_code,"len",len(resp.text))
    print("first 600 chars:\n",resp.text[:600])
    return resp

for attempt in range(5):
    try:
        r=raw(228.8012259,-20.8267668,8.0)
        if r.status_code==200 and len(r.text)>5:
            break
    except Exception as e:
        print("err",type(e).__name__,str(e)[:120])
    time.sleep(10)
