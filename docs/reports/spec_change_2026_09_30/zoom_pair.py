"""Native-resolution comparison of all spectra of one Gaia DR3 source from the SDSS DR17 and DESI DR1 stores (2026-09-30).
Each spectrum is divided by its median in 4000-7000 A; panels: full range and the H-delta, H-beta, H-alpha, Ca II K and He I 5876
regions. Usage: python zoom_pair.py <gaia> [...] -> results/zoom_<gaia>.png (inspection figures, not kept in the repository)"""
import os, sys, glob, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); ST = os.path.expanduser("~/claude_projects/spectra_store")
gs = np.load(os.path.join(ST, "sdss_dr17_wd", "grid.npy")); gd = np.load(os.path.join(ST, "desi_dr1_wd", "grid.npy"))
Ct = pd.read_csv(os.path.join(ST, "desi_dr1_wd", "class_table.csv"), dtype={"edr3id": str}); M = pd.read_csv(os.path.join(ST, "sdss_dr17_wd", "matches.csv"), dtype={"gaia": str})
def get(gg):
    out = []; sids = set(M[M.gaia == gg].sparcl_id); tids = set(Ct[Ct.edr3id == gg].DESIID.astype(np.int64))
    for fn in sorted(glob.glob(os.path.join(ST, "sdss_dr17_wd", "chunks", "*.npz"))):
        d = np.load(fn, allow_pickle=True)
        for s_, f, iv in zip(d["sparcl_id"], d["f"], d["iv"]):
            if s_ in sids and not any(o[0] == "S:" + s_[:8] for o in out): out.append(("S:" + s_[:8], gs, f, iv))
    for fn in sorted(glob.glob(os.path.join(ST, "desi_dr1_wd", "chunks", "*.npz"))):
        d = np.load(fn, allow_pickle=True)
        for t, f, iv in zip(d["targetid"], d["f"], d["iv"]):
            if int(t) in tids: out.append((f"D:{int(t)}", gd, f, iv))
    return out
REG = [(3800, 9000), (3900, 4000), (4050, 4150), (4780, 4940), (5820, 5930), (6450, 6680), (8450, 8700)]
for gg in sys.argv[1:]:
    S = get(gg); fig, ax = plt.subplots(2, 4, figsize=(20, 8)); ax = ax.ravel()
    for n, (lab, g, f, iv) in enumerate(S):
        m = np.nanmedian(f[(g > 4000) & (g < 7000)]); y = np.where(iv > 0, f / m, np.nan)
        for k, (a, b) in enumerate(REG):
            s = (g > a) & (g < b); yy = y[s] if k == 0 else np.convolve(np.nan_to_num(y[s], nan=np.nanmedian(y[s])), np.ones(3) / 3, "same")
            ax[k].plot(g[s], yy + (0 if k == 0 else 0), lw=0.6, label=lab)
    for k, (a, b) in enumerate(REG): ax[k].set_title(f"{a}-{b}", fontsize=8)
    ax[0].legend(fontsize=7); ax[0].set_title(gg); ax[7].axis("off"); plt.tight_layout(); plt.savefig(os.path.join(H, "results", f"zoom_{gg}.png"), dpi=60); plt.close()
    print(gg, [s[0] for s in S])
