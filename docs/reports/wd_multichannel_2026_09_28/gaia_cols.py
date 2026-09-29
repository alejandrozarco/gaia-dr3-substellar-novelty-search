"""Gaia DR3 columns for the SDSS-V white-dwarf sample by source_id (chunks of 800). Writes gaia_cols.csv; failed chunks -> gaia_failed.txt."""
import os
import pandas as pd, time
from astroquery.gaia import Gaia
T = pd.read_csv(os.path.expanduser("~/claude_projects/spectra_store/sdssv_dr20/targets.csv"), dtype={"gaia_dr3_source_id": str}, low_memory=False)
ids = [i for i in T.gaia_dr3_source_id.dropna().unique() if i.isdigit()]; out = []; bad = []
Q = "SELECT source_id, ra, dec, l, b, parallax, parallax_error, pmra, pmdec, ruwe, astrometric_excess_noise_sig, ipd_frac_multi_peak, ipd_gof_harmonic_amplitude, phot_g_n_obs, phot_g_mean_flux, phot_g_mean_flux_error, phot_g_mean_mag, bp_rp, phot_bp_rp_excess_factor, phot_variable_flag, radial_velocity FROM gaiadr3.gaia_source WHERE source_id IN ({})"
for k in range(0, len(ids), 800):
    ch = ids[k:k + 800]
    for a in range(4):
        try: out.append(Gaia.launch_job(Q.format(",".join(ch))).get_results().to_pandas()); break
        except Exception as e: time.sleep(15 * (a + 1))
    else: bad.append(k)
    if k % 8000 == 0: print(k, len(ids), flush=True)
G = pd.concat(out); G["source_id"] = G.source_id.astype("int64").astype(str); G.to_csv("gaia_cols.csv", index=False)
open("gaia_failed.txt", "w").write("\n".join(map(str, bad))); print("done", len(G), "of", len(ids), "failed chunks", bad)
