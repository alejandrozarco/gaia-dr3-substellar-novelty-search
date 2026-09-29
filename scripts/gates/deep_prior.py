"""Deep prior-research check for journaled candidates (2026-09-29).

Motivation: the ELM Survey South II table (J/ApJ/950/141) held a spectroscopic Teff/logg for WDJ0547-3922 that the earlier gate
dropped, because its VizieR filter kept only class/period columns and ADS full text does not index source ids.

Per object (Gaia DR3 id from deep_list.txt):
 1. VizieR all-table cone, 3 arcsec, at the Gaia 2016 and J2000-propagated positions. Every table that is not a large survey
    (catalogue prefixes I/, II/, IV/ and a list of whole-sky white-dwarf/XP catalogues) is kept with ALL non-empty column values.
 2. Each kept J/ table is traced to its paper (ADS by bibstem/volume/page); the paper's arXiv source is grepped for every alias.
 3. SIMBAD: all identifiers (aliases) and every referencing bibcode; each paper's arXiv source is grepped for the aliases.
 4. ESO archive: ObsCore spectra within 5 arcsec.
A failed service call is written as HOLE, never as 'nothing found'. Output: out/<gaia>.md and out/<gaia>.json; summary.csv.
Usage: python deep_prior.py deep_list.txt"""
import os, re, io, sys, json, time, gzip, tarfile, requests, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
from astroquery.gaia import Gaia
import astropy.coordinates as c, astropy.units as u
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, "out"); SRC = os.path.join(H, "arxiv_src"); os.makedirs(OUT, exist_ok=True); os.makedirs(SRC, exist_ok=True)
ADS = {"Authorization": "Bearer " + open(os.path.expanduser("~/.config/ads/token")).read().strip()}
TAP = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"
SURVEY_PREFIX = ("I/", "II/", "IV/", "VI/")
BIG = {"J/MNRAS/508/3877", "J/A+A/674/A33", "J/ApJ/984/58", "J/A+A/682/A5", "J/MNRAS/482/4570", "J/A+A/674/A22", "J/A+A/705/A247", "J/ApJ/970/181",
       "J/A+A/699/A3", "J/MNRAS/480/4505", "J/A+A/692/A115", "J/A+A/677/A159", "J/AJ/161/234", "J/A+A/649/A81", "J/MNRAS/515/4711", "J/A+A/668/A99",
       "J/MNRAS/482/715", "J/AJ/158/93", "J/AJ/159/84", "J/A+A/674/A25", "J/ApJS/281/52", "J/MNRAS/503/5263", "J/A+A/703/A261", "J/A+A/712/A171"}
JOUR = {"A+A": "A&A", "ApJ": "ApJ", "ApJS": "ApJS", "AJ": "AJ", "MNRAS": "MNRAS", "PASP": "PASP", "PASJ": "PASJ", "AcA": "AcA", "BaltA": "BaltA", "RAA": "RAA"}
va = Vizier(row_limit=3, timeout=180, columns=["**"])
def adsq(q, fl="bibcode,title,year,identifier", rows=5):
    for k in range(3):
        try: return requests.get("https://api.adsabs.harvard.edu/v1/search/query", params=dict(q=q, fl=fl, rows=rows), headers=ADS, timeout=60).json()["response"]["docs"]
        except Exception: time.sleep(5)
    return None
def arxiv_of(doc): a = [i for i in doc.get("identifier", []) if i.startswith("arXiv:")]; return a[0][6:] if a else None
def src_text(a):
    p = os.path.join(SRC, a.replace("/", "_") + ".tar")
    if not (os.path.exists(p) and os.path.getsize(p) > 1000):
        for k in range(3):
            try:
                r = requests.get(f"https://arxiv.org/e-print/{a}", headers={"User-Agent": "literature check"}, timeout=180)
                if r.status_code == 200 and len(r.content) > 1000: open(p, "wb").write(r.content); break
                if r.status_code in (403, 429): time.sleep(60)
            except Exception: time.sleep(20)
        time.sleep(4)
        if not os.path.exists(p): return None
    raw = open(p, "rb").read(); txt = ""
    try:
        with tarfile.open(fileobj=io.BytesIO(raw)) as t:
            for m in t.getmembers():
                if m.isfile() and m.size < 40_000_000 and not m.name.lower().endswith((".pdf", ".png", ".jpg", ".eps", ".ps", ".gz")):
                    try: txt += t.extractfile(m).read().decode("utf-8", "ignore") + "\n"
                    except Exception: pass
    except tarfile.TarError:
        try: txt = gzip.decompress(raw).decode("utf-8", "ignore")
        except Exception: txt = raw.decode("utf-8", "ignore")
    return txt
