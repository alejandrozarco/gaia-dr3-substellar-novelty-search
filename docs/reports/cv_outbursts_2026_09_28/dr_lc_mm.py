"""Second-method check: ZTF data-release PSF light curves (IRSA, 1.5 arcsec) for the tier-A candidates plus one known dwarf nova control.
Quiescent level = median mag; outburst points = catflags 0 and mag < median - 1.5; episodes = outburst points grouped by gaps > 15 d.
An empty IRSA reply is recorded as HOLE (it can be a silent failure), never as 'no outbursts'."""
import io, time, requests, pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
A = pd.read_csv("mm_cand.csv")
P = pd.read_csv("pool_all.csv", low_memory=False); C = pd.read_csv("controls.csv"); k = P[P.oid.isin(C[C.ctrl == "DN"].oid)].iloc[0]
T = pd.concat([A[["oid", "meanra", "meandec", "G"]], pd.DataFrame([dict(oid="CONTROL_" + k.oid, meanra=k.meanra, meandec=k.meandec, G=k.G)])])
rows = []; fig, ax = plt.subplots(int(np.ceil(len(T) / 3)), 3, figsize=(17, 3.2 * np.ceil(len(T) / 3))); ax = ax.ravel()
for a, r in zip(ax, T.itertuples()):
    d = None
    for i in range(3):
        try:
            q = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {r.meanra} {r.meandec} 0.00042", BANDNAME="g,r", FORMAT="csv"), timeout=300)
            if q.ok and q.text.count("\n") > 3: d = pd.read_csv(io.StringIO(q.text)); break
        except Exception: time.sleep(15)
    if d is None: rows.append(dict(oid=r.oid, dr="HOLE")); continue
    d = d[(d.catflags == 0) & (d.magerr < 0.3)]; d.to_csv(f"ztfdr/{r.oid}.csv", index=False)
    res = dict(oid=r.oid, dr_n=len(d))
    for b, c in (("zg", "g"), ("zr", "r")):
        x = d[d.filtercode == b].sort_values("mjd")
        if len(x) < 10: continue
        med = x.mag.median(); ob = x[x.mag < med - 1.5]; ep = int(((ob.mjd.diff() > 15).cumsum()).nunique()) if len(ob) else 0
        res.update({f"{b}_n": len(x), f"{b}_med": round(med, 2), f"{b}_min": round(x.mag.min(), 2), f"{b}_ob_pts": len(ob), f"{b}_ob_ep": ep, f"{b}_frac_ob": round(len(ob) / len(x), 3)})
        a.plot(x.mjd, x.mag, ".", ms=2, color=c)
    a.invert_yaxis(); a.axhline(r.G, color="k", lw=0.5, ls="--"); a.set_title(f"{r.oid} G{r.G:.1f}", fontsize=8); rows.append(res); time.sleep(2)
plt.tight_layout(); plt.savefig("mm_ztfdr.png", dpi=55)
R = pd.DataFrame(rows); R.to_csv("mm_ztfdr.csv", index=False); pd.set_option("display.width", 220); print(R.to_string(index=False))
