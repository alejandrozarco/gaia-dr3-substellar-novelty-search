# Final per-candidate figure: (top) per-visit spectra, XCSAO shift undone, continuum-normalised; (middle) S/N-weighted
# visit coadd with the best centred-dipole H-in-B model (bfit_fine); (bottom) Balmer component wavelengths vs B
# (Schimeczek & Wunner database) with the visible-surface field range of the best model shaded.
import sys, json, numpy as np, pandas as pd, spec as S, bfit as BF, hfield as H
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.ndimage import gaussian_filter1d
d = pd.read_csv("master.csv", low_memory=False).drop_duplicates("sdss_id").set_index("sdss_id")
TR = H.load_balmer()
for a in sys.argv[1:]:
    sid = int(a); r = d.loc[sid]; bf = json.load(open(f"bfit_fine_{sid}.json")); gaia = int(r.gaia_dr3_source_id)
    Vall = S.load_visits(sid); V = [v for v in Vall if v["snr"] >= 8] or sorted(Vall, key=lambda v: -v["snr"])[:1]
    fig = plt.figure(figsize=(13, 11)); gs = fig.add_gridspec(3, 1, height_ratios=[1.2, 1.2, 1.4], hspace=0.08)
    a1 = fig.add_subplot(gs[0]); a2 = fig.add_subplot(gs[1], sharex=a1); a3 = fig.add_subplot(gs[2], sharex=a1)
    lam = V[0]["lam"]; num = np.zeros_like(lam); den = np.zeros_like(lam)
    for k, v in enumerate(Vall):
        cv = S.continuum(v["lam"], v["flux"], v["ivar"]); okv = (v["ivar"] > 0) & np.isfinite(cv) & (cv > 0)
        fnv = np.where(okv, v["flux"] / np.where(okv, cv, 1), np.nan)
        m = okv & (v["lam"] > 3700) & (v["lam"] < 9300)
        a1.plot(v["lam"][m], gaussian_filter1d(np.nan_to_num(fnv), 2)[m] - 0.3 * k, lw=0.5, label=f"MJD {v['mjd']} ({v['tel'][5:]}) v_xcsao {v['v']:+.0f} km/s undone, S/N {v['snr']:.0f}")
        if v in V:
            ivn = np.where(okv, v["ivar"] * cv**2, 0); w = np.interp(lam, v["lam"], okv.astype(float)) > 0.99
            num += np.interp(lam, v["lam"], np.nan_to_num(fnv)) * np.interp(lam, v["lam"], ivn) * w; den += np.interp(lam, v["lam"], ivn) * w
    fn = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)
    a1.set_ylim(1.15 - 0.3 * len(Vall) - 0.35, 1.25); a1.legend(fontsize=6.5, loc="lower right"); a1.axhline(1, color="0.8", lw=0.5)
    T = BF.templates(bf["Bp"], bf["inc"], bf["sig"], bf["teff"])
    er = np.where(den > 0, 1 / np.sqrt(np.where(den > 0, den, 1)), np.nan)
    mask = np.ones_like(lam, bool)
    for lo, hi in S.MASK: mask &= ~((lam > lo) & (lam < hi))
    fit = BF.fit(lam, fn, er, bf["teff"], Bps=[bf["Bp"]], incs=(bf["inc"],), sigs=(bf["sig"],), mask=mask)
    m = np.isfinite(fn) & (lam > 3700) & (lam < 9300)
    a2.plot(lam[m], gaussian_filter1d(np.nan_to_num(fn), 2)[m], "k", lw=0.6, label="S/N-weighted coadd of visits with S/N>=8")
    a2.plot(lam[m], fit["model"][m], "r", lw=1.0, label=f"H in centred dipole: Bp={bf['Bp']:.0f} MG, i={bf['inc']} deg (visible |B| {bf['Bp']/2:.0f}-{bf['Bp']:.0f} MG)")
    a2.set_ylim(0.6, 1.2); a2.legend(fontsize=7, loc="lower right"); a2.axhline(1, color="0.8", lw=0.5)
    for l0 in (6564.61, 4862.68, 4341.69, 4102.89):
        for ax in (a1, a2, a3): ax.axvline(l0, color="tab:blue", ls=":", lw=0.6)
    Bmax = max(3 * bf["Bp"], 60)
    fs = {}
    ser = lambda l0: min((3, 4, 5, 6), key=lambda n: abs(l0 - H.LAM_RY / (0.25 - 1 / n**2)))
    for t in TR: fs[ser(t["lam0"])] = max(fs.get(ser(t["lam0"]), 0), np.nanmax(t["f"]))
    for t in TR:
        n = ser(t["lam0"]); col = {3: "tab:red", 4: "tab:blue", 5: "tab:green", 6: "tab:orange"}[n]
        ok = np.isfinite(t["lam"]) & (t["B_MG"] <= Bmax)
        if ok.sum() < 2 or np.nanmax(t["f"][ok]) / fs[n] < 0.05: continue
        pts = np.array([t["lam"][ok], t["B_MG"][ok]]).T; segs = np.stack([pts[:-1], pts[1:]], axis=1)
        al = np.clip(np.sqrt(t["f"][ok][:-1] / fs[n]), 0.05, 1)
        a3.add_collection(LineCollection(segs, colors=[matplotlib.colors.to_rgba(col, x) for x in al], linewidths=0.9))
    a3.axhspan(bf["Bp"] / 2, bf["Bp"], color="gold", alpha=0.25, label="visible field range of best model")
    a3.set_ylim(0, Bmax); a3.set_xlim(3700, 9300); a3.set_ylabel("B [MG]"); a3.set_xlabel("vacuum wavelength [A]"); a3.legend(fontsize=7, loc="upper right")
    a1.set_title(f"Gaia DR3 {gaia} (sdss_id {sid}) | SnowWhite {r.classification} | G {r.g_mag:.2f}, M_G {r.MG:.2f}, plx {r.plx:.2f} mas | Teff_phot {bf['teff']:.0f} K", fontsize=9, loc="left")
    a3.set_title("Balmer components vs B: Schimeczek & Wunner H database (DaRUS-2118); red Ha, blue Hb, green Hg, orange Hd; alpha ~ sqrt(osc. strength)", fontsize=8, loc="left")
    plt.setp(a1.get_xticklabels(), visible=False); plt.setp(a2.get_xticklabels(), visible=False)
    plt.savefig(f"plots/FINAL_{gaia}.png", dpi=85, bbox_inches="tight"); plt.close(fig); print("ok", gaia)
