# Legacy Survey DR10 tractor catalog: static sources in the 3-sigma box (stationary test)
import requests, time, io, csv, math
BASE="https://datalab.noirlab.edu/tap/async"
ra0,dec0=252.0790,-24.7890
rad=8.0/3600.0   # 8" box around predicted TNO position
adql=f"""SELECT t.ra,t.dec,t.type,t.flux_g,t.flux_r,t.flux_i,t.flux_z,t.dered_mag_g,t.dered_mag_r,t.dered_mag_z
FROM ls_dr10.tractor AS t WHERE 't'=q3c_radial_query(t.ra,t.dec,{ra0},{dec0},{rad})"""
r=requests.post(BASE,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql,'phase':'run'},timeout=60)
job=r.url.split('/phase')[0]
for i in range(120):
    p=requests.get(job+"/phase",timeout=30).text.strip()
    if p in ("COMPLETED","ERROR","ABORTED"): break
    time.sleep(5)
if p!="COMPLETED":
    open('ls_coadd.err','w').write(requests.get(job+"/error",timeout=30).text); print("LS ERR")
else:
    res=requests.get(job+"/results/result",timeout=120).text
    open('ls_coadd.csv','w').write(res)
    rows=list(csv.DictReader(io.StringIO(res)))
    print("LS DR10 sources within 8\" of predicted TNO posn:",len(rows))
    for x in rows:
        dra=(float(x['ra'])-ra0)*3600*math.cos(math.radians(dec0)); ddec=(float(x['dec'])-dec0)*3600
        print("  sep=%.2f\" dRA=%+.2f dDec=%+.2f type=%s g=%s r=%s z=%s"%((dra**2+ddec**2)**0.5,dra,ddec,x['type'],x.get('dered_mag_g'),x.get('dered_mag_r'),x.get('dered_mag_z')))
print("LSDONE")
