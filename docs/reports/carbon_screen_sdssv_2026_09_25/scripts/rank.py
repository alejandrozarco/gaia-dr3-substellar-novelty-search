import pandas as pd, numpy as np
o=pd.read_csv("screen2_out.csv",dtype={"sdss_id":str,"gaia":str})
s=pd.read_csv("daq_sample.csv",dtype={"sdss_id":str,"gaia_dr3_source_id":str})
s["bp_rp"]=s.bp_mag-s.rp_mag
with np.errstate(invalid="ignore"): s["MG"]=s.g_mag+5*np.log10(s.plx/100)
o=o.merge(s[["sdss_id","classification","teff","logg","g_mag","bp_rp","MG","is_control"]],on="sdss_id")
ok=o[o.status=="ok"].copy()
def visok(x):
    try: v=[float(a) for a in str(x).split("/") if a!=""]
    except: return 0
    return sum(a>3 for a in v), len(v)
ok["vis_pos"]=ok.C_vis.apply(lambda x: visok(x)[0]); ok["vis_n"]=ok.C_vis.apply(lambda x: visok(x)[1])
bg=ok[~ok.is_control]
print("screened", len(ok), "p99 C", round(np.percentile(bg.C,99),2), "p99.5", round(np.percentile(bg.C,99.5),2))
top=ok[(ok.C>=6.5)|(ok.CI>=7)|(ok.CII>=7)].sort_values("C",ascending=False)
pd.set_option("display.width",250)
print(top[["sdss_id","gaia","is_control","classification","teff","logg","g_mag","bp_rp","MG","snr_max","C","C_v","CI","CI_v","CII","CII_v","HeI","C_vis"]].to_string())
top.to_csv("top_hits.csv",index=False)
