# J0753 (Gaia DR3 3082614748370926848): refine the period with the candidate narrow ATLAS dip, with a look-elsewhere-controlled null.
# A) W1 period uncertainty: 4-harmonic flux template with per-visit mean + amplitude scale, chi2(f) curve (errors scaled to chi2_r = 1).
# B) Joint dip scan over P within +-6 sigma_W1: for each trial P, 2-harmonic baseline per band (o, c), then box dips (centre, width)
#    with a free depth per band; score = summed delta chi2 (o + c). Fast residual-projection scan, exact refit at the maximum.
# C) Null: the identical full scan on 200 datasets with fluxes shuffled within (band, season): distribution of the maximum score.
# D) At the best solution: depth per band in 2015-2020 and 2021-2026; W1 template chi2 at the new P relative to its best.
import json, numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
P0 = 0.1053647; c0 = SkyCoord(118.37915 * u.deg, -0.70268 * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd):
    t = Time(mjd, format="mjd", scale="utc", location=geo); return (t.tdb + t.light_travel_time(c0)).jd
# ---------- A) W1 period uncertainty
d = np.genfromtxt("../data/j0753_neowise_lc.csv", delimiter=",", skip_header=1, names=True)
tw = bjd(d["mjd"]); Fw = 10 ** (-0.4 * (d["w1mpro"] - 15.0)); ew = Fw * d["w1sigmpro"] / 1.0857
o_ = np.argsort(tw); tw, Fw, ew = tw[o_], Fw[o_], ew[o_]; vis = np.cumsum(np.r_[0, np.diff(tw) > 60])
def w1chi2(P, K=4):
    ph = (tw / P) % 1; H = np.vstack([fn(2 * np.pi * k * ph) for k in range(1, K + 1) for fn in (np.cos, np.sin)]).T
    V = np.vstack([(vis == v).astype(float) for v in np.unique(vis)]).T
    X = np.hstack([V, H]); w = 1 / ew; b, *_ = np.linalg.lstsq(X * w[:, None], Fw * w, rcond=None); tm = H @ b[V.shape[1]:]
    sc = np.ones_like(Fw)
    for v in np.unique(vis):
        m = vis == v; A = np.vstack([np.ones(m.sum()), tm[m]]).T; s, *_ = np.linalg.lstsq(A * w[m][:, None], Fw[m] * w[m], rcond=None); sc[m] = max(s[1], 0.05)
    X2 = np.hstack([V, H * sc[:, None]]); b2, *_ = np.linalg.lstsq(X2 * w[:, None], Fw * w, rcond=None); r = (Fw - X2 @ b2) * w
    return float(r @ r), len(Fw) - X2.shape[1]
Pg = P0 + np.linspace(-1.5e-6, 1.5e-6, 61); cg = np.array([w1chi2(p)[0] for p in Pg]); j = int(np.argmin(cg))
dof = w1chi2(Pg[j])[1]; s2 = cg[j] / dof
a, b_, c_ = np.polyfit(Pg[max(j - 6, 0):j + 7] - Pg[j], cg[max(j - 6, 0):j + 7], 2); Pw = Pg[j] - b_ / (2 * a)
sigPw = np.sqrt(s2 / a)            # delta chi2 = 1 after scaling chi2_r to 1
print(f"W1: best P = {Pw:.8f} d, sigma = {sigPw:.2e} d (chi2_r {s2:.2f}); P0 = {P0} is {abs(P0 - Pw)/sigPw:.1f} sigma away", flush=True)
# ---------- ATLAS data
lines = [l for l in open("../data/j0753_atlas_forcedphot_raw.txt").read().splitlines() if l.strip()]; hdr = lines[0].lstrip("#").split(); rows = [dict(zip(hdr, l.split())) for l in lines[1:]]
ok = [x for x in rows if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
med = {b: np.median([float(x["duJy"]) for x in ok if x["F"] == b]) for b in ("c", "o")}; ok = [x for x in ok if float(x["duJy"]) < 3 * med[x["F"]]]
data = {}
for b in ("o", "c"):
    s = [x for x in ok if x["F"] == b]; mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
    season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
    for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e)
    data[b] = dict(mjd=mjd[clip], t=bjd(mjd[clip]), f=f[clip], e=e[clip], season=season[clip])
centres = np.linspace(0, 1, 400, endpoint=False); widths = np.array([0.015, 0.02, 0.03, 0.04, 0.06])
Pscan = Pw + np.linspace(-6, 6, 121) * sigPw
def base(ph): return np.vstack([np.ones_like(ph)] + [fn(2 * np.pi * k * ph) for k in (1, 2) for fn in (np.cos, np.sin)]).T
def scores(P, fsets):
    """Summed (o+c) best-box delta chi2 over centres x widths for trial period P; fsets = {band: (flux, error) arrays}."""
    tot = np.zeros((len(widths), len(centres)))
    for b, D in data.items():
        ph = (D["t"] / P) % 1; f, e_ = fsets[b]; w = 1 / e_
        X = base(ph); bb, *_ = np.linalg.lstsq(X * w[:, None], f * w, rcond=None); r = f - X @ bb
        o = np.argsort(ph); phs = ph[o]; y = (r * w ** 2)[o]; z = (w ** 2)[o]
        ph2 = np.concatenate([phs, phs + 1]); cy = np.concatenate([[0], np.cumsum(np.concatenate([y, y]))]); cz = np.concatenate([[0], np.cumsum(np.concatenate([z, z]))])
        for iw, wd in enumerate(widths):
            lo = np.searchsorted(ph2, centres - wd / 2 + (centres - wd / 2 < 0)); hi = np.searchsorted(ph2, centres + wd / 2 + (centres - wd / 2 < 0))
            sy = cy[hi] - cy[lo]; sz = cz[hi] - cz[lo]
            dchi = np.where((sz > 0) & (sy < 0), sy ** 2 / np.maximum(sz, 1e-12), 0.0)      # dips only (negative residual sum)
            tot[iw] += dchi
    return tot
