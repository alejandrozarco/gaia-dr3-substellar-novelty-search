"""Multi-channel anomaly table for the SDSS-V DR20 white-dwarf sample (targets.csv, 50,886 objects).
Each channel gives (measured, flagged). Reference relations are robust medians/MADs in colour or magnitude bins.
Channels: HR (M_G residual vs BP-RP), RUWE, GVAR (Gaia G-flux scatter metric vs G), IR (G-W1 residual vs BP-RP),
UV (NUV-G residual vs BP-RP), XRAY (eRASS1/eRASS:3 match; measured only in the eROSITA-DE half, l >= 180),
HALPHA (H-alpha screen T1/T2, not nebular), HELINES (coadd screen DAB or DAO channel hit in a non-He class), MAG (magnetic class),
TESS (on-star-plausible TESS 2-min period; measured only for stars in the sweep). Blend veto: corrected BP/RP excess > 5 sigma
or ipd_frac_multi_peak > 10 -> the Gaia-photometry channels (HR, GVAR) and IR/UV are not counted.
Output: wd_channels.csv; channel rates and pair-coincidence excess printed."""
import os
import pandas as pd, numpy as np, itertools
S = os.path.expanduser("~/claude_projects/spectra_store/sdssv_dr20"); R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TS = os.environ.get("TESS2MIN_DIR", "tess2min")  # local directory with the TESS 2-min sweep outputs
T = pd.read_csv(f"{S}/targets.csv", dtype={"gaia_dr3_source_id": str, "sdss_id": str}, low_memory=False).rename(columns={"gaia_dr3_source_id": "gaia"})
G = pd.read_csv("gaia_cols.csv", dtype={"source_id": str}).rename(columns={"source_id": "gaia"})
D = T.merge(G, on="gaia", how="inner"); D = D.drop_duplicates("gaia")
def rz(x, key, width, min_n=30):
    """robust z of x relative to its median in bins of key"""
    b = np.floor(key / width); out = pd.Series(np.nan, index=x.index)
    for k, idx in x.groupby(b).groups.items():
        v = x.loc[idx]; v0 = v.dropna()
        if len(v0) < min_n: continue
        med = v0.median(); mad = 1.4826 * (v0 - med).abs().median()
        if mad > 0: out.loc[idx] = (v - med) / mad
    return out
