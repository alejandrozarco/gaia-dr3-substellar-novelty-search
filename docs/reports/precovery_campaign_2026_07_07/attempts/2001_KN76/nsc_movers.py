import requests, io, csv, math, json, time
TAP = "https://datalab.noirlab.edu/tap/sync"
def q(adql, timeout=280):
    r = requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql}, timeout=timeout)
    return r.status_code, r.text

def cone_obj(ra0, dec0, rad_as):
    adql=f"""SELECT o.id, o.ra, o.dec, o.gmag, o.rmag, o.imag, o.ndet, o.nphot, o.class_star, o.deltamjd, o.mjd
FROM nsc_dr2.object AS o
WHERE 't'=q3c_radial_query(o.ra, o.dec, {ra0}, {dec0}, {rad_as/3600.0})"""
    sc,txt=q(adql)
    if sc!=200 or txt.startswith('<?xml'): 
        print("ERR",sc,txt[:300]); return []
    return list(csv.DictReader(io.StringIO(txt)))

def sep_as(ra1,dec1,ra2,dec2):
    dr=(ra1-ra2)*math.cos(math.radians(dec2))*3600
    dd=(dec1-dec2)*3600
    return math.hypot(dr,dd)

# All predicted DECam-night positions (from Horizons) for the boxes we search:
targets = {
 '2013-03-11': (228.801221, -20.826958, 9.08, 2.05),   # ra,dec,SMAA,SMIA (3sig, arcsec)
 '2014-04-23': (229.721510, -21.097827, 11.23, 2.32),
 '2015-05-20': (230.716605, -21.351665, 13.50, 2.56),
 '2015-05-24': (230.630988, -21.330356, 13.45, 2.56),
 '2015-07-15': (229.796537, -21.092174, 12.99, 2.56),  # use last-frame position of night
 '2019-05-16': (237.215158, -22.801903, 25.94, 3.44),
}

allres={}
for lbl,(ra0,dec0,smaa,smia) in targets.items():
    # search radius = SMAA*1.5 buffer, min 20"
    rad = max(20.0, smaa*1.4)
    rows = cone_obj(ra0,dec0,rad)
    # candidates: single-epoch-ish (deltamjd small) OR ndet low, near track, not clearly stellar-static
    cands=[]
    for r in rows:
        s = sep_as(float(r['ra']),float(r['dec']),ra0,dec0)
        dmjd=float(r['deltamjd']); ndet=int(r['ndet'])
        # A mover appears as an object that exists only briefly (deltamjd~0) -> single night
        cands.append((s,dmjd,ndet,r))
    single = [c for c in cands if c[1] < 2.0]  # deltamjd < 2 days => single-night object
    print(f"[{lbl}] rad={rad:.0f}\" -> {len(rows)} objects, {len(single)} single-night (deltamjd<2d)")
    for s,dmjd,ndet,r in sorted(single,key=lambda x:x[0]):
        print(f"    sep={s:5.1f}\" id={r['id']} ra={float(r['ra']):.6f} dec={float(r['dec']):.6f} g={r['gmag']} r={r['rmag']} i={r['imag']} ndet={ndet} dmjd={dmjd:.3f} cstar={r['class_star']} mjd={r['mjd']}")
    allres[lbl]={'ra0':ra0,'dec0':dec0,'smaa':smaa,'smia':smia,'rad':rad,'n_obj':len(rows),
                 'single':[{'sep':s,'dmjd':dmjd,'ndet':ndet,**r} for s,dmjd,ndet,r in single]}
    time.sleep(1)
json.dump(allres, open('nsc_movers.json','w'), indent=1)
print("\nWrote nsc_movers.json")