real = np.array([scores(P, {b: (D["f"], D["e"]) for b, D in data.items()}) for P in Pscan])     # shape (nP, nw, nc)
k = np.unravel_index(np.argmax(real), real.shape); Pb, wb, cb = Pscan[k[0]], widths[k[1]], centres[k[2]]
score_P0 = scores(P0, {b: (D["f"], D["e"]) for b, D in data.items()}).max()
print(f"best joint dip: P = {Pb:.8f} d ({(Pb - Pw)/sigPw:+.1f} sigma_W1 from the W1 period), centre phase {cb:.3f}, width {wb:.3f} ({wb*Pb*1440:.1f} min), "
      f"joint delta chi2 {real.max():.1f}; at the W1 period the best joint score is {real[np.argmin(abs(Pscan - Pw))].max():.1f}; at P0 {score_P0:.1f}", flush=True)
rng = np.random.default_rng(21); null = []
for it in range(200):
    fs = {}
    for b, D in data.items():
        f = D["f"].copy(); e_ = D["e"].copy()
        for sv in np.unique(D["season"]):
            m = np.where(D["season"] == sv)[0]; pm = rng.permutation(m); f[m] = D["f"][pm]; e_[m] = D["e"][pm]    # flux and its error move together
        fs[b] = (f, e_)
    null.append(max(scores(P, fs).max() for P in Pscan[::3]))       # every third trial period (41 of 121) to keep the null tractable
null = np.array(null)
print(f"null (200 within-season shuffles, full centre/width scan, 41 trial periods): 95/99th pct {np.percentile(null,95):.1f}/{np.percentile(null,99):.1f}, max {null.max():.1f}; "
      f"p(real >= null) = {(np.sum(null >= real.max()) + 1) / (len(null) + 1):.3f}", flush=True)
# D) exact refit at the best solution: depth per band and per half
res = dict(W1_P=float(Pw), W1_sigma=float(sigPw), best_P=float(Pb), best_centre=float(cb), best_width=float(wb), joint_dchi2=float(real.max()),
           null_95=float(np.percentile(null, 95)), null_99=float(np.percentile(null, 99)), null_max=float(null.max()))
for b, D in data.items():
    fstar = 3631e6 * 10 ** (-0.4 * (19.62 if b == "o" else 20.55))
    for lab, m in (("2015-2020", D["mjd"] < 59215), ("2021-2026", D["mjd"] >= 59215), ("all", np.ones(len(D["f"]), bool))):
        ph = (D["t"][m] / Pb) % 1; w = 1 / D["e"][m]; box = (np.abs(((ph - cb + 0.5) % 1) - 0.5) < wb / 2).astype(float)
        X = np.hstack([base(ph), -box[:, None]]); bb, *_ = np.linalg.lstsq(X * w[:, None], D["f"][m] * w, rcond=None)
        C = np.linalg.inv((X * w[:, None]).T @ (X * w[:, None])); r = (D["f"][m] - X @ bb) * w; sc = np.sqrt(max(r @ r / max(m.sum() - X.shape[1], 1), 1))
        print(f"   {b} {lab}: depth {bb[-1]:.1f} +- {np.sqrt(C[-1,-1])*sc:.1f} uJy ({bb[-1]/fstar:.2f} of star), n in dip {int(box.sum())}")
        res[f"{b}_{lab}"] = [float(bb[-1]), float(np.sqrt(C[-1, -1]) * sc), int(box.sum())]
cW = w1chi2(Pb)[0]
print(f"W1 template chi2 at the dip period: {cW:.1f} vs {cg[j]:.1f} at the W1 best (delta {cW - cg[j]:.1f}; scaled {(cW - cg[j]) / s2:.1f})")
res["W1_dchi2_scaled_at_bestP"] = float((cW - cg[j]) / s2)
# ephemeris of the dip (BJD_TDB of a dip centre near the middle of the ATLAS data)
tmid = np.median(np.concatenate([D["t"] for D in data.values()])); E = np.round(tmid / Pb - cb); T0 = (E + cb) * Pb
res["T0_dip_BJD_TDB"] = float(T0); print(f"dip ephemeris: BJD_TDB {T0:.5f} + {Pb:.8f} E")
json.dump(res, open("../data/j0753_dip_refine.json", "w"), indent=1)
