"""Bulk period-novelty pre-gate for the TESS sweep candidates (candidates.csv): a local pass against the May-2026 ostinato
catalogue store (scripts/gates/local_known.py; authoritative hit, non-exhaustive miss), then one CDS XMatch call per catalogue
(VSX, Chen+2020, Jestin+2026, Gao+2025, Wang+2025, Ranaivomanana+2025, Steen+2024, Chen ZTF table3), plus local checks
(Oliveira da Rosa+2024 and Filiz+2026 arXiv tables by TIC; MWDD by Gaia id; known-UHE list). Writes candidates_gated.csv
with per-catalogue period columns and a 'known_period' verdict: True when any catalogued period matches f, 2f, f/2 or the
1-day alias within 1 percent, 'other' when a period exists but does not match, '' when none. XMatch failures are ERR columns."""
import os, re, json, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, astropy.units as u
from astropy.table import Table
from astroquery.xmatch import XMatch
H = os.path.dirname(os.path.abspath(__file__)); SP = os.environ.get("WD_WORKDIR", ".")  # directory holding the downloaded inputs named below
C = pd.read_csv(os.path.join(H, "candidates.csv"), dtype={"gaia": str})
T = Table.from_pandas(C[["gaia", "RA", "Dec"]])
CATS = {"vsx": ("vizier:B/vsx/vsx", "Period", 5), "chen2020": ("vizier:J/ApJS/249/18/table2", "Per", 3), "jestin": ("vizier:J/A+A/712/A243/tablea1", "Freq", 3),
        "gao": ("vizier:J/ApJS/276/57/table5", "Per", 3), "wang": ("vizier:J/ApJS/281/52/table1", "Period", 3), "rana": ("vizier:J/A+A/704/A70/tablea2", "Per", 3),
        "steen": ("vizier:J/ApJ/967/166/table3", "Per", 3), "inight": ("vizier:J/MNRAS/504/2420/tablea1", "Porb", 3)}
for tag, (cat, col, rad) in CATS.items():
    try:
        x = XMatch.query(cat1=T, cat2=cat, max_distance=rad * u.arcsec, colRA1="RA", colDec1="Dec").to_pandas()
        x["gaia"] = x.gaia.astype(str); x = x.sort_values("angDist").drop_duplicates("gaia")
        col2 = col if col in x.columns else next((c for c in x.columns if c.lower().startswith(col.lower()[:3]) and x[c].dtype != object), None)
        C[tag] = C.gaia.map(x.set_index("gaia")[col2]) if col2 else np.nan
    except Exception as ex:
        C[tag] = np.nan; print(tag, "ERR", str(ex)[:70])
OL = open(os.path.join(H, "..", "hot_periodic_wd_2026_09_27", "prior_art", "oliveira2024_arXiv2407.05214_tab.tex")).read()
FI = open(f"{SP}/filiz/aa57071-25corr.tex", errors="ignore").read() if os.path.exists(f"{SP}/filiz/aa57071-25corr.tex") else ""
def oliv(tic):
    m = re.search(rf"^\s*{tic}\s*&\s*([0-9.]+)", OL, re.M); return float(m.group(1)) if m else np.nan
C["oliveira_h"] = [oliv(t) for t in C.tic]
M = {}
mp = f"{SP}/mwdd_table.json"
if os.path.exists(mp):
    for r in json.load(open(mp))["data"]:
        if isinstance(r, dict) and r.get("gaiaedr3"): M[r["gaiaedr3"]] = f"{r.get('spectype')}|{r.get('teff')}|nper={r.get('number_periods')}"
