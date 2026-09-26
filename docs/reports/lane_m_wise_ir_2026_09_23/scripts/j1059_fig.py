# Figure for VarWISE J105943.85-274050.1 = Gaia DR3 5456743064671253632 (lane M VarWISE screen, 2026-09-23).
# NEOWISE-R single exposures (same query/cuts as wise_battery.py) and ZTF DR (catflags 0, |sharp| < 0.5), folded at 2P = 2 x 0.1053647 d;
# per-visit W1 mean and semi-amplitude vs time. Output: j1059_fig.png, j1059_lc.csv (self-describing header).
import io, csv, subprocess, time, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle
RA0, DE0, PMRA, PMDE = 164.93280120834928, -27.680560897461646, -49.95604041580538, -12.373514177220297
P = 0.12097159
def tap(q):
    for k in range(6):
        p = subprocess.run(["curl", "-s", "--max-time", "900", "--data-urlencode", f"QUERY={q}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL",
                            "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
        if p.stdout.startswith("allwise") or p.stdout.startswith("mjd"): return list(csv.DictReader(io.StringIO(p.stdout)))
        time.sleep(30 * (k + 1))
    raise SystemExit("IRSA TAP failed: " + p.stdout[:200])
rows = tap(f"SELECT allwise_cntr, mjd, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na "
           f"FROM neowiser_p1bs_psd WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA0},{DE0},0.01))=1")
T = []
for x in rows:
    try:
        yr = (float(x["mjd"]) - 57388.0) / 365.25; rap = RA0 + PMRA * yr / 3.6e6 / np.cos(np.radians(DE0)); dep = DE0 + PMDE * yr / 3.6e6
        if np.hypot((float(x["ra"]) - rap) * np.cos(np.radians(DE0)), float(x["dec"]) - dep) * 3600 > 3: continue
        if not (float(x["qual_frame"]) > 0 and float(x["qi_fact"]) > 0 and float(x["saa_sep"]) > 0 and x["moon_masked"][0] == "0" and x["cc_flags"][0] == "0" and x["nb"] == "1" and x["na"] == "0"): continue
        T.append((float(x["mjd"]), float(x["w1mpro"]), float(x["w1sigmpro"]), float(x["w2mpro"]) if x["w2mpro"] else np.nan, float(x["w2sigmpro"]) if x["w2sigmpro"] else np.nan))
    except ValueError: pass
T = np.array(T); t, w1, e1, w2, e2 = T.T
with open("../data/j1059_neowise_lc.csv", "w") as fh:
    fh.write("# VarWISE J105943.85-274050.1 = Gaia DR3 5456743064671253632; NEOWISE-R single exposures, clean cuts as lane M; mjd (UTC), Vega mags\n")
    fh.write("mjd,w1mpro,w1sigmpro,w2mpro,w2sigmpro\n"); [fh.write(",".join(f"{v:.6f}" for v in r) + "\n") for r in T]
url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{RA0 + PMRA*5/3.6e6/np.cos(np.radians(DE0))}%20{DE0 + PMDE*5/3.6e6}%200.000833&BANDNAME=g,r,i&FORMAT=CSV"
zq = ""
for k in range(5):
    zq = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
    if zq.startswith("oid"): break
    time.sleep(30 * (k + 1))
Z = []
for x in csv.DictReader(io.StringIO(zq)) if zq.startswith("oid") else []:
    try:
        if x["catflags"] == "0" and abs(float(x["sharp"])) < 0.5: Z.append((x["filtercode"], float(x["hjd"]), float(x["mag"]), float(x["magerr"]), x["oid"]))
    except (TypeError, ValueError, KeyError): pass
f0 = 1 / P
# W1 maximum epoch (brightest) from a sinusoid fit
X = np.vstack([np.ones_like(t), np.cos(2 * np.pi * f0 * t), np.sin(2 * np.pi * f0 * t)]).T; w = 1 / e1
b, *_ = np.linalg.lstsq(X * w[:, None], w1 * w, rcond=None); phf = (np.arctan2(b[2], b[1]) / (2 * np.pi)) % 1
T0 = (np.floor(np.median(t) * f0) + (phf + 0.5) % 1) / f0
fig, ax = plt.subplots(2, 2, figsize=(11, 8))
for a, (lab, tt, y, e) in zip(ax.flat[:2], (("NEOWISE W1", t, w1, e1), ("NEOWISE W2", t[np.isfinite(w2)], w2[np.isfinite(w2)], e2[np.isfinite(w2)]))):
    ph = ((tt - T0) * f0 / 2) % 1
    for k in (0, 1): a.errorbar(ph + k, y, e, fmt=".", ms=3, alpha=0.45, color="0.3")
    edges = np.linspace(0, 1, 21); mids = 0.5 * (edges[1:] + edges[:-1]); med = [np.median(y[(ph >= lo) & (ph < hi)]) for lo, hi in zip(edges[:-1], edges[1:])]
    for k in (0, 1): a.plot(mids + k, med, "s-", color="tab:red", ms=4)
    a.invert_yaxis(); a.set_title(f"{lab} (n={len(y)}) folded at 2P = {2*P:.7f} d", fontsize=9); a.set_xlabel("phase at 2P (W1 maxima at 0 and 0.5)")
a = ax[1, 0]
zb = np.array([z[0] for z in Z]); zt = np.array([z[1] for z in Z]); zm = np.array([z[2] for z in Z]); ze = np.array([z[3] for z in Z])
for bnd, c in (("zr", "tab:red"), ("zg", "tab:green"), ("zi", "tab:brown")):
    s = zb == bnd
    if s.sum():
        ph = ((zt[s] - 2400000.0 - T0) * f0 / 2) % 1      # hjd vs mjd-based T0: offset < 1e-3 d, fine for display
        for k in (0, 1): a.errorbar(ph + k, zm[s], ze[s], fmt="o", ms=3, color=c, alpha=0.7, label=f"ZTF {bnd} (n={s.sum()})" if k == 0 else None)
a.invert_yaxis(); a.legend(fontsize=7); a.set_xlabel("phase at 2P"); a.set_title("ZTF DR (near the survey limit)", fontsize=9)
a = ax[1, 1]
order = np.argsort(t); tv = t[order]; vis = np.cumsum(np.r_[0, np.diff(tv) > 60])
yrs, means, amps, eamps = [], [], [], []
for k in np.unique(vis):
    s = order[vis == k]
    if len(s) < 8: continue
    F = 10 ** (-0.4 * w1[s]); eF = F * e1[s] / 1.0857
    X = np.vstack([np.ones(len(s)), np.cos(2 * np.pi * f0 * t[s]), np.sin(2 * np.pi * f0 * t[s])]).T; ww = 1 / eF
    bb, *_ = np.linalg.lstsq(X * ww[:, None], F * ww, rcond=None); C = np.linalg.inv((X * ww[:, None]).T @ (X * ww[:, None]))
    yrs.append(2000 + (np.mean(t[s]) - 51544.5) / 365.25); means.append(-2.5 * np.log10(bb[0])); amps.append(np.hypot(bb[1], bb[2]) / bb[0]); eamps.append(np.sqrt((C[1, 1] + C[2, 2]) / 2) / bb[0])
a.plot(yrs, means, "o", color="k", label="W1 mean per visit (flux-averaged, mag)"); a.invert_yaxis()

a2 = a.twinx(); a2.errorbar(yrs, amps, eamps, fmt="s", color="tab:red", mfc="none", ms=4, label="W1 fractional semi-amplitude"); a2.set_ylim(0, 1.0); a2.set_ylabel("fractional semi-amplitude", color="tab:red")
a.legend(fontsize=6, loc="lower left"); a.set_xlabel("year"); a.set_title("per visit (detections only; faint phases partly censored)", fontsize=9)
fig.suptitle("VarWISE J105943.85-274050.1 = Gaia DR3 5456743064671253632; P = 0.12097159 d (2.9033 h; BJD alias audit)", fontsize=10)
plt.tight_layout(); plt.savefig("../figures/j1059_fold.png", dpi=115); print("saved; n W1", len(t), "n ZTF", len(Z))
