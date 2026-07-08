import requests, json
mjds=[57890.138207331,57890.139412822,57890.1414911299,57890.1435470843]
jds=[m+2400000.5 for m in mjds]
tlist="%20".join(f"'{jd:.7f}'" for jd in jds)
# Horizons API, center=W84 (CTIO), OBSERVER, quantities 1(astro RA/DEC),9(vmag),36(RA/DEC 3sig),37(POS uncert ellipse)
url=("https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND='2002%20KW14'"
     "&MAKE_EPHEM=YES&EPHEM_TYPE=OBSERVER&CENTER='coord@399'"
     )
# Use CTIO code directly: CENTER='W84@399' not valid; use SITE. Horizons obscode: CENTER='W84'
params={
 "format":"text",
 "COMMAND":"'2002 KW14'",
 "MAKE_EPHEM":"YES",
 "EPHEM_TYPE":"OBSERVER",
 "CENTER":"'W84'",
 "TLIST":" ".join(f"{jd:.7f}" for jd in jds),
 "TLIST_TYPE":"JD",
 "TIME_TYPE":"UT",
 "QUANTITIES":"'1,9,36,37'",
 "ANG_FORMAT":"DEG",
 "extra_prec":"YES",
 "CSV_FORMAT":"YES",
}
r=requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params=params, timeout=90)
print(r.status_code, len(r.text))
open("horizons_w84_4exp.txt","w").write(r.text)
# print SOE..EOE
t=r.text
import re
m=re.search(r"\$\$SOE(.*?)\$\$EOE", t, re.S)
print("=== EPHEM ===")
print(m.group(1).strip() if m else "NO SOE  --- head:\n"+t[:1500])
# also print the column header line before SOE
hdr=t.split("$$SOE")[0].splitlines()[-3:] if "$$SOE" in t else []
print("=== header ===")
for h in hdr: print(h)
