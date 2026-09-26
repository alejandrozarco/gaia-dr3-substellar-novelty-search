"""Fit TMAP H+He NLTE model spectra (TheoSSA, normalised-flux column) to SDSS-V coadds of hot white dwarfs.
Lines and windows (vacuum A, +-W): H-delta 4102.9 (35), H-gamma+He II 4341.7 (35), He II 4542.8 (20), He II 4687.0 (25), H-beta+He II
4862.7 (40), He II 5413.0 (25), H-alpha+He II 6564.6 (40). Model: normalised flux convolved with a Gaussian of FWHM = lambda/1800,
shifted by v (grid -150..+150 km/s, 10 km/s; one v per star); the observed spectrum in each window is fitted as (a + b x) * model
(linear least squares), chi2 summed over windows. Grid: Teff 60-200 kK, log g 6.5-8.0, He mass fraction 0-1 (subset). The model
wavelength scale is taken as given (TMAP); a free velocity absorbs any air/vacuum offset (about 80 km/s near 6500 A).
python fit_hot.py <sdss_id> ...  -> fit_hot.csv (appended), best-fit plots fit_<sdss_id>.png"""
import sys, os, glob, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import gaussian_filter1d
C = 299792.458; VS = np.arange(-150, 151, 10.0)
SETS = {"all": [(4027.3, 15), (4102.9, 60), (4341.7, 60), (4472.7, 15), (4542.8, 20), (4687.0, 35), (4862.7, 70), (4923.3, 12), (5413.0, 30), (5877.3, 20), (6564.6, 60)],
        "he": [(4027.3, 15), (4472.7, 15), (4542.8, 20), (4687.0, 35), (4923.3, 12), (5413.0, 30), (5877.3, 20)]}
LINES = SETS[os.environ.get("LINESET", "all")]
def load_models():
    import pickle
    if os.path.exists("/tmp/hotdq/hottest/models_cache_vac.pkl"):
        return pickle.load(open("/tmp/hotdq/hottest/models_cache_vac.pkl", "rb"))
    M = []
    for f in sorted(glob.glob("/tmp/hotdq/hottest/theossa/models/*.txt")):
        if os.path.getsize(f) < 100000: continue
        hd = {}
        with open(f) as fh: first = fh.readline()
        if first.startswith("<?xml"):
            # some grid points are served only as VOTable (same columns: wavelength, flux, normalised flux)
            from astropy.io.votable import parse; import warnings; warnings.filterwarnings("ignore"); v = parse(f)
            pv = {p.name: p.value for p in v.iter_fields_and_params() if getattr(p, "value", None) is not None}
            hd = {"Teff": pv["t_eff"], "logg": pv["log_g"], "Mass.Fraction.H": pv["w_H"], "Mass.Fraction.HE": 1 - float(pv["w_H"])}
            t = v.get_first_table().to_table(); w, n = np.asarray(t["spectral"], float), np.asarray(t["flux_norm"], float)
        else:
            with open(f) as fh:
                for line in fh:
                    if line.startswith("*"):
                        if "=" in line: k, v = line[1:].strip().split("=", 1); hd[k.strip()] = v.strip()
                        continue
                    break
            d = np.loadtxt(f, comments="*", usecols=(0, 2)); w, n = d[:, 0], d[:, 1]
        keep = (w > 3900) & (w < 6800); w, n = w[keep], n[keep]
        s2 = (1e4 / w) ** 2; w = w * (1 + 0.0000834254 + 0.02406147 / (130 - s2) + 0.00015998 / (38.9 - s2))  # air -> vacuum (Morton 2000)
        # convolve to R ~ 1800 on a log grid
        lg = np.arange(np.log(w[0]), np.log(w[-1]), 2e-5); nn = np.interp(lg, np.log(w), n); sig = (1 / 1800 / 2.355) / 2e-5
        M.append(dict(teff=float(hd["Teff"]), logg=float(hd["logg"]), XH=float(hd["Mass.Fraction.H"]), XHe=float(hd["Mass.Fraction.HE"]), lg=lg, n=gaussian_filter1d(nn, sig)))
    pickle.dump(M, open("/tmp/hotdq/hottest/models_cache_vac.pkl", "wb"))
    return M
