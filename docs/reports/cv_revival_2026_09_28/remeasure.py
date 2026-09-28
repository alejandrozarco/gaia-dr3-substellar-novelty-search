"""CV period revival, 2026-09-28: fresh blind period search of the 37 NOVEL/SUPERHUMP targets of the May verification report
(notes/verification_report_RECOVERED_2026_09_27.md) on freshly fetched ZTF DR light curves (cvrevival/ztf/<slug>.csv, IRSA 1.5 arcsec,
g+r). Quiescence mask: per band, points brighter than the running (90-day) median by more than 0.6 mag are removed (outbursts);
catflags == 0, magerr < 0.2. Per band and jointly: generalised Lomb-Scargle 0.5-72 c/d (1-day masks), top peak with Baluev FAP, and the
power/FAP at the report's claimed period where the Details text quotes one (numbers followed by 'min'). Writes cv_revival_remeasure.csv.
Usage: uv run python scripts/cv_revival_remeasure_2026_09_28.py <ztf_dir> <out_csv>"""
import os, re, sys, glob, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from astropy.timeseries import LombScargle
ROOT = os.path.expanduser("~/claude_projects/ostinato")  # the May report lives in the ostinato project
ZDIR, OUT = sys.argv[1], sys.argv[2]
rep = {}
for l in open(os.path.join(ROOT, "notes", "verification_report_RECOVERED_2026_09_27.md")):
    c = [x.strip() for x in l.split("|")]
    if len(c) >= 5 and c[1].isdigit():
        name, verdict, details = c[2], c[3], c[4]
        mins = [float(x) for x in re.findall(r"(?:ours|our|P\s*=|period(?: of)?)\s*~?\s*(\d+(?:\.\d+)?)\s*min", details, re.I)]
        allmins = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*min", details)]
        rep[name.split(" (")[0]] = dict(verdict=verdict, details=details[:200], claimed_min=(mins or allmins or [np.nan])[0])
FR = np.arange(0.5, 72, 0.00005); MASK = np.ones(len(FR), bool)
for n in range(1, 73):  # every integer cycle/day and its sidereal twin, with the skirt
    MASK &= (np.abs(FR - n) > 0.10) & (np.abs(FR - n * 1.0027379) > 0.10)
def quiescent(x):
    x = x.sort_values("mjd"); m = x.mag.values; t = x.mjd.values; keep = np.ones(len(x), bool)
    for i in range(len(x)):
        w = np.abs(t - t[i]) < 45; med = np.median(m[w]); keep[i] = m[i] > med - 0.6
    return x[keep]
rows = []
for f in sorted(glob.glob(os.path.join(ZDIR, "*.csv"))):
    slug = os.path.basename(f)[:-4]; d = pd.read_csv(f); d = d[(d.catflags == 0) & (d.magerr < 0.2)]
    rec = dict(name=slug, n_raw=len(d)); rec.update(rep.get(slug, {}))
    T, Y, E = [], [], []
    for b in ("zg", "zr"):
        x = quiescent(d[d.filtercode == b])
        if len(x) < 40: rec[f"n_{b}"] = len(x); continue
        t, y, e = x.mjd.values, 10 ** (-0.4 * (x.mag.values - np.median(x.mag))) - 1, 0.921 * x.magerr.values * (10 ** (-0.4 * (x.mag.values - np.median(x.mag))))
        ls = LombScargle(t, y, e); p = ls.power(FR); p[~MASK] = 0; k = np.argmax(p)
        rec.update({f"n_{b}": len(t), f"f_{b}": round(FR[k], 5), f"P_{b}_min": round(1440 / FR[k], 2), f"fap_{b}": float(f"{ls.false_alarm_probability(p[k], minimum_frequency=0.5, maximum_frequency=72):.2g}")})
        cm = rec.get("claimed_min")
        if cm and np.isfinite(cm):
            fc = 1440 / cm; w = np.abs(FR - fc) < 0.02
            if w.any(): kk = np.argmax(np.where(w, p, 0)); rec[f"fap_claimed_{b}"] = float(f"{ls.false_alarm_probability(p[kk], minimum_frequency=0.5, maximum_frequency=72):.2g}")
        T += list(t); Y += list(y); E += list(e)
    if len(T) >= 60:
        T, Y, E = map(np.array, (T, Y, E)); ls = LombScargle(T, Y, E); p = ls.power(FR); p[~MASK] = 0; k = np.argmax(p)
        rec.update(n_joint=len(T), f_joint=round(FR[k], 5), P_joint_min=round(1440 / FR[k], 2), fap_joint=float(f"{ls.false_alarm_probability(p[k], minimum_frequency=0.5, maximum_frequency=72):.2g}"))
        cm = rec.get("claimed_min")
        if cm and np.isfinite(cm):
            fc = 1440 / cm; rel = [abs(FR[k] - c) / c < 0.01 for c in (fc, 2 * fc, fc / 2, fc + 1, fc - 1)]
            rec["joint_matches_claimed"] = "f,2f,f/2,f+1,f-1".split(",")[rel.index(True)] if any(rel) else ""
    rows.append(rec); print(slug, rec.get("verdict", ""), "claimed", rec.get("claimed_min"), "| joint", rec.get("P_joint_min"), rec.get("fap_joint"), rec.get("joint_matches_claimed", ""), flush=True)
pd.DataFrame(rows).to_csv(OUT, index=False); print("wrote", OUT, len(rows))
