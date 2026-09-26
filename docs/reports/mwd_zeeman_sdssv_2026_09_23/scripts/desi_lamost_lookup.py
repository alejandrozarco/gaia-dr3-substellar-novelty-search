# Survey coverage per target: DESI DR1 spectra (Legacy Survey viewer layer desi-spec-dr1, 6" box around the J2000 and 2016.0
# positions) and LAMOST DR10 v2.0 low-resolution spectra (China-VO cone search, 9" radius; class/subclass parsed from the raw XML
# because the VOTable declares char fields with arraysize 1). Failed queries are recorded as HOLE, never as empty.
# Positive controls used on 2026-09-23: COSMOS box returns DESI spectra; Gaia DR3 3347953532952671360 returns LAMOST obsid 506009032.
import json, re, time, requests, numpy as np
C = json.load(open("coords_vis.json")); desi, lam = {}, {}
for g, c in C.items():
    ra16 = c["ra2000"] + c["pm"][0] * 16 / 3.6e6 / np.cos(np.radians(c["dec2000"])); de16 = c["dec2000"] + c["pm"][1] * 16 / 3.6e6
    d = 6 / 3600; dr = d / np.cos(np.radians(de16))
    try:
        r = requests.get("https://www.legacysurvey.org/viewer/desi-spec-dr1/1/cat.json", params=dict(ralo=min(ra16, c["ra2000"]) - dr, rahi=max(ra16, c["ra2000"]) + dr,
                         declo=min(de16, c["dec2000"]) - d, dechi=max(de16, c["dec2000"]) + d), timeout=60)
        j = r.json(); desi[g] = list(zip(j["name"], j.get("targetid", []), j.get("survey", []))) if r.status_code == 200 else "HOLE"
    except Exception as e: desi[g] = "HOLE " + str(e)[:80]
    de = (de16 + c["dec2000"]) / 2; ra = (ra16 + c["ra2000"]) / 2
    if de < -12: lam[g] = "OUT_OF_LAMOST_DEC"
    else:
        try:
            x = requests.get("https://www.lamost.org/dr10/v2.0/voservice/conesearch", params=dict(ra=ra, dec=de, sr=0.0025), timeout=90).text
            names = re.findall(r'<FIELD[^>]*name="([^"]+)"', x); rows = re.findall(r"<TR>(.*?)</TR>", x, re.S)
            lam[g] = [{k: dict(zip(names, re.findall(r"<TD>(.*?)</TD>", rr, re.S))).get(k) for k in ("obsid", "designation", "obsdate", "class", "subclass", "snrg")} for rr in rows]
        except Exception as e: lam[g] = "HOLE " + str(e)[:80]
    print(g, "DESI:", desi[g], "| LAMOST:", lam[g], flush=True); time.sleep(0.3)
json.dump(desi, open("desi_dr1_vis.json", "w"), indent=1); json.dump(lam, open("lamost_dr10_vis.json", "w"), indent=1)
