"""Cross-epoch radial-velocity change of white-dwarf Balmer cores by per-spectrum line-centre fits (2026-09-30).
Replaces rv_change.py: shifting one spectrum and linearly interpolating it onto the other's pixels smooths it by an amount that
depends on the sub-pixel shift, which biased the chi^2 minimum by up to ~half a pixel (30-50 km/s; H-alpha and H-beta shifts were
uncorrelated even at S/N > 100).
Here each spectrum is fitted on its own pixels (no resampling of data): within +-W A of the line (H-alpha 6564.61, W 40; H-beta
4862.68, W 30; H-gamma 4341.69, W 22; vacuum), model = (c0 + c1 x) - A1 exp(-x^2/2 s1^2) - A2 exp(-x^2/2 s2^2), x = lambda - mu,
common centre mu (scipy least_squares, pixel errors from ivar; error on mu from the covariance scaled by sqrt(reduced chi^2) if
> 1). Line usable when A1 + A2 > 5 x its error and the fit converged with mu within 15 A of the rest wavelength.
Pairs as spec_change.py (S/N >= 8, same Gaia DR3 source in the SDSS DR17 and DESI DR1 stores; the 8 class-table Gaia ids shared by
two WDJ names are excluded). dv = c (mu_a - mu_b) / lambda0 per line; pair-kind zero points (median over pairs) are subtracted.
Output: results/rv_fit_spectra.csv (per spectrum and line), results/rv_fit_pairs.csv."""
import os, glob, numpy as np, pandas as pd
from scipy.optimize import least_squares
H = os.path.dirname(os.path.abspath(__file__)); ST = os.path.expanduser("~/claude_projects/spectra_store"); OUT = os.path.join(H, "results")
C = 299792.458; LINES = {"Ha": (6564.61, 40), "Hb": (4862.68, 30), "Hg": (4341.69, 22)}
gs = np.load(os.path.join(ST, "sdss_dr17_wd", "grid.npy")); gd = np.load(os.path.join(ST, "desi_dr1_wd", "grid.npy"))
M = pd.read_csv(os.path.join(ST, "sdss_dr17_wd", "matches.csv"), dtype={"gaia": str}).drop_duplicates("sparcl_id")
Ct = pd.read_csv(os.path.join(ST, "desi_dr1_wd", "class_table.csv"), dtype={"edr3id": str})
dup = set(Ct.groupby("edr3id").Name.nunique().loc[lambda s: s > 1].index); d2g = dict(zip(Ct.DESIID.astype(np.int64), Ct.edr3id))
cnt = pd.concat([M.gaia, Ct.edr3id]).value_counts(); multi = set(cnt[cnt >= 2].index) - dup
def model(p, x):
    mu, c0, c1, a1, s1, a2, s2 = p; d = x - mu; return c0 + c1 * d - a1 * np.exp(-d**2 / (2 * s1**2)) - a2 * np.exp(-d**2 / (2 * s2**2))
def fitline(g, f, iv, l0, W):
    m = (g > l0 - W) & (g < l0 + W) & (iv > 0) & np.isfinite(f)
    if m.sum() < 20: return None
    x, y, e = g[m], f[m].astype(float), 1 / np.sqrt(iv[m].astype(float)); c = np.median(np.r_[y[:5], y[-5:]])
    if not c > 0: return None
    y, e = y / c, e / c; j = np.argmin(np.convolve(y, np.ones(3) / 3, "same")[2:-2]) + 2
    p0 = [x[j], 1.0, 0.0, 0.3, 3.0, 0.3, W / 3]
    lo = [l0 - 15, 0.2, -1, 0, 0.5, 0, 2]; hi = [l0 + 15, 3, 1, 2, 15, 2, 3 * W]
    try: r = least_squares(lambda p: (model(p, x) - y) / e, np.clip(p0, lo, hi), bounds=(lo, hi))
    except Exception: return None
    if not r.success: return None
    dof = max(len(x) - 7, 1); red = 2 * r.cost / dof
    try: cov = np.linalg.inv(r.jac.T @ r.jac) * max(1.0, red)
    except np.linalg.LinAlgError: return None
    amp = r.x[3] + r.x[5]; ea = np.sqrt(max(cov[3, 3] + cov[5, 5] + 2 * cov[3, 5], 0))
    if not (amp > 5 * ea) or abs(r.x[0] - l0) > 14.9: return None
    return r.x[0], np.sqrt(cov[0, 0]), red, amp
