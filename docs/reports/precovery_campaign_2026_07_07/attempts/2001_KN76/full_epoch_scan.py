import requests, io, csv, math, json, time
from astroquery.jplhorizons import Horizons
TAP = "https://datalab.noirlab.edu/tap/sync"
def q(adql, timeout=280):
    r = requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql}, timeout=timeout)
    return r.status_code, r.text
def cone_obj(ra0, dec0, rad_as):
    adql=f"""SELECT o.id,o.ra,o.dec,o.gmag,o.rmag,o.imag,o.ndet,o.class_star,o.deltamjd,o.mjd
FROM nsc_dr2.object AS o WHERE 't'=q3c_radial_query(o.ra,o.dec,{ra0},{dec0},{rad_as/3600.0})"""
    sc,txt=q(adql)
    if sc!=200 or txt.startswith('<?xml'): return None
    return list(csv.DictReader(io.StringIO(txt)))
def sep_as(ra1,dec1,ra2,dec2):
    dr=(ra1-ra2)*math.cos(math.radians((dec1+dec2)/2))*3600; dd=(dec1-dec2)*3600
    return dr,dd,math.hypot(dr,dd)

# All DECam nights (integer MJD) from SSOIS
decam_nights = [56362,56770,56836,56837,57162,57163,57164,57165,57166,57218,
                57781,57824,57875,57982,58543,58619,58641,59372,59503,59588,59954,60053,60144,60146]
# Batch Horizons for all nights at once (observer 807). Use MJD+0.15 (~night mid).
jds=[m+0.15+2400000.5 for m in decam_nights]
obj=Horizons(id='2001 KN76', location='807', epochs=jds)
eph=obj.ephemerides(quantities='1,9,36,37', extra_precision=True)
pred={}
for m,row in zip(decam_nights,eph):
    pred[m]=dict(ra=float(row['RA']),dec=float(row['DEC']),V=float(row['V']),
                 smaa=float(row['SMAA_3sigma']),smia=float(row['SMIA_3sigma']),th=float(row['Theta_3sigma']))

results=[]
for m in decam_nights:
    p=pred[m]
    rad=max(15.0, p['smaa']*1.3)
    rows=cone_obj(p['ra'],p['dec'],rad)
    if rows is None:
        print(f"MJD {m}: cone FAILED"); continue
    # nearest single-night object within ellipse (deltamjd<2, ndet small)
    best=None
    for r in rows:
        dr,dd,s=sep_as(float(r['ra']),float(r['dec']),p['ra'],p['dec'])
        dmjd=float(r['deltamjd'])
        # is this candidate's own mjd on THIS night?
        onnight = abs(float(r['mjd'])-m)<1.0
        if dmjd<3.0 and onnight and (best is None or s<best[0]):
            best=(s,dr,dd,r)
    tag=''
    if best:
        s,dr,dd,r=best
        # within-ellipse test: crude - sep < smaa and cross-track < smia*1.5
        inell = s < p['smaa']*1.1
        results.append(dict(mjd=m,pred_ra=p['ra'],pred_dec=p['dec'],V=p['V'],smaa=p['smaa'],smia=p['smia'],
                            sep=s,dr=dr,dd=dd,cand_id=r['id'],cra=float(r['ra']),cdec=float(r['dec']),
                            rmag=r['rmag'],gmag=r['gmag'],imag=r['imag'],ndet=r['ndet'],cand_mjd=float(r['mjd']),inell=inell))
        print(f"MJD {m} V~{p['V']:.1f} ell(SMAA={p['smaa']:.1f},SMIA={p['smia']:.2f}) rad={rad:.0f}\" nobj={len(rows)}: BEST sep={s:.2f}\" (dr={dr:+.1f},dd={dd:+.1f}) id={r['id']} r={r['rmag']} ndet={r['ndet']} {'<IN-ELL>' if inell else ''}")
    else:
        results.append(dict(mjd=m,pred_ra=p['ra'],pred_dec=p['dec'],V=p['V'],smaa=p['smaa'],smia=p['smia'],sep=None,cand_id=None))
        print(f"MJD {m} V~{p['V']:.1f} ell(SMAA={p['smaa']:.1f},SMIA={p['smia']:.2f}) rad={rad:.0f}\" nobj={len(rows)}: no single-night source on-night in ellipse")
    time.sleep(0.6)
json.dump({'pred':pred,'results':results}, open('full_epoch_scan.json','w'), indent=1, default=str)
print("\nWrote full_epoch_scan.json")
