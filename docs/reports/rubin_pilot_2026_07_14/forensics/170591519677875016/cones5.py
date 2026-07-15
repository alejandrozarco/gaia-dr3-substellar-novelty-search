import requests, json
RA, DEC = 306.74802, -11.81856
tokr = requests.get("https://datalab.noirlab.edu/auth/login", params={"username":"anonymous","password":""}, timeout=60)
tok = tokr.text.strip()
print("auth status:", tokr.status_code, "token-ish:", tok.startswith("anonymous"))
H = {"X-DL-AuthToken": tok}
out = {}
def q(sql, name):
    r = requests.get("https://datalab.noirlab.edu/query/query",
        params={"sql": sql, "ofmt": "csv"}, headers=H, timeout=180)
    print(f"--- {name} [{r.status_code}] ---"); print(r.text[:2500])
    out[name] = {"status": r.status_code, "csv": r.text[:30000]}

q(f"""SELECT id, ra, dec, gmag, rmag, imag, zmag, ndet, nphot, deltamjd, mjd, class_star,
    q3c_dist(ra,dec,{RA},{DEC})*3600 AS sep_as
    FROM nsc_dr2.object
    WHERE q3c_radial_query(ra,dec,{RA},{DEC},0.004167)
    ORDER BY sep_as""", "nsc_dr2")

q(f"""SELECT ls_id, ra, dec, type, mag_g, mag_r, mag_i, mag_z, mag_w1, mag_w2,
    q3c_dist(ra,dec,{RA},{DEC})*3600 AS sep_as
    FROM ls_dr10.tractor
    WHERE q3c_radial_query(ra,dec,{RA},{DEC},0.004167)
    ORDER BY sep_as""", "ls_dr10")
json.dump(out, open("/tmp/rubin_pilot/forensics/170591519677875016/cones5.json","w"), indent=1)
