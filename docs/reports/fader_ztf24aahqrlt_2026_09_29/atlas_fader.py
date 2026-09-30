"""ZTF24aahqrlt = Gaia DR3 4104182344862107904: the 2024-2026 dimming in ATLAS forced photometry (2026-09-30).
ATLAS measures difference flux against a template that contains the star, so a dimming appears as negative flux; the star's
total flux in each band is template flux + difference flux. Template flux is estimated from the pre-2024 median apparent magnitude
in ZTF (g 17.21, r 16.5 in the ZTF data release, switchon.csv / journal) converted to ATLAS bands is NOT attempted here; instead the
fractional flux remaining is referred to the out-of-event ATLAS level: F_star(o) is taken as the flux of a G 16.32 star with
BP-RP 1.32 in o (AB) - an approximation, stated in the output. Output: nightly medians per filter (atlas_nightly.csv), the o-c
difference-flux ratio during the event (colour of the missing light), and atlas_fader.png."""
import os, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.time import Time
H = os.path.dirname(os.path.abspath(__file__)); g = "4104182344862107904"
L = [l for l in open(os.path.join(H, "atlas", g + ".txt")).read().splitlines() if l.strip()]; h = L[0].lstrip("#").split(); R = pd.DataFrame([dict(zip(h, l.split())) for l in L[1:]])
for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
R = R[(R.err == 0) & (R["chi/N"] < 10) & (R.duJy > 0)]; R = R[R.duJy < 3 * R.duJy.median()]
R["night"] = np.floor(R.MJD); N = R.groupby(["F", "night"]).agg(uJy=("uJy", "median"), n=("uJy", "size"), e=("duJy", "median")).reset_index()
N["date"] = Time(N.night.values, format="mjd").iso; N["date"] = N.date.str[:10]; N.to_csv(os.path.join(H, "atlas_nightly.csv"), index=False)
for f in "oc":
    x = N[N.F == f]; yr = np.floor((x.night - 57023) / 365.25) + 2015
    print(f, "yearly median difference flux (uJy):", x.groupby(yr).uJy.median().round(0).to_dict(), "| min nightly %.0f on %s" % (x.uJy.min(), x.loc[x.uJy.idxmin(), "date"]))
pre = N[N.night < 60380]
for f in "oc": print(f, "pre-2024-03 nightly scatter (robust) %.0f uJy, median %.0f" % (1.4826 * np.median(np.abs(pre[pre.F == f].uJy - pre[pre.F == f].uJy.median())), pre[pre.F == f].uJy.median()))
# colour of the missing light: o and c nightly medians within 2 d of each other during the event
ev = N[N.night >= 60380]; o = ev[ev.F == "o"].set_index("night").uJy; c = ev[ev.F == "c"].set_index("night").uJy; pairs = []
for t, v in c.items():
    k = o.index[np.abs(o.index - t) <= 2]
    if len(k): pairs.append((t, v, o[k].median()))
P = pd.DataFrame(pairs, columns=["night", "c", "o"]); P = P[(P.o < -200)]
if len(P): print("event nights with c and o (o < -200 uJy):", len(P), "; median c/o difference-flux ratio %.2f (IQR %.2f-%.2f)" % (np.median(P.c / P.o), *np.percentile(P.c / P.o, [25, 75])))
fig, ax = plt.subplots(figsize=(12, 4))
for f, col in (("o", "tab:orange"), ("c", "tab:cyan")):
    x = N[N.F == f]; ax.plot(x.night, x.uJy, ".", color=col, ms=4, label=f)
ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("MJD"); ax.set_ylabel("nightly median difference flux (uJy)"); ax.legend(); ax.set_title("ZTF24aahqrlt / Gaia DR3 4104182344862107904: ATLAS")
plt.tight_layout(); plt.savefig(os.path.join(H, "atlas_fader.png"), dpi=80)
