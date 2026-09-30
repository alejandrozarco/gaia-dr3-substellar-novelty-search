"""Quick pre-screen of the RV candidates against published close-binary / RV-variability tables (2026-09-30), ahead of the full
deep_prior gate. VizieR cone 3 arcsec at the SDSS/DESI position for: B/cb/cbdata + B/cb/pcbdata (Ritter & Kolb), J/ApJ/889/49 (ELM
Survey final), J/A+A/661/A113 (Geier+2022 hot-subdwarf RV variability), J/MNRAS/468/2910 (Breedt+2017 SDSS DWD), J/A+A/638/A131
(Napiwotzki+2020 SPY). A catalogue that fails to answer is written as HOLE. Output: results/quick_binary_cats.csv."""
import os, pandas as pd, numpy as np, astropy.units as u, astropy.coordinates as c, warnings
warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
H = os.path.dirname(os.path.abspath(__file__)); ST = os.path.expanduser("~/claude_projects/spectra_store")
CATS = ["B/cb/cbdata", "B/cb/pcbdata", "J/ApJ/889/49", "J/A+A/661/A113", "J/MNRAS/468/2910", "J/A+A/638/A131"]
S = pd.read_csv(os.path.join(H, "results", "simbad_rv.csv"), dtype={"gaia": str})
M = pd.read_csv(os.path.join(ST, "sdss_dr17_wd", "matches.csv"), dtype={"gaia": str}).drop_duplicates("gaia").set_index("gaia")
C = pd.read_csv(os.path.join(ST, "desi_dr1_wd", "class_table.csv"), dtype={"edr3id": str}).drop_duplicates("edr3id").set_index("edr3id")
v = Vizier(row_limit=5, timeout=120, columns=["*"]); rows = []
for r in S.itertuples():
    ra, de = (M.loc[r.gaia, "ra"], M.loc[r.gaia, "dec"]) if r.gaia in M.index else (C.loc[r.gaia, "RA(deg)"], C.loc[r.gaia, "DEC(deg)"])
    out = dict(gaia=r.gaia, name=r.main_id, otype=r.otype, dv=round(r.dv)); hits = []
    for cat in CATS:
        try:
            t = v.query_region(c.SkyCoord(ra * u.deg, de * u.deg), radius=3 * u.arcsec, catalog=cat)
            if len(t): hits.append(cat)
        except Exception: hits.append(cat + ":HOLE")
    out["hits"] = ";".join(hits); rows.append(out); print(out, flush=True)
pd.DataFrame(rows).to_csv(os.path.join(H, "results", "quick_binary_cats.csv"), index=False)
