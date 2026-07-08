import requests, time, io, csv, json, math, sys
BASE="https://datalab.noirlab.edu/tap/async"
ra0,dec0=252.0790,-24.7890
rad=25.0/3600.0
adql=f"""SELECT m.ra,m.dec,m.mjd,m.mag_auto,m.magerr_auto,m.filter,m.fwhm,m.class_star,m.exposure,m.objectid
FROM nsc_dr2.meas AS m
WHERE 't'=q3c_radial_query(m.ra,m.dec,{ra0},{dec0},{rad})"""
# submit
r=requests.post(BASE,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql,'phase':'run'},timeout=60)
print("submit HTTP",r.status_code)
job=r.url
if '/async/' not in r.url:
    # find job url from response
    job=r.headers.get('Location',r.url)
print("job url:",job)
# poll phase
for i in range(60):
    p=requests.get(job+"/phase",timeout=30).text.strip()
    if i%3==0: print("phase",p)
    if p in ("COMPLETED","ERROR","ABORTED"): break
    time.sleep(5)
print("final phase",p)
if p=="COMPLETED":
    res=requests.get(job+"/results/result",timeout=120).text
    open('nsc_meas_async.csv','w').write(res)
    rows=list(csv.DictReader(io.StringIO(res)))
    print("rows:",len(rows))
    night=[x for x in rows if 57890.10<float(x['mjd'])<57890.20]
    print("=== NIGHT 2017-05-17 detections within 25\": %d ==="%len(night))
    for x in sorted(night,key=lambda z:float(z['mjd'])):
        dra=(float(x['ra'])-ra0)*3600*math.cos(math.radians(dec0)); ddec=(float(x['dec'])-dec0)*3600
        print("  mjd=%.5f dRA=%+.2f dDec=%+.2f mag=%s(%s) filt=%s fwhm=%s cstar=%s exp=%s obj=%s"%(
          float(x['mjd']),dra,ddec,x['mag_auto'],x['magerr_auto'],x['filter'],x['fwhm'],x['class_star'],x['exposure'],x['objectid']))
    from collections import Counter
    print("all-epoch mjd hist(0.01):", dict(sorted(Counter(round(float(x['mjd']),2) for x in rows).items())))
    # filter list of near-predicted (within 3") static-ish
else:
    print(requests.get(job+"/error",timeout=30).text[:500])
