import os
# XCSAO velocities of the in-stack visits for the 30 stars in the public Zeeman table (the mwmStar coadd is in the XCSAO rest frame).
import sys; sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts"))
import numpy as np, pandas as pd
from sdssv import visits
t = pd.read_csv(os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/tables/magnetic_zeeman.csv"), dtype={"gaia_dr3": str, "sdss_id": str})
C = 299792.458; rows = []
for _, r in t.iterrows():
    vs = [v for v in visits(r["sdss_id"]) if v["in_stack"]]
    v = np.array([x["xcsao_v"] for x in vs]); w = np.array([x["snr"] ** 2 for x in vs])
    vm = np.sum(v * w) / np.sum(w) if len(v) else np.nan
    rows.append(dict(gaia_dr3=r["gaia_dr3"], n_instack=len(vs), v_xcsao=[round(x) for x in v], v_mean=round(vm), dHa_A=round(-6564.61 * vm / C, 1), dHb_A=round(-4862.68 * vm / C, 1),
                     Ha_shift=r["Ha_shift_A"], Hb_shift=r["Hb_shift_A"], spectrum=r["spectrum"]))
d = pd.DataFrame(rows); pd.set_option("display.width", 250); print(d.to_string())
