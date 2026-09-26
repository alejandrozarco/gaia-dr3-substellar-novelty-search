# Stationary points (d lambda / d B = 0) of Balmer components in 1-2000 MG, from the Schimeczek & Wunner database.
import numpy as np, hfield as H, json
tr = H.load_balmer()
fmax = {}
def series(l0):
    for n, lab in ((3, "Ha"), (4, "Hb"), (5, "Hg"), (6, "Hd"), (7, "He"), (8, "H8")):
        if abs(l0 - H.LAM_RY / (0.25 - 1 / n**2)) < 40: return lab
    return "H9+"
out = []
for t in tr:
    B, lam, f = t["B_MG"], t["lam"], t["f"]; ok = np.isfinite(lam) & (B > 1) & (B < 2000)
    B, lam, f = B[ok], lam[ok], f[ok]
    if len(B) < 5: continue
    d = np.diff(lam) / np.diff(B)
    for i in np.where(np.sign(d[:-1]) != np.sign(d[1:]))[0]:
        out.append(dict(tr=t["name"], series=series(t["lam0"]), lam=float(lam[i + 1]), B=float(B[i + 1]), f=float(f[i + 1]), lam0=float(t["lam0"])))
fm = max(o["f"] for o in out)
out = [o for o in out if o["f"] > 0.01 * fm and 3500 < o["lam"] < 10000]
out.sort(key=lambda o: o["lam"])
for o in out: print(f"{o['series']:4s} {o['tr']:32s} lam_stat {o['lam']:8.1f} A  at B {o['B']:7.1f} MG  f_rel {o['f']/fm:.3f}")
json.dump(out, open("stationary_points.json", "w"), indent=1)
