#!/usr/bin/env python3
"""Static-source rejection (rule 6) via position-indexed object-table queries.
For each candidate detection position, find NSC mean-objects within 2.5" and report
ndet / per-band ndet / deltamjd. A persistent field star spans many nights (large
deltamjd, many ndet). The moving TNO should have NO persistent object at that position
(or only a same-night 1-2 detection object)."""
import urllib.request, urllib.parse, csv, math, time
TAP="https://datalab.noirlab.edu/tap/sync"
def tap(q,retries=4):
    data=urllib.parse.urlencode({"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q}).encode()
    for i in range(retries):
        try: return urllib.request.urlopen(TAP,data=data,timeout=180).read().decode()
        except Exception as e:
            last=str(e); time.sleep(3)
    return "ERR "+last

# candidate: label, det_ra, det_dec, sep, mag, filt
CANDS=[
 ("2014-06-06 e2",243.477505,-29.543449,0.26,"21.74","r"),  # will refine ra/dec below
 ("2015-06-20 e1",244.744031,-29.394707,0.42,"21.79","r"),
 ("2015-06-20 e2",244.743987,-29.394699,0.37,"21.79","r"),
 ("2016-03-08 e1",247.962213,-29.466620,0.97,"21.79","VR"),
]
# get precise detection ra/dec from the box detections csv
det={}
for row in csv.DictReader(open("/tmp/precovery_wave4/2010_JK124/nsc_box_detections.csv")):
    det[row["measid"]]=row
MEAS={"2014-06-06 e2":"c4d.320434.32.1594","2015-06-20 e1":"c4d.452212.29.4741",
      "2015-06-20 e2":"c4d.452213.29.5421","2016-03-08 e1":"c4d.524496.28.10505"}
for i,(label,ra,dec,sep,mag,filt) in enumerate(CANDS):
    mid=MEAS[label]
    if mid in det:
        ra=float(det[mid]["meas_ra"]); dec=float(det[mid]["meas_dec"])
    cosd=math.cos(math.radians(dec))
    print("="*72)
    print(f"CANDIDATE {label}  det=({ra:.6f},{dec:+.6f})  sep_from_pred={sep}\"  mag={mag} {filt}")
    for rad in [1.5,2.5]:
        dra=rad/3600.0/cosd; ddec=rad/3600.0
        q=(f"SELECT id,ra,dec,ndet,ndetr,ndetg,ndeti,ndetz,ndety,ndetvr,deltamjd,mjd "
           f"FROM nsc_dr2.object WHERE ra BETWEEN {ra-dra:.7f} AND {ra+dra:.7f} "
           f"AND dec BETWEEN {dec-ddec:.7f} AND {dec+ddec:.7f}")
        rows=list(csv.DictReader(tap(q).splitlines()))
        print(f"  mean-objects within {rad}\": {len(rows)}")
        for o in rows:
            osep=math.hypot((float(o['ra'])-ra)*cosd,(float(o['dec'])-dec))*3600.0
            print(f"     sep={osep:5.2f}\" id={o['id']:>14} ndet={o['ndet']:>3} "
                  f"(r={o['ndetr']} g={o['ndetg']} i={o['ndeti']} z={o['ndetz']} y={o['ndety']} vr={o['ndetvr']}) "
                  f"deltamjd={o['deltamjd']}")
        if rows: break
