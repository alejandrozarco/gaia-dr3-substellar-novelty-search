"""ATLAS check of Gaia DR3 eclipsing-binary white-dwarf candidates: broad LS (0.05-50 c/d) of difference flux / Gaia G flux,
peaks near the Gaia frequency f, 2f and f/2; fold at the best of these, binned light curve, eclipse depth (fraction of G flux)."""
import sys, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.timeseries import LombScargle
import astropy.units as u
GEO = EarthLocation.from_geocentric(0, 0, 0, unit="m")
T = {"5310197547872256512": (138.80583, -55.31969, 17.1005, 1.0821237), "6216651490910555008": (218.05892, -31.53522, 18.1753, 2.6941795),
     "6645284902019884928": (294.16388, -52.76669, 17.9746, 2.1015431), "4263036176971760768": (288.64126, -1.12491, 19.0440, 4.7878588)}
for sid, (ra, dec, G, fg) in T.items():
    REF = 3631e6 * 10 ** (-0.4 * G)
    L = [l for l in open(f"atlas_{sid}.txt").read().splitlines() if l.strip()]; hdr = L[0].lstrip("#").split()
    R = pd.DataFrame([dict(zip(hdr, l.split())) for l in L[1:]])
    for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
    R = R[(R.duJy > 0) & (R.err == 0) & (R["chi/N"] < 10)]
    parts = []
    for b, g in R.groupby("F"):
        g = g.copy(); g["season"] = np.floor((g.MJD - 57000) / 365.25)
        for s, h in g.groupby("season"):
            if len(h) < 20: continue
            y = (h.uJy - np.median(h.uJy)) / REF; e = h.duJy / REF
            mad = 1.4826 * np.median(np.abs(y - np.median(y))); k = np.abs(y - np.median(y)) < 8 * mad
            parts.append(pd.DataFrame(dict(t=h.MJD[k], y=y[k], e=e[k], F=b)))
    d = pd.concat(parts); tt = Time(d.t.values + 2400000.5, format="jd", scale="utc", location=GEO)
    d["bjd"] = (tt.tdb + tt.light_travel_time(SkyCoord(ra * u.deg, dec * u.deg), kind="barycentric")).jd
    fr = np.arange(0.05, 50, 0.1 / (d.bjd.max() - d.bjd.min())); ls = LombScargle(d.bjd, d.y, d.e); p = ls.power(fr, method="fast")
    top = fr[np.argmax(p)]; fap = ls.false_alarm_probability(p.max(), minimum_frequency=0.05, maximum_frequency=50, method="baluev")
    best = None
    for mult in (0.5, 1, 2):
        f0 = fg * mult; ff = np.linspace(f0 - 0.002, f0 + 0.002, 801); pp = ls.power(ff); k = np.argmax(pp)
        fa = ls.false_alarm_probability(pp[k], minimum_frequency=0.05, maximum_frequency=50, method="baluev")
        print(f"{sid} near {mult}f_gaia: f {ff[k]:.6f} power {pp[k]:.4f} FAP {fa:.1e}")
        if best is None or pp[k] > best[1]: best = (ff[k], pp[k], mult)
    print(f"{sid}: n {len(d)}, rms {100*np.std(d.y):.1f}%, median err {100*np.median(d.e):.1f}%; global top {top:.5f} c/d (FAP {fap:.1e}); Gaia f {fg:.6f}")
    # fold at the EB period: for eclipsing, use the Gaia frequency as orbital (two-Gaussian/one-Gaussian models are orbital)
    forb = fg if best[2] != 2 else fg
    ph = ((d.bjd - d.bjd.min()) * forb) % 1
    bins = np.linspace(0, 1, 51); idx = np.digitize(ph, bins) - 1
    med = np.array([np.median(d.y[idx == i]) if (idx == i).sum() > 5 else np.nan for i in range(50)])
    print(f"   folded at Gaia f: binned min {100*np.nanmin(med):.1f}% at phase {bins[np.nanargmin(med)]:.2f}, max {100*np.nanmax(med):.1f}%, n per bin ~{len(d)//50}")
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
    ax[0].plot(fr, p, lw=0.4); [ax[0].axvline(fg * m, color="r", ls=":") for m in (0.5, 1, 2)]; ax[0].set_xlim(0, 12); ax[0].set_xlabel("c/d")
    ax[1].plot(ph, d.y, ".", ms=1, alpha=0.3); ax[1].plot(bins[:-1] + 0.01, med, "k-"); ax[1].set_ylim(-0.6, 0.4); ax[1].set_xlabel(f"phase at Gaia f={fg:.5f}")
    fig.suptitle(f"Gaia DR3 {sid} ATLAS"); fig.tight_layout(); fig.savefig(f"eb_{sid}.png", dpi=80)
