import requests, time, io, csv, math
BASE="https://datalab.noirlab.edu/tap/async"
# +1 deg RA offset negative control (rule 6)
ra0,dec0=253.0790,-24.7890
rad=25.0/3600.0
adql=f"""SELECT m.ra,m.dec,m.mjd,m.mag_auto,m.magerr_auto,m.filter,m.fwhm,m.class_star,m.exposure,m.objectid
FROM nsc_dr2.meas AS m WHERE 't'=q3c_radial_query(m.ra,m.dec,{ra0},{dec0},{rad})"""
r=requests.post(BASE,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql,'phase':'run'},timeout=60)
job=r.url.split('/phase')[0]
for i in range(120):
    p=requests.get(job+"/phase",timeout=30).text.strip()
    if p in ("COMPLETED","ERROR","ABORTED"): break
    time.sleep(5)
if p!="COMPLETED":
    open('nsc_neg.err','w').write(requests.get(job+"/error",timeout=30).text); print("NEG ERR")
else:
    res=requests.get(job+"/results/result",timeout=180).text
    open('nsc_neg_async.csv','w').write(res)
    rows=list(csv.DictReader(io.StringIO(res)))
    night=[x for x in rows if 57890.10<float(x['mjd'])<57890.20]
    print("NEG total rows",len(rows),"night-detections",len(night))
    for x in sorted(night,key=lambda z:float(z['mjd'])):
        dra=(float(x['ra'])-ra0)*3600*math.cos(math.radians(dec0)); ddec=(float(x['dec'])-dec0)*3600
        print("  NEG mjd=%.5f dRA=%+.2f dDec=%+.2f mag=%s filt=%s cstar=%s exp=%s"%(float(x['mjd']),dra,ddec,x['mag_auto'],x['filter'],x['class_star'],x['exposure']))
print("NEGDONE")
