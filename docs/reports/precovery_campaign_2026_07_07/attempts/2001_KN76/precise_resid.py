import math, json
from astroquery.jplhorizons import Horizons

def sep_as(ra1,dec1,ra2,dec2):
    dr=(ra1-ra2)*math.cos(math.radians((dec1+dec2)/2))*3600; dd=(dec1-dec2)*3600
    return dr,dd,math.hypot(dr,dd)

# candidate detections (individual meas): oid, list of (mjd, ra, dec, mag, filt)
dets = {
 '133189_17045': [(56362.265414,228.8012394,-20.8267605,23.32,'r'),(56362.267488,228.8012123,-20.8267731,23.06,'r')],
 '133703_14601': [(57218.057851,229.7975286,-21.0925339,23.12,'r'),(57218.058744,229.7974849,-21.0925470,23.31,'r')],
 '133188_12384': None,  # will query cone again if needed
}

# Query Horizons at each exact detection MJD (batch per object)
out={}
for oid,dd in dets.items():
    if dd is None: continue
    jds=[d[0]+2400000.5 for d in dd]
    obj=Horizons(id='2001 KN76', location='807', epochs=jds)
    eph=obj.ephemerides(quantities='1,9,36,37', extra_precision=True)
    print(f"=== {oid} ===")
    resids=[]
    for d,row in zip(dd,eph):
        pra,pdec=float(row['RA']),float(row['DEC'])
        dr,ddc,s=sep_as(d[1],d[2],pra,pdec)
        smia=float(row['SMIA_3sigma']); smaa=float(row['SMAA_3sigma']); th=float(row['Theta_3sigma'])
        # cross-track residual = projection onto minor axis. Theta is PA of major axis (deg, N->E).
        thr=math.radians(th)
        # unit vector along major axis (E component = sin? ). Use standard: major axis PA from North toward East.
        # East = +RA(dr), North = +Dec(dd). major axis direction: (E,N)=(sin th, cos th)
        maj = dr*math.sin(thr)+ddc*math.cos(thr)   # along major
        minr= dr*math.cos(thr)-ddc*math.sin(thr)   # along minor
        n_maj = maj/(smaa/3.0); n_min = minr/(smia/3.0)  # in sigma units
        print(f"  MJD {d[0]:.5f} {d[4]} mag={d[3]:.2f}: resid=({dr:+.2f},{ddc:+.2f})\" sep={s:.2f}\" | along-maj={maj:+.2f}\"({n_maj:+.1f}σ) cross-min={minr:+.2f}\"({n_min:+.1f}σ)  [SMAA={smaa:.1f} SMIA={smia:.2f} PA={th:.0f}]")
        resids.append(dict(mjd=d[0],dr=dr,dd=ddc,sep=s,maj=maj,minr=minr,n_maj=n_maj,n_min=n_min,smia=smia,smaa=smaa))
    out[oid]=resids
json.dump(out, open('precise_resid.json','w'), indent=1)
