# Rank the three lane selections for spectrum download (budget-limited), using catalogue information only.
# A: p_mwd > 0.05 (7 stars, all taken)
# B: p_dah > 0.1 and p_dah+p_dahe+p_dbh+p_mwd <= 0.3 (1104 rows): SnowWhite DA-fit pathologies are the signal: logg at the
#    grid edge (>= 9.3), failed fit (-9999), or spectroscopic Teff far from the photometric Teff; ranked by S/N.
# C: classification contains 'DC', snr > 15 (1948 rows); main-sequence-dominated classes dropped; score = probability mass on
#    feature-bearing classes (CV, DQ, DZ, DA, DAH, MWD ...) and a hot-DC flag (photometric Teff > 11 kK: a DC that hot is
#    physically unexpected and the classic hiding place of high-field MWDs).
# Positive controls (MWDD B >= 20 MG) are tracked to show where they fall in each ranking.
import pandas as pd, numpy as np
d = pd.read_csv("master.csv", low_memory=False)
d["BDf"] = pd.to_numeric(d.mwdd_B, errors="coerce"); d["mwdd_teff"] = pd.to_numeric(d.mwdd_teff, errors="coerce")
# empirical photometric Teff from Gaia BP-RP, calibrated on MWDD Teff (rows that have both), for rows lacking MWDD Teff
ok = d.mwdd_teff.between(3500, 80000) & d.bp_rp.between(-0.6, 1.6)
cal = d[ok]; bins = np.arange(-0.6, 1.65, 0.05); idx = np.digitize(cal.bp_rp, bins)
med = pd.Series(np.log10(cal.mwdd_teff)).groupby(idx).median()
centers = np.array([bins[i - 1] + 0.025 for i in med.index]); vals = med.values
d["teff_bprp"] = np.where(d.bp_rp.notna(), 10 ** np.interp(d.bp_rp.fillna(0), centers, vals), np.nan)
d["teff_phot"] = d.mwdd_teff.where(d.mwdd_teff.between(3000, 150000), d.teff_bprp)
mag_known = d.mwdd_spectype.fillna("").str.replace("He", "").str.contains("H|P") | d.desi_amorim_class.fillna("").str.contains("DAH|DBH|DQH|MWD") \
    | d.swan_specType.fillna("").str.contains("DAH|DH|DBH|DQH")
d["mag_known"] = mag_known
done78 = set(pd.read_csv("/tmp/mwd/sw_magnetic.csv").gaia_dr3_source_id)
d["in78"] = d.gaia_dr3_source_id.isin(done78)
# --- A
A = d[d.p_mwd > 0.05].copy(); A["sel"] = "A"
# --- B
Bm = (d.p_dah > 0.1) & (d.p_dah + d.p_dahe + d.p_dbh + d.p_mwd <= 0.3) & ~d.in78
B = d[Bm].copy()
B["fitflag"] = (B.logg >= 9.3) | (B.teff < 0) | ((B.teff > 0) & (np.abs(np.log10(B.teff.clip(lower=1) / B.teff_phot)) > 0.2))
B["sel"] = "B"
# --- C
Cm = d.classification.str.contains("DC") & (d.snr > 15) & ~d.in78
C = d[Cm].copy()
ms_only = C.classification.apply(lambda s: all(("_MS" in p) or p.startswith("CV") for p in s.split("/")))
C = C[~ms_only].copy()
C["feat_mass"] = C[["p_cv", "p_dq", "p_dqpec", "p_hotdq", "p_dz", "p_dah", "p_dahe", "p_dbh", "p_mwd", "p_da", "p_db", "p_dao"]].sum(axis=1)
C["hot"] = C.teff_phot > 11000
C["sel"] = "C"
for name, X in (("B", B), ("C", C)):
    X.to_csv(f"sel_{name}.csv", index=False)
A.to_csv("sel_A.csv", index=False)
print("A", len(A), "B", len(B), "B fitflag", B.fitflag.sum(), "B fitflag & snr>=12 & not known", (B.fitflag & (B.snr >= 12) & ~B.mag_known).sum())
print("C", len(C), "C hot", C.hot.sum(), "C hot not known", (C.hot & ~C.mag_known).sum())
ctrl = d[d.BDf >= 20][["gaia_dr3_source_id", "mwdd_wdid", "BDf", "classification", "snr", "teff_phot"]]
print(ctrl.to_string())