def passages(txt, aliases, n=4):
    out = []
    for al in aliases:
        if len(al) < 6: continue
        pat = re.escape(al).replace(r"\ ", r"\s*").replace(r"\+", r"\s*[+\\$]*\s*\+?").replace(r"\-", r"\s*[-−$]*\s*")
        for m in re.finditer(pat, txt):
            s = re.sub(r"\s+", " ", txt[max(0, m.start() - 350): m.end() + 450]); s = s.replace("&", " | ")
            if s not in out: out.append(s)
            if len(out) >= n: return out
    return out
def aliases_for(gaia, extra):
    al = [f"Gaia DR3 {gaia}", gaia] + [x for x in extra if x]
    for x in list(al):
        m = re.match(r"(?:WDJ|J)(\d{2})(\d{2})(\d{2}(?:\.\d+)?)([+-])(\d{2})(\d{2})(\d{2}(?:\.\d+)?)", x.replace("WDJ", "J") if x.startswith(("WDJ", "J")) else "")
        if m:
            h, mi, s, sg, d, dm, ds = m.groups(); al += [f"J{h}{mi}{sg}{d}{dm}", f"J{h}{mi}{s[:2]}{sg}{d}{dm}{ds[:2]}", f"{h}{mi}{s[:2]}{sg}{d}{dm}{ds[:2]}", f"J{h}{mi}{sg}{d}{dm[:1]}"]
    seen = []; [seen.append(a) for a in al if a not in seen and len(a) >= 6]; return seen
