# Prior-classification gate, survey part, for the lane candidates: MWDD (Gaia id), DESI DR1 class tables (Amorim+2026,
# Swan+2026), DESI DR1 spectrum existence (Legacy Survey viewer layer desi-spec-dr1), LAMOST DR10 v2.0 cone, SDSS DR17
# SpecObjAll cone (older SDSS/BOSS spectra). Every failed query is recorded as HOLE.
import json, re, time, requests, numpy as np, pandas as pd, sys
C = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "coords.json")); out = {}
mw = {}
for r in json.load(open("/tmp/mwd/mwdd/table.json"))["data"]:
    if r.get("gaiaedr3") in C: mw[r["gaiaedr3"]] = {k: r.get(k) for k in ("wdid", "spectype", "teff", "logg", "BD", "source", "nbOpt", "allnames")}
A = pd.read_csv("/tmp/mwd/desi/DESI_CLASS_FINAL.txt", sep=r"\s+", header=0); A.columns = [c.lstrip("#") for c in A.columns]
Sw = pd.read_csv("/tmp/mwd/desi/swan_cat.csv.gz", usecols=["WDJname", "designation", "specType", "specType_confidence"])
for g, c in C.items():
    rec = dict(mwdd=mw.get(g))
    a = A[A.edr3id.astype(str) == g]; rec["desi_amorim"] = a[["Name", "CLASS"]].values.tolist()
    s = Sw[Sw.designation.str.endswith(" " + g)]; rec["desi_swan"] = s[["WDJname", "specType", "specType_confidence"]].values.tolist()
    d = 6 / 3600; dr = d / np.cos(np.radians(c["dec2016"]))
    try:
        r = requests.get("https://www.legacysurvey.org/viewer/desi-spec-dr1/1/cat.json", params=dict(
            ralo=min(c["ra2016"], c["ra2000"]) - dr, rahi=max(c["ra2016"], c["ra2000"]) + dr, declo=min(c["dec2016"], c["dec2000"]) - d, dechi=max(c["dec2016"], c["dec2000"]) + d), timeout=60)
        j = r.json(); rec["desi_dr1_spectra"] = list(zip(j.get("name", []), j.get("targetid", []), j.get("survey", []))) if r.status_code == 200 else f"HOLE HTTP {r.status_code}"
    except Exception as e: rec["desi_dr1_spectra"] = "HOLE " + str(e)[:80]
    ra, de = (c["ra2016"] + c["ra2000"]) / 2, (c["dec2016"] + c["dec2000"]) / 2
    if de < -12: rec["lamost_dr10"] = "OUT_OF_LAMOST_DEC"
    else:
        try:
            x = requests.get("https://www.lamost.org/dr10/v2.0/voservice/conesearch", params=dict(ra=ra, dec=de, sr=0.0025), timeout=90)
            names = re.findall(r'<FIELD[^>]*name="([^"]+)"', x.text); rows = re.findall(r"<TR>(.*?)</TR>", x.text, re.S)
            rec["lamost_dr10"] = [{k: dict(zip(names, re.findall(r"<TD>(.*?)</TD>", rr, re.S))).get(k) for k in ("obsid", "designation", "obsdate", "class", "subclass", "snrg")} for rr in rows] if x.status_code == 200 and names else f"HOLE HTTP {x.status_code}"
        except Exception as e: rec["lamost_dr10"] = "HOLE " + str(e)[:80]
    sql = (f"SELECT s.specObjID, s.plate, s.mjd, s.fiberID, s.run2d, s.class, s.subClass, s.z, s.snMedian, s.survey, "
           f"dbo.fDistanceArcMinEq({c['ra2000']},{c['dec2000']},s.ra,s.dec)*60 AS sep FROM SpecObjAll s WHERE "
           f"dbo.fDistanceArcMinEq({c['ra2000']},{c['dec2000']},s.ra,s.dec) < 0.1")
    try:
        r = requests.get("https://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch", params=dict(cmd=sql, format="csv"), timeout=120)
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        rec["sdss_dr17_specobjall"] = [dict(zip(lines[0].split(","), l.split(","))) for l in lines[1:]] if r.status_code == 200 and lines and lines[0].startswith("specObjID") else f"HOLE HTTP {r.status_code}: {r.text[:120]}"
    except Exception as e: rec["sdss_dr17_specobjall"] = "HOLE " + str(e)[:80]
    out[g] = rec
    print(g, "| MWDD", (rec["mwdd"] or {}).get("spectype"), (rec["mwdd"] or {}).get("wdid"), "| DESI-A", rec["desi_amorim"], "| Swan", rec["desi_swan"], "| DESI spec", rec["desi_dr1_spectra"],
          "| LAMOST", rec["lamost_dr10"], "| DR17", rec["sdss_dr17_specobjall"] if isinstance(rec["sdss_dr17_specobjall"], str) else [(x.get("plate"), x.get("mjd"), x.get("fiberID"), x.get("class"), x.get("subClass"), x.get("snMedian")) for x in rec["sdss_dr17_specobjall"]], flush=True)
    time.sleep(0.3)
json.dump(out, open(sys.argv[2] if len(sys.argv) > 2 else "gate_surveys.json", "w"), indent=1)
