"""Gaia-first selection, in 10-degree RA strips: Gaia DR3 sources in the cataclysmic-variable region of the HR diagram with
a Gaia G range > 1 mag and brightening-skewed magnitudes. Region: parallax_over_error > 3, -0.3 < BP-RP < 1.6,
4 + 3*(BP-RP) < M_G < 11.5 + 2.5*(BP-RP). Failed strips are retried, then listed in failed_strips.txt (holes)."""
import pandas as pd, time, os
from astroquery.gaia import Gaia
Q = """SELECT g.source_id, g.ra, g.dec, g.phot_g_mean_mag, g.bp_rp, g.parallax, g.parallax_over_error, g.pmra, g.pmdec, g.ruwe,
 g.phot_g_mean_mag + 5*LOG10(ABS(g.parallax)/100) AS mg, v.range_mag_g_fov, v.num_selected_g_fov, v.std_dev_mag_g_fov, v.skewness_mag_g_fov, v.median_mag_g_fov
FROM gaiadr3.vari_summary AS v JOIN gaiadr3.gaia_source AS g ON v.source_id = g.source_id
WHERE g.ra >= {a} AND g.ra < {b} AND v.range_mag_g_fov > 1.0 AND v.skewness_mag_g_fov < 0
 AND g.parallax_over_error > 3 AND g.bp_rp BETWEEN -0.3 AND 1.6
 AND g.phot_g_mean_mag + 5*LOG10(ABS(g.parallax)/100) > 4 + 3*g.bp_rp
 AND g.phot_g_mean_mag + 5*LOG10(ABS(g.parallax)/100) < 11.5 + 2.5*g.bp_rp"""
out = []; bad = []; strips = [(a, a + 10) for a in range(0, 360, 10)]
if len(os.sys.argv) > 1: strips = strips[:int(os.sys.argv[1])]
for a, b in strips:
    for k in range(4):
        try:
            t = Gaia.launch_job_async(Q.format(a=a, b=b)).get_results()
            d = t.to_pandas(); d["source_id"] = [str(x) for x in t["source_id"]]; out.append(d); print(a, len(d), flush=True); break
        except Exception as e: print(a, "retry", type(e).__name__, flush=True); time.sleep(30 * (k + 1))
    else: bad.append(a)
pd.concat(out).to_csv("gaia_cvregion.csv", index=False); open("failed_strips.txt", "w").write("\n".join(map(str, bad)))
print("done", sum(len(x) for x in out), "sources; failed strips", bad)
