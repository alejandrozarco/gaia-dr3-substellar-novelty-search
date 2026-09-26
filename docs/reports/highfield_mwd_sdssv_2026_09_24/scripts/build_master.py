# Build the lane master table: every SnowWhite-classified SDSS-V DR20 row (50,960) joined (by Gaia DR3 id) to prior
# classifications: MWDD master table (spectype, teff, B field 'BD'), DESI DR1 Amorim+2026 (CLASS), Swan+2026 DESI (specType).
# Note MWDD key 'gaiaedr3' == Gaia DR3 source_id (identical ids EDR3/DR3).
import pandas as pd, numpy as np, json, gzip
d = pd.read_csv("sw_classified_all.csv")
m = json.load(open("/tmp/mwd/mwdd/table.json"))["data"]
mw = {}
for r in m:
    g = r.get("gaiaedr3")
    if g:
        mw[int(g)] = dict(mwdd_spectype=r.get("spectype"), mwdd_teff=r.get("teff"), mwdd_B=r.get("BD"), mwdd_wdid=r.get("wdid"),
                          mwdd_source=r.get("source"))
M = pd.DataFrame.from_dict(mw, orient="index"); M.index.name = "gaia_dr3_source_id"; M = M.reset_index()
d = d.merge(M, on="gaia_dr3_source_id", how="left")
# DESI DR1 (Amorim+2026)
A = pd.read_csv("/tmp/mwd/desi/DESI_CLASS_FINAL.txt", sep=r"\s+", comment=None, header=0)
A.columns = [c.lstrip("#") for c in A.columns]
A = A.rename(columns={"edr3id": "gaia_dr3_source_id", "CLASS": "desi_amorim_class"})[["gaia_dr3_source_id", "desi_amorim_class"]]
A = A.groupby("gaia_dr3_source_id")["desi_amorim_class"].apply(lambda s: "|".join(sorted(set(map(str, s))))).reset_index()
d = d.merge(A, on="gaia_dr3_source_id", how="left")
S = pd.read_csv("/tmp/mwd/desi/swan_cat.csv.gz", usecols=["designation", "specType", "specType_confidence"])
S["gaia_dr3_source_id"] = S.designation.str.replace("Gaia DR3 ", "").str.replace("Gaia DR2 ", "").astype("int64")  # DR2 ids kept (usually identical)
S = S.groupby("gaia_dr3_source_id").agg(swan_specType=("specType", lambda s: "|".join(sorted(set(map(str, s))))),
                                         swan_conf=("specType_confidence", "max")).reset_index()
d = d.merge(S, on="gaia_dr3_source_id", how="left")
d["bp_rp"] = d.bp_mag - d.rp_mag
d["MG"] = np.where(d.plx > 0, d.g_mag + 5 * np.log10(d.plx.clip(lower=1e-3)) - 10, np.nan)
d.to_csv("master.csv", index=False)
print(len(d), "rows; with MWDD", d.mwdd_spectype.notna().sum(), "; DESI-Amorim", d.desi_amorim_class.notna().sum(), "; Swan", d.swan_specType.notna().sum())
