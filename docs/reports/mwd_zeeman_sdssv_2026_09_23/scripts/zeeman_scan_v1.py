# SDSS-V DR20 (Astra 0.8.1 mwmStar) spectra of SnowWhite magnetic-probability white dwarfs (sw_magnetic.csv; p_dah+p_dahe+p_dbh+p_mwd > 0.3):
# download, then fit H-alpha and H-beta with (a) one Gaussian absorption (no field) and (b) a linear-Zeeman triplet (pi at lambda0, sigma at
# lambda0 +- 4.67e-13 lambda0^2 B; B scanned 0.3-40 MG, joint for both lines). Report the best B, delta-chi2 (triplet vs single) and plots.
import csv, os, subprocess, json, numpy as np, warnings
warnings.filterwarnings("ignore")
from astropy.io import fits
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
rows = list(csv.DictReader(open("sw_magnetic.csv")))
os.makedirs("spec", exist_ok=True); os.makedirs("plots", exist_ok=True)
def url(r):
    s = r["sdss_id"]; return f"https://data.sdss.org/sas/dr20/spectro/astra/{r['v_astra']}/spectra/star/{s[-4:-2]}/{s[-2:]}/mwmStar-{r['v_astra']}-{s}.fits"
def get(r):
    fn = f"spec/mwmStar-{r['v_astra']}-{r['sdss_id']}.fits"
    if not (os.path.exists(fn) and os.path.getsize(fn) > 10000):
        for k in range(3):
            subprocess.run(["curl", "-s", "--max-time", "180", "-o", fn, url(r)])
            if os.path.exists(fn) and os.path.getsize(fn) > 10000: break
    return fn if os.path.exists(fn) and os.path.getsize(fn) > 10000 else None
with ThreadPoolExecutor(max_workers=4) as ex:
    files = list(ex.map(get, rows))
print(f"downloaded {sum(f is not None for f in files)} of {len(rows)}", flush=True)
def load(fn):
    h = fits.open(fn); best = None
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        d = h[i].data[0]; hd = h[i].header
        lam = np.array(d["wavelength"], float)
        f = np.array(d["flux"], float); iv = np.array(d["ivar"], float)
        snr = float(d["snr"]) if "snr" in h[i].columns.names else 0
        if best is None or snr > best[3]: best = (lam, f, iv, snr, h[i].name)
    return best
LINES = {"Ha": 6564.61, "Hb": 4862.68}          # vacuum wavelengths (BOSS spectra are in vacuum)
WIN = {"Ha": (6380, 6760), "Hb": (4700, 5030)}
def norm(lam, f, iv, lo, hi, core):
    m = (lam > lo) & (lam < hi) & (iv > 0) & np.isfinite(f)
    x, y, w = lam[m], f[m], iv[m]
    cont = (np.abs(x - core) > 0.45 * (hi - lo) - 5)         # outer ~10% of the window on each side
    if cont.sum() < 10: return None
    p = np.polyfit(x[cont], y[cont], 1, w=np.sqrt(w[cont])); c = np.polyval(p, x)
    return x, y / c, np.sqrt(w) * c
def model(x, l0, depth, sig, B, frac_pi=0.5):
    dl = 4.67e-13 * l0 ** 2 * B * 1e6
    g = lambda mu: np.exp(-0.5 * ((x - mu) / sig) ** 2)
    if B == 0: return 1 - depth * g(l0)
    return 1 - depth * (frac_pi * g(l0) + (1 - frac_pi) / 2 * (g(l0 - dl) + g(l0 + dl)))
def fit_line(x, y, w, l0, B):
    best = (np.inf, None)
    for sig in (3, 5, 8, 12, 18, 25, 35):
        for sh in np.linspace(-6, 6, 7):
            m1 = model(x, l0 + sh, 1.0, sig, B); A = 1 - m1           # linear in depth
            dep = np.sum(w ** 2 * A * (1 - y)) / max(np.sum(w ** 2 * A ** 2), 1e-12); dep = min(max(dep, 0), 1.2)
            chi = np.sum(w ** 2 * (y - (1 - dep * A)) ** 2)
            if chi < best[0]: best = (chi, (sh, sig, dep))
    return best
results = []
for r, fn in zip(rows, files):
    if fn is None: continue
    L = load(fn)
    if L is None: continue
    lam, f, iv, snr, arm = L
    segs = {k: norm(lam, f, iv, *WIN[k], LINES[k]) for k in LINES}
    if any(v is None for v in segs.values()): continue
    Bgrid = np.concatenate([[0.0], np.geomspace(0.3, 40, 60)])
    chis = []
    for B in Bgrid:
        chis.append(sum(fit_line(*segs[k], LINES[k], B)[0] for k in LINES))
    chis = np.array(chis); j = int(np.argmin(chis[1:])) + 1
    d = chis[0] - chis[j]; npix = sum(len(segs[k][0]) for k in LINES)
    results.append(dict(gaia=r["gaia_dr3_source_id"], sw=r["classification"], p_dah=float(r["p_dah"]), snr=snr, arm=arm, B_MG=float(Bgrid[j]), dchi2=float(d), chi2_0=float(chis[0]), npix=int(npix)))
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.2))
    for a, k in zip(ax, ("Hb", "Ha")):
        x, y, w = segs[k]; a.plot(x, y, color="0.3", lw=0.7)
        for B, col in ((0.0, "tab:blue"), (Bgrid[j], "tab:red")):
            chi, (sh, sig, dep) = fit_line(x, y, w, LINES[k], B); a.plot(x, model(x, LINES[k] + sh, dep, sig, B), color=col, lw=1.2, label=f"B={B:.1f} MG")
        a.set_title(f"{k}", fontsize=8); a.legend(fontsize=6)
    fig.suptitle(f"Gaia DR3 {r['gaia_dr3_source_id']} | SnowWhite {r['classification']} p_dah {float(r['p_dah']):.2f} | {arm} S/N {snr:.0f} | best B {Bgrid[j]:.1f} MG, dchi2 {d:.0f}", fontsize=8)
    plt.tight_layout(); plt.savefig(f"plots/{r['gaia_dr3_source_id']}.png", dpi=90); plt.close()
json.dump(results, open("zeeman_results.json", "w"), indent=1)
res = sorted(results, key=lambda x: -x["dchi2"] / max(x["chi2_0"] / x["npix"], 1))
print("gaia, SnowWhite class, p_dah, S/N, best B (MG), delta chi2 (triplet vs single), chi2_0/npix")
for x in res: print(f"  {x['gaia']} {x['sw']:9s} {x['p_dah']:.2f} snr {x['snr']:6.1f} B {x['B_MG']:6.2f} dchi2 {x['dchi2']:9.1f} chi2r0 {x['chi2_0']/x['npix']:.2f}")
