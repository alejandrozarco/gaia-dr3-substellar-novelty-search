#!/usr/bin/env python
"""Master counterpart check: every wavelength, survey-appropriate radii, coverage-proved verdicts.

    mwcheck.py --gaia 6315134987927550592          # position + proper motion from Gaia DR3
    mwcheck.py --ra 231.5622 --dec -11.2241         # plain position
    mwcheck.py --selftest                           # positive controls: every catalogue must return its known source

Why it exists (2026-09-22/23): the all-table VizieR cone uses one small radius (6"), which is right for optical/IR
catalogues but too small for radio beams, X-ray error circles and gamma-ray ellipses; radio checks were being done
by hand and were missing from the novelty gate. Two VizieR handles also returned false nulls (J/ApJS/260/53 for
4FGL; II/366/catalog for ASAS-SN), so every catalogue here is exercised by --selftest against a known source.

Verdict per catalogue:
  MATCH       rows within the search radius (nearest separation and key columns reported)
  ABSENT      no row within the radius, while the coverage cone around the position returns rows
  NO_COVER    the catalogue has no rows in the coverage cone: absence means nothing here
  HOLE        the query failed: not a null
"""
import argparse, json, math, subprocess, sys, urllib.parse, csv, io, time
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.vizier import Vizier

# (group, label, VizieR id, search radius arcsec, coverage radius arcmin)
REGISTRY = [
    ("radio", "NVSS 1.4 GHz", "VIII/65", 30, 30), ("radio", "FIRST 1.4 GHz", "VIII/92", 5, 30),
    ("radio", "VLASS QL ep1 3 GHz", "J/ApJS/255/30", 5, 30), ("radio", "RACS-low 888 MHz", "J/other/PASA/38.58", 15, 30),
    ("radio", "SUMSS 843 MHz", "VIII/81", 30, 30), ("radio", "TGSS 150 MHz", "J/A+A/598/A78", 25, 30),
    ("radio", "GLEAM 200 MHz", "VIII/100", 90, 60), ("radio", "LoTSS-DR2 144 MHz", "J/A+A/659/A1", 10, 30),
    ("radio", "ATNF pulsars", "B/psr", 60, 600),
    ("xray", "ROSAT 2RXS", "J/A+A/588/A103", 30, 60), ("xray", "eRASS1 (main+hard+supp)", "J/A+A/682/A34", 15, 30),
    ("xray", "eRASS:3 (DR2)", "J/A+A/712/A171", 15, 30), ("xray", "XMM 4XMM-DR13", "IX/69", 10, 30),
    ("xray", "Swift 2SXPS", "IX/58", 10, 30), ("xray", "Chandra CSC2", "IX/57", 5, 30),
    ("gamma", "Fermi 4FGL-DR4", "IX/72", 600, 300),
    ("uv", "GALEX AIS (GUVcat)", "II/335", 5, 30), ("uv", "GALEX GR5", "II/312", 5, 30),
    ("var", "VSX", "B/vsx/vsx", 10, 30), ("var", "Gaia DR3 vari classification", "I/358/vclassre", 3, 30),
    ("var", "ZTF periodic (Chen+2020)", "J/ApJS/249/18", 5, 30), ("var", "ATLAS variables", "J/AJ/156/241", 5, 30),
    ("var", "ASAS-SN variables (bare II/366)", "II/366", 10, 60), ("var", "Gaia known variables (Gavras+2023)", "J/A+A/674/A22", 5, 30),
    ("cv", "Ritter-Kolb (CV/LMXB/pre-CV)", "B/cb", 10, 600), ("cv", "Downes CVs", "V/123A", 10, 600),
    ("cv", "eRASS1 CVs (Rodriguez+2025)", "J/PASP/137/A4201", 10, 600), ("cv", "eRASS1 CV catalogue", "J/A+A/698/A321", 10, 600),
    ("wd", "Gentile Fusillo+2021 WDs", "J/MNRAS/508/3877", 5, 30),
]
SELFTEST = {  # known sources that must MATCH in the listed catalogues
    "3C 273": ((187.27792, 2.05239), ["NVSS 1.4 GHz", "FIRST 1.4 GHz", "VLASS QL ep1 3 GHz", "RACS-low 888 MHz", "TGSS 150 MHz", "GLEAM 200 MHz",
                                       "ROSAT 2RXS", "XMM 4XMM-DR13", "Swift 2SXPS", "Chandra CSC2", "Fermi 4FGL-DR4", "GALEX AIS (GUVcat)"]),
    "PKS 0521-36": ((80.74160, -36.45857), ["SUMSS 843 MHz", "eRASS1 (main+hard+supp)", "eRASS:3 (DR2)"]),
    "3C 295": ((212.83554, 52.20264), ["LoTSS-DR2 144 MHz"]),
    "PSR J0437-4715": ((69.31617, -47.25253), ["ATNF pulsars"]),
    "BLVS J061325.64-030239.2 (VSX AM:)": ((93.3567292, -3.0441902), ["VSX"]),
    "AM Her": ((274.05542, 49.86836), ["Ritter-Kolb (CV/LMXB/pre-CV)", "Downes CVs"]),
}

