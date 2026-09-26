# Gaia DR3 sources within R arcsec of a star (2016.0), with variability-table flags -> used for TESS contamination assessment
import sys, csv, io, json, requests
TAP = "https://gea.esac.esa.int/tap-server/tap/sync"
def adql(q):
    r = requests.post(TAP, data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=300)
    if r.status_code != 200: print("HOLE HTTP", r.status_code, r.text[:300]); sys.exit(2)
    return list(csv.DictReader(io.StringIO(r.text)))
sid = sys.argv[1]; R = float(sys.argv[2]) if len(sys.argv) > 2 else 180
g = adql(f"SELECT ra, dec FROM gaiadr3.gaia_source WHERE source_id={sid}")[0]
q = (f"SELECT g.source_id, g.ra, g.dec, g.phot_g_mean_mag, g.phot_bp_mean_mag, g.phot_rp_mean_mag, g.parallax, g.phot_variable_flag, "
     f"DISTANCE(POINT({g['ra']},{g['dec']}), POINT(g.ra,g.dec))*3600 AS sep, v.best_class_name, v.best_class_score "
     f"FROM gaiadr3.gaia_source AS g LEFT OUTER JOIN gaiadr3.vari_classifier_result AS v ON v.source_id = g.source_id "
     f"WHERE 1=CONTAINS(POINT(g.ra,g.dec), CIRCLE({g['ra']},{g['dec']},{R/3600})) AND g.phot_g_mean_mag < 20.5 ORDER BY sep")
N = adql(q)
print(f"{sid}: {len(N)} Gaia DR3 sources G<20.5 within {R}\"")
for n in N:
    G = float(n['phot_g_mean_mag']); br = (float(n['phot_bp_mean_mag']) - float(n['phot_rp_mean_mag'])) if n['phot_bp_mean_mag'] and n['phot_rp_mean_mag'] else float('nan')
    print(f"  {n['source_id']:>20s} sep={float(n['sep']):6.1f}\" G={G:6.2f} BP-RP={br:5.2f} plx={n['parallax'][:6]:>6s} var={n['phot_variable_flag']:<14s} {n['best_class_name'] or ''} {n['best_class_score'][:5] if n['best_class_score'] else ''}")
json.dump(N, open(f"data/gaia_env_{sid}.json", "w"), indent=1)
