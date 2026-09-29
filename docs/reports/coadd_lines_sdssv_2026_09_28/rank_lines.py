"""Rank the coadd line-screen output by channel and plot the line windows of the top candidates.
Channels (DA group, white-dwarf locus M_G > 8.5, BP-RP < 1): DAO = He II 4686 and 5412 both in absorption (z < -5 and z < -3) with
EW(4686) > 0.3 A; DAB = He I 5876 and 4471 both in absorption (z < -5, z < -3) with EW(5876) > 0.3 A; UHE = at least two of the
UHE features (4500, 5290, 5673, 6068) at z < -4 in any group. Known types (coadd_controls.csv) are listed separately.
Usage: python rank_lines.py coadd_lines.csv [--plots N]"""
import os, sys, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = os.path.dirname(os.path.abspath(__file__)); f = sys.argv[1]; nplots = int(sys.argv[sys.argv.index("--plots") + 1]) if "--plots" in sys.argv else 0
N = pd.read_csv(f, dtype={"sdss_id": str, "gaia": str}, low_memory=False); N = N[N.status == "ok"].copy()
for c in N.columns:
    if c.endswith(("_zabs", "_zem", "_ew", "_vabs", "_snr")) or c in ("G", "bprp", "MG", "snr"): N[c] = pd.to_numeric(N[c], errors="coerce")
ctrl = pd.read_csv(os.path.join(D, "coadd_controls.csv"), dtype=str); N = N.merge(ctrl[["sdss_id", "control"]], on="sdss_id", how="left"); N["control"] = N.control.fillna("")
locus = (N.MG > 8.5) & (N.bprp < 1); da = (N.grp == "DA") & locus
dao = da & (N.HeII4686_zabs < -5) & (N.HeII5412_zabs < -3) & (N.HeII4686_ew > 0.3)
dab = da & (N.HeI5876_zabs < -5) & (N.HeI4471_zabs < -3) & (N.HeI5876_ew > 0.3)
uhe_n = sum((N[f"{k}_zabs"] < -4).astype(int) for k in ("UHE4500", "UHE5290", "UHE5673", "UHE6068")); uhe = locus & (uhe_n >= 2)
N["chan"] = np.where(dao, "DAO", np.where(dab, "DAB", np.where(uhe, "UHE", "")))
print("screened", len(N), "| DAO channel:", int(dao.sum()), "(known DAO among them:", int((dao & N.control.str.startswith("DAO")).sum()), "of", int((da & N.control.str.startswith("DAO")).sum()), "known DAO on the DA locus)",
      "| DAB channel:", int(dab.sum()), "(known DAB:", int((dab & N.control.str.startswith("DAB")).sum()), "of", int((da & N.control.str.startswith("DAB")).sum()), ")", "| UHE channel:", int(uhe.sum()), "(known UHE:", int((uhe & N.control.str.startswith("UHE")).sum()), "of", int((locus & N.control.str.startswith("UHE")).sum()), ")")
cols = ["sdss_id", "gaia", "cls", "control", "G", "bprp", "MG", "snr", "HeII4686_zabs", "HeII4686_ew", "HeII5412_zabs", "HeII5412_ew", "HeI4471_zabs", "HeI4471_ew", "HeI5876_zabs", "HeI5876_ew", "UHE4500_zabs", "UHE5290_zabs", "UHE5673_zabs", "UHE6068_zabs"]
pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 14)
out = N[N.chan != ""].sort_values(["chan", "HeII4686_zabs"]); out[cols + ["chan"]].to_csv(os.path.join(D, "line_candidates.csv"), index=False)
for ch, key in (("DAO", "HeII4686_zabs"), ("DAB", "HeI5876_zabs"), ("UHE", "UHE5290_zabs")):
    o = out[out.chan == ch].sort_values(key); print(f"--- {ch}: {len(o)} (new, i.e. no known type: {int((o.control == '').sum())})"); print(o[cols].head(25).round(2).to_string(index=False))
if nplots:
    G = np.load(os.path.join(D, "coadd_grid.npy")); os.makedirs(os.path.join(D, "plots_lines"), exist_ok=True)
    LW = {"DAO": [4687.0, 5413.0, 4862.7], "DAB": [4472.7, 5877.2, 6679.9], "UHE": [4500.0, 5290.0, 5673.0, 6068.0]}
    for ch in ("DAO", "DAB", "UHE"):
        o = out[(out.chan == ch) & (out.control == "")].sort_values("HeII4686_zabs" if ch != "DAB" else "HeI5876_zabs").head(nplots)
        for sid in o.sdss_id:
            d = np.load(os.path.join(D, "coadd_store", sid[-2:], f"{sid}.npz")); fl = d["f"].astype(float); iv = d["iv"].astype(float); ok = (iv > 0) & np.isfinite(fl)
            lines = LW[ch]; fig, ax = plt.subplots(1, len(lines) + 1, figsize=(4 * (len(lines) + 1), 3.2))
            m = ok & (G > 3800) & (G < 7000); ax[0].plot(G[m], fl[m], "k", lw=0.5); ax[0].set_title(f"{sid} {ch} G {N.set_index('sdss_id').loc[sid].G:.2f} S/N {N.set_index('sdss_id').loc[sid].snr:.0f}", fontsize=8)
            for a, lam in zip(ax[1:], lines):
                mm = ok & (np.abs(G - lam) < 120); a.plot(G[mm], fl[mm], "k", lw=0.7); a.axvline(lam, color="C3", lw=0.5); a.set_title(f"{lam:.0f}", fontsize=8)
            fig.tight_layout(); fig.savefig(os.path.join(D, "plots_lines", f"{ch}_{sid}.png"), dpi=90); plt.close(fig)
    print("plots written")
