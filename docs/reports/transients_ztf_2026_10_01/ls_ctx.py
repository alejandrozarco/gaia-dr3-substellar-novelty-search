"""Legacy Surveys DR10 tractor sources within 6 arcsec of each position (NOIRLab Data Lab TAP), with type, g/r/z mags and
photo-z (ls_dr10.photo_z). Positive control: M31 bulge region returns rows. Usage: python ls_ctx.py name:ra:dec [...]"""
import sys, requests, io, pandas as pd, numpy as np
U = "https://datalab.noirlab.edu/tap/sync"
def q(ra, de, r=6):
    s = f"""SELECT t.ls_id, t.ra, t.dec, t.type, t.flux_g, t.flux_r, t.flux_z, t.shape_r, p.z_phot_median, p.z_phot_l68, p.z_phot_u68, p.z_spec
FROM ls_dr10.tractor AS t LEFT JOIN ls_dr10.photo_z AS p ON t.ls_id = p.ls_id
WHERE 't' = q3c_radial_query(t.ra, t.dec, {ra}, {de}, {r/3600})"""
    x = requests.post(U, data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=s), timeout=120)
    if not x.ok or x.text.lstrip().startswith("<"): return "HOLE " + x.text[:300]
    d = pd.read_csv(io.StringIO(x.text))
    if "flux_g" not in d.columns: return "HOLE " + x.text[:200]
    if not len(d): return d
    d["sep"] = np.hypot((d.ra - ra) * np.cos(np.radians(de)), d.dec - de) * 3600
    for b in "grz": d[b] = (22.5 - 2.5 * np.log10(d[f"flux_{b}"].where(d[f"flux_{b}"] > 0))).round(2)
    return d.sort_values("sep")[["sep", "type", "g", "r", "z", "shape_r", "z_phot_median", "z_phot_l68", "z_phot_u68", "z_spec"]].round(3)
c = q(40.6696, -0.0133, 10); print("control (NGC 1068):", c if isinstance(c, str) else len(c))
for a in sys.argv[1:]:
    n, ra, de = a.split(":"); r = q(float(ra), float(de)); print("####", n); print(r if isinstance(r, str) or len(r) else "no LS DR10 source within 6 arcsec (or outside footprint)")
