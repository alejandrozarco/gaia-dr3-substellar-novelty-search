# Generic WISE test battery: period search (W1, W2), fold at trial periods, photocentre vs brightness, WISE proper motion, field controls, ZTF amplitude at same period
import io, csv, sys, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.timeseries import LombScargle
from astroquery.gaia import Gaia
sid = sys.argv[1]; trials = [float(x) for x in sys.argv[2:]]
g = Gaia.launch_job(f"SELECT ra, dec, pmra, pmdec, parallax, phot_g_mean_mag, bp_rp FROM gaiadr3.gaia_source WHERE source_id={sid}").get_results()[0]
RA0, DE0, PMRA, PMDE = float(g["ra"]), float(g["dec"]), float(g["pmra"]), float(g["pmdec"])
print(f"Gaia DR3 {sid}: G {float(g['phot_g_mean_mag']):.2f}, BP-RP {float(g['bp_rp']):.2f}, plx {float(g['parallax']):.2f}, pm ({PMRA:.1f}, {PMDE:.1f})")
def tap(q):
    p = subprocess.run(["curl", "-s", "--max-time", "900", "--data-urlencode", f"QUERY={q}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL",
                        "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
    if not (p.stdout.startswith("mjd") or p.stdout.startswith("allwise")): raise RuntimeError(p.stdout[:300])
    return list(csv.DictReader(io.StringIO(p.stdout)))
rows = tap(f"SELECT allwise_cntr, mjd, ra, dec, sigra, sigdec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na "
           f"FROM neowiser_p1bs_psd WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA0},{DE0},0.1))=1")
clean = lambda x: float(x["qual_frame"]) > 0 and float(x["qi_fact"]) > 0 and float(x["saa_sep"]) > 0 and x["moon_masked"][0] == "0" and x["cc_flags"][0] == "0" and x["nb"] == "1" and x["na"] == "0"
T = []
for x in rows:
    try:
        yr = (float(x["mjd"]) - 57388.0) / 365.25
        rap = RA0 + PMRA*yr/3.6e6/np.cos(np.radians(DE0)); dep = DE0 + PMDE*yr/3.6e6
        dx = (float(x["ra"]) - rap)*np.cos(np.radians(DE0))*3600; dy = (float(x["dec"]) - dep)*3600
        if np.hypot(dx, dy) < 3.0 and clean(x):
            T.append((float(x["mjd"]) + 2400000.5, float(x["w1mpro"]), float(x["w1sigmpro"]), float(x["w2mpro"]) if x["w2mpro"] else np.nan,
                      float(x["w2sigmpro"]) if x["w2sigmpro"] else np.nan, dx, dy, float(x["sigra"]), float(x["sigdec"]), yr))
    except ValueError: pass
T = np.array(T); t, w1, e1, w2, e2, dx, dy, sra, sde, yr = T.T
print(f"NEOWISE clean epochs: {len(T)}; W1 median {np.median(w1):.2f}; robust sd {1.4826*np.median(np.abs(w1-np.median(w1))):.3f}; median err {np.median(e1):.3f}")
ls1 = LombScargle(t, w1, e1); f, p1 = ls1.autopower(minimum_frequency=0.5, maximum_frequency=40, samples_per_peak=10)
top = np.argsort(p1)[::-1]; seen = []
for j in top:
    if all(abs(f[j] - s) > 0.02 for s in seen): seen.append(f[j])
    if len(seen) == 6: break
print("W1 top peaks (P d, power):", [(round(1/s, 7), round(float(ls1.power(np.array([s]))[0]), 3)) for s in seen])
m2 = np.isfinite(w2) & np.isfinite(e2); ls2 = LombScargle(t[m2], w2[m2], e2[m2])
def amp(tt, mm, ee, fr):
    X = np.column_stack([np.ones_like(tt), np.sin(2*np.pi*fr*tt), np.cos(2*np.pi*fr*tt)]); w = 1/ee**2; C = np.linalg.inv(X.T @ (X*w[:, None])); p = C @ (X.T @ (mm*w))
    r = mm - X @ p; s2 = np.sum(r**2*w)/max(1, len(tt)-3); a = np.hypot(p[1], p[2]); ea = np.sqrt(s2*(C[1,1]*p[1]**2 + C[2,2]*p[2]**2)/max(a**2, 1e-12))
    return 2*a, 2*ea
# ZTF
url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{RA0 + PMRA*5/3.6e6/np.cos(np.radians(DE0))}%20{DE0 + PMDE*5/3.6e6}%200.000833&BANDNAME=g,r,i&FORMAT=CSV"
q = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
Z = [x for x in csv.DictReader(io.StringIO(q)) if x.get("catflags") == "0" and abs(float(x["sharp"])) < 0.5] if q.startswith("oid") else []
zb = np.array([x["filtercode"] for x in Z]); zt = np.array([float(x["hjd"]) for x in Z]); zm = np.array([float(x["mag"]) for x in Z]); ze = np.array([float(x["magerr"]) for x in Z])
zo = np.array([x["oid"] for x in Z])
for o in set(zo): zm[zo == o] -= np.median(zm[zo == o])
for P in trials + [1/seen[0]]:
    fr = 1/P; fr = np.linspace(fr - 2e-4, fr + 2e-4, 4001)[np.argmax(ls1.power(np.linspace(fr - 2e-4, fr + 2e-4, 4001)))] if P == 1/seen[0] else fr
    a1, ea1 = amp(t - 2459000, w1, e1, fr); a2, ea2 = amp(t[m2] - 2459000, w2[m2], e2[m2], fr)
    s = f"P={1/fr:.8f} d ({24/fr:.4f} h): W1 power {ls1.power(np.array([fr]))[0]:.3f} amp {a1:.3f}+-{ea1:.3f}; W2 power {ls2.power(np.array([fr]))[0]:.3f} amp {a2:.3f}+-{ea2:.3f}"
    for b in ("zg", "zr", "zi"):
        sb = zb == b
        if sb.sum() >= 20:
            ab, eab = amp(zt[sb] - 2459000, zm[sb], ze[sb], fr); s += f"; {b} (n={sb.sum()}) power {LombScargle(zt[sb], zm[sb], ze[sb]).power(np.array([fr]))[0]:.3f} amp {ab:.3f}+-{eab:.3f}"
    print(s)
med = np.median(w1); br = w1 < med - 0.15; fa = w1 > med + 0.15
for lab, s in (("bright", br), ("faint", fa)):
    if s.sum() < 5: continue
    wx = 1/(sra[s]**2 + 1e-4); wy = 1/(sde[s]**2 + 1e-4)
    print(f"photocentre ({lab}, n={s.sum()}): dRA* {np.average(dx[s], weights=wx):+.3f}+-{1/np.sqrt(wx.sum()):.3f}in dDec {np.average(dy[s], weights=wy):+.3f}+-{1/np.sqrt(wy.sum()):.3f}in")
fx = dx + PMRA*yr/1000; fy = dy + PMDE*yr/1000; A = np.column_stack([np.ones_like(yr), yr])
cx = np.linalg.lstsq(A/sra[:, None], fx/sra, rcond=None)[0]; cy = np.linalg.lstsq(A/sde[:, None], fy/sde, rcond=None)[0]
rx = fx - A @ cx; ry = fy - A @ cy; den = np.sum((yr - yr.mean())**2)
print(f"WISE proper motion: ({cx[1]*1000:+.0f} +- {np.sqrt(np.sum(rx**2)/(len(rx)-2)/den)*1000:.0f}, {cy[1]*1000:+.0f} +- {np.sqrt(np.sum(ry**2)/(len(ry)-2)/den)*1000:.0f}) mas/yr vs Gaia ({PMRA:+.1f}, {PMDE:+.1f})")
src = {}
for x in rows:
    try:
        if clean(x) and x["allwise_cntr"] not in ("", "0"): src.setdefault(x["allwise_cntr"], []).append((float(x["mjd"]), float(x["w1mpro"]), float(x["w1sigmpro"]), float(x["ra"]), float(x["dec"])))
    except ValueError: pass
f0 = seen[0]; pc = []
for kx, v in src.items():
    a = np.array(v)
    if len(a) < 100 or abs(np.median(a[:, 1]) - med) > 1.2: continue
    if np.hypot((np.median(a[:, 3]) - RA0)*np.cos(np.radians(DE0)), np.median(a[:, 4]) - DE0)*3600 < 5: continue
    pc.append(float(LombScargle(a[:, 0], a[:, 1], a[:, 2]).power(np.array([f0]))[0]))
print(f"field controls (|W1-{med:.1f}|<1.2, >=100 epochs, n={len(pc)}): power at best W1 frequency median {np.median(pc):.3f}, max {max(pc):.3f}")