# blend veto (Riello+2021 corrected excess C*)
x = D.bp_rp; C = D.phot_bp_rp_excess_factor - (1.154360 + 0.033772 * x + 0.032277 * x**2)
C = C.where(x >= 0.5, D.phot_bp_rp_excess_factor - (1.154360 + 0.033772 * x + 0.032277 * x**2))
sig = 0.0059898 + 8.817481e-12 * D.phot_g_mean_mag ** 7.618399
D["blend"] = (C.abs() / sig > 5) | (D.ipd_frac_multi_peak > 10)
D["MGg"] = D.phot_g_mean_mag + 5 * np.log10(D.parallax / 100)
ch = {}
m = (D.parallax / D.parallax_error > 5) & ~D.blend; z = rz(D.MGg, D.bp_rp, 0.05); ch["HR"] = (m & z.notna(), m & (z.abs() > 4)); D["z_HR"] = z
m = D.ruwe.notna(); ch["RUWE"] = (m, m & (D.ruwe > 1.4))
V = np.log10(np.sqrt(D.phot_g_n_obs) * D.phot_g_mean_flux_error / D.phot_g_mean_flux); z = rz(V, D.phot_g_mean_mag, 0.25); D["z_GVAR"] = z
m = z.notna() & ~D.blend; ch["GVAR"] = (m, m & ((z > 5) | (D.phot_variable_flag == "VARIABLE")))
W = pd.read_csv("xm_allwise.csv", dtype={"source_id": str}).set_index("source_id")
ok = (W.e_W1mag < 0.2) & (W.ex == 0) & (W.ccf.astype(str).str[0].isin(["0", "nan"]))
D["W1"] = W.W1mag.where(ok).reindex(D.gaia).values; z = rz(D.phot_g_mean_mag - D.W1, D.bp_rp, 0.1); D["z_IR"] = z
m = z.notna() & ~D.blend; ch["IR"] = (m, m & (z > 5))
U = pd.read_csv("xm_galex.csv", dtype={"source_id": str}).set_index("source_id")
D["NUV"] = U.nuv_mag.where(U.nuv_magerr < 0.2).reindex(D.gaia).values; z = rz(D.NUV - D.phot_g_mean_mag, D.bp_rp, 0.1); D["z_UV"] = z
m = z.notna() & ~D.blend; ch["UV"] = (m, m & (z.abs() > 5))
xr = set(pd.read_csv("xm_erass1.csv", dtype={"source_id": str}).source_id) | set(pd.read_csv("xm_erass3.csv", dtype={"source_id": str}).source_id)
m = D.l >= 180; ch["XRAY"] = (m, m & D.gaia.isin(xr))
V2 = pd.read_csv(f"{S}/vet_list.csv", dtype={"gaia": str}, low_memory=False); CL = pd.read_csv(f"{S}/candidates_clean.csv", dtype={"gaia": str}, low_memory=False)
F = pd.read_csv(f"{S}/screen_full.csv", dtype={"gaia": str}, usecols=["gaia", "status"], low_memory=False)
ha = set(CL[CL.rank_class.isin(["T1", "T2"])].gaia) | set(V2[(V2.rank_class == "T1") & (V2.nebular != True)].gaia)
m = D.gaia.isin(set(F[F.status == "ok"].gaia)); ch["HALPHA"] = (m, m & D.gaia.isin(ha))
LC = pd.read_csv(f"{S}/line_candidates.csv", dtype={"gaia": str}, low_memory=False); CO = pd.read_csv(f"{S}/coadd_lines.csv", dtype={"gaia": str}, usecols=["gaia", "cls", "status"], low_memory=False)
hecls = D.classification.astype(str).str.contains(r"DB|DO|He|DZB|DBA|DAB|DAO", regex=True)
lc = LC[LC.chan.isin(["DAB", "DAO"])]  # the UHE channel of the coadd screen is too loose to use
m = D.gaia.isin(set(CO[CO.status == "ok"].gaia)) & ~hecls; ch["HELINES"] = (m, m & D.gaia.isin(set(lc.gaia)))
mag = D.classification.astype(str).str.contains("H", regex=False) & ~D.classification.astype(str).str.contains("He", regex=False)
ch["MAG"] = (D.classification.notna(), D.classification.notna() & mag)
sw = pd.concat([pd.read_csv(f"{TS}/sweep.csv", dtype={"gaia": str}, usecols=["gaia"]), pd.read_csv(f"{TS}/sweep_rest.csv", dtype={"gaia": str}, usecols=["gaia"])]).gaia
tc = pd.concat([pd.read_csv(f"{R}/tess_2min_rest_2026_09_28/candidates_final_all.csv", dtype={"gaia": str}), pd.read_csv(f"{R}/tess_2min_s70s106_2026_09_27/candidates_retiered.csv", dtype={"gaia": str})])
tc = tc[tc.crowdsap >= 0.7]
m = D.gaia.isin(set(sw)); ch["TESS"] = (m, m & D.gaia.isin(set(tc.gaia)))
for k, (mm, ff) in ch.items(): D[f"m_{k}"] = mm.fillna(False).values; D[f"f_{k}"] = ff.fillna(False).values
names = list(ch); D["n_meas"] = D[[f"m_{k}" for k in names]].sum(1); D["n_flag"] = D[[f"f_{k}" for k in names]].sum(1)
D["flags"] = D.apply(lambda r: "+".join(k for k in names if r[f"f_{k}"]), axis=1)
print(f"{len(D)} objects; blend-vetoed {D.blend.sum()}")
print("channel  measured  flagged  rate")
for k in names: mm = D[f"m_{k}"].sum(); ff = D[f"f_{k}"].sum(); print(f"{k:8s} {mm:8d} {ff:7d}  {ff/max(mm,1):.4f}")
print("n_flag distribution:", D.n_flag.value_counts().sort_index().to_dict())
print("\npair coincidences (observed vs expected under independence among co-measured):")
rows = []
for a, b in itertools.combinations(names, 2):
    both = D[f"m_{a}"] & D[f"m_{b}"]; n = both.sum()
    if n == 0: continue
    ra = D.loc[both, f"f_{a}"].mean(); rb = D.loc[both, f"f_{b}"].mean(); obs = (D.loc[both, f"f_{a}"] & D.loc[both, f"f_{b}"]).sum()
    rows.append((a, b, n, obs, round(n * ra * rb, 2)))
P = pd.DataFrame(rows, columns=["a", "b", "n_comeas", "obs", "exp"]); P["ratio"] = (P.obs / P.exp.replace(0, np.nan)).round(1)
print(P.sort_values("obs", ascending=False).to_string(index=False))
D.to_csv("wd_channels.csv", index=False)
