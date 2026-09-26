"""Query SDSS-V DR20 CAS per-visit RVs (mwm_apogee_allvisit, mwm_boss_allvisit) for targets.csv Gaia DR3 ids, in batches.
Failed batches are logged as HOLE lines and retried at the end."""
import requests, io, time, pandas as pd, sys
CAS = "https://skyserver.sdss.org/dr20/SkyServerWS/SearchTools/SqlSearch"
Q = {"apogee": "SELECT gaia_dr3_source_id, sdss_id, telescope, mjd, jd, v_rad, v_rel, e_v_rel, bc, snr, spectrum_flags, doppler_teff, doppler_logg, doppler_rchi2, n_components FROM mwm_apogee_allvisit WHERE gaia_dr3_source_id IN ({})",
     "boss": "SELECT gaia_dr3_source_id, sdss_id, telescope, mjd, tai_beg, xcsao_v_rad, xcsao_e_v_rad, xcsao_rxc, xcsao_teff, snr, g_mag FROM mwm_boss_allvisit WHERE gaia_dr3_source_id IN ({})"}
ids = pd.read_csv("targets.csv", dtype=str).gaia.tolist(); B = 250
def run(kind, chunk):
    for k in range(4):
        try:
            r = requests.get(CAS, params=dict(cmd=Q[kind].format(",".join(chunk)), format="csv"), timeout=300)
            if r.status_code == 200 and (r.text.startswith("#Table") or r.text.startswith("gaia")):
                t = r.text.split("\n", 1)[1] if r.text.startswith("#Table") else r.text
                return pd.read_csv(io.StringIO(t), dtype=str)
        except Exception: pass
        time.sleep(3 + 5 * k)
    return None
for kind in ("apogee", "boss"):
    out = []; holes = []
    for i in range(0, len(ids), B):
        d = run(kind, ids[i:i + B])
        if d is None: holes.append(i); print("HOLE", kind, i, flush=True)
        else: out.append(d)
        time.sleep(0.5)
    for i in holes:
        d = run(kind, ids[i:i + B])
        if d is not None: out.append(d); print("hole filled", kind, i, flush=True)
        else: print("HOLE_FINAL", kind, i, flush=True)
    df = pd.concat(out) if out else pd.DataFrame(); df.to_csv(f"rv_{kind}.csv", index=False)
    print(kind, "rows", len(df), "objects", df.gaia_dr3_source_id.nunique() if len(df) else 0, flush=True)
print("RV_QUERY_DONE")
