# J1226-2304: NEOWISE periodicity (W1, W2), photocentre vs phase (blend test), WISE source proper motion vs Gaia, field controls
import io, csv, subprocess, json, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.timeseries import LombScargle
RA0, DE0, PMRA, PMDE = 186.6576601770502, -23.070649744994668, -51.51495040669747, 7.449848962974899   # Gaia DR3, epoch 2016.0
def tap(q):
    p = subprocess.run(["curl", "-s", "--max-time", "900", "--data-urlencode", f"QUERY={q}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL",
                        "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
    if not (p.stdout.startswith("mjd") or p.stdout.startswith("allwise")): raise RuntimeError(p.stdout[:300])
    return list(csv.DictReader(io.StringIO(p.stdout)))
rows = tap(f"SELECT allwise_cntr, mjd, ra, dec, sigra, sigdec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, w1snr, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na "
           f"FROM neowiser_p1bs_psd WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA0},{DE0},0.1))=1")
def clean(x):
    return (float(x["qual_frame"]) > 0 and float(x["qi_fact"]) > 0 and float(x["saa_sep"]) > 0 and x["moon_masked"][0] == "0" and x["cc_flags"][0] == "0" and x["nb"] == "1" and x["na"] == "0")
T = []
for x in rows:
    try:
        yr = (float(x["mjd"]) - 57388.0) / 365.25   # years from 2016.0
        rap = RA0 + PMRA*yr/3.6e6/np.cos(np.radians(DE0)); dep = DE0 + PMDE*yr/3.6e6
        dx = (float(x["ra"]) - rap) * np.cos(np.radians(DE0)) * 3600; dy = (float(x["dec"]) - dep) * 3600
        if np.hypot(dx, dy) < 3.0 and clean(x):
            T.append((float(x["mjd"]) + 2400000.5, float(x["w1mpro"]), float(x["w1sigmpro"]), float(x["w2mpro"]) if x["w2mpro"] else np.nan,
                      float(x["w2sigmpro"]) if x["w2sigmpro"] else np.nan, dx, dy, float(x["sigra"]), float(x["sigdec"]), yr))
    except ValueError: pass
T = np.array(T); t, w1, e1, w2, e2, dx, dy, sra, sde, yr = T.T
print(f"J1226 NEOWISE clean epochs within 3in of the PM-propagated Gaia position: {len(T)}; W1 median {np.median(w1):.2f}; span {t.min()-2400000.5:.0f}-{t.max()-2400000.5:.0f}")
ls1 = LombScargle(t, w1, e1); f, p1 = ls1.autopower(minimum_frequency=0.5, maximum_frequency=40, samples_per_peak=10); k = np.argmax(p1); f0 = f[k]
print(f"W1: best P = {1/f0:.8f} d ({24/f0:.4f} h), power {p1[k]:.3f}, FAP {ls1.false_alarm_probability(p1[k], minimum_frequency=0.5, maximum_frequency=40):.1e}")
top = np.argsort(p1)[::-1]; seen = []
for j in top:
    if all(abs(f[j] - s) > 0.02 for s in seen): seen.append(f[j])
    if len(seen) == 6: break
print("  top W1 peaks (P d, power):", [(round(1/s, 7), round(float(ls1.power(np.array([s]))[0]), 3)) for s in seen])
m2 = np.isfinite(w2) & np.isfinite(e2)
ls2 = LombScargle(t[m2], w2[m2], e2[m2]); f2, p2 = ls2.autopower(minimum_frequency=0.5, maximum_frequency=40, samples_per_peak=10); k2 = np.argmax(p2)
print(f"W2 (independent search): best P = {1/f2[k2]:.8f} d, power {p2[k2]:.3f}, FAP {ls2.false_alarm_probability(p2[k2], minimum_frequency=0.5, maximum_frequency=40):.1e}; W2 power at W1 period {ls2.power(np.array([f0]))[0]:.3f}")
# refine f0 and fold
fr = np.linspace(f0 - 3e-4, f0 + 3e-4, 6001); f0 = fr[np.argmax(ls1.power(fr))]
ph = ((t - 2459000.0) * f0) % 1
def binned(v, n=10):
    return np.array([np.median(v[(ph >= j/n) & (ph < (j+1)/n)]) for j in range(n)])
b1, b2 = binned(w1), binned(np.where(m2, w2, np.nan)[m2] if False else w2)
b2 = np.array([np.nanmedian(w2[(ph >= j/10) & (ph < (j+1)/10)]) for j in range(10)])
print(f"refined P = {1/f0:.8f} d; W1 bins: {' '.join(f'{v:.2f}' for v in b1)} (range {b1.max()-b1.min():.2f}); W2 bins: {' '.join(f'{v:.2f}' for v in b2)} (range {np.nanmax(b2)-np.nanmin(b2):.2f})")
# photocentre vs brightness: split into bright (W1 below median-0.15) and faint (above median+0.15) epochs
med = np.median(w1); br = w1 < med - 0.15; fa = w1 > med + 0.15
for lab, s in (("bright", br), ("faint", fa), ("all", np.ones_like(br, bool))):
    wgt = 1 / (sra[s]**2 + 1e-4)
    print(f"  photocentre offset from PM-propagated Gaia ({lab:6s}, n={s.sum():3d}): dRA* {np.average(dx[s], weights=wgt):+.3f} +- {1/np.sqrt(wgt.sum()):.3f}in, "
          f"dDec {np.average(dy[s], weights=1/(sde[s]**2+1e-4)):+.3f} +- {1/np.sqrt((1/(sde[s]**2+1e-4)).sum()):.3f}in")
# WISE-source proper motion: fit dx, dy relative to a FIXED position (Gaia at 2016 without PM) vs time
fx = (dx + PMRA*yr/1000); fy = (dy + PMDE*yr/1000)    # offsets from the fixed 2016 position
A = np.column_stack([np.ones_like(yr), yr])
cx = np.linalg.lstsq(A * (1/sra)[:, None], fx / sra, rcond=None)[0]; cy = np.linalg.lstsq(A * (1/sde)[:, None], fy / sde, rcond=None)[0]
rx = fx - A @ cx; ry = fy - A @ cy
ecx = np.sqrt(np.sum(rx**2) / (len(rx) - 2) / np.sum(((yr - yr.mean()))**2)); ecy = np.sqrt(np.sum(ry**2) / (len(ry) - 2) / np.sum(((yr - yr.mean()))**2))
print(f"  WISE-measured proper motion: pmRA* {cx[1]*1000:+.0f} +- {ecx*1000:.0f} mas/yr, pmDec {cy[1]*1000:+.0f} +- {ecy*1000:.0f} mas/yr (Gaia: {PMRA:+.1f}, {PMDE:+.1f})")
json.dump(dict(t=t.tolist(), w1=w1.tolist(), e1=e1.tolist(), w2=w2.tolist(), e2=e2.tolist(), P=1/f0), open("j1226_wise.json", "w"))
# field controls: all other sources within 6 arcmin with 13.5 < W1 < 15.5 and >=100 clean epochs, power at f0
src = {}
for x in rows:
    try:
        if clean(x) and x["allwise_cntr"] not in ("", "0"): src.setdefault(x["allwise_cntr"], []).append((float(x["mjd"]) + 2400000.5, float(x["w1mpro"]), float(x["w1sigmpro"]), float(x["ra"]), float(x["dec"])))
    except ValueError: pass
pc = []
for kx, v in src.items():
    a = np.array(v)
    if len(a) < 100 or not (13.3 < np.median(a[:, 1]) < 15.8): continue
    sep = np.hypot((np.median(a[:, 3]) - RA0) * np.cos(np.radians(DE0)), np.median(a[:, 4]) - DE0) * 3600
    if sep < 5: continue
    pc.append(float(LombScargle(a[:, 0], a[:, 1], a[:, 2]).power(np.array([f0]))[0]))
print(f"  field controls (13.3<W1<15.8, >=100 epochs, n={len(pc)}): power at the J1226 frequency median {np.median(pc):.3f}, max {max(pc):.3f}")
