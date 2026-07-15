import requests, json, csv, io, math
RA, DEC = 306.74802, -11.81856
r_deg = 0.004167  # 15"
cosd = math.cos(math.radians(DEC))
out = {}
def tap(q, name):
    r = requests.get("https://datalab.noirlab.edu/tap/sync",
        params={"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q}, timeout=180)
    out[name] = {"status": r.status_code, "csv": r.text[:60000]}
    rows = list(csv.DictReader(io.StringIO(r.text))) if r.text.startswith(("id","ls_id","ra")) or "," in r.text.splitlines()[0] else []
    print(f"--- {name} [{r.status_code}] ---")
    if "ERROR" in r.text[:500]:
        print(r.text[:800]); return
    for row in rows:
        try:
            sep = math.hypot((float(row["ra"])-RA)*cosd, float(row["dec"])-DEC)*3600
            row["sep_as"] = f"{sep:.2f}"
        except Exception: pass
    rows.sort(key=lambda x: float(x.get("sep_as", 999)))
    print(f"nrows={len(rows)}")
    for row in rows[:15]: print(row)

tap(f"""SELECT id, ra, dec, gmag, rmag, imag, zmag, ndet, nphot, deltamjd, mjd, class_star
    FROM nsc_dr2.object
    WHERE ra BETWEEN {RA-r_deg/cosd} AND {RA+r_deg/cosd} AND dec BETWEEN {DEC-r_deg} AND {DEC+r_deg}""", "nsc_dr2")

tap(f"""SELECT ls_id, ra, dec, type, mag_g, mag_r, mag_i, mag_z, mag_w1, mag_w2
    FROM ls_dr10.tractor
    WHERE ra BETWEEN {RA-r_deg/cosd} AND {RA+r_deg/cosd} AND dec BETWEEN {DEC-r_deg} AND {DEC+r_deg}""", "ls_dr10")
json.dump(out, open("/tmp/rubin_pilot/forensics/170591519677875016/cones7.json","w"), indent=1)
