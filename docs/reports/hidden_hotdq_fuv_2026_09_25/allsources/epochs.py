"""Multi-epoch photometry for the two hot DQs from the catalogues in the user's list:
NSC DR2 measurements (Astro Data Lab), PS1 DR2 detections (MAST), SkyMapper DR4 (TAP)."""
import pyvo, requests, io, numpy as np, pandas as pd, sys, warnings
warnings.filterwarnings("ignore")
OBJ = {"J0735": (113.76710362, -79.73630, 5.641, -7.907), "J2051": (312.82994747, -16.29705, 50.673, -77.539)}
def at_epoch(ra, dec, pmra, pmdec, year):
    dt = year - 2016.0
    return ra + pmra*dt/3.6e6/np.cos(np.radians(dec)), dec + pmdec*dt/3.6e6
for name,(ra,dec,pmra,pmdec) in OBJ.items():
    # NSC DR2: object table (epoch ~2016 mean) then measurements
    try:
        dl = pyvo.dal.TAPService("https://datalab.noirlab.edu/tap")
        ob = dl.search(f"select id, ra, dec, pmra, pmdec, ndet, gmag, rmag, gerr from nsc_dr2.object where q3c_radial_query(ra,dec,{ra},{dec},{5/3600})").to_table().to_pandas()
        print(name, "NSC DR2 objects within 5 arcsec:", len(ob)); print(ob.to_string()[:800])
        if len(ob):
            oid = ob.sort_values("ndet").iloc[-1]["id"]
            me = dl.search(f"select mjd, filter, mag_auto, magerr_auto, ra, dec, exposure from nsc_dr2.meas where objectid='{oid}'").to_table().to_pandas()
            me.to_csv(f"nsc_{name}.csv", index=False); print(" meas", len(me), me.groupby("filter").size().to_dict())
    except Exception as e:
        print(name, "NSC ERROR", repr(e)[:200])
    if dec > -30:
        try:
            r = requests.get("https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/detection.csv",
                             params=dict(ra=ra, dec=dec, radius=3/3600, columns="[objID,obsTime,filterID,psfFlux,psfFluxErr,psfQfPerfect,infoFlag,infoFlag2,ra,dec]"), timeout=120)
            df = pd.read_csv(io.StringIO(r.text)); df.to_csv(f"ps1_{name}.csv", index=False)
            print(name, "PS1 DR2 detections", len(df), df.groupby("filterID").size().to_dict() if len(df) else "")
        except Exception as e:
            print(name, "PS1 ERROR", repr(e)[:200])
    try:
        sm = pyvo.dal.TAPService("https://api.skymapper.nci.org.au/public/tap/")
        o = sm.search(f"select object_id, raj2000, dej2000, g_psf, g_ngood, r_ngood, u_ngood, v_ngood from dr4.master where 1=contains(point('ICRS',raj2000,dej2000), circle('ICRS',{ra},{dec},{4/3600}))").to_table().to_pandas()
        print(name, "SkyMapper DR4 master:", o.to_string()[:400])
        if len(o):
            p = sm.search(f"select p.filter, p.mag_psf, p.e_mag_psf, p.flags, p.nimaflags, p.use_in_clipped, i.date from dr4.photometry p join dr4.images i on i.image_id=p.image_id where p.object_id={int(o.iloc[0]['object_id'])}").to_table().to_pandas()
            p.to_csv(f"smss_{name}.csv", index=False); print(" SkyMapper epochs", len(p), p.groupby("filter").size().to_dict())
    except Exception as e:
        print(name, "SkyMapper ERROR", repr(e)[:300])
print("EPOCHS_DONE")
