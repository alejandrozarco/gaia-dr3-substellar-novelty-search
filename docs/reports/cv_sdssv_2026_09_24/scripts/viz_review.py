# Review the all-table VizieR cone results: drop generic all-sky photometric/astrometric catalogues and print the rest
# (with VizieR description and a compact first row) so every remaining table can be judged by eye.
import json, sys, re
a = json.load(open(sys.argv[1]))
GENERIC = re.compile(r"^(I/(2[0-9][0-9]|3[0-5][0-9]|360)/|II/(24[0-9]|2[5-9][0-9]|3[0-8][0-9]|39[0-9])/|IV/3[89]/|V/1(39|47|49|53|54|56|58|60|61|62|64|65)/|VI/42|VII/(233|28[0-9]|29[0-9])/|METAobj|ReadMeObj|B/assocdata|J/ApJ/867/105/refcat2|J/A\+A/692/A115|J/AJ/161/234|J/MNRAS/508/3877|J/MNRAS/482/4570|J/A\+A/674/A25/vspursig|J/ApJS/247/66)")
cands = sys.argv[2:] if len(sys.argv) > 2 else list(a)
for g in cands:
    r = a[g]
    if r["vizier_tables"] == "HOLE":
        print(g, "VIZIER HOLE"); continue
    keep = [t for t in r["vizier_tables"] if not GENERIC.match(t)]
    print(f"=== {g}: {len(r['vizier_tables'])} tables, {len(keep)} non-generic; SIMBAD cone: {r['simbad_cone'] if r['simbad_cone']=='HOLE' else [(x['main_id'], x['otype'], round(x['sep'],1)) for x in r['simbad_cone']]}")
    for t in keep:
        info = r["vizier_rows"].get(t, {})
        row = info.get("rows", [{}])[0] if info.get("rows") else {}
        cols = {k: v for k, v in row.items() if k not in ("_RA", "_DE", "RAJ2000", "DEJ2000", "RA_ICRS", "DE_ICRS", "recno", "_r") }
        print(f"   {t:32s} {info.get('desc','')[:70]:70s} | " + "; ".join(f"{k}={v}" for k, v in list(cols.items())[:10])[:230])
