"""Coverage-proved absence checks: target cone 15" + coverage cone 20' per catalogue.
A catalogue counts as 'absent' only if the 20' cone returns rows (coverage) and the 15" cone returns none."""
import json, time
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
T = {"AREV_747_000417_zg_c05_q1": (152.58791749272, -3.53085080729, "3828306424841718656"),
     "AREV_1918_000493_zg_c16_q4": (320.51722263429, 6.955780047, "1738942132557316864"),
     "AREV_990_000495_zg_c14_q3": (337.7538767593, 6.763791034, "2709405317531811840")}
CATS = [("B/vsx/vsx", "VSX"), ("J/ApJS/249/18", "ZTF periodic variables (Chen+2020)"), ("J/AJ/156/241", "ATLAS variables (Heinze+2018)"),
        ("I/358/vclassre", "Gaia DR3 variability classification"), ("I/358/veb", "Gaia DR3 eclipsing binaries"),
        ("J/A+A/674/A22", "Gaia known-variable cross-match (Gavras+2023)"), ("II/366", "ASAS-SN variables (bare II/366)"),
        ("J/A+A/648/A44", "Gaia DR2 large-amplitude variables (Mowlavi+2021)"), ("J/A+A/677/A137", "Gaia DR3 dispersions (Maiz Apellaniz+2023)")]
out = {}
for sid, (ra, dec, dr3) in T.items():
    c = SkyCoord(ra, dec, unit="deg"); out[sid] = []
    for cat, lab in CATS:
        rec = dict(catalog=cat, label=lab)
        try:
            v = Vizier(columns=["**", "_r"], row_limit=50); v.TIMEOUT = 600
            tt = v.query_region(c, radius=15 * u.arcsec, catalog=cat)
            rec["target_rows"] = sum(len(t) for t in tt)
            rec["target_rmin"] = min((float(min(t["_r"])) for t in tt if len(t)), default=None)
            rec["target_first"] = {k: str(tt[0][0][k]) for k in tt[0].colnames[:25]} if len(tt) and len(tt[0]) else None
            cv = Vizier(columns=["_r"], row_limit=50); cv.TIMEOUT = 600
            tc = cv.query_region(c, radius=20 * u.arcmin, catalog=cat)
            rec["coverage_rows_20arcmin"] = sum(len(t) for t in tc)
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"[:200]
        verdict = ("HOLE" if "error" in rec else
                   "MATCH" if rec["target_rows"] else
                   "ABSENT, coverage proved" if rec["coverage_rows_20arcmin"] else "NO COVERAGE (false null risk)")
        rec["verdict"] = verdict; out[sid].append(rec)
        print(f"{sid} {lab:48s} target {rec.get('target_rows','-')} (rmin {rec.get('target_rmin')}) coverage20' {rec.get('coverage_rows_20arcmin','-')} -> {verdict}", flush=True)
        time.sleep(1)
json.dump(out, open("/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/arev/coverage.json", "w"), indent=1)
