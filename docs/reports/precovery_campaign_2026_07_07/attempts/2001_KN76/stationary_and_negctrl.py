import requests, io, csv, math, json, time
from astroquery.jplhorizons import Horizons
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=280):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
    return r.status_code,r.text
def cone_obj(ra0,dec0,rad_as,extra=""):
    adql=f"""SELECT o.id,o.ra,o.dec,o.gmag,o.rmag,o.imag,o.ndet,o.class_star,o.deltamjd,o.mjd
FROM nsc_dr2.object AS o WHERE 't'=q3c_radial_query(o.ra,o.dec,{ra0},{dec0},{rad_as/3600.0}){extra}"""
    sc,txt=q(adql)
    if sc!=200 or txt.startswith('<?xml'): return None
    return list(csv.DictReader(io.StringIO(txt)))
def sep_as(ra1,dec1,ra2,dec2):
    dr=(ra1-ra2)*math.cos(math.radians((dec1+dec2)/2))*3600; dd=(dec1-dec2)*3600
    return math.hypot(dr,dd)

# --- STATIONARY-SOURCE REJECTION ---
# For each candidate, list ALL mean objects within 3" and check for a persistent (deltamjd large, ndet high) source.
cand_pos={'133189_17045':(228.80122,-20.826767),'133703_14601':(229.797507,-21.092540)}
print("=== STATIONARY-SOURCE CHECK (all objects within 3\") ===")
for oid,(ra,dec) in cand_pos.items():
    rows=cone_obj(ra,dec,3.0)
    print(f"\n{oid} @ ({ra},{dec}):")
    for r in rows:
        s=sep_as(float(r['ra']),float(r['dec']),ra,dec)
        print(f"   sep={s:.2f}\" id={r['id']} ndet={r['ndet']} deltamjd={float(r['deltamjd']):.2f} r={r['rmag']} cstar={r['class_star']} mjd={float(r['mjd']):.3f}")

# --- NEGATIVE CONTROL: +1 deg Dec offset, same two nights, same search ---
print("\n\n=== NEGATIVE CONTROL (+1 deg Dec offset) ===")
nights={56362:(228.801217,-20.826957,9.1,2.05),57218:(229.797647,-21.092806,13.0,2.56)}
for m,(ra0,dec0,smaa,smia) in nights.items():
    for tag,dcoff in [('TRUE',0.0),('OFFSET+1deg',1.0)]:
        d0=dec0+dcoff
        rad=max(15.0,smaa*1.3)
        rows=cone_obj(ra0,d0,rad)
        # count single-night (deltamjd<3) on-night sources in ellipse
        onnight=[r for r in rows if float(r['deltamjd'])<3.0 and abs(float(r['mjd'])-m)<1.0 and sep_as(float(r['ra']),float(r['dec']),ra0,d0)<smaa*1.1]
        print(f"  MJD {m} [{tag}] rad={rad:.0f}\": total_obj={len(rows)}, single-night-on-night-in-ellipse={len(onnight)}")
        for r in onnight:
            s=sep_as(float(r['ra']),float(r['dec']),ra0,d0)
            print(f"       sep={s:.2f}\" id={r['id']} r={r['rmag']} ndet={r['ndet']} mjd={float(r['mjd']):.3f}")
    time.sleep(0.5)
