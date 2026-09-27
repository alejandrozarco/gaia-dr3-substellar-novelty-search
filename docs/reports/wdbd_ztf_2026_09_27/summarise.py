"""detected.csv: ZTF signal near the Gaia frequency (FAP < 1e-5, amplitude > 5 sigma in g or r). blue_red_enhanced.csv: detected, r amplitude > 5 sigma,
r/g >= 1.5, BP-RP < -0.15, with SIMBAD main id / type / reference count and the VSX entry within 5"."""
import os, requests, warnings, numpy as np, pandas as pd; warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier; from astropy.coordinates import SkyCoord; import astropy.units as u
X = os.path.dirname(os.path.abspath(__file__)); T = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"
R = pd.read_csv(f"{X}/results.csv", dtype={"source_id": str}); R = R[R.status == "ok"].copy()
R["MG"] = R.phot_g_mean_mag + 5 * np.log10(R.parallax / 100); R["sig_g"] = R.A1_zg / R.eA1_zg; R["sig_r"] = R.A1_zr / R.eA1_zr
D = R[(R.fap < 1e-5) & (np.maximum(R.sig_g, R.sig_r) > 5)]; D.to_csv(f"{X}/detected.csv", index=False); print(len(R), "measured;", len(D), "detected")
c = D[(D.r_over_g >= 1.5) & (D.sig_r > 5) & (D.bp_rp < -0.15)].sort_values("f_ztf", ascending=False)
V = Vizier(columns=["**"], row_limit=3); rows = []
def tap(q): return requests.post(T, data=dict(request="doQuery", lang="adql", format="json", query=q), timeout=60).json()["data"]
for _, r in c.iterrows():
    g = r.source_id; b = tap(f"SELECT b.main_id, b.otype, b.sp_type FROM ident i JOIN basic b ON b.oid=i.oidref WHERE i.id='Gaia DR3 {g}'")
    n = tap(f"SELECT count(*) FROM ident i JOIN has_ref h ON h.oidref=i.oidref WHERE i.id='Gaia DR3 {g}'")[0][0]
    vs = V.query_region(SkyCoord(r.ra, r.dec, unit="deg"), radius=5 * u.arcsec, catalog="B/vsx/vsx"); vsx = (str(vs[0]["Name"][0]), str(vs[0]["Type"][0]), str(vs[0]["Period"][0])) if len(vs) else None
    rows.append(dict(source_id=g, G=round(r.phot_g_mean_mag, 2), bp_rp=round(r.bp_rp, 2), MG=round(r.MG, 2), P_h=round(24 / r.f_ztf, 3), r_over_g=round(r.r_over_g, 2), A_r=round(r.A1_zr, 1), simbad=(b[0] if b else None), nref=n, vsx=vsx))
pd.DataFrame(rows).to_csv(f"{X}/blue_red_enhanced.csv", index=False)
