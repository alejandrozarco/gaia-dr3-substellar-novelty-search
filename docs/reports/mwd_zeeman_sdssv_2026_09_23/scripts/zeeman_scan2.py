# Zeeman test v2 on the 78 SnowWhite magnetic-probability white dwarfs (SDSS-V DR20 mwmStar spectra already in spec/).
# v1 compared a linear-Zeeman triplet with ONE Gaussian: every star (incl. ordinary DAs) preferred B ~5-8 MG, because a single Gaussian
# cannot fit a Balmer line with a narrow core AND broad wings. v2 null = core + wing (two concentric Gaussians, free widths, non-negative
# depths) per line; magnetic model = the same core+wing profile replicated as a triplet (pi 0.5 at lambda0, sigma 0.25 each at
# lambda0 -+ 4.67e-13 lambda0^2 B), B common to H-alpha and H-beta, scanned 0.2-30 MG. Metric = delta chi2 / chi2_r(best), i.e. the
# improvement in units of the best model's reduced chi2 (robust to underestimated ivar). Positive controls: the 19 SIMBAD DAH/DAP stars.
import csv, json, numpy as np, warnings
warnings.filterwarnings("ignore")
from astropy.io import fits
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows = list(csv.DictReader(open("sw_magnetic.csv"))); S = json.load(open("simbad_78.json"))
LINES = {"Ha": 6564.61, "Hb": 4862.68}; WIN = {"Ha": (6340, 6790), "Hb": (4680, 5040)}
SIG = np.array([2, 3, 4.5, 6.5, 9, 13, 18, 25, 35, 50, 70, 100.0]); SH = np.linspace(-8, 8, 17)
BGRID = np.concatenate([[0.0], np.geomspace(0.2, 30, 70)])
def load(fn):
    h = fits.open(fn); best = None
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        d = h[i].data[0]; snr = float(d["snr"])
        if best is None or snr > best[3]:
            best = (np.array(d["wavelength"], float), np.array(d["flux"], float), np.array(d["ivar"], float), snr, h[i].name)
    return best
def segment(lam, f, iv, lo, hi, core, edge):
    m = (lam > lo) & (lam < hi) & (iv > 0) & np.isfinite(f); x, y, w2 = lam[m], f[m], iv[m]
    cont = np.abs(x - core) > edge
    p = np.polyfit(x[cont], y[cont], 1, w=np.sqrt(w2[cont])); c = np.polyval(p, x)
    return x, y / c, w2 * c ** 2                     # normalised flux and inverse variance
def best_chi2(x, y, w2, l0, B):
    """min chi2 over shift, (core, wing) widths and non-negative depths for the triplet(B) core+wing profile."""
    dl = 4.67e-13 * l0 ** 2 * B * 1e6; r = 1 - y; rr = np.sum(w2 * r * r); best = (rr, None)
    comps = ((0.0, 1.0),) if B == 0 else ((0.0, 0.5), (-dl, 0.25), (dl, 0.25))
    for sh in SH:
        T = np.zeros((len(SIG), len(x)))
        for off, wt in comps: T += wt * np.exp(-0.5 * ((x[None, :] - (l0 + sh + off)) / SIG[:, None]) ** 2)
        G = (T * w2) @ T.T; bvec = (T * w2) @ r
        for i in range(len(SIG)):                       # single component
            d = bvec[i] / G[i, i]
            if d > 0:
                c = rr - d * bvec[i]
                if c < best[0]: best = (c, (sh, SIG[i], d, None, 0.0))
            for j in range(i + 1, len(SIG)):            # core + wing
                det = G[i, i] * G[j, j] - G[i, j] ** 2
                if det <= 0: continue
                d1 = (G[j, j] * bvec[i] - G[i, j] * bvec[j]) / det; d2 = (G[i, i] * bvec[j] - G[i, j] * bvec[i]) / det
                if d1 <= 0 or d2 <= 0: continue
                c = rr - d1 * bvec[i] - d2 * bvec[j]
                if c < best[0]: best = (c, (sh, SIG[i], d1, SIG[j], d2))
    return best
