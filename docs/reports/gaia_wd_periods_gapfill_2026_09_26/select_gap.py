"""Gap-fill selection for the 2026-09-24 Gaia-period lane (gaia_wd_periods_2026_09_24).
That lane tested only (tier 1) FAP < 1e-5 stars NOT in Steen+2024, Jestin+2026 or VSX-with-period, and (tier 2) FAP 1e-5 to 1e-3
with M_G > 9.5. This selects what it left out: FAP < 1e-3, N >= 20, |IPD correlation| < 0.5, frequency > 0.03 c/d from 4k c/d and
from the (4k - 1/63) sidebands, not already tested (unconfirmed.csv / confirm.csv), Dec > -28 (ZTF), not in Steen, and then
(interactive step) Jestin+2026 Variable != True and no VSX period (VSX API, 5 arcsec). Output todo.csv (13 stars)."""
import pandas as pd, numpy as np, requests, time
D = "../gaia_wd_periods_2026_09_24/data/"
w = pd.read_csv(D + "wd_vspur.csv", dtype={"source_id": str})
c = pd.read_csv(D + "cand_annot.csv", dtype={"source_id": str}); u = pd.read_csv(D + "unconfirmed.csv", dtype={"source_id": str})
cf = pd.read_csv(D + "confirm.csv", dtype={"source_id": str})
j = pd.read_csv("jestin_tablea1.csv", dtype={"GaiaDR3": str}).set_index("GaiaDR3")  # VizieR J/A+A/712/A243/tablea1
w["M_G"] = w.phot_g_mean_mag + 5 * np.log10(w.parallax / 100)
spin = np.min(np.abs(w.gls_freq_g_fov.values[:, None] - np.array([4, 8, 12, 16, 20, 24, 11.984, 15.984, 7.984])[None, :]), axis=1)
s = w[(w.gls_freq_fap_g_fov < 1e-3) & (w.num_obs_g_fov >= 20) & (w.spearman_corr_ipd_g_fov.abs() < 0.5) & (spin > 0.03)]
s = s[~(s.source_id.isin(u.source_id) | s.source_id.isin(cf.source_id)) & (s.dec > -28)]
cm = c.set_index("source_id"); s = s.assign(steen=s.source_id.map(cm.steen), vsx_period=s.source_id.map(cm.vsx_period),
                                            vsx_type=s.source_id.map(cm.vsx_type), main_id=s.source_id.map(cm.main_id),
                                            in_jestin=s.source_id.isin(j.index), jestin_var=s.source_id.map(j.Variable.astype(str)))
s = s[s.steen.astype(str) != "True"]
for i, r in s[~s.source_id.isin(cm.index)].iterrows():
    try:
        v = requests.get("https://www.aavso.org/vsx/index.php", params=dict(view="api.list", ra=r.ra, dec=r.dec, radius=0.0014, format="json"), timeout=60).json()
        o = v.get("VSXObjects", {}).get("VSXObject", []) if isinstance(v.get("VSXObjects"), dict) else []
        s.loc[i, "vsx_type"] = o[0].get("VariabilityType") if o else "none"; s.loc[i, "vsx_period"] = o[0].get("Period") if o else np.nan
    except Exception:
        s.loc[i, "vsx_type"] = "HOLE"
    time.sleep(0.5)
todo = s[(s.jestin_var.astype(str) != "True") & (s.vsx_period.isna() | s.vsx_period.astype(str).isin(["", "nan", "None"]))]
print(len(s), "gap;", len(todo), "to test"); todo.to_csv("todo.csv", index=False)
