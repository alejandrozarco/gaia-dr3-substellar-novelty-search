# Empirical test: J1226's g-r and absolute magnitudes vs real M dwarfs of the same PS1 i-z and z-y (Gaia DR3 x PS1 DR1 best neighbours)
import warnings, numpy as np
warnings.filterwarnings("ignore")
from astroquery.gaia import Gaia
q = """SELECT TOP 30000 g.source_id, g.parallax, g.phot_g_mean_mag AS G, g.phot_rp_mean_mag AS RP, g.bp_rp, g.pmra, g.pmdec, g.ruwe,
       p.g_mean_psf_mag AS ps_g, p.r_mean_psf_mag AS ps_r, p.i_mean_psf_mag AS ps_i, p.z_mean_psf_mag AS ps_z, p.y_mean_psf_mag AS ps_y
FROM gaiadr3.gaia_source AS g
JOIN gaiadr3.panstarrs1_best_neighbour AS x ON x.source_id = g.source_id
JOIN gaiadr2.panstarrs1_original_valid AS p ON p.obj_id = x.original_ext_source_id
WHERE g.parallax > 6 AND g.parallax_over_error > 20 AND g.ruwe < 1.3
AND p.i_mean_psf_mag - p.z_mean_psf_mag BETWEEN 0.76 AND 0.92 AND p.z_mean_psf_mag - p.y_mean_psf_mag BETWEEN 0.22 AND 0.38
AND p.g_mean_psf_mag > 0 AND p.r_mean_psf_mag > 0 AND p.i_mean_psf_mag < 20.5"""
t = Gaia.launch_job(q).get_results()
print("comparison M dwarfs (i-z 0.76-0.92, z-y 0.22-0.38, plx>6 mas):", len(t))
plx = np.array(t["parallax"], float); dm = 5*np.log10(100/plx)
gr = np.array(t["ps_g"] - t["ps_r"], float); ri = np.array(t["ps_r"] - t["ps_i"], float); iz = np.array(t["ps_i"] - t["ps_z"], float)
Mz = np.array(t["ps_z"], float) - dm; MG = np.array(t["G"], float) - dm; GRP = np.array(t["G"] - t["RP"], float)
vt = 4.74*np.hypot(np.array(t["pmra"], float), np.array(t["pmdec"], float))/plx
for lab, s in (("all", np.ones(len(t), bool)), ("v_tan > 60 km/s (thick disc/halo proxy)", vt > 60), ("v_tan > 100 km/s", vt > 100)):
    if s.sum() < 5: print(lab, "n", s.sum()); continue
    print(f"{lab}: n={s.sum()}; g-r median {np.nanmedian(gr[s]):.2f} (1st pct {np.nanpercentile(gr[s], 1):.2f}, min {np.nanmin(gr[s]):.2f}); r-i {np.nanmedian(ri[s]):.2f}; "
          f"M_z {np.nanmedian(Mz[s]):.2f} +- {np.nanstd(Mz[s]):.2f}; M_G {np.nanmedian(MG[s]):.2f}; G-RP {np.nanmedian(GRP[s]):.3f}")
# J1226
pg, pr, pi, pz, py = 20.7787, 20.1473, 18.985, 18.1421, 17.8429; G, RP, plx0 = 19.536, 18.465, 3.9585
dm0 = 5*np.log10(100/plx0)
print(f"J1226: g-r {pg-pr:.2f}, r-i {pr-pi:.2f}, i-z {pi-pz:.2f}, z-y {pz-py:.2f}; M_z {pz-dm0:.2f} (+-0.21 from parallax), M_G {G-dm0:.2f}, G-RP {G-RP:.3f}, v_tan {4.74*np.hypot(-51.5, 7.45)/plx0:.0f} km/s")
sgr = np.nanstd(gr); print(f"g-r offset from comparison median: {pg-pr-np.nanmedian(gr):+.2f} mag ({(pg-pr-np.nanmedian(gr))/sgr:+.1f} sigma of the comparison spread {sgr:.2f}); fraction of comparison stars with g-r <= {pg-pr:.2f}: {np.mean(gr <= pg-pr):.4f}")
