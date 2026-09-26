# Run the crude field estimator (bfit.py) on a list of stars. Uses the observed-frame visit coadd (XCSAO shift undone per
# visit) when a mwmVisit file exists, else the mwmStar coadd. usage: python run_bfit.py <tag> sid[:teff[:label]] ...
import sys, os, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import spec as S, bfit as BF
d = pd.read_csv("master.csv", low_memory=False).drop_duplicates("sdss_id").set_index("sdss_id")
tag = sys.argv[1]; res = {}
MASKW = S.MASK
for arg in sys.argv[2:]:
    p = arg.split(":"); sid = int(p[0])
    teff = float(p[1]) if len(p) > 1 and p[1] else float(d.loc[sid].teff_phot) if sid in d.index else 10000.0
    label = p[2] if len(p) > 2 else ""
    src = "visits" if os.path.exists(f"spec/mwmVisit-0.8.1-{sid}.fits") and "star" not in p[3:] else "mwmStar"
    if src == "visits":
        # per-visit continuum normalisation (XCSAO shift undone), then S/N^2-weighted mean of the normalised spectra;
        # visits with S/N < 8 are dropped (v2 of the coadd, 2026-09-24: v1 flux-averaged all S/N>=3 visits and let a
        # S/N 3.6 visit with sky residuals dominate the red end)
        V = [v for v in S.load_visits(sid) if v["snr"] >= 8]
        if not V: V = sorted(S.load_visits(sid), key=lambda v: -v["snr"])[:1]
        lam = V[0]["lam"]; num = np.zeros_like(lam); den = np.zeros_like(lam)
        for v in V:
            cv = S.continuum(v["lam"], v["flux"], v["ivar"])
            okv = (v["ivar"] > 0) & np.isfinite(cv) & (cv > 0)
            fnv = np.where(okv, v["flux"] / np.where(okv, cv, 1), 0.0); ivn = np.where(okv, v["ivar"] * cv**2, 0.0)
            f = np.interp(lam, v["lam"], fnv); iv = np.interp(lam, v["lam"], ivn) * (np.interp(lam, v["lam"], okv.astype(float)) > 0.99)
            num += f * iv; den += iv
        fn = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan); er = np.where(den > 0, 1 / np.sqrt(np.where(den > 0, den, 1)), np.nan)
        flux, ivar = fn, den
    else:
        if not os.path.exists(f"spec/mwmStar-0.8.1-{sid}.fits"):
            os.symlink(f"/tmp/mwd/spec/mwmStar-0.8.1-{sid}.fits", f"spec/mwmStar-0.8.1-{sid}.fits")
        s = S.load_star(sid); lam, flux, ivar = s["lam"], s["flux"], s["ivar"]
        c = S.continuum(lam, flux, ivar)
        ok = (ivar > 0) & np.isfinite(c) & (c > 0)
        fn = np.where(ok, flux / c, np.nan); er = np.where(ok, 1 / np.sqrt(np.where(ivar > 0, ivar, 1)) / c, np.nan)
    mask = np.ones_like(lam, bool)
    for a, b in MASKW: mask &= ~((lam > a) & (lam < b))
    r = BF.fit(lam, fn, er, teff, mask=mask)
    gmin = np.nanmin(r["grid"], axis=(1, 2))
    dchi = gmin - r["chi2"]
    scale = max(r["chi2"] / r["npix"], 1.0)           # rescale errors so that chi2_red(best) = 1 (the model is crude)
    rng = r["Bps"][dchi / scale < 9]                   # crude acceptable range: rescaled delta chi2 < 9
    lowB = np.nanmin(gmin[r["Bps"] < 3.0]); highB = np.nanmin(gmin[r["Bps"] > 10.0])
    d_low_high = (lowB - highB) / scale                 # >0: a >10 MG field fits better than any <3 MG (line-broadening) solution
    res[sid] = dict(label=label, teff=teff, src=src, Bp=r["Bp"], inc=r["inc"], sig=r["sig"], A=[float(x) for x in r["A"]],
                    chi2=r["chi2"], chi2_nofield=r["chi2_nofield"], npix=r["npix"], Bp_range=[float(rng.min()), float(rng.max())], chi2_scale=scale,
                    dchi2_nofield_rescaled=float((r["chi2_nofield"] - r["chi2"]) / scale), dchi2_low_minus_high=float(d_low_high))
    print(f"{sid} {label:28s} Teff {teff:6.0f} src {src:7s} best Bp {r['Bp']:7.1f} MG inc {r['inc']:2d} sig {r['sig']:2d} | chi2 {r['chi2']:.0f} vs no-field {r['chi2_nofield']:.0f} "
          f"(npix {r['npix']}) | range(resc.dchi2<9) {rng.min():.1f}-{rng.max():.1f} MG | no-field worse by {(r['chi2_nofield'] - r['chi2']) / scale:.0f} | B<3 minus B>10: {d_low_high:+.0f} (rescaled) | A={np.round(r['A'], 3)}", flush=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(13, 7), gridspec_kw=dict(height_ratios=[2, 1]))
    m = np.isfinite(fn) & (lam > 3700) & (lam < 9300)
    a1.plot(lam[m], gaussian_filter1d(np.nan_to_num(fn), 2)[m], "k", lw=0.5, label="data (continuum-normalised)")
    a1.plot(lam[m], r["model"][m], "r", lw=0.9, label=f"H-in-B model: centred dipole Bp={r['Bp']:.0f} MG, i={r['inc']} deg, sigma={r['sig']} A")
    for l0 in (6564.61, 4862.68, 4341.69, 4102.89): a1.axvline(l0, color="tab:blue", ls=":", lw=0.6)
    a1.set_ylim(0.4, 1.25); a1.legend(fontsize=7, loc="lower right")
    a1.set_title(f"{sid} {label} | Teff {teff:.0f} K | chi2 {r['chi2']:.0f} (no field: {r['chi2_nofield']:.0f}, npix {r['npix']})", fontsize=9, loc="left")
    for k, inc in enumerate(r["incs"]):
        a2.plot(r["Bps"], np.nanmin(r["grid"][:, k, :], axis=1) - r["chi2"], label=f"i={inc}")
    a2.set_xscale("log"); a2.set_ylim(-5, max(200, 0.3 * (r["chi2_nofield"] - r["chi2"]))); a2.axhline(9 * scale, color="0.6", ls="--")
    a2.set_xlabel("polar field Bp [MG]"); a2.set_ylabel("chi2 - chi2_min"); a2.legend(fontsize=7)
    plt.tight_layout(); plt.savefig(f"plots/bfit_{tag}_{sid}.png", dpi=80); plt.close(fig)
json.dump(res, open(f"bfit_{tag}.json", "w"), indent=1)
