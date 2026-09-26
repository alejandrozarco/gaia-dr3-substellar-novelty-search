"""Cross-survey Ca II switch search: SDSS-V pass-2 (lane_gasdisc/p2_final.csv, positions from sw_all.csv) x DESI DR1 pass-2
(lane_desi_gas/desi_pass2.csv), nearest match < 2 arcsec. Switch candidates: both snr_cat > 10, max(z_cat) > 8, min(z_cat) < 3.
Run from /tmp/hotdq. Output lane_gastime/sdssv_desi_pairs.csv (all pairs)."""
import pandas as pd, numpy as np
from scipy.spatial import cKDTree
s = pd.read_csv("lane_gasdisc/p2_final.csv", dtype={"sdss_id": str, "gaia": str})
sw = pd.read_csv("lane_gasdisc/sw_all.csv", dtype=str)[["sdss_id", "ra", "dec"]].drop_duplicates("sdss_id")
s = s.merge(sw, on="sdss_id", how="left"); s["ra"] = s.ra.astype(float); s["dec"] = s.dec.astype(float)
d = pd.read_csv("lane_desi_gas/desi_pass2.csv", dtype={"targetid": str})
def xyz(ra, dec):
    r, dd = np.radians(ra), np.radians(dec); return np.c_[np.cos(dd) * np.cos(r), np.cos(dd) * np.sin(r), np.sin(dd)]
ok = np.isfinite(s.ra); t = cKDTree(xyz(d.ra.values, d.dec.values)); dist, idx = t.query(xyz(s.ra[ok].values, s.dec[ok].values))
m = s[ok].copy(); m["sep"] = np.degrees(dist) * 3600; m["d_idx"] = idx; m = m[m.sep < 2.0]
dd = d.iloc[m.d_idx.values].reset_index(drop=True); m = m.reset_index(drop=True)
x = pd.concat([m[["sdss_id", "gaia", "cls", "grp", "G", "MG", "snr_cat", "z_cat", "z_lines", "z_fake", "sep"]].add_prefix("v_"),
               dd[["targetid", "name", "cls", "grp", "snr_cat", "z_cat", "z_lines", "z_fake"]].add_prefix("d_")], axis=1)
x.to_csv("lane_gastime/sdssv_desi_pairs.csv", index=False)
good = (x.v_snr_cat > 10) & (x.d_snr_cat > 10); hi = np.maximum(x.v_z_cat, x.d_z_cat); lo = np.minimum(x.v_z_cat, x.d_z_cat)
print(len(x), "pairs;", good.sum(), "with both S/N > 10;", (good & (hi > 8) & (lo < 3)).sum(), "switch candidates")