def obs(sid):
    vs = sdssv.visits(sid); vs = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(vs)[:3]; return w, f, iv
def chi2(w, f, iv, m, v):
    tot, n = 0.0, 0; lw = np.log(w / (1 + v / C))
    for l, hw in LINES:
        s = (np.abs(w - l) < hw) & (iv > 0) & np.isfinite(f)
        if s.sum() < 10: continue
        mod = np.interp(lw[s], m["lg"], m["n"]); x = (w[s] - l) / hw; A = np.vstack([mod, mod * x]).T * np.sqrt(iv[s])[:, None]
        coef, *_ = np.linalg.lstsq(A, f[s] * np.sqrt(iv[s]), rcond=None); r = f[s] * np.sqrt(iv[s]) - A @ coef; tot += float(r @ r); n += int(s.sum())
    return tot, n
if __name__ == "__main__":
    M = load_models(); print(len(M), "models", flush=True); rows = []
    for sid in sys.argv[1:]:
        w, f, iv = obs(sid)
        # velocity from the best model at a coarse pass
        best = (np.inf, None, 0); pre = sorted(M, key=lambda m: chi2(w, f, iv, m, 0.0)[0])[:20]
        for m in pre:
            for v in VS:
                c, n = chi2(w, f, iv, m, v)
                if c < best[0]: best = (c, m, v)
        v0 = best[2]; res = []
        for m in M:
            c, n = chi2(w, f, iv, m, v0); res.append((c, n, m))
        res.sort(key=lambda x: x[0]); c0, n0, m0 = res[0]; s = c0 / n0
        ok = [r for r in res if r[0] <= c0 + max(s, 1) * 6.0]  # ~95% region for 3 parameters, chi2 rescaled
        T = [r[2]["teff"] for r in ok]; G = [r[2]["logg"] for r in ok]; He = [r[2]["XHe"] for r in ok]
        rows.append(dict(lineset=os.environ.get("LINESET", "all"), sdss_id=sid, teff=m0["teff"], teff_lo=min(T), teff_hi=max(T), logg=m0["logg"], logg_lo=min(G), logg_hi=max(G), XHe=round(m0["XHe"], 2),
                         XHe_lo=round(min(He), 2), XHe_hi=round(max(He), 2), v=v0, chi2r=round(s, 2)))
        print(rows[-1], flush=True)
        fig, ax = plt.subplots(1, len(LINES), figsize=(2.2 * len(LINES), 3))
        lw = np.log(w / (1 + v0 / C))
        for a, (l, hw) in zip(ax, LINES):
            sl = (np.abs(w - l) < hw) & (iv > 0)
            if sl.sum() < 10: continue
            mod = np.interp(lw[sl], m0["lg"], m0["n"]); x = (w[sl] - l) / hw; A = np.vstack([mod, mod * x]).T; coef, *_ = np.linalg.lstsq(A * np.sqrt(iv[sl])[:, None], f[sl] * np.sqrt(iv[sl]), rcond=None)
            cont = coef[0] + coef[1] * x; a.plot(w[sl], f[sl] / cont, "k", lw=.7); a.plot(w[sl], mod, "r", lw=.8); a.set_title(f"{l:.0f}", fontsize=8)
        fig.suptitle(f"{sid}: Teff {m0['teff']:.0f} logg {m0['logg']} X(He) {m0['XHe']:.2f}", fontsize=9); plt.tight_layout(); plt.savefig(f"/tmp/hotdq/hottest/fit_{os.environ.get('LINESET', 'all')}_{sid}.png", dpi=70); plt.close()
    pd.DataFrame(rows).to_csv("fit_hot.csv", mode="a", header=not os.path.exists("/tmp/hotdq/hottest/fit_hot.csv"), index=False)
