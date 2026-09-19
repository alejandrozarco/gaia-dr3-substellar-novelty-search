#!/usr/bin/env python3
"""Target list: Gaia DR3 bright stars NOT flagged variable, in a well-covered ZTF field.

The gap this lane exploits: a shallow (<0.3 mag), short-duty-cycle (<10%) eclipse
contributes almost nothing to RMS, so scatter-based variability selection - which
feeds Gaia's phot_variable_flag and most published ZTF variable catalogues - misses
it. Our own filed discovery (ZTF18abxnwmb, 5.7% duty, 0.216 mag, r=12.7, 2564 epochs,
uncatalogued) is the existence proof. So: deliberately select NON-variable-flagged
stars and run BLS directly, with no RMS pre-cut.
"""
import subprocess, urllib.parse, csv, io, json, random

def gaia(q, t=300):
    u = "https://gea.esac.esa.int/tap-server/tap/sync?" + urllib.parse.urlencode(
        {"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q})
    return subprocess.run(["curl","-sL","--max-time",str(t),u],capture_output=True,text=True).stdout

# Field centred near our proven EB (RA 338.6 +8.1): known-good ZTF coverage,
# moderate galactic latitude, avoids the worst crowding.
RA0, DEC0, BOX = 338.6, 8.1, 2.5
q = (f"SELECT source_id,ra,dec,phot_g_mean_mag,bp_rp,parallax,parallax_error,pmra,pmdec,ruwe "
     f"FROM gaiadr3.gaia_source "
     f"WHERE ra BETWEEN {RA0-BOX} AND {RA0+BOX} AND dec BETWEEN {DEC0-BOX} AND {DEC0+BOX} "
     f"AND phot_g_mean_mag BETWEEN 13.0 AND 17.0 "
     f"AND phot_variable_flag != 'VARIABLE' "
     f"AND ruwe < 1.4 "
     f"AND astrometric_excess_noise < 1.0")
print("querying Gaia DR3 ...", flush=True)
body = gaia(q)
rows = list(csv.DictReader(io.StringIO(body)))
print(f"Gaia DR3 sources, G 13-17, NOT variable-flagged, in {2*BOX}x{2*BOX} deg: {len(rows)}")
if not rows:
    print(body[:400]); raise SystemExit(1)

# Gaia source_ids are 19-digit -> keep as STRINGS (CLAUDE.md)
targets = [{"source_id": r["source_id"], "ra": float(r["ra"]), "dec": float(r["dec"]),
            "g": float(r["phot_g_mean_mag"]),
            "bp_rp": (float(r["bp_rp"]) if r["bp_rp"] not in ("","null") else None)}
           for r in rows]
random.seed(20260919); random.shuffle(targets)   # unbiased partial runs
json.dump(targets, open("targets.json","w"))
print(f"wrote targets.json ({len(targets)} targets, randomised order)")
import statistics
print(f"  G: median {statistics.median(t['g'] for t in targets):.2f}")
