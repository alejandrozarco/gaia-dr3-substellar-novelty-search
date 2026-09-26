import json, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.table import Table
x = Table.read("lane_m_xmatch.fits")
R = json.load(open("/tmp/track1/ms_ridge.json"))
b = np.array(R["bins"]) + 0.05; ridge = np.array(R["ridge"], float); p99 = np.array(R["p99"], float)
ok = np.isfinite(ridge) & np.isfinite(p99)
plx = np.array(x["Plx"], float); eplx = np.array(x["e_Plx"], float); G = np.array(x["Gmag"], float); c = np.array(x["BP-RP"], float)
good = (plx / eplx > 5) & np.isfinite(c) & (c > -0.5) & (c < 4.2)
MG = G + 5 * np.log10(plx / 100)
rid = np.interp(c, b[ok], ridge[ok]); env = np.interp(c, b[ok], p99[ok])
below = good & (MG - rid > 1.0) & (MG > env)
print("matches with plx/err>5:", good.sum(), " below-MS (d_ridge>1 and below p99 envelope):", below.sum())
s = x[below]
s["MG"] = MG[below]; s["d_ridge"] = (MG - rid)[below]
# blending: number of Gaia matches within 4 arcsec of the same WISE source, and whether a brighter one exists
w = np.array(x["wise"]); Gall = G
brighter = []
for r in s:
    same = (w == r["wise"])
    brighter.append(int(np.sum(Gall[same] < r["Gmag"] - 0.0) ))
s["n_brighter_4as"] = brighter
s.sort("d_ridge", reverse=True)
keep = ["wise", "Source", "angDist", "RAJ2000", "DEJ2000", "Gmag", "BP-RP", "Plx", "e_Plx", "MG", "d_ridge", "RUWE", "P", "amp", "w1", "w2", "npts", "n_brighter_4as"]
s[keep].write("lane_m_below.fits", overwrite=True)
print("positive control J1526 (WISE J152614.95-111326.4) selected:", "J152614.95-111326.4" in set(s["wise"]))
print("J1435 WISE in Petrosky periodic P<0.35?", any("J143549" in str(v) for v in x["wise"]))
import collections
print("P (d) histogram of selected:", np.histogram(np.array(s["P"]), bins=[0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35])[0])
print("Dec>-28 (ZTF):", np.sum(np.array(s["DEJ2000"]) > -28), " unblended (no brighter Gaia within 4as):", np.sum(np.array(s["n_brighter_4as"]) == 0))
for r in s[:60]:
    print(f"{r['wise']} {r['Source']} G={r['Gmag']:.2f} BP-RP={r['BP-RP']:.2f} plx={r['Plx']:.2f}+-{r['e_Plx']:.2f} MG={r['MG']:.2f} dR={r['d_ridge']:+.2f} RUWE={r['RUWE']:.2f} P={r['P']:.4f} Wamp={r['amp']:.2f} W1={r['w1']:.2f} W1-W2={r['w1']-r['w2']:+.2f} nb={r['n_brighter_4as']}")
