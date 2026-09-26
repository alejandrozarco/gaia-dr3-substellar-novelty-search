# Empirical M-dwarf template for the J0753 (Gaia DR3 3082614748370926848) SED decomposition: Gaia DR3 x PS1 DR1 x 2MASS stars with
# parallax > 10 mas (> 20 sigma), RUWE < 1.3, 2MASS J/Ks quality A, grouped by absolute M_J; median absolute magnitudes in
# G, BP, RP, g, r, i, z, y, J, Ks per 0.2-mag M_J bin. Output: mtemplate.csv
import numpy as np, warnings
warnings.filterwarnings("ignore")
from astroquery.gaia import Gaia
q = """SELECT TOP 40000 g.parallax, g.phot_g_mean_mag AS G, g.phot_bp_mean_mag AS BP, g.phot_rp_mean_mag AS RP,
       p.g_mean_psf_mag AS ps_g, p.r_mean_psf_mag AS ps_r, p.i_mean_psf_mag AS ps_i, p.z_mean_psf_mag AS ps_z, p.y_mean_psf_mag AS ps_y,
       t.j_m, t.ks_m, t.ph_qual
FROM gaiadr3.gaia_source AS g
JOIN gaiadr3.panstarrs1_best_neighbour AS x ON x.source_id = g.source_id
JOIN gaiadr2.panstarrs1_original_valid AS p ON p.obj_id = x.original_ext_source_id
JOIN gaiadr3.tmass_psc_xsc_best_neighbour AS tx ON tx.source_id = g.source_id
JOIN gaiadr1.tmass_original_valid AS t ON t.designation = tx.original_ext_source_id
WHERE g.parallax > 10 AND g.parallax_over_error > 20 AND g.ruwe < 1.3 AND g.bp_rp BETWEEN 2.6 AND 4.4
AND p.g_mean_psf_mag > 0 AND p.r_mean_psf_mag > 0 AND p.i_mean_psf_mag > 0 AND p.z_mean_psf_mag > 0 AND p.y_mean_psf_mag > 0"""
t = Gaia.launch_job(q).get_results()
pq = np.array([str(s) for s in t["ph_qual"]]); ok = np.array([s[0] == "A" and s[2] == "A" for s in pq])
t = t[ok]; dm = 5 * np.log10(100 / np.array(t["parallax"], float))
cols = {"G": "G", "BP": "BP", "RP": "RP", "g": "ps_g", "r": "ps_r", "i": "ps_i", "z": "ps_z", "y": "ps_y", "J": "j_m", "Ks": "ks_m"}
M = {k: np.array(t[v], float) - dm for k, v in cols.items()}
edges = np.arange(8.4, 11.21, 0.2)
with open("../data/mdwarf_template.csv", "w") as fh:
    fh.write("# Empirical M-dwarf absolute magnitudes (medians) vs M_J bin; Gaia DR3 x PS1 DR1 x 2MASS, plx > 10 mas (> 20 sigma), RUWE < 1.3, 2MASS JKs qual A\n")
    fh.write("MJ_centre,n," + ",".join(cols) + "\n")
    for lo, hi in zip(edges[:-1], edges[1:]):
        s = (M["J"] >= lo) & (M["J"] < hi)
        if s.sum() < 15: continue
        fh.write(f"{(lo+hi)/2:.2f},{s.sum()}," + ",".join(f"{np.median(M[k][s]):.3f}" for k in cols) + "\n")
print(open("../data/mdwarf_template.csv").read())
