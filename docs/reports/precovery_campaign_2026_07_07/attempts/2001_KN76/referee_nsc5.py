import numpy as np, requests, io, csv, math, time
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=280,tries=4):
    for k in range(tries):
        try:
            r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
            if r.status_code==200 and not r.text.startswith('<?xml'):
                return list(csv.DictReader(io.StringIO(r.text)))
            print(f"   try{k} status {r.status_code} {r.text[:120]}")
        except Exception as e:
            print(f"   try{k} err {type(e).__name__}")
        time.sleep(6)
    return None
def sep(r1,d1,r2,d2):
    return math.hypot((r1-r2)*math.cos(math.radians(d2))*3600,(d1-d2)*3600)

def obj_cone(ra,dec,rad,label):
    rows=q(f"SELECT id,ra,dec,gmag,rmag,imag,ndet,nphot,class_star,deltamjd,mjd_first,mjd_last FROM nsc_dr2.object AS o WHERE 't'=q3c_radial_query(o.ra,o.dec,{ra},{dec},{rad/3600.0})")
    print(f"\n=== OBJECT cone {label}: {rad}\" -> {0 if rows is None else len(rows)} mean-objects ===")
    if rows:
        for r in sorted(rows,key=lambda x:sep(float(x['ra']),float(x['dec']),ra,dec)):
            s=sep(float(r['ra']),float(r['dec']),ra,dec)
            print(f"  sep={s:5.2f}\" id={r['id']} ndet={r['ndet']} dmjd={float(r['deltamjd']):.2f} r={r['rmag']} g={r['gmag']} cstar={r['class_star']} mjd0={float(r['mjd_first']):.1f} mjd1={float(r['mjd_last']):.1f}")
    return rows

# Mean-object cones (stationary-source check) at both candidate positions
obj_cone(228.8012259,-20.8267668,10.0,"CAND1 2013")
obj_cone(229.7975068,-21.0925405,10.0,"CAND2 2015")
