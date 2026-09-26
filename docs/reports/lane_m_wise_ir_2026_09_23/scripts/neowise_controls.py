# Systematics test: fold every comparable NEOWISE source within 6 arcmin of J1526 on J1526's period; also W2 for J1526
import io, csv, subprocess, numpy as np, json
from astropy.timeseries import LombScargle
RA, DE, P = 231.5620, -11.2245, 0.09379696
def tap(q):
    p = subprocess.run(["curl", "-s", "--max-time", "900", "--data-urlencode", f"QUERY={q}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL",
                        "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
    assert p.stdout.startswith("mjd") or p.stdout.startswith("allwise_cntr"), p.stdout[:300]
    return list(csv.DictReader(io.StringIO(p.stdout)))
rows = tap(f"SELECT allwise_cntr, mjd, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na "
           f"FROM neowiser_p1bs_psd WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA},{DE},0.1))=1")
print("rows", len(rows))
src = {}
for x in rows:
    try: w1 = float(x["w1mpro"]); e1 = float(x["w1sigmpro"])
    except ValueError: continue
    if not (float(x["qual_frame"]) > 0 and float(x["qi_fact"]) > 0 and float(x["saa_sep"]) > 0 and x["moon_masked"][0] == "0" and x["cc_flags"][0] == "0" and x["nb"] == "1" and x["na"] == "0"): continue
    k = x["allwise_cntr"]
    if not k or k == "0": continue
    try: w2 = float(x["w2mpro"]); e2 = float(x["w2sigmpro"])
    except ValueError: w2, e2 = np.nan, np.nan
    src.setdefault(k, []).append((float(x["mjd"]), w1, e1, w2, e2, float(x["ra"]), float(x["dec"])))
f0 = 1 / P
res = []
for k, v in src.items():
    a = np.array(v)
    if len(a) < 120: continue
    t, m, e = a[:, 0], a[:, 1], a[:, 2]
    med = np.median(m)
    if not (11.3 < med < 14.8): continue
    ra, de = np.median(a[:, 5]), np.median(a[:, 6])
    sep = np.hypot((ra - RA) * np.cos(np.radians(DE)), de - DE) * 3600
    ls = LombScargle(t, m, e); pw = float(ls.power(np.array([f0]))[0])
    ph = (t * f0) % 1
    b = [np.median(m[(ph >= j/10) & (ph < (j+1)/10)]) for j in range(10) if ((ph >= j/10) & (ph < (j+1)/10)).sum() > 3]
    res.append(dict(cntr=k, sep=round(sep, 1), n=len(a), W1=round(med, 2), rsig=round(1.4826*np.median(np.abs(m-med)), 3), mederr=round(np.median(e), 3),
                    power_f0=round(pw, 3), fold_range=round(max(b) - min(b), 3)))
res.sort(key=lambda r: r["sep"])
for r in res: print(r)
tgt = [r for r in res if r["sep"] < 3]
ctl = [r for r in res if r["sep"] >= 3]
print(f"\ncontrols: {len(ctl)}; fold range median {np.median([r['fold_range'] for r in ctl]):.3f}, max {max(r['fold_range'] for r in ctl):.3f}; "
      f"power_f0 median {np.median([r['power_f0'] for r in ctl]):.3f}, max {max(r['power_f0'] for r in ctl):.3f}")
# J1526 W2 fold
k = min(src, key=lambda kk: np.hypot((np.median(np.array(src[kk])[:, 5]) - RA) * np.cos(np.radians(DE)), np.median(np.array(src[kk])[:, 6]) - DE))
a = np.array(src[k]); a = a[np.isfinite(a[:, 3])]
t, m2, e2, m1 = a[:, 0], a[:, 3], a[:, 4], a[:, 1]
ph = (t * f0) % 1
b1 = [np.median(m1[(ph >= j/10) & (ph < (j+1)/10)]) for j in range(10)]
b2 = [np.median(m2[(ph >= j/10) & (ph < (j+1)/10)]) for j in range(10)]
print("J1526 cntr", k, "n", len(a))
print("  W1 bins:", " ".join(f"{x:.2f}" for x in b1), f" range {max(b1)-min(b1):.3f}")
print("  W2 bins:", " ".join(f"{x:.2f}" for x in b2), f" range {max(b2)-min(b2):.3f}")
print("  W1-W2 bins:", " ".join(f"{x-y:+.2f}" for x, y in zip(b1, b2)))
ls2 = LombScargle(t, m2, e2); fw, pw = ls2.autopower(minimum_frequency=0.5, maximum_frequency=40, samples_per_peak=10)
print(f"  W2 global LS best P={1/fw[np.argmax(pw)]:.7f} d power {pw.max():.3f}; power at f0 {ls2.power(np.array([f0]))[0]:.3f}")
json.dump(dict(controls=ctl, target=tgt), open("neowise_controls.json", "w"), indent=1)