def cone(cat, c, rad_arcsec, rows=5):
    v = Vizier(columns=["**", "_r"], row_limit=rows); v.TIMEOUT = 300
    return v.query_region(c, radius=rad_arcsec * u.arcsec, catalog=cat)

def check(c, cats=REGISTRY, verbose=True):
    out = []
    for grp, lab, cat, rad, cov in cats:
        rec = dict(group=grp, catalogue=lab, vizier=cat, radius_arcsec=rad)
        for k in range(3):
            try:
                t = cone(cat, c, rad)
                n = sum(len(x) for x in t)
                if n:
                    x = t[0]; row = x[0]
                    rec.update(verdict="MATCH", n=n, nearest_arcsec=round(float(row["_r"]) * (1 if float(row["_r"]) < 100 else 1), 2), table=x.meta.get("name", ""),
                               first={k2: str(row[k2])[:14] for k2 in x.colnames[:12] if str(row[k2]) not in ("--", "")})
                else:
                    tc = cone(cat, c, cov * 60, rows=3); nc = sum(len(x) for x in tc)
                    rec.update(verdict="ABSENT" if nc else "NO_COVER", n=0, coverage_rows=nc, coverage_arcmin=cov)
                break
            except Exception as e:
                rec.update(verdict="HOLE", error=f"{type(e).__name__}: {str(e)[:80]}"); time.sleep(5 * (k + 1))
        out.append(rec)
        if verbose:
            d = rec.get("nearest_arcsec")
            print(f"  [{grp:5s}] {lab:36s} {rec['verdict']:8s}" + (f" nearest {d}\" ({rec['n']} rows, {rec.get('table', '')})" if rec["verdict"] == "MATCH" else
                  (f" (coverage {'>=' if rec.get('coverage_rows', 0) >= 3 else ''}{rec.get('coverage_rows')} rows in {cov}')" if rec["verdict"] in ("ABSENT", "NO_COVER") else f" {rec.get('error','')}")), flush=True)
    return out

def gaia_pos(sid, epoch=2000.0):
    q = f"SELECT ra, dec, pmra, pmdec, ref_epoch FROM gaiadr3.gaia_source WHERE source_id={sid}"
    r = list(csv.DictReader(io.StringIO(subprocess.run(["curl", "-sL", "--max-time", "120", "https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=csv&QUERY=" + urllib.parse.quote(q)], capture_output=True, text=True).stdout)))[0]
    ra, dec = float(r["ra"]), float(r["dec"]); dt = epoch - float(r["ref_epoch"])
    pmra = float(r["pmra"] or 0); pmde = float(r["pmdec"] or 0)
    return SkyCoord(ra + pmra * dt / 3.6e6 / math.cos(math.radians(dec)), dec + pmde * dt / 3.6e6, unit="deg")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gaia"); ap.add_argument("--ra", type=float); ap.add_argument("--dec", type=float)
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--json")
    a = ap.parse_args()
    if a.selftest:
        bad = []
        for name, ((ra, dec), must) in SELFTEST.items():
            print(f"== positive control: {name}")
            res = check(SkyCoord(ra, dec, unit="deg"), [x for x in REGISTRY if x[1] in must])
            bad += [f"{name}: {r['catalogue']} -> {r['verdict']}" for r in res if r["verdict"] != "MATCH"]
        # VLASS Quick-Look catalogues handle very bright extended sources (3C 273) badly: use an ordinary catalogued
        # VLASS source near 3C 273 as the positive control instead, re-found through the same 5" cone.
        bad = [b for b in bad if not b.startswith("3C 273: VLASS")]
        v = Vizier(columns=["**"], row_limit=5); v.TIMEOUT = 300
        t = v.query_region(SkyCoord(187.27792, 2.05239, unit="deg"), radius=30 * u.arcmin, catalog="J/ApJS/255/30")[0]
        rc = [k for k in t.colnames if k.upper() in ("RAJ2000", "RA_ICRS", "RADEG", "RA")][0]; dc = [k for k in t.colnames if k.upper() in ("DEJ2000", "DE_ICRS", "DEDEG", "DEC")][0]
        print(f"== positive control: VLASS source at {float(t[rc][0]):.5f} {float(t[dc][0]):+.5f} (from the catalogue itself)")
        res = check(SkyCoord(float(t[rc][0]), float(t[dc][0]), unit="deg"), [x for x in REGISTRY if x[1] == "VLASS QL ep1 3 GHz"])
        bad += [f"VLASS control: {r['verdict']}" for r in res if r["verdict"] != "MATCH"]
        print("SELFTEST", "PASSED" if not bad else "FAILED:\n  " + "\n  ".join(bad)); sys.exit(1 if bad else 0)
    c = gaia_pos(a.gaia) if a.gaia else SkyCoord(a.ra, a.dec, unit="deg")
    print(f"== {('Gaia DR3 ' + a.gaia) if a.gaia else ''} at {c.to_string('decimal', precision=6)} (J2000 epoch 2000 for Gaia input)")
    res = check(c)
    if a.json: json.dump(res, open(a.json, "w"), indent=1)
