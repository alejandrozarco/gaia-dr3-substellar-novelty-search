import requests, io, csv, math, json, time
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=280):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
    return r.status_code,r.text
def cone_obj(ra0,dec0,rad_as):
    adql=f"""SELECT o.id,o.ra,o.dec,o.rmag,o.ndet,o.deltamjd,o.mjd
FROM nsc_dr2.object AS o WHERE 't'=q3c_radial_query(o.ra,o.dec,{ra0},{dec0},{rad_as/3600.0})"""
    sc,txt=q(adql)
    if sc!=200 or txt.startswith('<?xml'): return None
    return list(csv.DictReader(io.StringIO(txt)))

# --- Chance-coincidence: density of single-night faint (r 22.5-23.7) sources in a large field ---
# Big 300" cone around 2013 position, count deltamjd<3 objects with r in [22.5,23.7]
for lbl,(ra,dec) in [('2013 field',(228.8012,-20.8270)),('2015 field',(229.7965,-21.0922))]:
    R=300.0
    rows=cone_obj(ra,dec,R)
    if rows is None: 
        print(lbl,"cone failed"); continue
    def isnum(x):
        try: return float(x)<50
        except: return False
    single=[r for r in rows if float(r['deltamjd'])<3.0]
    single_faint=[r for r in single if isnum(r['rmag']) and 22.5<=float(r['rmag'])<=23.7]
    area=math.pi*(R/3600.0)**2  # deg^2
    dens=len(single_faint)/area  # per deg^2
    # expected in the search ellipse ~ pi*SMAA*SMIA (arcsec^2) -> deg^2
    smaa,smia=(9.1,2.05) if '2013' in lbl else (13.0,2.56)
    ell_area=math.pi*smaa*smia/(3600.0**2)
    exp=dens*ell_area
    print(f"{lbl}: {len(rows)} total, {len(single)} single-night, {len(single_faint)} single-night & r∈[22.5,23.7] in {R}\" cone")
    print(f"   density={dens:.0f}/deg^2; ellipse area={ell_area*3600*3600:.0f} arcsec^2 -> expected chance single-night faint in ellipse = {exp:.4f}")
    time.sleep(0.5)
