"""Rank the per-exposure RV sweep using only exposures in which all three Balmer lines agree (n_lines = 3). Per object: weighted
mean, chi2, reduced chi2, largest pairwise difference and significance, time between the extreme exposures. Candidates:
>= 2 such exposures, sig_max >= 6, dv_max >= 60 km/s, reduced chi2 >= 6 and M_G > 6 (white-dwarf luminosity)."""
import sys, numpy as np, pandas as pd
E = pd.read_csv(sys.argv[1], dtype={"sdss_id": str}); S = pd.read_csv(sys.argv[2], dtype={"sdss_id": str, "gaia_dr3_source_id": str})
S["MG"] = S.g_mag.astype(float) + 5 * np.log10(S.plx.astype(float).where(S.plx.astype(float) > 0) / 100)
g19 = set(open(sys.argv[3]).read().split())
E = E[(E.n_lines == 3) & np.isfinite(E.v)]; rows = []
for sid, g in E.groupby("sdss_id"):
    if len(g) < 2: continue
    v, e, t = g.v.values, g.e.values, g.mjd_mid.values; w = 1 / e ** 2; mu = np.sum(w * v) / w.sum(); chi2 = float(np.sum(((v - mu) / e) ** 2))
    dv = np.abs(v[:, None] - v[None, :]); sg = dv / np.sqrt(e[:, None] ** 2 + e[None, :] ** 2); i, j = np.unravel_index(np.argmax(sg), sg.shape)
    rows.append(dict(sdss_id=sid, n3=len(g), chi2r=round(chi2 / (len(g) - 1), 2), dv_max=round(float(dv.max()), 1), sig_max=round(float(sg.max()), 1), dt_extreme_d=round(abs(t[i] - t[j]), 4),
                     v_list=" ".join(f"{a:.0f}" for a in v), t_list=" ".join(f"{a:.4f}" for a in t)))
R = pd.DataFrame(rows).merge(S[["sdss_id", "gaia_dr3_source_id", "g_mag", "teff", "logg", "snr", "MG", "classification"]], on="sdss_id")
R["dr19_dwd"] = R.gaia_dr3_source_id.isin(g19)
C = R[(R.sig_max >= 6) & (R.dv_max >= 60) & (R.chi2r >= 6) & (R.MG > 6)].sort_values("sig_max", ascending=False)
pd.set_option("display.width", 280); print(len(R), "objects with >= 2 three-line exposures;", len(C), "candidates;", int(R.dr19_dwd.sum()), "DR19 candidates measured,", int(C.dr19_dwd.sum()), "recovered")
print(C[["sdss_id", "gaia_dr3_source_id", "g_mag", "MG", "teff", "logg", "n3", "chi2r", "dv_max", "sig_max", "dt_extreme_d", "dr19_dwd", "v_list"]].to_string(index=False))
C.to_csv(sys.argv[4], index=False); R.to_csv(sys.argv[5], index=False)
