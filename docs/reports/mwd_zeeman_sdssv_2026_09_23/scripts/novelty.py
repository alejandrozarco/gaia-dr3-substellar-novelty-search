# Novelty gate for the visually magnetic SnowWhite stars: (1) SIMBAD identifiers + bibcodes (TAP), (2) all-table VizieR cone
# (every table, 5" around the J2000-propagated position, plus the Gaia-epoch position), (3) flag any table row carrying a spectral
# type / class column with H, P or 'magnetic'. Every query is checked for failure and recorded as HOLE (never as an empty result).
# Note: in the 2026-09-23 run the SIMBAD join used b.oidbibref (wrong column) and returned HOLE for every target; SIMBAD was then
# queried with simbad_refs.py (data/simbad_refs_vis.json). The join is corrected here. Lists: vis_list.txt (targets), ctrl_list.txt.
import json, csv, time, sys, numpy as np, warnings, requests
warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
rows = {r["gaia_dr3_source_id"]: r for r in csv.DictReader(open("sw_magnetic.csv"))}
targets = [l.split()[0] for l in open("vis_list.txt") if l.strip() and not l.startswith("#")]
# Gaia astrometry for epoch propagation
q = "SELECT source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag, bp_rp FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(targets) + ")"
g = requests.get("https://gea.esac.esa.int/tap-server/tap/sync", params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=q), timeout=120).json()
cols = [c["name"] for c in g["metadata"]]; gaia = {str(r[0]): dict(zip(cols, r)) for r in g["data"]}
print("gaia rows", len(gaia), "of", len(targets), flush=True)
def simbad(gid):
    adql = ("SELECT i2.id, b.bibcode FROM ident AS i1 JOIN ident AS i2 ON i1.oidref = i2.oidref LEFT JOIN has_ref AS h ON h.oidref = i1.oidref "
            "LEFT JOIN ref AS b ON b.oidbib = h.oidbibref WHERE i1.id = 'Gaia DR3 " + gid + "'")
    for k in range(3):
        try:
            r = requests.post("https://simbad.cds.unistra.fr/simbad/sim-tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=adql), timeout=90)
            if r.status_code == 200:
                d = r.json()["data"]; return sorted({x[0] for x in d}), sorted({x[1] for x in d if x[1]})
        except Exception as e: err = str(e)
        time.sleep(3)
    return None, None
V = Vizier(columns=["**"], row_limit=50); V.TIMEOUT = 180
def allvizier(c):
    for k in range(3):
        try:
            return V.query_region(c, radius=5 * u.arcsec)
        except Exception as e:
            time.sleep(10)
    return None
out = {}
for gid in targets:
    s = gaia[gid]; dt = 2000.0 - 2016.0
    c2000 = SkyCoord((s["ra"] + s["pmra"] * dt / 3.6e6 / np.cos(np.radians(s["dec"]))) * u.deg, (s["dec"] + s["pmdec"] * dt / 3.6e6) * u.deg)
    ids, bibs = simbad(gid)
    tl = allvizier(c2000)
    rec = dict(gaia=gid, pm=[s["pmra"], s["pmdec"]], plx=s["parallax"], G=s["phot_g_mean_mag"], ra2000=c2000.ra.deg, dec2000=c2000.dec.deg,
               simbad_ids=ids, simbad_bibcodes=bibs, vizier=None, spectral_hits=[])
    if tl is not None:
        rec["vizier"] = []
        for t in tl:
            name = t.meta.get("name", "?"); rec["vizier"].append(name)
            for col in t.colnames:
                lc = col.lower()
                if any(k in lc for k in ("sptype", "sp", "spt", "class", "type", "mag_field", "bfield", "field", "b_mg", "remark", "note", "comment")):
                    for v in t[col]:
                        sv = str(v)
                        if any(k in sv for k in ("DAH", "DAP", "DH", "DBH", "DQH", "DZH", "H:", "magnet", "Magnet", "MWD", "Zeeman")) or (lc in ("b", "bfield", "b_mg") and sv not in ("--", "nan")):
                            rec["spectral_hits"].append(f"{name}:{col}={sv}")
    out[gid] = rec
    print(gid, "simbad ids", None if ids is None else len(ids), "bibs", None if bibs is None else len(bibs), "vizier tables", None if rec["vizier"] is None else len(rec["vizier"]),
          "MAG-HITS:", rec["spectral_hits"][:6], flush=True)
    json.dump(out, open("novelty.json", "w"), indent=1, default=str)
    time.sleep(1)
print("done")