rows = []
def add(lab, gg, g, f, iv, snw):
    sn = float(np.nanmedian(f[snw] * np.sqrt(np.clip(iv[snw], 0, None))))
    if not sn >= 8: return
    r = dict(gaia=gg, spec=lab, sn=sn)
    for k, (l0, W) in LINES.items():
        q = fitline(g, np.asarray(f, float), np.clip(np.asarray(iv, float), 0, None), l0, W)
        if q: r[f"mu_{k}"], r[f"e_{k}"], r[f"red_{k}"], r[f"amp_{k}"] = q
    rows.append(r)
seen = set()
for fn in sorted(glob.glob(os.path.join(ST, "sdss_dr17_wd", "chunks", "*.npz"))):
    d = np.load(fn, allow_pickle=True)
    for s_, gg, f, iv in zip(d["sparcl_id"], d["gaia"], d["f"], d["iv"]):
        gg = str(gg)
        if gg in multi and s_ not in seen: seen.add(s_); add("S:" + str(s_), gg, gs, f, iv, (gs > 4500) & (gs < 5500))
for fn in sorted(glob.glob(os.path.join(ST, "desi_dr1_wd", "chunks", "*.npz"))):
    d = np.load(fn, allow_pickle=True)
    for t, f, iv in zip(d["targetid"], d["f"], d["iv"]):
        gg = d2g.get(int(t))
        if gg in multi: add(f"D:{int(t)}", gg, gd, f, iv, (gd > 4500) & (gd < 5500))
S = pd.DataFrame(rows); S.to_csv(os.path.join(OUT, "rv_fit_spectra.csv"), index=False); print(len(S), "spectra fitted", flush=True)
pr = []
for gg, x in S.groupby("gaia"):
    x = x.sort_values("sn", ascending=False).to_dict("records")
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            a, b = x[i], x[j]; r = dict(gaia=gg, a=a["spec"], b=b["spec"], sn_a=a["sn"], sn_b=b["sn"])
            for k, (l0, W) in LINES.items():
                if np.isfinite(a.get(f"mu_{k}", np.nan)) and np.isfinite(b.get(f"mu_{k}", np.nan)):
                    r[f"v_{k}"] = C * (a[f"mu_{k}"] - b[f"mu_{k}"]) / l0; r[f"e_{k}"] = C * np.hypot(a[f"e_{k}"], b[f"e_{k}"]) / l0
            pr.append(r)
P = pd.DataFrame(pr); P["kind"] = P.a.str[0] + P.b.str[0]
for k in LINES:
    zp = P.groupby("kind")[f"v_{k}"].median(); print(k, "zero points", zp.round(1).to_dict(), flush=True)
    P[f"vc_{k}"] = P[f"v_{k}"] - P.kind.map(zp); P[f"z_{k}"] = P[f"vc_{k}"] / P[f"e_{k}"]
P.to_csv(os.path.join(OUT, "rv_fit_pairs.csv"), index=False)
b = P.dropna(subset=["vc_Ha", "vc_Hb"]); print(len(P), "pairs; both Ha+Hb:", len(b), "corr %.3f" % np.corrcoef(b.vc_Ha, b.vc_Hb)[0, 1], flush=True)
for k in LINES:
    z = P[f"z_{k}"].dropna(); print(k, "z robust scale %.2f" % (1.4826 * np.median(np.abs(z - z.median()))), flush=True)
