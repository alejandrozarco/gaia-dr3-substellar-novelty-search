import requests, io, csv, math, json, time
from astroquery.jplhorizons import Horizons
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=280):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
    return r.status_code,r.text
def cone_meas_byexp_disabled(): pass
def cone_obj(ra0,dec0,rad_as):
    adql=f"""SELECT o.id,o.ra,o.dec,o.rmag,o.gmag,o.ndet,o.deltamjd,o.mjd
FROM nsc_dr2.object AS o WHERE 't'=q3c_radial_query(o.ra,o.dec,{ra0},{dec0},{rad_as/3600.0})"""
    sc,txt=q(adql)
    if sc!=200 or txt.startswith('<?xml'): return None
    return list(csv.DictReader(io.StringIO(txt)))
def sep_as(ra1,dec1,ra2,dec2):
    dr=(ra1-ra2)*math.cos(math.radians((dec1+dec2)/2))*3600; dd=(dec1-dec2)*3600
    return dr,dd,math.hypot(dr,dd)

# Predicted position on EACH 2015-05 night at the VR exposure times; look for ANY source within ellipse
print("=== 2015-05 run: predicted pos per night + nearest single-night NSC source (deltamjd<3) ===")
run_mjds=[57162.126,57163.127,57164.211,57166.124]
jds=[m+2400000.5 for m in run_mjds]
obj=Horizons(id='2001 KN76',location='807',epochs=jds)
eph=obj.ephemerides(quantities='1,9,36,37',extra_precision=True)
for m,row in zip(run_mjds,eph):
    pra,pdec=float(row['RA']),float(row['DEC']); smaa=float(row['SMAA_3sigma']);smia=float(row['SMIA_3sigma'])
    rows=cone_obj(pra,pdec,max(18,smaa*1.3))
    onn=[]
    for r in rows or []:
        dr,dd,s=sep_as(float(r['ra']),float(r['dec']),pra,pdec)
        if float(r['deltamjd'])<3.0 and abs(float(r['mjd'])-m)<1.0:
            onn.append((s,dr,dd,r))
    onn.sort()
    best="none" if not onn else f"sep={onn[0][0]:.1f}\" r={onn[0][3]['rmag']} id={onn[0][3]['id']}"
    print(f"  MJD {m:.3f} pred=({pra:.5f},{pdec:.5f}) V={float(row['V']):.2f} SMAA={smaa:.1f}: {len(rows or [])} obj, on-night-single={len(onn)} -> {best}")
    time.sleep(0.4)

# CO-FIT: use the two detection points (2013, 2015) as if adding to arc. 
# Simple test: their along-track residual vs JPL. If both share ~same small offset, consistent single orbit.
print("\n=== along-track residuals (from precise_resid.json) ===")
pr=json.load(open('precise_resid.json'))
for oid,rs in pr.items():
    maj=[x['maj'] for x in rs]; minr=[x['minr'] for x in rs]
    print(f"  {oid}: along-track {sum(maj)/len(maj):+.2f}\"  cross-track {sum(minr)/len(minr):+.2f}\"")
