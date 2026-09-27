"""Rank the UHE screen: empirical noise per feature from the control windows (robust scatter of c5480 and c5100 in S/N bins),
significance z = EW / max(formal error, empirical scatter at that S/N). Candidates: z(f5280) >= 5 and f5280 >= 0.6 A, or z(f4655) >= 5
and z(f6068) >= 4. Known UHE white dwarfs (uhe_known_gaia.csv) and the target list are marked."""
import sys, numpy as np, pandas as pd
R = pd.read_csv(sys.argv[1], dtype={"sdss_id": str}); S = pd.read_csv(sys.argv[2], dtype={"sdss_id": str, "gaia_dr3_source_id": str})
R = R[R.status == "ok"].merge(S[["sdss_id", "gaia_dr3_source_id", "classification", "teff", "logg", "snr", "g_mag", "bp_mag", "rp_mag", "plx"]], on="sdss_id", how="left")
R["snrbin"] = pd.cut(R.snr.astype(float), [0, 12, 16, 20, 25, 30, 40, 60, 1000])
sc = R.groupby("snrbin", observed=True).apply(lambda g: 1.4826 * np.nanmedian(np.abs(np.r_[g.c5480, g.c5100] - np.nanmedian(np.r_[g.c5480, g.c5100]))))
R["emp"] = R.snrbin.map(sc).astype(float)
for k in ["f5280", "f5243", "f4655", "f6068"]:
    R["z_" + k] = R[k] / np.maximum(R[k + "_e"], R.emp)
print("empirical scatter by S/N bin:", {str(k): round(v, 2) for k, v in sc.items()})
cand = R[((R.z_f5280 >= 5) & (R.f5280 >= 0.6)) | ((R.z_f4655 >= 5) & (R.z_f6068 >= 4))].sort_values("z_f5280", ascending=False)
pd.set_option("display.width", 250)
print(len(R), "measured;", len(cand), "candidates")
print(cand[["sdss_id", "gaia_dr3_source_id", "classification", "snr", "g_mag", "f5280", "z_f5280", "f5243", "z_f5243", "f4655", "z_f4655", "f6068", "z_f6068", "c5480", "c5100", "f5280_visits"]].to_string(index=False))
R.to_csv(sys.argv[3], index=False)
