# Consolidate the per-object novelty checks for the 32 visually Zeeman-split SnowWhite stars into one CSV:
# SnowWhite DR20 class, measured fields, SIMBAD type/refs, VizieR all-table magnetic hits, ADS alias hits, DESI DR1 spectrum and
# classifications (Amorim+2026 GitHub list, Swan+2026 catalogue), LAMOST DR10 spectrum class, MWDD spectral type, and matches in the
# arXiv sources of 10 papers (Kilic+2020, Kilic+2025 Table2_ALL, Caron+2023, Jewett+2024, Moss+2025, Amorim+2026 x2, Swan+2026,
# Yu+2026, Garcia-Zamora+2026).
import json, csv, gzip, glob, numpy as np
from astropy.coordinates import SkyCoord; import astropy.units as u
T = [l.split()[0] for l in open("vis_list.txt") if l.strip() and not l.startswith("#")]
SW = {r["gaia_dr3_source_id"]: r for r in csv.DictReader(open("sw_magnetic.csv"))}
S78 = json.load(open("simbad_78.json")); SR = json.load(open("simbad_refs_vis.json")); NV = json.load(open("novelty.json"))
AD = json.load(open("ads_aliases_vis.json")); DE = json.load(open("desi_dr1_vis.json")); LA = json.load(open("lamost_dr10_vis.json"))
ZF = json.load(open("zfit_free_batch.json")); C = json.load(open("coords_vis.json"))
mw = {}
for r in json.load(open("mwdd/table.json"))["data"]:
    for k in ("gaiaedr3", "gaiadr2"):
        if r.get(k): mw[r[k]] = r
am = {}
for line in open("desi/DESI_CLASS_FINAL.txt"):
    if line.startswith("#"): hdr = line[1:].split(); continue
    p = line.split()
    if len(p) > 6: am[p[1]] = p[6]
sw_desi = {}
for r in csv.DictReader(gzip.open("desi/swan_cat.csv.gz", "rt")):
    sw_desi[r["designation"].split()[-1]] = r["specType"]
papers = {"Kilic2020": "2006.00323", "Kilic2025": "2412.04611", "Caron2023": "2212.08014", "Jewett2024": "2407.04827", "Moss2025": "2507.06102",
          "Amorim2026a": "2603.20487", "Amorim2026b": "2607.00430", "Swan2026": "2609.04314", "Yu2026": "2603.11004", "GarciaZamora2026": "2605.16493"}
tex = {k: "\n".join(open(f, errors="ignore").read() for f in glob.glob(f"arx/{a}/*") if f.endswith((".tex", ".txt"))) for k, a in papers.items()}
def names(g):
    c = C[g]; out = {g}
    ra16 = c["ra2000"] + c["pm"][0] * 16 / 3.6e6 / np.cos(np.radians(c["dec2000"])); de16 = c["dec2000"] + c["pm"][1] * 16 / 3.6e6
    for ra, de in ((c["ra2000"], c["dec2000"]), (ra16, de16)):
        s = SkyCoord(ra * u.deg, de * u.deg); h, m, _ = s.ra.hms; d, dm, _ = np.abs(s.dec.dms); sg = "+" if de >= 0 else "-"
        out |= {f"J{int(h):02d}{int(m):02d}{sg}{int(d):02d}{int(abs(dm)):02d}", f"J{int(h):02d}{int(m):02d}${sg}${int(d):02d}{int(abs(dm)):02d}"}
    return out
rows = []
for g in T:
    nm = names(g); texhits = sorted({k for k, t in tex.items() for p in nm if p in t})
    lam = LA.get(g); lam_s = lam if isinstance(lam, str) else ("no spectrum" if not lam else "spectrum")
    desi_spec = DE.get(g); desi_s = "no spectrum" if desi_spec == [] else ("; ".join(x[0] for x in desi_spec) if isinstance(desi_spec, list) else desi_spec)
    known = []
    if am.get(g) == "DAH": known.append("Amorim+2026 DESI DR1 DAH")
    if sw_desi.get(g) == "DAH": known.append("Swan+2026 DESI DR1 DAH")
    if (mw.get(g, {}).get("spectype") or "").startswith(("DAH", "DAP", "DBH", "DH")): known.append(f"MWDD {mw[g]['spectype']}")
    if NV[g]["spectral_hits"]: known.append("VizieR: " + ", ".join(sorted({h.split(':')[0] for h in NV[g]['spectral_hits']})))
    for k in ("Jewett2024", "Yu2026", "GarciaZamora2026", "Moss2025", "Amorim2026a"):
        if k in texhits: known.append(f"{k} (source match)")
    z = ZF[g]; c = C[g]
    rows.append(dict(gaia_dr3=g, simbad_name=S78[g]["main_id"], simbad_sptype=S78[g]["sp_type"] or "", ra2000=round(c["ra2000"], 5), dec2000=round(c["dec2000"], 5),
                     G=round(float(SW[g]["g_mag"]), 2), dist_pc=round(1000 / float(SW[g]["plx"]), 0), snowwhite_class=SW[g]["classification"], sdssv_snr=round(z["snr"], 1),
                     B_Ha_MG=round(z["Ha"]["B"], 2), eB_Ha=round(z["Ha"]["eB"], 2), B_Hb_MG=round(z["Hb"]["B"], 2), eB_Hb=round(z["Hb"]["eB"], 2),
                     mwdd_sptype=mw.get(g, {}).get("spectype", "absent"), desi_dr1=desi_s, lamost_dr10=lam_s,
                     vizier_tables=len(NV[g]["vizier"] or []), vizier_magnetic_hits=len(NV[g]["spectral_hits"]), ads_alias_hits=AD[g]["n"],
                     paper_source_matches=";".join(texhits), prior_magnetic=" | ".join(known) if known else "none found",
                     verdict="KNOWN_MAGNETIC" if known else "NO_MAGNETIC_LABEL"))
with open("report/novelty_summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r["gaia_dr3"], r["verdict"], r["snowwhite_class"], r["mwdd_sptype"], r["B_Ha_MG"], r["B_Hb_MG"], r["prior_magnetic"][:110])
print(sum(r["verdict"] == "KNOWN_MAGNETIC" for r in rows), "known;", sum(r["verdict"] == "NO_MAGNETIC_LABEL" for r in rows), "no label")
