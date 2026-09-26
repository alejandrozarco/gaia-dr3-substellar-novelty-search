# 3eRASS J035311.8-550237 = Gaia DR3 4731701084150029824 (110 pc, G 18.37, BP-RP 2.82): ATLAS o and c folds at 0.0739348 d show a
# narrow dip at the same phase in both bands. (1) Joint box-dip scan over period (0.0739348 d +- 3e-5 d), centre and width with a free
# depth per band; (2) permutation null (flux+error pairs shuffled within band and season) of the joint maximum over the same scan;
# (3) half and double period checks; (4) depth per band and per half of the data; ephemeris (BJD_TDB of mid-dip).
import numpy as np, json
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
geo = EarthLocation.from_geocentric(0, 0, 0, unit="m"); c0 = SkyCoord(58.30184 * u.deg, -55.04399 * u.deg)
L = [l for l in open("atlas_raw/4731701084150029824.txt").read().splitlines() if l.strip()]; hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
ok = [x for x in R if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
D = {}
for b in ("o", "c"):
    s = [x for x in ok if x["F"] == b]; med = np.median([float(x["duJy"]) for x in s]); s = [x for x in s if float(x["duJy"]) < 3 * med]
    mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
    season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
    for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e)
    t = Time(mjd[clip], format="mjd", scale="utc", location=geo); D[b] = dict(t=(t.tdb + t.light_travel_time(c0)).jd, f=f[clip], e=e[clip], sv=season[clip], mjd=mjd[clip])
P0 = 0.0739348; centres = np.linspace(0, 1, 300, endpoint=False); widths = np.array([0.02, 0.03, 0.04, 0.06, 0.08])
def score(P, fl):
    tot = np.zeros((len(widths), len(centres)))
    for b, d in D.items():
        f, e = fl[b]; w2 = 1 / e ** 2; ph = (d["t"] / P) % 1; r = f - np.sum(f * w2) / np.sum(w2)
        o = np.argsort(ph); phs = ph[o]; y = (r * w2)[o]; z = w2[o]
        ph2 = np.concatenate([phs, phs + 1]); cy = np.concatenate([[0], np.cumsum(np.concatenate([y, y]))]); cz = np.concatenate([[0], np.cumsum(np.concatenate([z, z]))])
        for iw, wd in enumerate(widths):
            lo = np.searchsorted(ph2, centres - wd / 2 + (centres - wd / 2 < 0)); hi = np.searchsorted(ph2, centres + wd / 2 + (centres - wd / 2 < 0))
            sy = cy[hi] - cy[lo]; sz = cz[hi] - cz[lo]; tot[iw] += np.where((sz > 0) & (sy < 0), sy ** 2 / np.maximum(sz, 1e-12), 0)
    return tot
Ps = P0 + np.linspace(-3e-5, 3e-5, 121); real = np.array([score(P, {b: (d["f"], d["e"]) for b, d in D.items()}) for P in Ps])
k = np.unravel_index(np.argmax(real), real.shape); Pb, wb, cb = Ps[k[0]], widths[k[1]], centres[k[2]]
print(f"joint box: P {Pb:.8f} d ({Pb*24:.4f} h), centre {cb:.3f}, width {wb} ({wb*Pb*1440:.1f} min), delta chi2 {real.max():.1f}")
for lab, Pt in (("P/2", Pb / 2), ("2P", 2 * Pb)):
    sc = score(Pt, {b: (d["f"], d["e"]) for b, d in D.items()}); print(f"   at {lab}: best joint delta chi2 {sc.max():.1f}")
rng = np.random.default_rng(11); null = []
for it in range(100):
    fl = {}
    for b, d in D.items():
        f, e = d["f"].copy(), d["e"].copy()
        for s in np.unique(d["sv"]):
            m = np.where(d["sv"] == s)[0]; pm = rng.permutation(m); f[m] = d["f"][pm]; e[m] = d["e"][pm]
        fl[b] = (f, e)
    null.append(max(score(P, fl).max() for P in Ps[::6]))
null = np.array(null); print(f"null (100 shuffles, 21 trial periods, full centre/width scan): 95th {np.percentile(null,95):.1f}, max {null.max():.1f}; p = {(np.sum(null >= real.max()) + 1)/101:.3f}")
res = dict(P=float(Pb), centre=float(cb), width=float(wb), dchi2=float(real.max()), null95=float(np.percentile(null, 95)), nullmax=float(null.max()))
for b, d in D.items():
    for lab, m in (("all", np.ones(len(d["t"]), bool)), ("first half", d["mjd"] < np.median(d["mjd"])), ("second half", d["mjd"] >= np.median(d["mjd"]))):
        ph = (d["t"][m] / Pb) % 1; inb = np.abs(((ph - cb + 0.5) % 1) - 0.5) < wb / 2; w = 1 / d["e"][m] ** 2
        dep = np.sum(d["f"][m][inb] * w[inb]) / np.sum(w[inb]) - np.sum(d["f"][m][~inb] * w[~inb]) / np.sum(w[~inb]); err = 1 / np.sqrt(np.sum(w[inb]))
        print(f"   {b} {lab}: dip depth {dep:.1f} +- {err:.1f} uJy, n in dip {inb.sum()}"); res[f"{b}_{lab}"] = [float(dep), float(err), int(inb.sum())]
tmid = np.median(np.concatenate([d["t"] for d in D.values()])); E = np.round(tmid / Pb - cb); T0 = (E + cb) * Pb
print(f"ephemeris: BJD_TDB {T0:.5f} + {Pb:.8f} E"); res["T0"] = float(T0)
json.dump(res, open("j0353_eclipse.json", "w"), indent=1)
