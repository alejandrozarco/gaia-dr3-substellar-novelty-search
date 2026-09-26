# Gaia DR3 astrometry + neighbours for the positive (known MWD rotators) and negative (non-magnetic DA) controls.
import json, csv, io, sys, requests
TAP = "https://gea.esac.esa.int/tap-server/tap/sync"
def adql(q):
    r = requests.post(TAP, data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=300)
    if r.status_code != 200: print("HOLE HTTP", r.status_code, r.text[:300]); sys.exit(2)
    return list(csv.DictReader(io.StringIO(r.text)))
pos = [("2712240064671438720", "EGGR 156 = SDSS J2257+0755", "P = 22.4 min (Williams+2022 AJ 164 131; Moss+2025 0.37 h, ZTF)", 22.4 / 60 / 24),
       ("1878189370339859328", "SDSS J222348.52+231909.2", "P = 1.42 h (Moss+2025, ZTF)", 1.42 / 24),
       ("1304733106575117056", "SDSS J1630+2724", "P = 14.86 h (Moss+2025, ZTF)", 14.86 / 24),
       ("1273088783971336576", "SDSS J1543+3021", "P = 1.31 h (Moss+2025 TESS+ZTF; Oliveira da Rosa+2024)", 1.31 / 24)]
neg = [("1355633897871121280", "SDSS J164255.17+393105.2", "non-magnetic DA, SnowWhite p_da>0.97, Teff~25 kK", None),
       ("3620237490101826688", "Gaia DR3 3620237490101826688", "non-magnetic DA, SnowWhite p_da>0.97, Teff~21 kK", None),
       ("1016882298157369984", "Gaia DR3 1016882298157369984", "non-magnetic DA, SnowWhite p_da>0.97, Teff~18 kK", None)]
out = []
for grp, L in (("pos_ctrl", pos), ("neg_ctrl", neg)):
    for sid, name, note, Pd in L:
        g = adql("SELECT source_id, ra, dec, pmra, pmdec, parallax, parallax_error, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, ruwe, "
                 f"phot_variable_flag, has_epoch_photometry FROM gaiadr3.gaia_source WHERE source_id = {sid}")
        assert len(g) == 1, sid
        g = g[0]
        N = adql("SELECT source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, "
                 f"DISTANCE(POINT({g['ra']},{g['dec']}), POINT(ra,dec))*3600 AS sep FROM gaiadr3.gaia_source "
                 f"WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({g['ra']},{g['dec']},{10/3600})) AND source_id != {sid} ORDER BY sep")
        rec = dict(g); rec.update(name=name, group=grp, note=note, P_pub_d=Pd, neighbours_10as=N)
        out.append(rec)
        print(grp, sid, name[:28].ljust(28), "G=%.2f" % float(g['phot_g_mean_mag']), "dec=%+.2f" % float(g['dec']), "var=" + g['phot_variable_flag'],
              "nb<5\":", [(round(float(n['sep']), 2), round(float(n['phot_g_mean_mag']), 2) if n['phot_g_mean_mag'] else None) for n in N if float(n['sep']) < 5])
json.dump(out, open("data/controls.json", "w"), indent=1)
