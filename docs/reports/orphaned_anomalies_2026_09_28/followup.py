"""Orphaned-anomaly harvester, stage 3: for flagged paragraphs (unexplained > 0.6, follow-up > 0.5, resolved < 0.4 in judged.csv),
take the object name from the paragraph label (or the first catalogue-style name in the text) and count later work: SIMBAD references
of the object with year > paper year (TAP) and ADS full-text papers mentioning the name after the paper year. Writes worklist.csv
sorted by weirdness with n_later_simbad_refs and n_later_ads; objects with none are the orphans. A failed lookup is HOLE (-1)."""
import os, re, time, requests, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); ADS = {"Authorization": "Bearer " + open(os.path.expanduser("~/.config/ads/token")).read().strip()}
TAP = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"
J = pd.read_csv(os.path.join(H, "judged.csv"), dtype={"year": str})
F = J[(J.unexplained > 0.6) & (J.followup > 0.5) & (J.resolved < 0.4) & (J.physical > 0.6)].copy()
NAME = re.compile(r"\b((?:2MASS|SDSS|GALEX|WISE|WISEA|CRTS|ZTF|ASASSN|ATLAS|TIC|KIC|EPIC|PSR|HD|HIP|TYC|BD|CD|NGC|IC|PG|PN|LMC|SMC|GD|WD|LP|LHS|G|EC|HS|HE|KUV|PHL|Ton|Gaia DR[23]|OGLE|MACHO|XMM|1RXS|eRASS|4XMM|Swift|Fermi|3C|4C|PKS|B|J)\s?J?\d{2,}[+\-.\d]*[A-Za-z]?)\b")
def name_of(r):
    h = re.sub(r"\s+[a-z0-9_]{3,}$", "", str(r["head"]).strip())  # drop a trailing LaTeX label token ("RS Pup rspup" -> "RS Pup")
    h = re.sub(r"[:;,]\s*$", "", h).strip()
    if h and len(h) > 3 and not h.lower().startswith(("the ", "a ", "notes", "individual")): return h
    m = NAME.search(str(r.text)); return m.group(1) if m else ""
def simbad_up():
    try: return requests.get(TAP, params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY="SELECT TOP 1 oidbib FROM ref"), timeout=15).ok
    except Exception: return False
SIMBAD_UP = simbad_up(); print("SIMBAD TAP reachable:", SIMBAD_UP)
def later_simbad(name, year):
    if not SIMBAD_UP: return -1
    q = f"SELECT COUNT(*) FROM ident AS i JOIN has_ref AS h ON i.oidref = h.oidref JOIN ref AS r ON h.oidbibref = r.oidbib WHERE i.id = '{name.replace(chr(39), '')}' AND r.year > {int(year)}"
    try:
        t = requests.get(TAP, params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=90).text.strip().split("\n")
        return int(t[1]) if len(t) > 1 and t[1].strip().isdigit() else -1
    except Exception: return -1
def later_ads(name, year):
    try:
        j = requests.get("https://api.adsabs.harvard.edu/v1/search/query", params=dict(q=f'full:"{name}" year:{int(year) + 1}-2026 collection:astronomy', fl="bibcode", rows=1), headers=ADS, timeout=60).json()
        return j["response"]["numFound"]
    except Exception: return -1
out = []
for _, r in F.iterrows():
    nm = name_of(r)
    rec = dict(r); rec["object"] = nm
    if nm:
        rec["n_later_simbad_refs"] = later_simbad(nm, r.year); rec["n_later_ads"] = later_ads(nm, r.year); time.sleep(0.3)
    else:
        rec["n_later_simbad_refs"] = rec["n_later_ads"] = -2
    out.append(rec)
W = pd.DataFrame(out).sort_values(["weird", "unexplained"], ascending=False); W.to_csv(os.path.join(H, "worklist.csv"), index=False)
orph = W[(W.n_later_ads == 0) & (W.n_later_simbad_refs <= 0)]
print(len(W), "flagged paragraphs;", (W.object == "").sum(), "without a name;", len(orph), "orphans (no later ADS mention, no later SIMBAD refs)")
pd.set_option("display.width", 250); print(orph[["year", "object", "weird", "unexplained", "kind", "title"]].head(25).to_string(index=False))
