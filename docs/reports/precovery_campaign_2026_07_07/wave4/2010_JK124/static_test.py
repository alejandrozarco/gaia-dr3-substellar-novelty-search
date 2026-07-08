#!/usr/bin/env python3
"""Static-source rejection (rule 6): for each candidate measurement, get its objectid,
then list ALL measurements of that object across all nights. A persistent star spans
many nights; the moving TNO appears only at same-night same-position."""
import urllib.request, urllib.parse, csv, math
TAP="https://datalab.noirlab.edu/tap/sync"
def tap(q):
    data=urllib.parse.urlencode({"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q}).encode()
    return urllib.request.urlopen(TAP,data=data,timeout=120).read().decode()

CANDS=[
 ("2014-06-06 e2",0.26,"c4d.320434.32.1594"),
 ("2015-06-20 e1",0.42,"c4d.452212.29.4741"),
 ("2015-06-20 e2",0.37,"c4d.452213.29.5421"),
 ("2016-03-08 e1",0.97,"c4d.524496.28.10505"),
]
for label,sep,measid in CANDS:
    print("="*70)
    print(f"CANDIDATE {label}  sep={sep}\"  measid={measid}")
    q=(f"SELECT measid,objectid,ra,dec,mjd,mag_auto,filter,exposure,class_star,fwhm "
       f"FROM nsc_dr2.meas WHERE measid='{measid}'")
    r=list(csv.DictReader(tap(q).splitlines()))
    if not r:
        print("  meas not found!"); continue
    m=r[0]; oid=m["objectid"]
    print(f"  objectid={oid}  ra={m['ra']} dec={m['dec']} mag={m['mag_auto']} {m['filter']} cstar={m['class_star']}")
    # object table entry
    qo=(f"SELECT id,ra,dec,ndet,ndetr,ndetg,ndeti,ndetz,ndety,ndetu,ndetvr,"
        f"mjdstart,mjddiff,deltamjd,variable10sig,nphot FROM nsc_dr2.object WHERE id='{oid}'")
    ro=list(csv.DictReader(tap(qo).splitlines()))
    if ro:
        o=ro[0]
        print(f"  OBJECT ndet={o['ndet']} (r={o['ndetr']} g={o['ndetg']} i={o['ndeti']} z={o['ndetz']} y={o['ndety']} vr={o['ndetvr']})")
        print(f"         mjdstart={o['mjdstart']} deltamjd={o['deltamjd']} (span days) nphot={o['nphot']}")
    # all measurements of this object
    qa=(f"SELECT mjd,ra,dec,mag_auto,filter,exposure FROM nsc_dr2.meas "
        f"WHERE objectid='{oid}' ORDER BY mjd")
    ra_all=list(csv.DictReader(tap(qa).splitlines()))
    print(f"  ALL {len(ra_all)} measurements of objectid {oid}:")
    for a in ra_all:
        print(f"     mjd={a['mjd']:>18} {a['filter']:>3} mag={a['mag_auto']:>9} exp={a['exposure']}")
