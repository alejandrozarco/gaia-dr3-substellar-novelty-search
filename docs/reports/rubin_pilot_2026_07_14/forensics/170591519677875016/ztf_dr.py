import requests
RA, DEC = 306.74802, -11.81856
# IRSA ZTF DR light curve API (public detections, not forced): 3" radius
r = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves",
    params={"POS": f"CIRCLE {RA} {DEC} 0.000833", "FORMAT": "csv", "BAD_CATFLAGS_MASK": "32768"},
    timeout=180)
print("status:", r.status_code)
lines = r.text.splitlines()
print("nrows:", max(0, len(lines)-1))
print("\n".join(lines[:5]))
open("/tmp/rubin_pilot/forensics/170591519677875016/ztf_dr_lc.csv","w").write(r.text)
