"""VSX values for two eclipsing white-dwarf binaries from ATLAS forced photometry (o, c; uJy difference fluxes), 2026-09-29.
  WDJ143844.65-305148.24 = Gaia DR3 6217118886429978112 (dwarf nova; P near 0.0628990 d)
  WDJ111803.09-544218.04 = Gaia DR3 5346312514819760896 (white dwarf + M dwarf; P near 0.0938896 d)
Cleaning as for 2MASS J03531244-5502363 (docs/reports/track1_wd_binaries_2026_09_23/atlas_south/j0353_eclipse.py): duJy > 0,
err == 0, chi/N < 10, duJy < 3x the band median. For the dwarf nova, outburst nights (nightly median > 5 robust sigma above the
quiescent level) and 5 days after them are removed first. Per-season medians are subtracted, then points more than 5 robust sigma (+3 median errors) above the
level are clipped; on the faint side only points below that limit minus 600 uJy are clipped, so eclipse points survive. Times are BJD_TDB.
The eclipse centre is first located by a coarse box search over the full orbital phase (the starting epochs are not trusted).
Model per band (linear for fixed eclipse geometry): offset + first and second orbital harmonics (reflection / double hump) minus
depth x trapezoid (common centre, total width T in phase, flat fraction). Grid over period, centre, T, flat fraction; period error
from delta chi2 = 1 after scaling chi2_r to 1; centre, duration and depth errors from a bootstrap over nights (200 resamples).
Output: eclipse_fit.json and <name>_fold.png."""
import numpy as np, json, sys, os
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
H = os.path.dirname(os.path.abspath(__file__)); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
STARS = {"WDJ1438-3051": dict(gaia="6217118886429978112", ra=219.68603, dec=-30.86347, P0=1 / 15.898512, T0=2460000.52013, dn=True),
         "WDJ1118-5442": dict(gaia="5346312514819760896", ra=169.51289, dec=-54.70501, P0=1 / 10.650777, T0=2459999.47136, dn=False)}
def load(s):
    c0 = SkyCoord(s["ra"] * u.deg, s["dec"] * u.deg)
    L = [l for l in open(os.path.join(H, "atlas_raw", s["gaia"] + ".txt")).read().splitlines() if l.strip()]
    hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
    ok = [x for x in R if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
    D = {}; nout = 0
    for b in ("o", "c"):
        x = [r for r in ok if r["F"] == b]; med = np.median([float(r["duJy"]) for r in x]); x = [r for r in x if float(r["duJy"]) < 3 * med]
        mjd = np.array([float(r["MJD"]) for r in x]); f = np.array([float(r["uJy"]) for r in x]); e = np.array([float(r["duJy"]) for r in x])
        if s["dn"]:
            n = np.floor(mjd); un = np.unique(n); nm = np.array([np.median(f[n == k]) for k in un])
            q = np.median(nm); sig = 1.4826 * np.median(np.abs(nm - q)); bad = un[nm > q + 5 * max(sig, 10)]
            keep = ~np.any((mjd[:, None] >= bad[None, :]) & (mjd[:, None] <= bad[None, :] + 5), axis=1) if len(bad) else np.ones(len(mjd), bool)
            nout += int((~keep).sum()); mjd, f, e = mjd[keep], f[keep], e[keep]
        season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
        for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
        thr = 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e); clip = (f < thr) & (f > -thr - 600)  # one-sided: deep eclipse points must survive
        t = Time(mjd[clip], format="mjd", scale="utc", location=geo)
        D[b] = dict(t=(t.tdb + t.light_travel_time(c0)).jd, f=f[clip], e=e[clip])
    return D, nout
def trap(x, T, fr):
    a = np.abs(x); tf = fr * T; m = np.zeros_like(a); m[a <= tf / 2] = 1
    r = (a > tf / 2) & (a < T / 2); m[r] = (T / 2 - a[r]) / max(T / 2 - tf / 2, 1e-12); return m
def design(ph, m):
    return np.vstack([np.ones_like(ph), np.cos(2 * np.pi * ph), np.sin(2 * np.pi * ph), np.cos(4 * np.pi * ph), np.sin(4 * np.pi * ph), -m]).T
CEN = np.arange(-0.03, 0.03001, 0.001); TW = np.arange(0.012, 0.3201, 0.004); FR = (0.0, 0.25, 0.5, 0.75, 0.95)
def scan(P, Tref, data):
    """grid minimum of chi2; normal equations with the harmonic block precomputed per band"""
    best = (np.inf, None); pre = {}
    for b, d in data.items():
        ph = ((d["t"] - Tref) / P + 0.5) % 1 - 0.5; w = 1 / d["e"] ** 2; B = design(ph, np.zeros_like(ph))[:, :5]
        pre[b] = (ph, w, B, (B * w[:, None]).T @ B, (B * w[:, None]).T @ d["f"], np.sum(w * d["f"] ** 2), d["f"])
    for T in TW:
        for fr in FR:
            for c in CEN:
                chi = 0; par = {}
                for b, (ph, w, B, G, By, yy, y) in pre.items():
                    m = -trap(ph - c, T, fr); wm = w * m; Bm = B.T @ wm
                    N = np.empty((6, 6)); N[:5, :5] = G; N[:5, 5] = Bm; N[5, :5] = Bm; N[5, 5] = wm @ m
                    rhs = np.append(By, wm @ y)
                    try: coef = np.linalg.solve(N, rhs)
                    except np.linalg.LinAlgError: coef = np.linalg.lstsq(N, rhs, rcond=None)[0]
                    chi += yy - coef @ rhs; par[b] = coef
                if chi < best[0]: best = (chi, (c, T, fr, par))
    return best
