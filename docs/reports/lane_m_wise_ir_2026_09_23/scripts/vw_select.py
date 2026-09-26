import json, numpy as np, pandas as pd
R = json.load(open("/tmp/track1/ms_ridge.json")); b = np.array(R["bins"]) + 0.05; ridge = np.array(R["ridge"], float); p99 = np.array(R["p99"], float); ok = np.isfinite(ridge) & np.isfinite(p99)
cref = np.array([0.8, 1.0, 1.4, 1.8, 2.0, 2.3, 2.6, 2.9, 3.3, 3.8, 4.2]); gw = np.array([1.35, 1.7, 2.2, 2.65, 2.95, 3.45, 3.9, 4.35, 4.95, 5.6, 6.1])
out = []
for T in ("varwisepure", "varwiseext"):
    d = pd.read_csv(f"vw_{T}.csv"); d["cat"] = T
    out.append(d)
d = pd.concat(out).drop_duplicates("designation", keep="first")
d["bprp"] = d.bpmag - d.rpmag; d["MG"] = d.gmag + 5*np.log10(d.plx/100)
d["d_ridge"] = d.MG - np.interp(d.bprp, b[ok], ridge[ok]); d["env"] = np.interp(d.bprp, b[ok], p99[ok])
d["gw1_exc"] = d.gmag - d.w1mag - np.interp(d.bprp, cref, gw)
sel = d[(d.d_ridge > 1.0) & (d.MG > d.env) & (d.bprp > -0.6)]
print("VarWISE unique:", len(d), " below-MS:", len(sel))
print(sel.vartype.value_counts().to_dict())
cons = sel[(sel.gw1_exc < 2.0) & (sel.blended_source.fillna(0) < 0.5) & (sel.latent_artifact.fillna(0) < 0.5)]
print("colour-consistent, not blended/latent:", len(cons)); print(cons.vartype.value_counts().to_dict())
print("SIMBAD types present:", cons.simbad_type.fillna("-").value_counts().head(25).to_dict())
cons = cons.sort_values("d_ridge", ascending=False)
cons.to_csv("vw_below_ms.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(cons[["designation", "vartype", "confidence", "period1", "suspect_period", "w1_amp", "w2_amp", "gmag", "bprp", "plx", "MG", "d_ridge", "gw1_exc", "w1mag", "simbad_type"]].to_string(index=False))
