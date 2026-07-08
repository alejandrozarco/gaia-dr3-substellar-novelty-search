import requests, time, io, csv, json, math
BASE="https://datalab.noirlab.edu/tap/async"
ra0,dec0=252.0790,-24.7890
def run(rad_as,tbl='meas',cols=None):
    rad=rad_as/3600.0
    if tbl=='meas':
        adql=f"""SELECT m.ra,m.dec,m.mjd,m.mag_auto,m.magerr_auto,m.filter,m.fwhm,m.class_star,m.exposure,m.objectid
FROM nsc_dr2.meas AS m WHERE 't'=q3c_radial_query(m.ra,m.dec,{ra0},{dec0},{rad})"""
    else:
        adql=f"""SELECT o.ra,o.dec,o.gmag,o.rmag,o.imag,o.ymag,o.zmag,o.ndet,o.deltamjd,o.id
FROM nsc_dr2.object AS o WHERE 't'=q3c_radial_query(o.ra,o.dec,{ra0},{dec0},{rad})"""
    r=requests.post(BASE,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql,'phase':'run'},timeout=60,allow_redirects=True)
    job=r.url.split('/phase')[0]
    for i in range(120):
        p=requests.get(job+"/phase",timeout=30).text.strip()
        if p in ("COMPLETED","ERROR","ABORTED"): break
        time.sleep(5)
    if p!="COMPLETED":
        return None,requests.get(job+"/error",timeout=30).text
    return requests.get(job+"/results/result",timeout=180).text,None

# meas
res,err=run(25.0,'meas')
if err: open('nsc_meas.err','w').write(err); print("MEAS ERR")
else:
    open('nsc_meas_async.csv','w').write(res); print("MEAS OK rows",res.count(chr(10)))
# object
res2,err2=run(25.0,'object')
if err2: open('nsc_obj.err','w').write(err2); print("OBJ ERR")
else:
    open('nsc_obj_async.csv','w').write(res2); print("OBJ OK rows",res2.count(chr(10)))
print("DONE")
