import pyvo, warnings, numpy as np; warnings.filterwarnings("ignore")
dl = pyvo.dal.TAPService("https://datalab.noirlab.edu/tap")
for name,(ra,dec) in {"J0735":(113.76710362,-79.73630),"J2051":(312.82994747,-16.29705)}.items():
    try:
        ob = dl.search(f"select id, ra, dec, pmra, pmdec, ndet, gmag, rmag from nsc_dr2.object where ra between {ra-5/3600/np.cos(np.radians(dec))} and {ra+5/3600/np.cos(np.radians(dec))} and dec between {dec-5/3600} and {dec+5/3600}").to_table().to_pandas()
        print(name, "NSC objects", len(ob)); print(ob.to_string())
        if len(ob):
            oid = ob.sort_values("ndet").iloc[-1]["id"]
            me = dl.search(f"select mjd, filter, mag_auto, magerr_auto, ra, dec, exposure from nsc_dr2.meas where objectid='{oid}'").to_table().to_pandas()
            me.to_csv(f"nsc_{name}.csv", index=False); print(" meas", len(me), me.groupby("filter").size().to_dict())
    except Exception as e:
        print(name, "NSC ERROR", repr(e)[:300])
