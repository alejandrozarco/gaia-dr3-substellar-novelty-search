import io, csv, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
W = json.load(open("j1226_wise.json")); P = W["P"]; f0 = 1/P
t = np.array(W["t"]); w1 = np.array(W["w1"]); e1 = np.array(W["e1"]); w2 = np.array(W["w2"]); e2 = np.array(W["e2"])
T0 = 2459000.0
def fitchi(tt, mm, ee, fr, nh):
    cols = [np.ones_like(tt)]
    for k in range(1, nh+1): cols += [np.sin(2*np.pi*k*fr*tt), np.cos(2*np.pi*k*fr*tt)]
    X = np.column_stack(cols); w = 1/ee**2; p = np.linalg.solve(X.T @ (X*w[:, None]), X.T @ (mm*w)); r = mm - X @ p
    return float(np.sum(r**2*w)), p
# P vs 2P test: 2-harmonic at P (5 params) vs 4-harmonic at 2P (9 params; contains the P model as a subset)
c1, _ = fitchi(t - T0, w1, e1, f0, 2); c2, p2 = fitchi(t - T0, w1, e1, f0/2, 4)
n = len(t); bic1 = c1 + 5*np.log(n); bic2 = c2 + 9*np.log(n)
print(f"W1: chi2 P-model {c1:.1f} (5 par) vs 2P-model {c2:.1f} (9 par); delta chi2 {c1-c2:.1f}; BIC {bic1:.1f} vs {bic2:.1f}; n={n}")
ph2 = ((t - T0) * f0/2) % 1
h1 = np.median(w1[(ph2 < 0.5)]); h2 = np.median(w1[(ph2 >= 0.5)])
print(f"  2P fold: median of first half {h1:.3f}, second half {h2:.3f}")
# epoch halves stability
mid = np.median(t)
for lab, s in (("2014-2019", t < mid), ("2019-2024", t >= mid)):
    X = np.column_stack([np.ones(s.sum()), np.sin(2*np.pi*f0*(t[s]-T0)), np.cos(2*np.pi*f0*(t[s]-T0))]); w = 1/e1[s]**2
    p = np.linalg.solve(X.T @ (X*w[:, None]), X.T @ (w1[s]*w)); print(f"  {lab}: W1 sinusoid amplitude {2*np.hypot(p[1], p[2]):.3f}, phase of max {(np.arctan2(-p[1], -p[2])/(2*np.pi)) % 1:.2f}")
# figure: W1, W2 folds + ZTF r fold
url = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20186.65760%20-23.07065%200.000833&BANDNAME=g,r&FORMAT=CSV"
q = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
Z = [x for x in csv.DictReader(io.StringIO(q)) if x["catflags"] == "0" and float(x["mag"]) < float(x["limitmag"]) - 0.2]
fig, ax = plt.subplots(3, 1, figsize=(6.4, 8.2), sharex=True)
ph = ((t - T0) * f0) % 1
for a, m, e, lab, col in ((ax[0], w1, e1, "NEOWISE W1", "C3"), (ax[1], w2, e2, "NEOWISE W2", "C1")):
    ok = np.isfinite(m)
    a.errorbar(np.r_[ph[ok], ph[ok]+1], np.r_[m[ok], m[ok]], np.r_[e[ok], e[ok]], fmt=".", ms=3, color=col, alpha=0.35, elinewidth=0.5)
    bb = np.linspace(0, 1, 11); md = [np.nanmedian(m[ok][(ph[ok] >= bb[j]) & (ph[ok] < bb[j+1])]) for j in range(10)]
    a.plot(np.r_[bb[:-1]+0.05, bb[:-1]+1.05], np.r_[md, md], "ks-", ms=5); a.invert_yaxis(); a.set_ylabel(f"{lab} (mag)")
zr = [x for x in Z if x["filtercode"] == "zr"]; zt = np.array([float(x["hjd"]) for x in zr]); zm = np.array([float(x["mag"]) for x in zr]); ze = np.array([float(x["magerr"]) for x in zr])
zph = ((zt - T0) * f0) % 1
ax[2].errorbar(np.r_[zph, zph+1], np.r_[zm, zm], np.r_[ze, ze], fmt=".", ms=3, color="C0", alpha=0.4, elinewidth=0.5)
bb = np.linspace(0, 1, 6); md = [np.median(zm[(zph >= bb[j]) & (zph < bb[j+1])]) for j in range(5)]
ax[2].plot(np.r_[bb[:-1]+0.1, bb[:-1]+1.1], np.r_[md, md], "ks-", ms=5); ax[2].invert_yaxis(); ax[2].set_ylabel("ZTF r (mag)"); ax[2].set_xlabel(f"phase (P = {P:.8f} d = {24*P:.4f} h, T0 = BJD 2459000.0)")
ax[0].set_title("Gaia DR3 3513017956589117056 (WISE J122637.85-230414.2)", fontsize=10)
plt.tight_layout(); plt.savefig("j1226_fold.png", dpi=130); print("figure written")
