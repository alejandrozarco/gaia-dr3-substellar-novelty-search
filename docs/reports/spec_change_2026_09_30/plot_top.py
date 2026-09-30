"""Diagnostic plots for the top spectral-change pairs that SIMBAD does not class as CV (2026-09-30): pair a (black) and the
polynomial-scaled pair b (red), full range and a zoom on the flagged window. Pages of 12 -> results/pages/page_NN.png (inspection figures, not kept in the repository)."""
import os, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from numpy.polynomial import legendre as L
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, "results"); os.makedirs(os.path.join(R, "pages"), exist_ok=True)
T = pd.read_csv(os.path.join(R, "top.csv"), dtype={"gaia": str}).reset_index(drop=True); S = pd.read_csv(os.path.join(R, "simbad_top.csv"), dtype={"gaia": str}).set_index("gaia")
Z = np.load(os.path.join(R, "top_spectra.npz")); cen = Z["cen"]; x = (cen - cen.mean()) / (cen.max() - cen.mean())
sel = [n for n, r in T.iterrows() if r.score > 8 and S.loc[r.gaia, "otype"] != "CV*"]
seen = set(); sel = [n for n in sel if not (T.gaia[n] in seen or seen.add(T.gaia[n]))]   # best pair per star
print(len(sel), "stars")
def scaled(n):
    Fa, Wa = Z[f"a{n}"]; Fb, Wb = Z[f"b{n}"]; ok = (Wa > 0) & (Wb > 0) & (Fb > 0.02 * np.median(Fb[Wb > 0])); rat = Fa / np.where(Fb != 0, Fb, 1)
    wr = np.where(ok, 1 / (1 / np.where(Wa > 0, Wa, 1) + rat**2 / np.where(Wb > 0, Wb, 1)) * Fb**2, 0); use = ok.copy()
    for it in range(3):
        c = L.legfit(x[use], rat[use], 7, w=np.sqrt(wr[use])); r = L.legval(x, c); res = (rat - r) * np.sqrt(wr); use = ok & (np.abs(res) < 4 * max(1, 1.4826 * np.median(np.abs(res[ok]))))
    return np.where(Wa > 0, Fa, np.nan), np.where(Wb > 0, r * Fb, np.nan)
for p in range(0, len(sel), 12):
    fig, ax = plt.subplots(6, 4, figsize=(20, 18))
    for k, n in enumerate(sel[p:p + 12]):
        r = T.loc[n]; a, b = scaled(n); s = S.loc[r.gaia]; A = ax[k // 2, (k % 2) * 2]; B = ax[k // 2, (k % 2) * 2 + 1]
        A.plot(cen, a, "k", lw=0.5); A.plot(cen, b, "r", lw=0.5, alpha=0.7); A.axvspan(r.win_lo, r.win_hi, color="y", alpha=0.3)
        A.set_title(f"#{n} {r.gaia} {s.main_id} [{s.otype}] {r.cls if isinstance(r.cls, str) else ''} score {r.score:.0f}", fontsize=7)
        A.set_ylim(np.nanpercentile(a, 0.5) * 0.8, np.nanpercentile(a, 99.5) * 1.2)
        lo, hi = r.win_lo - 150, r.win_hi + 150; m = (cen > lo) & (cen < hi)
        B.plot(cen[m], a[m], "k", lw=0.8, label=r.a[:14]); B.plot(cen[m], b[m], "r", lw=0.8, label=r.b[:14]); B.axvspan(r.win_lo, r.win_hi, color="y", alpha=0.3); B.legend(fontsize=6)
        B.set_title(f"S/N {r.sn_a:.0f}/{r.sn_b:.0f}", fontsize=7)
    plt.tight_layout(); plt.savefig(os.path.join(R, "pages", f"page_{p // 12:02d}.png"), dpi=55); plt.close()
