import requests, json, csv, io, math
RA, DEC = 306.74802, -11.81856
out = {}
def tap(q, name):
    r = requests.get("https://datalab.noirlab.edu/tap/sync",
        params={"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q}, timeout=180)
    out[name] = {"status": r.status_code, "csv": r.text[:60000]}
    rows = []
    try:
        rows = list(csv.DictReader(io.StringIO(r.text)))
    except Exception:
        pass
    print(f"--- {name} [{r.status_code}] nrows={len(rows)} ---")
    for row in rows[:12]:
        try:
            sep = math.hypot((float(row["ra"])-RA)*math.cos(math.radians(DEC)), float(row["dec"])-DEC)*3600
            row["_sep_as"] = round(sep,2)
        except Exception: pass
        print({k: v for k, v in row.items()})
    return rows

tap(f"""SELECT id, ra, dec, gmag, rmag, imag, zmag, ndet, nphot, deltamjd, mjd, class_star
    FROM nsc_dr2.object
    WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA},{DEC},0.004167))=1""", "nsc_dr2")

tap(f"""SELECT ls_id, ra, dec, type, mag_g, mag_r, mag_i, mag_z, mag_w1, mag_w2
    FROM ls_dr10.tractor
    WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA},{DEC},0.004167))=1""", "ls_dr10")
json.dump(out, open("/tmp/rubin_pilot/forensics/170591519677875016/cones6.json","w"), indent=1)
