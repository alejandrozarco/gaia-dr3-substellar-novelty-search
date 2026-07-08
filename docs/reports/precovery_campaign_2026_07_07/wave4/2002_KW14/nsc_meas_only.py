import requests, io, csv, json, math, time
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=300):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
    return r.status_code,r.text
ra0,dec0=252.0790,-24.7890
for rad_as in [20.0]:
    rad=rad_as/3600.0
    adql=f"""SELECT m.ra,m.dec,m.mjd,m.mag_auto,m.magerr_auto,m.filter,m.fwhm,m.class_star,m.exposure,m.objectid
FROM nsc_dr2.meas AS m
WHERE 't'=q3c_radial_query(m.ra,m.dec,{ra0},{dec0},{rad})"""
    for attempt in range(4):
        sc,txt=q(adql)
        print("rad",rad_as,"attempt",attempt,"HTTP",sc,"bytes",len(txt))
        if sc==200 and not txt.lstrip().startswith('<'):
            break
        time.sleep(5)
    if sc==200 and not txt.lstrip().startswith('<'):
        rows=list(csv.DictReader(io.StringIO(txt)))
        json.dump(rows,open('nsc_meas_cone20.json','w'))
        print("total meas within %g\": %d"%(rad_as,len(rows)))
        night=[r for r in rows if 57890.10<float(r['mjd'])<57890.20]
        print("=== NIGHT 2017-05-17 detections: %d ==="%len(night))
        for r in sorted(night,key=lambda x:float(x['mjd'])):
            dra=(float(r['ra'])-ra0)*3600*math.cos(math.radians(dec0)); ddec=(float(r['dec'])-dec0)*3600
            print("  mjd=%.5f dRA=%+.2f\" dDec=%+.2f\" mag=%s(%s) filt=%s fwhm=%s cstar=%s exp=%s obj=%s"%(
              float(r['mjd']),dra,ddec,r['mag_auto'],r['magerr_auto'],r['filter'],r['fwhm'],r['class_star'],r['exposure'],r['objectid']))
        # also list all epochs present (to see which exposures NSC ingested near here)
        from collections import Counter
        print("epoch mjd histogram (rounded 0.01):", dict(Counter(round(float(r['mjd']),2) for r in rows)))
    else:
        print("FAILED", txt[:300])
