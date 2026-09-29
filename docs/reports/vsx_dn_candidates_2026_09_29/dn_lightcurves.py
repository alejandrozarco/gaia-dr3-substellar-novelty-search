"""Outburst census for the seven ZTF dwarf-nova candidates (2026-09-29), for VSX drafts.
Data: ZTF data-release PSF light curves (ztfdr/<oid>.csv; IRSA, 1.5 arcsec, catflags == 0; per filter the ZTF object id with most
points) and ALeRCE alert light curves (alerts/<oid>.csv; isdiffpos = 1, magpsf_corr < 90, drb >= 0.8 or rb >= 0.6 when drb is absent).
Quiescence = median DR magnitude per filter (a filter with < 10 DR points uses the other filter's median). An outburst point is
> 1.5 mag brighter than quiescence. Outburst points are grouped into episodes (gaps > 15 d); an episode counts only if it has
>= 2 outburst points (DR and alerts combined, any filter), so one isolated point cannot make an outburst. ZTF alerts usually
give one point per filter per night, so a decline over several nights counts. Single-point episodes are listed separately. Output: dn_census.csv, <oid>_lc.png."""
import numpy as np, pandas as pd, os, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__))
C = [("6291945806661266560", "ZTF20aaxughc"), ("3082396190372984832", "ZTF18acrmcvc"), ("5614298790271682688", "ZTF20actkemr"),
     ("5701425912708783488", "ZTF22aaahiva"), ("3109248424693126400", "ZTF18actbmig"), ("4308831935765230720", "ZTF21abuysmk"),
     ("5182404743053707904", "ZTF24abfojgu")]
rows = []
for gaia, oid in C:
    d = pd.read_csv(os.path.join(H, "ztfdr", oid + ".csv")); d = d[d.catflags == 0]
    a = pd.read_csv(os.path.join(H, "alerts", oid + ".csv"))
    a = a[(a.isdiffpos.astype(str).isin(["1", "t", "True"])) & (a.magpsf_corr < 90)]
    good = np.where(a.drb.notna(), a.drb >= 0.8, a.rb >= 0.6); a = a[good]
    med = {}; pts = []; fig, ax = plt.subplots(figsize=(11, 3.6))
    for fc, fid, col in (("zg", 1, "g"), ("zr", 2, "r")):
        x = d[d.filtercode == fc]
        if len(x): x = x[x.oid == x.oid.value_counts().index[0]]
        if len(x) >= 10:
            med[fc] = float(np.median(x.mag)); ax.errorbar(x.mjd, x.mag, x.magerr, fmt=".", ms=3, color=col, alpha=0.5, lw=0.4, label=f"ZTF DR {fc[1]} (median {med[fc]:.2f})")
            for m, mg, e in zip(x.mjd, x.mag, x.magerr): pts.append(("DR", fc, m, mg, e))
        y = a[a.fid == fid]
        if len(y): ax.plot(y.mjd, y.magpsf_corr, "x", color=col, ms=5, label=f"alerts {fc[1]}")
        for m, mg, e in zip(y.mjd, y.magpsf_corr, y.sigmapsf_corr): pts.append(("alert", fc, m, mg, e))
    P = pd.DataFrame(pts, columns=["src", "fc", "mjd", "mag", "err"])
    for fc, oth in (("zg", "zr"), ("zr", "zg")):
        if fc not in med and oth in med: med[fc] = med[oth]
    P["ob"] = [row.mag < med[row.fc] - 1.5 if row.fc in med else False for row in P.itertuples()]
    O = P[P.ob].copy().sort_values("mjd"); O["night"] = np.floor(O.mjd)
    allg = [] if len(O) == 0 else np.split(O.mjd.values, np.where(np.diff(O.mjd.values) > 15)[0] + 1)
    eps = [np.unique(np.floor(g)) for g in allg if len(g) >= 2]; singles = [g for g in allg if len(g) < 2]
    nights = np.concatenate(eps) if eps else np.array([])
    cnt = O.groupby("night").size()
    peak = {fc: float(P[(P.fc == fc)].mag.min()) if (P.fc == fc).any() else np.nan for fc in ("zg", "zr")}
    peak_conf = {fc: float(O[(O.fc == fc) & O.night.isin(nights)].mag.min()) if ((O.fc == fc) & O.night.isin(nights)).any() else np.nan for fc in ("zg", "zr")}
    ep_desc = "; ".join(f"MJD {int(e[0])}" + (f"-{int(e[-1])} ({int(e[-1]-e[0])+1} d)" if len(e) > 1 else "") for e in eps)
    rows.append(dict(gaia=gaia, oid=oid, n_dr=len(d), n_alert_good=len(a), med_g=med.get("zg"), med_r=med.get("zr"),
                     n_outburst_points=len(O), n_outburst_nights=len(nights), n_single_point_episodes=len(singles), n_episodes=len(eps),
                     peak_g=peak_conf["zg"], peak_r=peak_conf["zr"], episodes=ep_desc, mjd_first=float(P.mjd.min()), mjd_last=float(P.mjd.max())))
    for e in eps: ax.axvspan(e[0] - 1, e[-1] + 2, color="orange", alpha=0.25)
    ax.invert_yaxis(); ax.set_xlabel("MJD"); ax.set_ylabel("mag"); ax.legend(fontsize=7, ncol=4)
    ax.set_title(f"{oid} = Gaia DR3 {gaia}: {len(nights)} outburst nights in {len(eps)} episodes (each >= 2 points > 1.5 mag above quiescence)", fontsize=9)
    plt.tight_layout(); plt.savefig(os.path.join(H, f"{oid}_lc.png"), dpi=90); plt.close()
    print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(os.path.join(H, "dn_census.csv"), index=False)
