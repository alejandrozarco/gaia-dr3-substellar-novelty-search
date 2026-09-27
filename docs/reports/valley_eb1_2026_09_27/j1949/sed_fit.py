"""WDJ1949+6730 SED: GALEX AIS FUV/NUV, Pan-STARRS DR1 g r i z (y excluded; kept for the residual), Gaia DR3 G/BP (RP kept for the residual).
Montreal pure-H synthetic absolute magnitudes (Table_DA) at log g 7.0 (colours), Teff grid; E(B-V) 0-0.19 (SFD/S&F total column 0.19-0.22);
extinction coefficients A/E(B-V): FUV 4.89, NUV 7.24 (Yuan et al. 2013), PS1 g 3.172 r 2.271 i 1.682 z 1.322 y 1.087 (Schlafly & Finkbeiner 2011),
Gaia G 2.74 BP 3.37 RP 2.04. Free magnitude offset -> radius relative to the log g 7.0 model at d = 739 pc (1/parallax, +-7%)."""
import numpy as np
L = open("Table_DA.txt").readlines(); hdr = L[1].replace("log g", "logg").split(); D = np.array([[float(x) for x in l.split()] for l in L[2:] if len(l.split()) == len(hdr)])
ps = [i for i, h in enumerate(hdr) if h == "g"][1]; col = {"FUV": hdr.index("FUV"), "NUV": hdr.index("NUV"), "g": ps, "r": ps + 1, "i": ps + 2, "z": ps + 3, "y": ps + 4, "G": hdr.index("G3"), "BP": hdr.index("G3_BP"), "RP": hdr.index("G3_RP")}
obs = {"FUV": (17.853, 0.068), "NUV": (18.172, 0.050), "g": (18.105, 0.015), "r": (18.138, 0.035), "i": (18.355, 0.051), "z": (18.573, 0.049), "y": (18.372, 0.025), "G": (18.027, 0.02), "BP": (18.029, 0.03), "RP": (18.007, 0.045)}
R = {"FUV": 4.89, "NUV": 7.24, "g": 3.172, "r": 2.271, "i": 1.682, "z": 1.322, "y": 1.087, "G": 2.74, "BP": 3.37, "RP": 2.04}
fit_b = ["FUV", "NUV", "g", "r", "i", "z", "G", "BP"]; DM = 5 * np.log10(739 / 10)
q = D[np.isclose(D[:, 1], 7.0)]; q = q[np.argsort(q[:, 0])]
best = []
for te in np.arange(8000, 60001, 250):
    mod = {b: np.interp(te, q[:, 0], q[:, col[b]]) for b in col}
    for ebv in np.arange(0, 0.195, 0.01):
        res = np.array([obs[b][0] - R[b] * ebv - DM - mod[b] for b in fit_b]); w = np.array([1 / max(obs[b][1], 0.03) ** 2 for b in fit_b])
        off = np.sum(res * w) / np.sum(w); chi = np.sum((res - off) ** 2 * w); best.append((chi, te, ebv, off))
best.sort(); chi0 = best[0][0]
print("best: chi2 %.1f (8 bands, 3 params), Teff %d K, E(B-V) %.2f, offset %.2f mag" % best[0])
ok = [b for b in best if b[0] <= chi0 + 4]; te = [b[1] for b in ok]; eb = [b[2] for b in ok]; of = [b[3] for b in ok]
print("delta chi2 <= 4 ranges: Teff %d-%d K, E(B-V) %.2f-%.2f, offset %.2f to %.2f" % (min(te), max(te), min(eb), max(eb), min(of), max(of)))
for ebv in (0.0, 0.10, 0.19):
    s = [b for b in best if abs(b[2] - ebv) < 1e-6]; print("  E(B-V) fixed %.2f: best Teff %d, chi2 %.1f, offset %.2f" % (ebv, s[0][1], s[0][0], s[0][3]))
Msun, Rsun, Gc = 1.989e33, 6.957e10, 6.674e-8
def rad(te, off):
    m = np.interp(te, q[:, 0], q[:, 2]); r7 = np.sqrt(Gc * m * Msun / 10 ** 7.0) / Rsun; return r7 * 10 ** (-0.2 * off), r7
chi, te0, eb0, off0 = best[0]; r, r7 = rad(te0, off0); print(f"radius: {r:.4f} Rsun (log g 7.0 model radius {r7:.4f}); range over delta chi2 <= 4: {min(rad(t, o)[0] for _, t, _, o in ok):.4f}-{max(rad(t, o)[0] for _, t, _, o in ok):.4f} (plus 7% distance)")
mod = {b: np.interp(te0, q[:, 0], q[:, col[b]]) for b in col}
print("residuals (obs - model - DM - A), mag:", {b: round(obs[b][0] - R[b] * eb0 - DM - mod[b] - off0, 3) for b in col})
