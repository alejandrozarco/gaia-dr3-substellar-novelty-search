"""Switch-on search (2026-09-29): ALeRCE CV/Nova-class objects created 2023 or later (first alert >= MJD 59945) with a Gaia DR3
counterpart, Galactic (proper motion or parallax > 3 sigma), alerts spanning > 150 d with >= 20 detections (switchon_pre.csv):
105 not in VSX or CV lists, plus known controls (polars AM*, novalikes NL*/VY, WZ Sge-type UGWZ).
For each, the ZTF data-release PSF light curve (IRSA, 1.5 arcsec, catflags 0, magerr < 0.3; per filter the ZTF object id with most
points). "Before" = points more than 30 d before the first alert; "after" = points after the first alert. A switch-on is a
sustained change: after-median >= 1.0 mag brighter than before-median, >= 70% of after points more than 0.75 mag brighter than
the before-median, and after data spanning >= 100 d. A switch-off is the mirror image (after-median >= 1.0 mag fainter,
>= 70% of after points more than 0.75 mag fainter) (per filter; the filter with more points decides). An empty IRSA reply is
retried and then recorded as HOLE, never as a null. Output: switchon.csv; light curves ztfdr_so/<oid>.csv."""
import io, os, time, requests, pandas as pd, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); os.makedirs(os.path.join(H, "ztfdr_so"), exist_ok=True)
S = pd.read_csv(os.path.join(H, "switchon_pre.csv"), dtype={"gaia_id": str})
unk = S[~S.in_vsx & ~S.in_cvlist]
ctrl = S[S.in_vsx & S.vsx_type.fillna("").str.contains(r"^AM|NL|VY|UGWZ", regex=True)].head(15)
T = pd.concat([unk.assign(set="candidate"), ctrl.assign(set="control")])
rows = []
for r in T.itertuples():
    fn = os.path.join(H, "ztfdr_so", r.oid + ".csv"); d = None
    if os.path.exists(fn): d = pd.read_csv(fn)
    else:
        for i in range(3):
            try:
                q = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {r.meanra} {r.meandec} 0.00042", BANDNAME="g,r", FORMAT="csv"), timeout=300)
                if q.ok and q.text.count("\n") > 3: d = pd.read_csv(io.StringIO(q.text)); break
            except Exception: pass
            time.sleep(15 * (i + 1))
        if d is not None: d.to_csv(fn, index=False)
        time.sleep(2)
    res = dict(oid=r.oid, set=r.set, vsx_type=r.vsx_type, G=r.G, firstmjd=r.firstmjd, ndet=r.ndet)
    if d is None: res["verdict"] = "HOLE"; rows.append(res); print(res, flush=True); continue
    d = d[(d.catflags == 0) & (d.magerr < 0.3)]; best = None
    for b in ("zg", "zr"):
        x = d[d.filtercode == b]
        if len(x) == 0: continue
        x = x[x.oid == x.oid.value_counts().index[0]]
        bef = x[x.mjd < r.firstmjd - 30]; aft = x[x.mjd >= r.firstmjd]
        if len(bef) < 10 or len(aft) < 5: continue
        mb, ma = bef.mag.median(), aft.mag.median(); frac = float(np.mean(aft.mag < mb - 0.75)); frac_f = float(np.mean(aft.mag > mb + 0.75)); span = float(aft.mjd.max() - aft.mjd.min())
        cand = dict(band=b, n_before=len(bef), n_after=len(aft), med_before=round(mb, 2), med_after=round(ma, 2), delta=round(mb - ma, 2), frac_bright=round(frac, 2), frac_faint=round(frac_f, 2), after_span=round(span))
        if best is None or len(aft) > best["n_after"]: best = cand
    if best is None: res["verdict"] = "insufficient DR data"
    else:
        res.update(best)
        res["verdict"] = ("SWITCH-ON" if (best["delta"] >= 1.0 and best["frac_bright"] >= 0.7 and best["after_span"] >= 100) else
                          "SWITCH-OFF" if (best["delta"] <= -1.0 and best["frac_faint"] >= 0.7 and best["after_span"] >= 100) else
                          "brightened" if best["delta"] >= 0.5 else "faded" if best["delta"] <= -0.5 else "no sustained change")
    rows.append(res); print(res, flush=True)
R = pd.DataFrame(rows); R.to_csv(os.path.join(H, "switchon.csv"), index=False)
print(R.groupby(["set", "verdict"]).size().to_string())
