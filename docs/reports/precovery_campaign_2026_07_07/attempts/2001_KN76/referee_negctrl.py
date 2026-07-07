import numpy as np, requests, io, csv, math, time
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=290,tries=5):
    for k in range(tries):
        try:
            r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
            if r.status_code==200 and not r.text.startswith('<?xml'):
                return list(csv.DictReader(io.StringIO(r.text)))
        except Exception as e: print(f"  try{k} {type(e).__name__}")
        time.sleep(7)
    return None
def sep(r1,d1,r2,d2): return math.hypot((r1-r2)*math.cos(math.radians(d2))*3600,(d1-d2)*3600)

# For each candidate night, count single-night objects (on that night) that fall inside the 3sigma ellipse
# at the TRUE predicted position vs several OFFSET positions (+1deg dec and a few RA offsets).
# Ellipse test: point inside if (along/a)^2+(cross/b)^2 <=1, a=SMAA(3s), b=SMIA(3s), theta=PA.
def in_ellipse(dra,ddec,a,b,theta_deg):
    th=math.radians(theta_deg)
    along=dra*math.sin(th)+ddec*math.cos(th)
    cross=dra*math.cos(th)-ddec*math.sin(th)
    return (along/a)**2+(cross/b)**2<=1.0, along, cross

def test(ra0,dec0,a,b,theta,mjd_lo,mjd_hi,label):
    # cone bigger than ellipse, restrict to single-night on the right night
    rows=q(f"""SELECT id,ra,dec,rmag,ndet,deltamjd,mjd FROM nsc_dr2.object AS o
      WHERE 't'=q3c_radial_query(o.ra,o.dec,{ra0},{dec0},{max(a*1.5,20)/3600.0})
      AND o.deltamjd<2.0 AND o.mjd BETWEEN {mjd_lo} AND {mjd_hi}""")
    if rows is None: print(f"{label}: QUERY FAIL"); return
    inside=[]
    for r in rows:
        dra=(float(r['ra'])-ra0)*3600*math.cos(math.radians(dec0)); ddec=(float(r['dec'])-dec0)*3600
        ok,al,cr=in_ellipse(dra,ddec,a,b,theta)
        if ok: inside.append((r['id'],float(r['rmag']),al,cr))
    print(f"{label}: {len(rows)} single-night objs in cone, {len(inside)} INSIDE 3sig ellipse")
    for i in inside: print(f"    id={i[0]} r={i[1]:.2f} along={i[2]:+.2f} cross={i[3]:+.2f}")

# 2013 night: mjd ~56362, ellipse a=9.08 b=2.05 theta=-15.30
print("### 2013-03-11 night (mjd 56361.5-56362.5)")
test(228.801221,-20.826958,9.08,2.05,-15.30,56361.5,56362.5,"  TRUE 2013")
test(228.801221,-19.826958,9.08,2.05,-15.30,56361.5,56362.5,"  OFFSET +1degDec 2013")
test(228.301221,-20.826958,9.08,2.05,-15.30,56361.5,56362.5,"  OFFSET -0.5degRA 2013")
test(229.301221,-20.826958,9.08,2.05,-15.30,56361.5,56362.5,"  OFFSET +0.5degRA 2013")

print("\n### 2015-07-15 night (mjd 57217.5-57218.5)")
test(229.796537,-21.092174,12.99,2.56,-15.02,57217.5,57218.5,"  TRUE 2015")
test(229.796537,-20.092174,12.99,2.56,-15.02,57217.5,57218.5,"  OFFSET +1degDec 2015")
test(229.296537,-21.092174,12.99,2.56,-15.02,57217.5,57218.5,"  OFFSET -0.5degRA 2015")
test(230.296537,-21.092174,12.99,2.56,-15.02,57217.5,57218.5,"  OFFSET +0.5degRA 2015")
