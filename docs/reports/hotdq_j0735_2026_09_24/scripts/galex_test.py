# GALEX far-UV test for Gaia DR3 5208047381438507520: FUV-NUV and NUV-G versus Gaia BP-RP for (a) SDSS-V SnowWhite spectroscopic DA
# (571) and DB/DBA (14) white dwarfs with -0.55 < BP-RP < -0.25, plx > 4 mas, S/N > 10; (b) MWDD DQ-type white dwarfs with
# Teff >= 15 kK (68). Gaia DR3 photometry/astrometry from the Gaia TAP; positions propagated to 2007.0 (GALEX mid-mission);
# GALEX GUVcat_AIS (VizieR II/335/galex_ais) via CDS XMatch, 4" radius, nearest match. Reddening is ignored (d < 250 pc mostly);
# note that interstellar extinction makes FUV-NUV bluer (R_FUV < R_NUV, Yuan+2013), so it cannot produce a red FUV-NUV.
import json, io, numpy as np, pandas as pd, requests
from astropy.table import Table
from astroquery.xmatch import XMatch
import astropy.units as u
TAP = "https://gea.esac.esa.int/tap-server/tap/sync"
sw = pd.read_csv("sw_hot_controls.csv"); hq = json.load(open("mwdd_hotdq.json"))
ids = {str(int(x)): ("DA" if c == "DA" else "DB") for x, c in zip(sw["gaia_dr3_source_id"], sw["classification"]) if x > 0}
for h in hq: ids[h["gaia"]] = "DQ(MWDD)"
ids["5208047381438507520"] = "TARGET"
rows = []
L = list(ids)
for i in range(0, len(L), 300):
    q = ("SELECT source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(L[i:i + 300]) + ")")
    r = requests.post(TAP, data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=300); r.raise_for_status()
    rows.append(pd.read_csv(io.StringIO(r.text), dtype={"source_id": str}))
g = pd.concat(rows); g["grp"] = g["source_id"].map(ids)
print("Gaia rows", len(g), "of", len(ids), g["grp"].value_counts().to_dict())
dt = 2007.0 - 2016.0
g["ra07"] = g["ra"] + (g["pmra"].fillna(0) * dt / 3.6e6) / np.cos(np.radians(g["dec"])); g["de07"] = g["dec"] + g["pmdec"].fillna(0) * dt / 3.6e6
t = Table.from_pandas(g[["source_id", "ra07", "de07"]])
x = XMatch.query(cat1=t, cat2="vizier:II/335/galex_ais", max_distance=4 * u.arcsec, colRA1="ra07", colDec1="de07").to_pandas()
x["source_id"] = x["source_id"].astype(str); x = x.sort_values("angDist").drop_duplicates("source_id")
print("GALEX matches:", len(x), "columns sample:", [c for c in x.columns if "mag" in c.lower() or "FUV" in c or "NUV" in c][:12])
d = g.merge(x[["source_id", "angDist", "FUVmag", "e_FUVmag", "NUVmag", "e_NUVmag"]], on="source_id", how="left")
d["bprp"] = d["phot_bp_mean_mag"] - d["phot_rp_mean_mag"]; d["fuvnuv"] = d["FUVmag"] - d["NUVmag"]; d["nuvg"] = d["NUVmag"] - d["phot_g_mean_mag"]
d["MG"] = d["phot_g_mean_mag"] + 5 * np.log10(d["parallax"] / 100)
d.to_csv("galex_test.csv", index=False)
T = d[d.grp == "TARGET"].iloc[0]
print(f"TARGET: BP-RP {T.bprp:.3f}  FUV {T.FUVmag:.3f}+-{T.e_FUVmag:.3f}  NUV {T.NUVmag:.3f}+-{T.e_NUVmag:.3f}  FUV-NUV {T.fuvnuv:+.3f}  NUV-G {T.nuvg:+.3f}  M_G {T.MG:.2f}")
for grp in ["DA", "DB", "DQ(MWDD)"]:
    s = d[(d.grp == grp) & d.fuvnuv.notna() & (d.e_FUVmag < 0.1)]
    near = s[np.abs(s.bprp - T.bprp) < 0.06]
    if len(s) == 0: continue
    print(f"{grp:9s}: {len(s)} with FUV+NUV; all: FUV-NUV median {s.fuvnuv.median():+.2f}; within 0.06 of target BP-RP: n={len(near)}, "
          f"FUV-NUV median {near.fuvnuv.median():+.2f}, range {near.fuvnuv.min():+.2f}..{near.fuvnuv.max():+.2f}, fraction >= target {np.mean(near.fuvnuv >= T.fuvnuv) if len(near) else float('nan'):.3f}; "
          f"NUV-G median {near.nuvg.median():+.2f}")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
for grp, col, mk in [("DA", "0.6", "."), ("DB", "tab:green", "s"), ("DQ(MWDD)", "tab:purple", "D")]:
    s = d[(d.grp == grp) & d.fuvnuv.notna() & (d.e_FUVmag < 0.1)]
    ax[0].scatter(s.bprp, s.fuvnuv, s=12 if grp == "DA" else 22, c=col, marker=mk, label=f"{grp} ({len(s)})")
    ax[1].scatter(s.bprp, s.nuvg, s=12 if grp == "DA" else 22, c=col, marker=mk)
for a, y in zip(ax, [T.fuvnuv, T.nuvg]): a.scatter([T.bprp], [y], s=160, c="red", marker="*", label="5208047381438507520", zorder=5)
ax[0].set_xlabel("Gaia BP-RP"); ax[0].set_ylabel("GALEX FUV-NUV"); ax[1].set_xlabel("Gaia BP-RP"); ax[1].set_ylabel("GALEX NUV - Gaia G")
ax[0].legend(fontsize=8); ax[0].set_title("GUVcat AIS; SDSS-V SnowWhite DA/DB and MWDD DQ (Teff >= 15 kK)", fontsize=9)
plt.tight_layout(); plt.savefig("fig_galex.png", dpi=90)