L = [l.split("|") for l in open(sys.argv[1]).read().splitlines() if l.strip()]
rows = []
for parts in L:
    gaia = parts[0].strip(); status = parts[1].strip(); nm = parts[2].strip()
    if os.path.exists(os.path.join(OUT, gaia + ".json")): continue
    rec = dict(gaia=gaia, status=status, name=nm, holes=[])
    pos = None
    for attempt in range(3):  # Gaia archive is unstable before DR4; retry, then fall back to the VizieR copy of DR3
        try:
            t = Gaia.launch_job(f"SELECT ra, dec, pmra, pmdec FROM gaiadr3.gaia_source WHERE source_id={gaia}").get_results()
            pos = (float(t["ra"][0]), float(t["dec"][0]), float(t["pmra"][0] or 0), float(t["pmdec"][0] or 0)); break
        except Exception: time.sleep(15 * (attempt + 1))
    if pos is None:
        try:
            t = Vizier(columns=["RA_ICRS", "DE_ICRS", "pmRA", "pmDE"], row_limit=1).query_constraints(catalog="I/355/gaiadr3", Source=gaia)[0]
            pos = (float(t["RA_ICRS"][0]), float(t["DE_ICRS"][0]), float(t["pmRA"][0] or 0), float(t["pmDE"][0] or 0))
        except Exception: pass
    if pos is None: rec["holes"].append("gaia"); json.dump(rec, open(os.path.join(OUT, gaia + ".json"), "w")); continue
    ra, de, pmra, pmde = pos
    ra0 = ra - pmra * 16 / 3.6e6 / np.cos(np.radians(de)); de0 = de - pmde * 16 / 3.6e6
    # SIMBAD identifiers and references
    sim_ids, sim_refs = [], []
    try:
        q = f"SELECT i2.id FROM ident AS i1 JOIN ident AS i2 ON i1.oidref=i2.oidref WHERE i1.id='Gaia DR3 {gaia}'"
        r = requests.get(TAP, params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=90); sim_ids = [x.strip('"') for x in r.text.strip().split("\n")[1:]]
        q = f'SELECT r.bibcode, r."year", r.title FROM ident AS i JOIN has_ref AS h ON i.oidref=h.oidref JOIN ref AS r ON h.oidbibref=r.oidbib WHERE i.id=\'Gaia DR3 {gaia}\''
        r = requests.get(TAP, params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=90)
        sim_refs = pd.read_csv(io.StringIO(r.text)).to_dict("records") if r.ok and r.text.startswith("bibcode") else []
    except Exception: rec["holes"].append("simbad")
    names = [x.strip() for x in re.split(r"[=()]", nm) if x.strip()]
    AL = aliases_for(gaia, names + [s for s in sim_ids if not s.startswith("Gaia")])
    rec["aliases"] = AL; rec["simbad_refs"] = sim_refs
    # VizieR cones
    tables = {}
    for (a, d) in ((ra, de), (ra0, de0)):
        try:
            res = va.query_region(c.SkyCoord(a, d, unit="deg"), radius=3 * u.arcsec)
            for tt in res:
                tid = tt.meta.get("ID", "")
                if tid.startswith("J_A_A_"): cat = "J/A+A/" + "/".join(tid[6:].split("_")[:2])
                elif tid.startswith("J_"): cat = "/".join(tid.split("_")[:4])
                else: cat = tid.replace("_", "/", 2)
                if cat.startswith(SURVEY_PREFIX) or cat in tables: continue
                row = {k: str(tt[k][0]) for k in tt.colnames if str(tt[k][0]) not in ("--", "", "nan")}
                tables[cat] = dict(table=tid, desc=tt.meta.get("description", ""), row=row)
        except Exception as e: rec["holes"].append(f"vizier {type(e).__name__}")
    rec["tables"] = tables
    # papers: from J/ tables (not the whole-sky catalogues) + SIMBAD refs
    bibs = {}
    for cat in tables:
        m = re.match(r"J/([^/]+)/(\d+)/([^/]+)", cat)
        if not m or cat in BIG: continue
        j, vol, page = m.groups(); j = JOUR.get(j, j)
        docs = adsq(f'bibstem:"{j}" volume:{vol} page:{page}')
        if docs is None: rec["holes"].append(f"ads {cat}"); continue
        for dd in docs[:1]: bibs[dd["bibcode"]] = dict(title=(dd.get("title") or [""])[0], arxiv=arxiv_of(dd), via=f"VizieR {cat}")
    for sr in sim_refs:
        b = sr["bibcode"]
        if b in bibs: continue
        docs = adsq(f"bibcode:{b}")
        if docs: bibs[b] = dict(title=(docs[0].get("title") or [""])[0], arxiv=arxiv_of(docs[0]), via="SIMBAD")
    pap = {}
    for b, info in bibs.items():
        if not info["arxiv"]: pap[b] = dict(info, passages=[], note="no arXiv source"); continue
        txt = src_text(info["arxiv"])
        if txt is None: pap[b] = dict(info, passages=[], note="HOLE: source not fetched"); rec["holes"].append(f"arxiv {info['arxiv']}"); continue
        pap[b] = dict(info, passages=passages(txt, AL))
    rec["papers"] = pap
    # ESO archive spectra
    try:
        q = f"SELECT obs_collection, instrument_name, dp_id, t_min, em_min, em_max, s_ra, s_dec FROM ivoa.ObsCore WHERE dataproduct_type='spectrum' AND CONTAINS(POINT('ICRS',s_ra,s_dec), CIRCLE('ICRS',{ra},{de},{5/3600}))=1"
        r = requests.get("https://archive.eso.org/tap_obs/sync", params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=120)
        rec["eso"] = pd.read_csv(io.StringIO(r.text)).to_dict("records") if r.ok else "HOLE"
    except Exception: rec["eso"] = "HOLE"; rec["holes"].append("eso")
    json.dump(rec, open(os.path.join(OUT, gaia + ".json"), "w"), default=str)
    with open(os.path.join(OUT, gaia + ".md"), "w") as f:
        f.write(f"# {nm} (Gaia DR3 {gaia}) — {status}\nAliases: {', '.join(AL)}\nHoles: {rec['holes'] or 'none'}\n\n## Science tables (VizieR, non-survey)\n")
        for cat, tinfo in tables.items(): f.write(f"- **{cat}** {tinfo['desc'][:90]}: " + "; ".join(f"{k}={v}" for k, v in list(tinfo['row'].items())[:40]) + "\n")
        f.write("\n## Papers mentioning the object (arXiv source grep)\n")
        for b, p in pap.items():
            f.write(f"- **{b}** ({p['via']}) {p['title'][:100]} — {len(p['passages'])} passages {p.get('note','')}\n")
            for s in p["passages"]: f.write(f"    > {s[:800]}\n")
        f.write(f"\n## ESO archive spectra (5 arcsec)\n{rec['eso'] if isinstance(rec['eso'], str) else [(x['instrument_name'], x['dp_id'], round(x['t_min'],1)) for x in rec['eso']]}\n")
    rows.append(dict(gaia=gaia, name=nm, status=status, n_tables=len(tables), n_papers=len(pap), n_papers_with_text=sum(1 for p in pap.values() if p["passages"]),
                     n_eso=len(rec["eso"]) if isinstance(rec["eso"], list) else -1, holes=";".join(rec["holes"])))
    print(gaia, nm[:40], "tables", len(tables), "papers", len(pap), "with passages", rows[-1]["n_papers_with_text"], "eso", rows[-1]["n_eso"], "holes", rec["holes"], flush=True)
S = os.path.join(H, "summary.csv"); pd.concat([pd.read_csv(S, dtype={"gaia": str}) if os.path.exists(S) else pd.DataFrame(), pd.DataFrame(rows)]).to_csv(S, index=False)
print("ALL-DONE", flush=True)