out = {}
for name, s in STARS.items():
    D, nout = load(s)
    # coarse full-phase search for the eclipse centre at the starting period (the starting epoch is not trusted)
    cc = np.arange(0, 1, 0.0025); sc = []
    for c0_ in cc:
        v = 0
        for d in D.values():
            ph = ((d["t"] - s["T0"]) / s["P0"] - c0_ + 0.5) % 1 - 0.5; w = 1 / d["e"] ** 2; m = np.abs(ph) < 0.015
            v += (np.sum(d["f"][m] * w[m]) / np.sum(w[m]) - np.sum(d["f"] * w) / np.sum(w)) / (1 / np.sqrt(np.sum(w[m])))
        sc.append(v)
    c_coarse = cc[int(np.argmin(sc))]; T0c = s["T0"] + c_coarse * s["P0"]
    print(f"{name}: coarse eclipse centre at phase {c_coarse:.4f} of the starting ephemeris (significance {min(sc):.1f})", flush=True)
    Tref = T0c + round((np.median(np.concatenate([d["t"] for d in D.values()])) - T0c) / s["P0"]) * s["P0"]
    span = max(d["t"].max() for d in D.values()) - min(d["t"].min() for d in D.values())
    dP = 3 * s["P0"] ** 2 / span; Ps = s["P0"] + np.linspace(-dP, dP, 41)
    chis = np.array([scan(P, Tref, D)[0] for P in Ps]); j = int(np.argmin(chis)); n = sum(len(d["t"]) for d in D.values()); s2 = chis[j] / (n - 13)
    sl = slice(max(j - 5, 0), j + 6); a, b_, _ = np.polyfit(Ps[sl] - Ps[j], chis[sl], 2); P = Ps[j] - b_ / (2 * a); sP = np.sqrt(s2 / a)
    chi, (c, T, fr, par) = scan(P, Tref, D); T0 = Tref + c * P
    rng = np.random.default_rng(3); boot = []; nights = {b: np.floor(d["t"] - 0.3).astype(int) for b, d in D.items()}
    for it in range(200):
        bd = {}
        for b, d in D.items():
            un = np.unique(nights[b]); pick = rng.choice(un, len(un)); idx = np.concatenate([np.where(nights[b] == k)[0] for k in pick]); bd[b] = dict(t=d["t"][idx], f=d["f"][idx], e=d["e"][idx])
        _, (cb, Tb, frb, pb) = scan(P, Tref, bd); boot.append((cb, Tb, frb, pb["o"][5], pb["c"][5]))
    boot = np.array(boot); eb = boot.std(axis=0)
    r = dict(gaia=s["gaia"], P=P, sigP=sP, chi2r=s2, T0_BJD_TDB=T0, eT0_min=eb[0] * P * 1440, T0_HJD_approx=None, dur_phase=T, dur_min=T * P * 1440,
             e_dur_min=eb[1] * P * 1440, flat_fraction=fr, flat_boot=np.unique(boot[:, 2], return_counts=True)[1].tolist(),
             depth_o=par["o"][5], e_depth_o=eb[3], depth_c=par["c"][5], e_depth_c=eb[4],
             harm_o=par["o"][1:5].tolist(), harm_c=par["c"][1:5].tolist(), n_o=len(D["o"]["t"]), n_c=len(D["c"]["t"]), n_outburst_removed=nout,
             t_first=float(min(d["t"].min() for d in D.values())), t_last=float(max(d["t"].max() for d in D.values())))
    out[name] = r
    print(f"{name}: P = {P:.9f} +- {sP:.9f} d ({P*1440:.4f} min); chi2_r {s2:.2f}; T0 BJD_TDB {T0:.5f} +- {eb[0]*P*1440:.2f} min; "
          f"duration {T*P*1440:.1f} +- {eb[1]*P*1440:.1f} min ({T*100:.1f}% of P); flat {fr}; depth o {par['o'][5]:.1f}+-{eb[3]:.1f}, c {par['c'][5]:.1f}+-{eb[4]:.1f} uJy; "
          f"n o/c {r['n_o']}/{r['n_c']}; outburst points removed {nout}", flush=True)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(11, 6), gridspec_kw=dict(width_ratios=[2, 1]))
    for k, b in enumerate(("o", "c")):
        d = D[b]; ph = ((d["t"] - T0) / P + 0.5) % 1 - 0.5; w = 1 / d["e"] ** 2
        for col, (xl, nb) in enumerate(((0.5, 50), (0.12, 30))):
            ed = np.linspace(-xl, xl, nb + 1); cen = (ed[:-1] + ed[1:]) / 2; mb, er = [], []
            for i in range(nb):
                m = (ph >= ed[i]) & (ph < ed[i + 1]); mb.append(np.sum(d["f"][m] * w[m]) / np.sum(w[m]) if m.any() else np.nan); er.append(1 / np.sqrt(np.sum(w[m])) if m.any() else np.nan)
            ax = axs[k, col]; ax.errorbar(cen, mb, er, fmt="o", ms=3, color="k"); x = np.linspace(-xl, xl, 1000)
            ax.plot(x, design(x, trap(x, T, fr)) @ par[b], color="tab:red", lw=1); ax.set_xlim(-xl, xl); ax.set_xlabel("orbital phase"); ax.set_ylabel("ATLAS difference flux (uJy)")
            ax.set_title(f"{name} ATLAS {b} (n={len(d['t'])}), P = {P:.8f} d, phase 0 = BJD_TDB {T0:.5f}", fontsize=7)
    plt.tight_layout(); plt.savefig(os.path.join(H, f"{name}_fold.png"), dpi=100); plt.close()
json.dump(out, open(os.path.join(H, "eclipse_fit.json"), "w"), indent=1, default=float)
