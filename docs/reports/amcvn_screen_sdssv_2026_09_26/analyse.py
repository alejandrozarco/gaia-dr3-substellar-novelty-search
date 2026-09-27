"""Rank the helium-emission screen. Emission = negative EW. Candidates: He I 5877 EW <= -1.5 A and significant (>= 5 sigma using
max(formal error, empirical scatter of |HeI6680 - ...|) ), with H-alpha emission weaker than He I 5877 emission (EW(Ha) > 0.5 * EW(HeI5877),
i.e. less negative) -> AM CVn-like; also listed: any object with He I 5877 and He I 6680 both in emission at >= 4 sigma."""
import sys, numpy as np, pandas as pd
R = pd.read_csv(sys.argv[1], dtype={"sdss_id": str}); S = pd.read_csv(sys.argv[2], dtype={"sdss_id": str, "gaia_dr3_source_id": str})
R = R[R.status == "ok"].merge(S[["sdss_id", "gaia_dr3_source_id", "classification", "snr", "g_mag", "bp_mag", "rp_mag", "plx", "ra", "dec"]], on="sdss_id", how="left")
for k in ["HeI4473", "HeII4686", "HeI5877", "HeI6680", "Ha", "Hb"]:
    R["z_" + k] = R[k] / R[k + "_e"].clip(lower=0.1)
emp = 1.4826 * np.nanmedian(np.abs(R.HeI5877 - np.nanmedian(R.HeI5877))); print("robust scatter He I 5877 EW:", round(emp, 2))
c1 = R[(R.HeI5877 <= -1.5) & (R.z_HeI5877 <= -5) & ((R.Ha > 0.5 * R.HeI5877) | R.Ha.isna())]
c2 = R[(R.z_HeI5877 <= -4) & (R.z_HeI6680 <= -4)]
C = pd.concat([c1.assign(kind="He emission, weak H"), c2[~c2.sdss_id.isin(c1.sdss_id)].assign(kind="He I 5877+6680 emission")])
pd.set_option("display.width", 260)
print(len(R), "measured;", len(C), "candidates")
print(C[["kind", "sdss_id", "gaia_dr3_source_id", "classification", "snr", "g_mag", "HeI5877", "HeI6680", "HeI4473", "HeII4686", "Ha", "Hb"]].to_string(index=False))
C.to_csv(sys.argv[3], index=False)
