import pandas as pd, numpy as np
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 50)
OD = "/tmp/rubin_pilot/forensics/170591507978387512/"
src = pd.read_csv(OD + "fink_sources_raw.csv")
fp  = pd.read_csv(OD + "fink_fp_raw.csv")

def njy_to_mag(f):
    return -2.5*np.log10(np.asarray(f, float)*1e-9) + 8.90  # nJy AB

s = src.sort_values("r:midpointMjdTai")
s["mag"] = njy_to_mag(s["r:psfFlux"])
s["mag_err"] = 1.0857*s["r:psfFluxErr"]/s["r:psfFlux"]
s["sci_mag"] = njy_to_mag(s["r:scienceFlux"])
cols = ["r:diaSourceId","r:midpointMjdTai","r:band","r:psfFlux","r:psfFluxErr","mag","mag_err","sci_mag","r:snr","r:reliability","r:extendedness","r:isDipole","r:isNegative","r:ra","r:dec","r:visit","r:detector"]
print(s[cols].to_string(index=False))
print()
flagcols = [c for c in src.columns if "pixelFlags" in c or "flag" in c.lower()]
print("Any true flags per row:")
for _, row in s.iterrows():
    trues = [c for c in flagcols if row.get(c) in (True, "True", 1)]
    print(f"  mjd {row['r:midpointMjdTai']:.4f}: {trues if trues else 'none'}")
print()
print("Fink science scores per alert:")
fs = [c for c in src.columns if c.startswith("f:")]
print(s[["r:midpointMjdTai"] + [c for c in fs if "clf" in c]].to_string(index=False))
print()
print("Crossmatch fields (non-null):")
for c in [c for c in fs if c.startswith("f:xm")]:
    v = src[c].dropna().unique()
    v = [x for x in v if str(x) not in ("", "nan", "None")]
    if len(v): print(" ", c, "=", v)
print()
f2 = fp.sort_values("r:midpointMjdTai")
f2["mag_diff"] = njy_to_mag(f2["r:psfFlux"].where(f2["r:psfFlux"]>0))
f2["sci_mag"] = njy_to_mag(f2["r:scienceFlux"].where(f2["r:scienceFlux"]>0))
print("Forced photometry:")
print(f2[["r:diaForcedSourceId","r:midpointMjdTai","r:band","r:psfFlux","r:psfFluxErr","mag_diff","r:scienceFlux","r:scienceFluxErr","sci_mag","r:visit"]].to_string(index=False))
print()
print("position scatter: RA std (mas):", np.std(s["r:ra"])*3.6e6, "Dec std (mas):", np.std(s["r:dec"])*3.6e6)
print("mean pos:", s["r:ra"].mean(), s["r:dec"].mean())
