import sys, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
f = sys.argv[1]; d = pd.read_csv(f, sep=r"\s+"); d.columns = [c.lstrip("#") for c in d.columns]
d = d[(d.err == 0) & (d.duJy > 0) & (d["chi/N"] < 20)].copy()
# quiescent reference: Gaia G 19.66 -> ~49 uJy total; ATLAS diff flux relative to template; quiescent level = median
q = d.groupby("F").uJy.median(); print("median diff flux (uJy):", q.round(1).to_dict(), "| n:", d.F.value_counts().to_dict())
d["tot"] = d.uJy - d.F.map(q) + 3631e6 * 10 ** (-0.4 * 19.66)  # approximate total flux with quiescence at Gaia G
d["mag"] = -2.5 * np.log10(d.tot.clip(lower=1)) + 23.9
nois = 1.4826 * np.median(np.abs(d.uJy - d.F.map(q))); thr = 3631e6 * 10 ** (-0.4 * 19.66) * 1.0  # brightening > +1 quiescent flux (0.75 mag)
d["out"] = (d.uJy - d.F.map(q)) > max(5 * nois, thr)
o = d[d.out].sort_values("MJD"); print(f"robust scatter {nois:.1f} uJy; outburst points: {len(o)}")
# group outbursts separated by > 10 d
if len(o):
    grp = (o.MJD.diff() > 10).cumsum(); 
    for g, s in o.groupby(grp):
        print(f"  outburst: MJD {s.MJD.min():.1f}-{s.MJD.max():.1f} ({s.MJD.max()-s.MJD.min():.1f} d, {len(s)} pts), peak mag {s.mag.min():.2f}")
fig, ax = plt.subplots(2, 1, figsize=(14, 7))
for flt, col in (("c", "C0"), ("o", "C1")):
    s = d[d.F == flt]; ax[0].plot(s.MJD, s.mag, ".", ms=2, color=col, label=f"ATLAS {flt}")
ax[0].invert_yaxis(); ax[0].set_ylim(21, 16); ax[0].set_ylabel("approx. mag"); ax[0].legend(); ax[0].set_title("CRTS J205436.5-541810: ATLAS forced photometry (quiescence set to Gaia G 19.66)")
if len(o):
    s0 = o[o.MJD == o.MJD.min()]; m0 = o.MJD.min(); k = (d.MJD > m0 - 20) & (d.MJD < m0 + 80)
    for flt, col in (("c", "C0"), ("o", "C1")):
        s = d[k & (d.F == flt)]; ax[1].plot(s.MJD - m0, s.mag, "o", ms=3, color=col)
    ax[1].invert_yaxis(); ax[1].set_xlabel("days since first outburst point"); ax[1].set_ylabel("approx. mag")
plt.tight_layout(); plt.savefig(sys.argv[2], dpi=80)
