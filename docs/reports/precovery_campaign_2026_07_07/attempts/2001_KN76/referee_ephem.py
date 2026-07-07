import numpy as np
from astroquery.jplhorizons import Horizons

# Exact frame MJDs from astrometry_for_review.csv (UTC)
frames = [
    ("133189_17045", 56362.265414, 228.8012394, -20.8267605, 23.32),
    ("133189_17045", 56362.267488, 228.8012123, -20.8267731, 23.06),
    ("133703_14601", 57218.057851, 229.7975286, -21.0925339, 23.12),
    ("133703_14601", 57218.058744, 229.7974849, -21.0925470, 23.31),
]

# Horizons uses JD_TDB epochs list. Give exact MJD->JD (UTC). astroquery epochs assumed UTC.
jds = [56362.265414+2400000.5, 56362.267488+2400000.5,
       57218.057851+2400000.5, 57218.058744+2400000.5]

obj = Horizons(id='2001 KN76', location='807', epochs=jds)
eph = obj.ephemerides(quantities='1,36,37,9')
cols = ['datetime_str','RA','DEC','V','RA_3sigma','DEC_3sigma','SMAA_3sigma','SMIA_3sigma','Theta_3sigma']
print("EPHEMERIS at exact frame MJDs:")
for c in cols:
    if c in eph.colnames:
        print(f"  {c}: {list(eph[c])}")

print("\n--- RESIDUALS (measured - predicted) ---")
for i,(fid,mjd,mra,mdec,mag) in enumerate(frames):
    pra = float(eph['RA'][i]); pdec = float(eph['DEC'][i])
    cosd = np.cos(np.radians(pdec))
    dra = (mra-pra)*3600.0*cosd
    ddec = (mdec-pdec)*3600.0
    sep = np.hypot(dra,ddec)
    smaa = float(eph['SMAA_3sigma'][i]); smia=float(eph['SMIA_3sigma'][i])
    theta = float(eph['Theta_3sigma'][i])
    # rotate residual into ellipse frame. Theta = PA of SMAA (deg, from N through E typically)
    # dEast=dra, dNorth=ddec. PA measured from North to East.
    th = np.radians(theta)
    # component along SMAA (major, along-track): project onto (sin th, cos th) in (E,N)
    along = dra*np.sin(th)+ddec*np.cos(th)
    cross = dra*np.cos(th)-ddec*np.sin(th)
    print(f"{fid} mjd={mjd:.6f}: dRA={dra:+.3f}\" dDec={ddec:+.3f}\" sep={sep:.3f}\"")
    print(f"    predV={float(eph['V'][i]):.2f} measr={mag} | SMAA3s={smaa:.2f} SMIA3s={smia:.2f} theta={theta:.2f}")
    print(f"    along(major)={along:+.3f}\" ({along/(smaa/3):+.2f}sig) cross(minor)={cross:+.3f}\" ({cross/(smia/3):+.2f}sig)")
