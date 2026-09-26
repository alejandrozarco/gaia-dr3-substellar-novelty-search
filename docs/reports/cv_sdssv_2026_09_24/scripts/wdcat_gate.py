# Local WD-catalogue gate (Gaia DR3/EDR3 id match): MWDD master table (/tmp/mwd/mwdd/table.json, 163,279 WDs, spectype),
# DESI DR1 Amorim+2026 (/tmp/mwd/desi/DESI_CLASS_FINAL.txt, CLASS) and Swan+2026 (/tmp/mwd/desi/swan_cat.csv.gz, specType).
import json, pandas as pd, gzip
sw = pd.read_csv("sw_cv_x2.csv"); ids = set(str(int(x)) for x in sw.gaia_dr3_source_id if x > 0)
mw = json.load(open("/tmp/mwd/mwdd/table.json"))["data"]
mwd = {}
for r in mw:
    for k in ("gaiaedr3", "gaiadr2"):
        g = r.get(k)
        if g in ids: mwd[g] = f"MWDD[{r.get('wdid','')}|{r.get('spectype','')}|{r.get('binarity','')}]"
print("MWDD rows", len(mw), "matched", len(mwd))
am = {}
with open("/tmp/mwd/desi/DESI_CLASS_FINAL.txt") as f:
    for line in f:
        if line.startswith("#"): continue
        p = line.split()
        if len(p) > 6 and p[1] in ids: am[p[1]] = f"Amorim2026DESI[{p[0]}|{p[6]}]"
print("Amorim matched", len(am))
sc = pd.read_csv("/tmp/mwd/desi/swan_cat.csv.gz", usecols=["WDJname", "designation", "specType"], dtype=str)
sc["g"] = sc.designation.str.replace("Gaia DR3 ", "", regex=False)
swn = {r.g: f"Swan2026DESI[{r.WDJname}|{r.specType}]" for r in sc.itertuples() if r.g in ids}
print("Swan matched", len(swn), "of", len(sc))
sw["wdcat_hits"] = [";".join(x for x in (mwd.get(g, ""), am.get(g, ""), swn.get(g, "")) if x) for g in sw.gaia_dr3_source_id.astype("int64").astype(str)]
sw.to_csv("sw_cv_x3.csv", index=False)
print((sw.wdcat_hits != "").sum(), "objects with WD-catalogue entries")
print(sw.wdcat_hits[sw.wdcat_hits.str.contains("CV|cv|Em|e\\]|DAe", regex=True)].head(30).to_string())
