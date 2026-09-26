# Novelty gate for Ca II / Balmer emission-line white dwarfs: SIMBAD (ids/type/refs), MWDD table.json, VizieR all-table 5" cone (emission/gas/binary-type
# values flagged), DESI DR1 (Amorim+2026 by position; Swan+2026 by Gaia id), arXiv source grep (Gaia id + Jhhmm+ddmm at 2000/2016),
# ADS full text by aliases. Failed queries are HOLE.
import sys, json, glob, os, re, gzip, io, requests, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
sys.path.insert(0, "/tmp/fanout"); from ads import search
ids = sys.argv[1:]
TAP = "https://gea.esac.esa.int/tap-server/tap/sync"
g = pd.read_csv(io.StringIO(requests.post(TAP, data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY="SELECT source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag, bp_rp FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(ids) + ")"), timeout=120).text), dtype={"source_id": str}).set_index("source_id")
M = {r["gaiaedr3"]: r for r in json.load(open("/tmp/mwd/mwdd/table.json"))["data"] if r.get("gaiaedr3")}
amor = pd.read_csv("/tmp/mwd/desi/DESI_CLASS_FINAL.txt", sep=r"\s+", dtype={"edr3id": str}) if os.path.exists("/tmp/mwd/desi/DESI_CLASS_FINAL.txt") else None
swan = pd.read_csv("/tmp/mwd/desi/swan_cat.csv.gz") if os.path.exists("/tmp/mwd/desi/swan_cat.csv.gz") else None
texts = {}
for f in glob.glob("/tmp/mwd/arx/**/*", recursive=True) + glob.glob("/tmp/fanout/exotic_atm/arx/**/*", recursive=True) + glob.glob("/tmp/fanout/magpuls/arx/**/*", recursive=True) + glob.glob("/tmp/hotdq/lane_gasdisc/arx/**/*", recursive=True):
    if os.path.isfile(f) and f.lower().endswith((".tex", ".txt", ".dat", ".csv", ".tab", ".mrt", ".bbl")):
        try: texts[f] = open(f, errors="ignore").read()
        except Exception: pass
print("arXiv source files:", len(texts), "papers:", len({f.split('/arx/')[1].split('/')[0] for f in texts}))
MAGRE = re.compile(r"gas|dis[ck]|emis|DAe|DAHe|DZe|DBe|[A-Z]e\b|CV|WD\+|PCEB|\+dM|\+M|MS|polar|nova", re.I)
out = {}
for gid in ids:
    r = g.loc[gid]; res = {}
    ra20, de20 = r.ra - (r.pmra * 16 / 3.6e6) / np.cos(np.radians(r.dec)), r.dec - r.pmdec * 16 / 3.6e6
    q = f"SELECT i2.id, b.main_id, b.otype, b.sp_type FROM ident i1 JOIN ident i2 ON i1.oidref = i2.oidref JOIN basic b ON b.oid = i1.oidref WHERE i1.id = 'Gaia DR3 {gid}'"
    try:
        s = pd.read_csv(io.StringIO(requests.post("https://simbad.cds.unistra.fr/simbad/sim-tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=60).text))
        res["simbad"] = dict(main_id=s.main_id.iloc[0] if len(s) else None, otype=s.otype.iloc[0] if len(s) else None, sp_type=s.sp_type.iloc[0] if len(s) else None, ids=s.id.tolist())
        q2 = f"SELECT r.bibcode FROM ident i JOIN has_ref h ON h.oidref = i.oidref JOIN ref r ON r.oidbib = h.oidbibref WHERE i.id = 'Gaia DR3 {gid}'"
        res["simbad_refs"] = pd.read_csv(io.StringIO(requests.post("https://simbad.cds.unistra.fr/simbad/sim-tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q2), timeout=60).text)).bibcode.tolist()
    except Exception as e: res["simbad"] = f"HOLE {e}"
    res["mwdd"] = (M.get(gid) or {}).get("spectype", "not listed")
    try:
        V = Vizier(columns=["**"], row_limit=50); V.TIMEOUT = 120
        tl = V.query_region(SkyCoord((ra20 + r.ra) / 2 * u.deg, (de20 + r.dec) / 2 * u.deg), radius=5 * u.arcsec)
        hits = []
        for t in tl:
            for c in t.colnames:
                if re.search(r"sp|type|class|SpT|Cl", c, re.I):
                    for v in t[c]:
                        if isinstance(v, (str, np.str_)) and MAGRE.search(str(v)): hits.append((t.meta.get("name", ""), c, str(v)))
        res["vizier"] = dict(n_tables=len(tl), em_type_hits=hits[:10])
    except Exception as e: res["vizier"] = f"HOLE {e}"
    if amor is not None:
        hit = amor[amor.edr3id == gid]
        sep = np.hypot((amor["RA(deg)"] - r.ra) * np.cos(np.radians(r.dec)), amor["DEC(deg)"] - r.dec) * 3600; k = int(np.argmin(sep))
        res["desi_amorim"] = dict(by_id=hit.CLASS.tolist(), nearest_arcsec=round(float(sep.iloc[k]), 1), nearest_class=str(amor.CLASS.iloc[k]))
    if swan is not None:
        hs = swan[swan.designation.astype(str).str.endswith(" " + gid)]
        res["desi_swan"] = dict(n=int(len(hs)), specType=hs.specType.astype(str).tolist(), teff=hs.TEFF.tolist())
    names = {gid}
    for ra, de in ((ra20, de20), (r.ra, r.dec)):
        c = SkyCoord(ra * u.deg, de * u.deg); h, m, s_ = c.ra.hms; d, dm, ds = np.abs(c.dec.dms); sg = "+" if de >= 0 else "-"
        for sgt in (sg, "$" + sg + "$", "−" if sg == "-" else "+"):
            names.add(f"J{int(h):02d}{int(m):02d}{sgt}{int(d):02d}{int(abs(dm)):02d}")
    res["arxiv_src_hits"] = sorted({f.split("/arx/")[1].split("/")[0] + ":" + p for f, t in texts.items() for p in names if p in t})
    res["ads"] = {}
    for a in sorted(names | set(res.get("simbad", {}).get("ids", []) if isinstance(res.get("simbad"), dict) else [])):
        if "$" in a: continue
        d_, n_ = search(f'full:"{a}"', 5)
        res["ads"][a] = "HOLE" if d_ is None else [x["bibcode"] for x in d_]
    out[gid] = res
    print(gid, json.dumps({k: v for k, v in res.items() if k != "ads"}, default=str)[:900]); print("   ADS:", {k: v for k, v in res["ads"].items() if v})
json.dump(out, open("gate_gas.json", "w"), indent=1, default=str)
