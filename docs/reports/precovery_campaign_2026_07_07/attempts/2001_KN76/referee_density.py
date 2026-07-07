import numpy as np, requests, io, csv, math, time
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=290,tries=5):
    for k in range(tries):
        try:
            r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
            if r.status_code==200 and not r.text.startswith('<?xml'):
                return list(csv.DictReader(io.StringIO(r.text)))
            if '<?xml' in r.text: print("  SQLERR",r.text[r.text.find('ERROR'):r.text.find('ERROR')+140])
            else: print("  status",r.status_code)
        except Exception as e:
            print(f"  try{k} {type(e).__name__}")
        time.sleep(7)
    return None

# Count single-night (deltamjd<2) NSC objects with faint r in [22.5,23.7] in a big field around each candidate.
# This is the population that could randomly fall in the ellipse and mimic a mover.
def density(ra,dec,fieldrad_as,label):
    rows=q(f"""SELECT id,ra,dec,rmag,ndet,deltamjd FROM nsc_dr2.object AS o
      WHERE 't'=q3c_radial_query(o.ra,o.dec,{ra},{dec},{fieldrad_as/3600.0})
      AND o.deltamjd<2.0 AND o.rmag BETWEEN 22.5 AND 23.7 AND o.rmag<50""")
    n=0 if rows is None else len(rows)
    area=math.pi*fieldrad_as**2
    dens=n/area  # per sq arcsec
    print(f"\n{label}: {n} single-night faint(22.5-23.7) objs in {fieldrad_as}\" field (area={area:.0f} sq\")")
    print(f"   surface density = {dens:.3e} /sq\" = {dens*3600:.4f} /sq arcmin")
    return dens

# ellipse area for each epoch (3sigma). Expected number in ellipse = dens * (pi*a*b), a=SMAA/?
# NOTE report used 3-sigma SMAA/SMIA directly as the *search* ellipse; use that as the acceptance area.
d2013=density(228.8012259,-20.8267668,300.0,"FIELD 2013")
d2015=density(229.7975068,-21.0925405,300.0,"FIELD 2015")

# Acceptance ellipse: the box actually used was the 3-sigma ellipse. But the candidate landed at ~0.7-1.1"
# from center on the MINOR axis. The relevant acceptance region for "a source this consistent" is roughly
# the sub-ellipse out to the observed offset. Compute two numbers:
for lbl,d,smaa,smia in [("2013",d2013,9.08,2.05),("2015",d2015,12.99,2.56)]:
    a=smaa; b=smia  # 3-sigma semi-axes in arcsec
    area_full=math.pi*a*b
    exp_full=d*area_full
    print(f"\n[{lbl}] 3sig ellipse area={area_full:.1f} sq\" -> expected # single-night faint = {exp_full:.4f}")

# Also: how many single-night faint objects fall ON that night specifically?
# The object table deltamjd is per-object; a single-night object's mjd tells us its night.
