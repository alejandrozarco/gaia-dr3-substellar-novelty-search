import os
# Evaluate the Zeeman table 'coadd' rows re-measured on a coadd of in-stack visits with the XCSAO shift undone (instead of the
# mwmStar coadd, which is in the XCSAO frame and stacks visits at their individual XCSAO shifts).
import sys; sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts"))
import numpy as np, pandas as pd
import zeeman_split as Z
from sdssv import visits, coadd
t = pd.read_csv(os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/tables/magnetic_zeeman.csv"), dtype={"gaia_dr3": str, "sdss_id": str})
rows = []
for _, r in t.iterrows():
    if r["spectrum"] != "coadd": continue
    vs = [v for v in visits(r["sdss_id"]) if v["in_stack"]]
    lam, f, iv = coadd(vs); snr = float(np.sqrt(np.sum([v["snr"] ** 2 for v in vs])))
    out = dict(gaia_dr3=r["gaia_dr3"], n=len(vs), snr_old=r["snr"], snr_new=round(snr, 1))
    for k in ("Ha", "Hb"):
        m = (lam > Z.WIN[k][0]) & (lam < Z.WIN[k][1]) & np.isfinite(f); p, C = Z.fit(lam[m], f[m], iv[m], Z.L0[k], 6.0 * Z.K[k])
        out[f"B_{k}_old"] = r[f"B_split_{k}_MG"]; out[f"B_{k}_new"] = round((p[10] + p[11]) / 2 / Z.K[k], 2)
        out[f"eB_{k}_new"] = round(0.5 * np.sqrt(C[10, 10] + C[11, 11] + 2 * C[10, 11]) / Z.K[k], 2)
        out[f"sh_{k}_old"] = r[f"{k}_shift_A"]; out[f"sh_{k}_new"] = round(p[12], 1)
    rows.append(out); print(out, flush=True)
d = pd.DataFrame(rows); d["dB_Ha"] = d.B_Ha_new - d.B_Ha_old; d["dB_Hb"] = d.B_Hb_new - d.B_Hb_old
pd.set_option("display.width", 250); print(d.to_string()); d.to_csv("recoadd_eval.csv", index=False)