C["mwdd"] = C.gaia.map(M).fillna("")
import sys; sys.path.insert(0, os.path.join(H, "..", "..", "..", "scripts"))
from gates import local_known
lm = local_known.match(C.set_index("gaia"), ra_col="RA", dec_col="Dec", radius_arcsec=5.0)
C["store_hits"] = C.gaia.map(lm.groupby("idx").apply(lambda x: "; ".join(f"{r.catalog}:{r['name']}({r.otype})" for _, r in x.iterrows())) if len(lm) else pd.Series(dtype=str)).fillna("")
uhe = set(pd.read_csv(os.path.join(H, "..", "uhe_screen_sdssv_2026_09_26", "data", "known_uhe_all.csv"), dtype=str).gaia)
C["known_uhe"] = C.gaia.isin(uhe)
def match(f, P_d):
    if not np.isfinite(P_d) or P_d <= 0: return False
    fc = 1 / P_d
    return any(abs(f - m) / m < 0.01 for m in (fc, 2 * fc, fc / 2, abs(fc - 1), fc + 1) if m > 0)
verd = []
for _, r in C.iterrows():
    hits = []
    for tag in list(CATS) + ["oliveira_h"]:
        v = r[tag]
        if not np.isfinite(v) if isinstance(v, float) else False: continue
        try: v = float(v)
        except Exception: continue
        if not np.isfinite(v) or v == 0: continue
        P_d = (1 / v if tag == "jestin" else v / 24 if tag in ("oliveira_h", "inight") else v)  # jestin: frequency; oliveira and inight: hours; others: days
        hits.append((tag, P_d, match(r.f, P_d)))
    verd.append("match:" + ",".join(t for t, _, m in hits if m) if any(m for _, _, m in hits) else ("other:" + ",".join(t for t, _, _ in hits) if hits else ""))
C["known_period"] = verd
C.to_csv(os.path.join(H, "candidates_gated.csv"), index=False)
n = C.known_period.str.startswith("match").sum(); o = C.known_period.str.startswith("other").sum()
print(len(C), "candidates:", n, "catalogued-period matches,", o, "with a different catalogued period,", len(C) - n - o, "with none")
pd.set_option("display.width", 300)
print(C[C.known_period == ""].sort_values("fap_min").head(30)[["gaia", "WDJname", "G", "TeffH", "P_h", "P_min", "fap_min", "amp", "crowdsap", "n_detected", "n_sectors", "detr_ratio", "mwdd", "known_uhe"]].to_string(index=False))

# Tiering. 'ours': already in the project register/journals or the public tables. Attribution: the implied semi-amplitude on the
# white dwarf is amp/crowdsap; > 0.5 is treated as contamination by neighbours in the aperture. Slow frequencies (f < 1.5 c/d)
# must survive the 1-day-median detrend (ratio > 0.5) and appear in >= 2 sectors (scattered-light systematics live there).
reg = pd.read_csv(os.path.join(H, "..", "..", "object_journals", "findings_register.csv"), dtype={"source_id": str})
idx = open(os.path.join(H, "..", "..", "object_journals", "INDEX.md")).read()
pub = ""
for tb in ("periodic_white_dwarfs", "irradiated_companions", "hot_wd_periods", "dae_wd_periods"):
    p = f"../white-dwarfs-2026/tables/{tb}.csv"
    if os.path.exists(p): pub += open(p).read()
C["ours"] = [g in set(reg.source_id) or g in idx or g in pub for g in C.gaia]
C["implied_amp"] = C.amp.round(3)  # PDCSAP is already crowding-corrected: the requirement on the star is the PDCSAP amplitude itself (corrected 2026-09-28)
slow_ok = (C.f >= 1.5) | ((C.detr_ratio > 0.5) & (C.n_detected >= 2))
C["tier"] = np.where(C.known_period.str.startswith("match"), "known",
            np.where(C.ours, "ours",
            np.where((C.implied_amp < 0.5) & slow_ok & ((C.n_detected >= 2) | (C.fap_min < 1e-30)), "A",
            np.where((C.implied_amp < 1.0) & slow_ok, "B", "contaminated/systematic"))))
C.to_csv(os.path.join(H, "candidates_gated.csv"), index=False)
print(C.tier.value_counts().to_string())
print(C[C.tier == "A"].sort_values("fap_min")[["gaia", "WDJname", "G", "TeffH", "MassH", "P_h", "P_min", "fap_min", "amp", "crowdsap", "implied_amp", "n_detected", "n_sectors", "detr_ratio", "dip_sigma", "mwdd", "known_uhe", "known_period"]].to_string(index=False))
