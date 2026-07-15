import requests, io, pandas as pd, numpy as np
RA, DEC = 313.22651, -14.84044
OD = "/tmp/rubin_pilot/forensics/170591507978387512/"

def dl_sql(q, name):
    r = requests.get("https://datalab.noirlab.edu/query/query",
        params={"sql": q, "ofmt": "csv", "async": "false"}, timeout=300)
    if r.status_code != 200 or r.text.lstrip().startswith("<") or "Error" in r.text[:200]:
        print(name, "ERROR", r.status_code, r.text[:300]); return None
    df = pd.read_csv(io.StringIO(r.text))
    df.to_csv(OD + name + ".csv", index=False)
    print(f"--- {name}: {len(df)} rows")
    return df

q = f"""SELECT ra,dec,type,flux_g,flux_r,flux_i,flux_z,flux_w1,flux_w2,ls_id,ebv,
  q3c_dist(ra,dec,{RA},{DEC})*3600 as sep_as
FROM ls_dr10.tractor WHERE q3c_radial_query(ra,dec,{RA},{DEC},0.00277778) ORDER BY sep_as"""
ls = dl_sql(q, "ls_dr10")
if ls is not None and len(ls):
    for b in ["g","r","i","z","w1","w2"]:
        f = ls["flux_"+b]
        ls["mag_"+b] = 22.5 - 2.5*np.log10(f.where(f>0))
    print(ls[["sep_as","type","mag_g","mag_r","mag_i","mag_z","mag_w1","mag_w2","ebv","ls_id"]].to_string(index=False))

q = f"""SELECT id,ra,dec,gmag,rmag,imag,zmag,ndet,nphot,deltamjd,mjd,variable10sig,class_star,
  q3c_dist(ra,dec,{RA},{DEC})*3600 as sep_as
FROM nsc_dr2.object WHERE q3c_radial_query(ra,dec,{RA},{DEC},0.00277778) ORDER BY sep_as"""
nsc = dl_sql(q, "nsc_dr2_obj")
if nsc is not None and len(nsc): print(nsc.to_string(index=False))

q = f"""SELECT source_id,ra,dec,parallax,parallax_error,pmra,pmdec,phot_g_mean_mag,bp_rp,phot_variable_flag,
  q3c_dist(ra,dec,{RA},{DEC})*3600 as sep_as
FROM gaia_dr3.gaia_source WHERE q3c_radial_query(ra,dec,{RA},{DEC},0.00833333) ORDER BY sep_as"""
g = dl_sql(q, "gaia_dr3")
if g is not None and len(g): print(g.to_string(index=False))

q = f"""SELECT source_name,ra,dec,w1mpro,w2mpro,q3c_dist(ra,dec,{RA},{DEC})*3600 as sep_as
FROM catwise2020.main WHERE q3c_radial_query(ra,dec,{RA},{DEC},0.00277778) ORDER BY sep_as"""
cw = dl_sql(q, "catwise2020")
if cw is not None and len(cw): print(cw.to_string(index=False))
