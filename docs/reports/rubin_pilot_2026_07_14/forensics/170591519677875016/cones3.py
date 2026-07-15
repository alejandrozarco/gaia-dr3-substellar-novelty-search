import requests, json
RA, DEC = 306.74802, -11.81856
out = {}
def tap(q, name):
    r = requests.get("https://datalab.noirlab.edu/tap/sync",
        params={"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q}, timeout=120)
    print(f"--- {name} [{r.status_code}] ---"); print(r.text[:2500])
    out[name] = {"status": r.status_code, "csv": r.text[:30000]}

tap(f"""SELECT id, ra, dec, gmag, rmag, imag, zmag, ndet, nphot, deltamjd, mjd, variable10, class_star,
    DISTANCE(POINT('ICRS',ra,dec),POINT('ICRS',{RA},{DEC}))*3600 AS sep_as
    FROM nsc_dr2.object
    WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA},{DEC},0.004167))=1
    ORDER BY sep_as""", "nsc_dr2")

tap(f"""SELECT ls_id, ra, dec, type, mag_g, mag_r, mag_i, mag_z, mag_w1, mag_w2, fitbits,
    DISTANCE(POINT('ICRS',ra,dec),POINT('ICRS',{RA},{DEC}))*3600 AS sep_as
    FROM ls_dr10.tractor
    WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA},{DEC},0.004167))=1
    ORDER BY sep_as""", "ls_dr10")
json.dump(out, open("/tmp/rubin_pilot/forensics/170591519677875016/cones3.json","w"), indent=1)
