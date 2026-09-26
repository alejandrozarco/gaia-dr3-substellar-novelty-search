# J0753 (Gaia DR3 3082614748370926848): ATLAS o/c (season-detrended difference flux) and NEOWISE W1 folded on the same BJD_TDB phase.
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
P = 0.1053647; c0 = SkyCoord(118.37915 * u.deg, -0.70268 * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd):
    t = Time(mjd, format="mjd", scale="utc", location=geo); return (t.tdb + t.light_travel_time(c0)).jd
d = np.genfromtxt("../data/j0753_neowise_lc.csv", delimiter=",", skip_header=1, names=True); phw = (bjd(d["mjd"]) / P) % 1; Fw = 10 ** (-0.4 * (d["w1mpro"] - 15.0))
lines = [l for l in open("../data/j0753_atlas_forcedphot_raw.txt").read().splitlines() if l.strip()]; hdr = lines[0].lstrip("#").split(); rows = [dict(zip(hdr, l.split())) for l in lines[1:]]
ok = [x for x in rows if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
med = {b: np.median([float(x["duJy"]) for x in ok if x["F"] == b]) for b in ("c", "o")}; ok = [x for x in ok if float(x["duJy"]) < 3 * med[x["F"]]]
fig, ax = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
edges = np.linspace(0, 1, 21); mids = 0.5 * (edges[1:] + edges[:-1])
def binned(ph, y, w=None):
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (ph >= lo) & (ph < hi)
        if w is None: out.append((np.median(y[m]), 1.2533 * np.std(y[m]) / np.sqrt(m.sum())))
        else: out.append((np.average(y[m], weights=w[m]), 1 / np.sqrt(np.sum(w[m]))))
    return np.array(out)
bw = binned(phw, Fw / np.median(Fw))
for k in (0, 1): ax[0].errorbar(mids + k, bw[:, 0], bw[:, 1], fmt="o-", color="tab:red", ms=4)
ax[0].set_ylabel("NEOWISE W1 flux / median"); ax[0].set_title("J0753-0042 = Gaia DR3 3082614748370926848, P = 0.1053647 d (BJD_TDB phase, same zero point)", fontsize=9)
for a, (b, fstar, col) in zip(ax[1:], (("o", 3631e6 * 10 ** (-0.4 * 19.62), "tab:orange"), ("c", 3631e6 * 10 ** (-0.4 * 20.55), "tab:cyan"))):
    s = [x for x in ok if x["F"] == b]; mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
    season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
    for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e)
    ph = (bjd(mjd[clip]) / P) % 1; bb = binned(ph, f[clip] / fstar + 1, (fstar / e[clip]) ** 2)
    for k in (0, 1): a.errorbar(mids + k, bb[:, 0], bb[:, 1], fmt="s-", color=col, ms=4)
    a.set_ylabel(f"ATLAS {b} flux / star (approx.)")
ax[2].set_xlabel("phase (P = 0.1053647 d)"); plt.tight_layout(); plt.savefig("../figures/j0753_optir.png", dpi=110); print("saved")
