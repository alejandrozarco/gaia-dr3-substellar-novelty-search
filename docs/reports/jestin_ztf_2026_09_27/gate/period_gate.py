"""Novelty gate for ZTF detections among Jestin+2026 'Variable False' white dwarfs (detected.csv, alias-flagged excluded).
Per star: VizieR all-table cone (5") -> every table with a non-empty period/frequency-like column (Per*, Period*, P, Freq*, f*) is listed
with its value; TIC id (MAST TIC, 2") -> Oliveira da Rosa+2024 table (arXiv:2407.05214 source); MWDD table.json number_periods and
spectype; SIMBAD main id and otype. A failed query is recorded as ERR (a hole, not a null). Frequency clusters: f_top values shared by
>= 3 detections within 0.003 c/d are flagged as possible ZTF systematics.
Usage: python period_gate.py [controls.csv] (writes gate/period_gate.csv, or gate/period_gate_controls.csv for a control list)."""
import os, re, sys, json, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from astroquery.vizier import Vizier; from astroquery.simbad import Simbad; from astroquery.mast import Catalogs
import astropy.units as u; from astropy.coordinates import SkyCoord
X = os.path.dirname(os.path.abspath(__file__)); SP = os.environ.get("WD_WORKDIR", ".")  # directory holding the downloaded inputs named below
D = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else f"{X}/../detected.csv", dtype={"GaiaDR3": str}); D = D[~D.alias].copy()
OL = open(f"{X}/../../hot_periodic_wd_2026_09_27/prior_art/oliveira2024_arXiv2407.05214_tab.tex").read()
M = {r["gaiaedr3"]: r for r in json.load(open(f"{SP}/mwdd_table.json"))["data"] if isinstance(r, dict) and r.get("gaiaedr3")} if os.path.exists(f"{SP}/mwdd_table.json") else {}
V = Vizier(columns=["**"], row_limit=3); V.TIMEOUT = 200
PAT = re.compile(r"^(Per|Period|Porb|Prot|Pbest|Pday|P|Pd|Freq|Frequency|pPer|Pers)(\d|_\w+)?$"); SKIP = ("I/355/", "I/358/", "J/A+A/674/A25")
fs = D.f_top.values; D["f_cluster"] = [int((np.abs(fs - f) < 0.003).sum()) for f in fs]
rows = []
for _, r in D.iterrows():
    c = SkyCoord(r.RA_ICRS, r.DE_ICRS, unit="deg"); out = dict(GaiaDR3=r.GaiaDR3, WDJname=r.WDJname, G=r.Gmag, f_top=r.f_top, P_h=round(24 / r.f_top, 4), fap_top=r.fap_top,
               A_g=round(r.A1_zg, 2), A_r=round(r.A1_zr, 2), r_over_g=round(r.r_over_g, 2), f_cluster=r.f_cluster, gaia_agree=r.gaia_agree)
    try:
        allt = V.query_region(c, radius=5 * u.arcsec); hits = []
        for k in allt.keys():
            if k.startswith(SKIP): continue
            t = allt[k]
            for col in t.colnames:
                if PAT.match(col):
                    v = t[0][col]
                    if not np.ma.is_masked(v) and str(v).strip() not in ("", "0", "0.0", "--", "nan"):
                        hits.append(f"{k}:{col}={v}")
        out["period_tables"] = "; ".join(hits); out["n_tables"] = len(allt)
    except Exception as ex: out["period_tables"] = f"ERR {ex}"[:80]
    try:
        t = Catalogs.query_region(c, radius=2 * u.arcsec, catalog="TIC"); tic = [str(x) for x in t["ID"]]
        out["tic"] = " ".join(tic); out["oliveira"] = " | ".join(l.split("&")[0].strip() + ":" + l.split("&")[1].strip() for l in OL.splitlines() if any(re.match(rf"\s*{x}\s*&", l) for x in tic))
    except Exception as ex: out["tic"] = f"ERR {ex}"[:60]
    m = M.get(r.GaiaDR3); out["mwdd"] = f"{m.get('spectype')} {m.get('teff')} nper={m.get('number_periods')} {m.get('source')}" if m else "not in MWDD"
    try:
        s = Simbad.query_region(c, radius=5 * u.arcsec); out["simbad"] = f"{s[0]['main_id']}" if s is not None and len(s) else ""
    except Exception as ex: out["simbad"] = f"ERR {ex}"[:60]
    rows.append(out); print(out["GaiaDR3"], out["P_h"], out.get("period_tables", "")[:300], "|", out.get("oliveira"), "|", out["mwdd"], flush=True)
pd.DataFrame(rows).to_csv(f"{X}/period_gate.csv" if len(sys.argv) == 1 else f"{X}/period_gate_controls.csv", index=False)
