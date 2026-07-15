import requests, io, pandas as pd, numpy as np
RA, DEC = 313.22651, -14.84044
OD = "/tmp/rubin_pilot/forensics/170591507978387512/"
HDR = {"X-DL-AuthToken": "anonymous.0.0.anon_access"}
def dl_sql(q, name):
    r = requests.get("https://datalab.noirlab.edu/query/query",
        params={"sql": q, "ofmt": "csv", "async": "false"}, headers=HDR, timeout=300)
    if r.status_code != 200:
        print(name, "ERROR", r.status_code, r.text[:200]); return None
    try:
        df = pd.read_csv(io.StringIO(r.text))
    except Exception as e:
        print(name, "parse err", r.text[:200]); return None
    df.to_csv(OD+name+".csv", index=False)
    print(f"--- {name}: {len(df)} rows"); return df

# full flux + nobs + dchisq detail for the LS source
q = f"""SELECT ls_id,ra,dec,type,flux_g,flux_r,flux_i,flux_z,flux_ivar_g,flux_ivar_r,flux_ivar_i,flux_ivar_z,
 nobs_g,nobs_r,nobs_i,nobs_z,snr_g,snr_r,snr_i,snr_z,shape_r,sersic,
 q3c_dist(ra,dec,{RA},{DEC})*3600 as sep_as
FROM ls_dr10.tractor WHERE ls_id=10995375804519828"""
d = dl_sql(q, "ls_dr10_detail")
if d is not None: print(d.to_string(index=False))

# photo-z (if table exists)
q = f"""SELECT ls_id, z_phot_median, z_phot_std, z_spec FROM ls_dr10.photo_z WHERE ls_id=10995375804519828"""
pz = dl_sql(q, "ls_dr10_photoz")
if pz is not None and len(pz): print(pz.to_string(index=False))

# NSC DR2 individual measurements (in case object table missed it)
q = f"""SELECT measid,mjd,filter,mag_auto,magerr_auto,class_star,
 q3c_dist(ra,dec,{RA},{DEC})*3600 as sep_as
FROM nsc_dr2.meas WHERE q3c_radial_query(ra,dec,{RA},{DEC},0.00138889) ORDER BY mjd"""
m = dl_sql(q, "nsc_dr2_meas")
if m is not None and len(m): print(m.to_string(index=False))

# unWISE
q = f"""SELECT unwise_objid,ra,dec,flux_w1,flux_w2, q3c_dist(ra,dec,{RA},{DEC})*3600 as sep_as
FROM unwise_dr1.object WHERE q3c_radial_query(ra,dec,{RA},{DEC},0.00277778) ORDER BY sep_as"""
uw = dl_sql(q, "unwise_dr1")
if uw is not None and len(uw): print(uw.head(10).to_string(index=False))
