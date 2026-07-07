import math, json
from astroquery.jplhorizons import Horizons

def sep_as(ra1,dec1,ra2,dec2):
    dr=(ra1-ra2)*math.cos(math.radians((dec1+dec2)/2))*3600
    dd=(dec1-dec2)*3600
    return dr,dd,math.hypot(dr,dd)

cands = {
 '133189_17045': [(56362.265414,228.8012394,-20.8267605,23.32),(56362.267488,228.8012123,-20.8267731,23.06)],
 '133703_14601': [(57218.057851,229.7975286,-21.0925339,23.12),(57218.058744,229.7974849,-21.0925470,23.31)],
 '133189_15021': [(57218.046050,228.8067637,-20.8281600,22.02),(57218.046956,228.8067887,-20.8281358,21.54)],
}

# Get Horizons predicted rate + position at each candidate's exact mean MJD (observer 807 = CTIO)
for oid,dets in cands.items():
    mjd_mean = sum(d[0] for d in dets)/len(dets)
    jd = mjd_mean + 2400000.5
    obj = Horizons(id='2001 KN76', location='807', epochs=[jd])
    eph = obj.ephemerides(quantities='1,3,9,36,37', extra_precision=True)
    r = eph[0]
    pra, pdec = float(r['RA']), float(r['DEC'])
    rra = float(r['RA_rate'])   # arcsec/hour (Horizons RA_rate is *cos(dec) in "/hr for qty 3)
    rdec = float(r['DEC_rate'])
    smaa=float(r['SMAA_3sigma']); smia=float(r['SMIA_3sigma']); th=float(r['Theta_3sigma'])
    # candidate observed motion
    d0,d1 = dets[0],dets[1]
    dt_hr = (d1[0]-d0[0])*24
    dr,dd,tot = sep_as(d1[1],d1[2],d0[1],d0[2])
    obs_rra = dr/dt_hr; obs_rdec=dd/dt_hr
    # candidate mean position offset from predicted
    cra=sum(d[1] for d in dets)/2; cdec=sum(d[2] for d in dets)/2
    odr,odd,osep = sep_as(cra,cdec,pra,pdec)
    print(f"=== {oid} @ MJD {mjd_mean:.4f} ===")
    print(f"  Predicted: RA={pra:.6f} Dec={pdec:.6f} V={float(r['V']):.2f} rate=({rra:+.2f},{rdec:+.2f})\"/hr ell(SMAA={smaa:.1f},SMIA={smia:.2f},th={th:.0f})")
    print(f"  Cand mean: RA={cra:.6f} Dec={cdec:.6f}  offset=({odr:+.2f},{odd:+.2f})\" sep={osep:.2f}\"")
    print(f"  Cand motion over {dt_hr*60:.1f}min: ({obs_rra:+.2f},{obs_rdec:+.2f})\"/hr   [pred ({rra:+.2f},{rdec:+.2f})]")
    # motion match: is obs rate within tolerance of predicted?
    rate_err = math.hypot(obs_rra-rra, obs_rdec-rdec)
    print(f"  |obs_rate - pred_rate| = {rate_err:.2f}\"/hr")
    # project offset onto ellipse axes to see if within 3-sigma
    thr=math.radians(th)
    # rotate offset into ellipse frame (Theta measured from N through E typically)
    print()
