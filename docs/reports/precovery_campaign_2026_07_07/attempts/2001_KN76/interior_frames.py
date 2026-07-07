import requests, io, csv, math, json
from astroquery.jplhorizons import Horizons
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=280):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
    return r.status_code,r.text

# The 4 r-frames on 2013-03-11: tu2088892, tu2090119, tu2091019, tu2092162
# Get their MJD/depth from exposure table, and predicted object pos at each.
adql=f"""SELECT e.exposure,e.mjd,e.depth95,e.fwhm,e.exptime FROM nsc_dr2.exposure e
WHERE e.exposure IN ('tu2088892','tu2090119','tu2091019','tu2092162')"""
sc,txt=q(adql)
rows=list(csv.DictReader(io.StringIO(txt)))
rows.sort(key=lambda r:float(r['mjd']))
print("=== 2013-03-11 four r-frames ===")
mjds=[float(r['mjd']) for r in rows]
jds=[m+2400000.5 for m in mjds]
obj=Horizons(id='2001 KN76',location='807',epochs=jds)
eph=obj.ephemerides(quantities='1,9,36,37',extra_precision=True)
for r,row in zip(rows,eph):
    print(f"  {r['exposure']} mjd={float(r['mjd']):.5f} depth95={float(r['depth95']):.2f} fwhm={r['fwhm']} predRA={float(row['RA']):.6f} predDec={float(row['DEC']):.6f}")
print("\nNSC detected the source on ONLY tu2088892 (mjd 56362.2654) & tu2092162 (56362.2675).")
print("Interior frames tu2090119, tu2091019: no NSC detection grouped. Check depths above.")

# predicted motion across the 4 frames (~5 min span): total displacement
d_span=(mjds[-1]-mjds[0])*24  # hr
print(f"\nFrame span: {d_span*60:.1f} min. Predicted rate ~1.2\"/hr -> total motion ~{1.2*d_span:.2f}\" across night.")