def profile(x, l0, B, par):
    sh, s1, d1, s2, d2 = par; dl = 4.67e-13 * l0 ** 2 * B * 1e6
    comps = ((0.0, 1.0),) if B == 0 else ((0.0, 0.5), (-dl, 0.25), (dl, 0.25)); m = np.zeros_like(x)
    for off, wt in comps:
        m += wt * d1 * np.exp(-0.5 * ((x - (l0 + sh + off)) / s1) ** 2)
        if s2 is not None: m += wt * d2 * np.exp(-0.5 * ((x - (l0 + sh + off)) / s2) ** 2)
    return 1 - m
out = []
for r in rows:
    g = r["gaia_dr3_source_id"]; lam, f, iv, snr, arm = load(f"spec/mwmStar-{r['v_astra']}-{r['sdss_id']}.fits")
    segs = {k: segment(lam, f, iv, *WIN[k], LINES[k], 190 if k == "Ha" else 150) for k in LINES}
    chis = np.array([sum(best_chi2(*segs[k], LINES[k], B)[0] for k in LINES) for B in BGRID])
    j = int(np.argmin(chis[1:])) + 1; npix = sum(len(segs[k][0]) for k in LINES)
    chir = chis[j] / (npix - 12); dchi = chis[0] - chis[j]
    sp = S.get(g, {}).get("sp_type") or ""; name = S.get(g, {}).get("main_id") or ""
    out.append(dict(gaia=g, name=name, simbad_sp=sp, sw=r["classification"], p_dah=float(r["p_dah"]), p_mwd=float(r["p_mwd"]), snr=snr, arm=arm,
                    B_MG=float(BGRID[j]), dchi2=float(dchi), chi2r_best=float(chir), chi2r_null=float(chis[0] / (npix - 11)), metric=float(dchi / max(chir, 1)),
                    chis=chis.tolist(), segs={k: [segs[k][0].tolist(), segs[k][1].tolist()] for k in LINES},
                    par0={k: best_chi2(*segs[k], LINES[k], 0.0)[1] for k in LINES}, parB={k: best_chi2(*segs[k], LINES[k], BGRID[j])[1] for k in LINES}))
    print(f"{g} {sp:6s} {r['classification']:9s} snr {snr:6.1f} B {BGRID[j]:6.2f} MG  dchi2 {dchi:9.1f}  chi2r null {chis[0]/(npix-11):6.2f} best {chir:6.2f}  metric {dchi/max(chir,1):8.1f}", flush=True)
json.dump([{k: v for k, v in o.items() if k not in ("segs",)} for o in out], open("zeeman_v2.json", "w"), indent=0, default=lambda v: None if v is None else float(v))
# grid of profile plots sorted by metric (magnetic-known flagged)
out.sort(key=lambda o: -o["metric"])
for page in range(0, len(out), 20):
    sub = out[page:page + 20]; fig, axs = plt.subplots(10, 4, figsize=(15, 26))
    for n, o in enumerate(sub):
        for c, k in enumerate(("Hb", "Ha")):
            a = axs[n // 2, (n % 2) * 2 + c]; x, y = map(np.array, o["segs"][k])
            a.plot(x, y, color="0.25", lw=0.5)
            if o["par0"][k] is not None: a.plot(x, profile(x, LINES[k], 0.0, o["par0"][k]), color="tab:blue", lw=0.9)
            if o["parB"][k] is not None: a.plot(x, profile(x, LINES[k], o["B_MG"], o["parB"][k]), color="tab:red", lw=0.9)
            known = o["simbad_sp"].startswith(("DAH", "DAP", "DBH", "DH", "DQH", "DZH", "H", "P"))
            a.set_title(f"{o['gaia']} {k} | SIMBAD {o['simbad_sp'] or '-'}{' (KNOWN MAG)' if known else ''} | SW {o['sw']} | S/N {o['snr']:.0f} | B {o['B_MG']:.1f} MG m {o['metric']:.0f}",
                        fontsize=6.5, color="tab:green" if known else "k")
            a.set_ylim(0.2, 1.3); a.tick_params(labelsize=5)
    plt.tight_layout(); plt.savefig(f"plots/grid_v2_{page//20}.png", dpi=75); plt.close()
print("done")
