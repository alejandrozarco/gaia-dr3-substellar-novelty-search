# Build master.csv = SnowWhite CV selection (sw_cv_x3.csv: SW columns + Gaia DR3 + local/arXiv/WD-catalogue prior hits)
# + line measurements (lines_all.csv) + SDSS-V cartons + SIMBAD otype. Prior flag = any catalogue/arXiv hit, MWDD/DESI CV class,
# or SIMBAD CV-family otype.
import pandas as pd, numpy as np, json
sw = pd.read_csv("sw_cv_x3.csv"); L = pd.read_csv("lines_all.csv").drop(columns=["gaia"]); c = pd.read_csv("sw_cartons.csv")
m = sw.merge(L, on="sdss_id").merge(c, on="sdss_id", how="left")
sb = json.load(open("simbad_bulk.json"))["found"]
g = m.gaia_dr3_source_id.astype("int64").astype(str)
m["simbad_otype"] = [sb.get(x, {}).get("otype", "") for x in g]
m["simbad"] = [sb.get(x, {}).get("otype", "") + "|" + str(sb.get(x, {}).get("main_id", "")) for x in g]
m["prior"] = (m.n_local > 0) | (m.n_arx > 0) | m.wdcat_hits.fillna("").str.contains("CV|AMCVn") | m.simbad_otype.isin(
    ["CV*", "CV?", "No*", "No?", "AM*", "AM?", "DN*", "DQ*", "NL*", "XB*", "LXB", "HXB"])
m["redblue"] = m.f7400_7600 / m.f4000_4200; m["heii_hb"] = m.HeII4686_ew / m.Hb_ew
m["neb"] = ((m.NII6585_sig > 4) & (m.NII6585_ew > 1)) | ((m.SII6718_sig > 4) & (m.SII6718_ew > 1)) | ((m.OIII5008_sig > 5) & (m.OIII5008_ew > 2))
em = (m.Ha_ew > 5) & (m.Ha_sig > 5)
m["cvlike"] = em & ((m.Ha_fwhm > 400) | ((m.HeI5876_sig > 3) & (m.HeI5876_ew > 0)) | ((m.HeI6678_sig > 3) & (m.HeI6678_ew > 0)) | ((m.HeII4686_sig > 3) & (m.HeII4686_ew > 0)))
m["heonly"] = ((m.HeI5876_sig > 4) & (m.HeI5876_ew > 2)) & ~em
m.to_csv("master.csv", index=False)
print(len(m), "rows; prior", m.prior.sum(), "; nebular-flagged", m.neb.sum(), "; cvlike", m.cvlike.sum(), "; cvlike&~prior&~neb", (m.cvlike & ~m.prior & ~m.neb).sum())
