"""Per-exposure radial velocities of SDSS-V DR20 low-mass DA white dwarfs from the BOSS spec-full files (run2d v6_2_1,
spectra/daily/full; independent of the Astra XCSAO velocities).
Sample (sample.csv): SnowWhite class starting with DA (no MS/CV/QSO/STAR), S/N >= 10, 5 < log g < 7.6, 7 kK < Teff < 40 kK.
Visits (visits.csv): spAll rows (field, mjd, catalogid) for the sample's sdss_id.
Per object: template = inverse-variance coadd of the COADD extensions of all its visits on a log-wavelength grid; for each exposure
extension (MJD_EXP_*), velocities of H-alpha, H-beta and H-gamma against the template (linear continuum at 2500-3500 km/s,
chi2 over |v| < 1500 km/s, shifts -700..+700 km/s in 5 km/s steps with parabola refinement); consensus = mean of the lines within
max(3 sigma, 40 km/s) of their median (at least two lines); error = max(scatter/sqrt(n), median error/sqrt(n), 8 km/s).
Exposure mid-time = TAI-BEG + EXPTIME/2 (MJD). Summary per object: number of exposures with a consensus velocity, weighted mean,
chi2 and reduced chi2 about the mean, largest pairwise difference and its significance.
python dwd_sweep.py <sample.csv> <visits.csv> <out_dir> [n_workers]"""
import os, sys, tempfile, subprocess, numpy as np, pandas as pd
from astropy.io import fits
from concurrent.futures import ThreadPoolExecutor
C = 299792.458; LINES = {"Ha": 6564.61, "Hb": 4862.68, "Hg": 4341.69}; S = np.arange(-700, 701, 5.0)
BASE = "https://data.sdss.org/sas/dr20/spectro/boss/redux/v6_2_1/spectra/daily/full"
def seg(w, f, iv, l):
    v = (w / l - 1) * C; m = (np.abs(v) < 3500) & (iv > 0) & np.isfinite(f); v, f, iv = v[m], f[m], iv[m]; c = np.abs(v) > 2500
    if c.sum() < 6: return None
    p = np.polyfit(v[c], f[c], 1, w=np.sqrt(iv[c])); cc = np.polyval(p, v)
    return (v, f / cc, iv * cc ** 2) if np.median(cc) > 0 else None
def one(sid, V, out):
    tmp = tempfile.mkdtemp(dir=os.path.join(out, "tmp")); files = []
    try:
        for _, r in V.iterrows():
            f = f"{int(r.field):06d}"; name = f"spec-{f}-{int(r.mjd)}-{int(r.catalogid)}.fits"; p = os.path.join(tmp, name)
            subprocess.run(["curl", "-s", "-m", "300", "-o", p, f"{BASE}/{f[:3]}XXX/{f}/{int(r.mjd)}/{name}"])
            if os.path.exists(p) and os.path.getsize(p) > 10000: files.append((r, p))
        if not files: return [], dict(sdss_id=sid, status="no files")
        grid = 10 ** np.arange(np.log10(3600), np.log10(10300), 1e-4); num = np.zeros_like(grid); den = np.zeros_like(grid); hdus = []
        for r, p in files:
            h = fits.open(p); hdus.append((r, h)); d = h["COADD"].data; w = 10 ** d["LOGLAM"]; iv = d["IVAR"] * (d["AND_MASK"] == 0)
            fi = np.interp(grid, w, d["FLUX"], left=np.nan, right=np.nan); ii = np.interp(grid, w, iv, left=0, right=0); ok = np.isfinite(fi) & (ii > 0)
            num[ok] += fi[ok] * ii[ok]; den[ok] += ii[ok]
        tf = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan); T = {n: seg(grid, tf, den, l) for n, l in LINES.items()}
        rows = []
        for r, h in hdus:
            for x in h:
                if not x.name.startswith("MJD_EXP"): continue
                d = x.data; w = 10 ** d["LOGLAM"]; iv = d["IVAR"] * (d["AND_MASK"] == 0); t = (x.header["TAI-BEG"] + x.header["EXPTIME"] / 2) / 86400
                res = {}
                for n, l in LINES.items():
                    if T[n] is None: continue
                    X = seg(w, d["FLUX"], iv, l)
                    if X is None: continue
                    xv, xf, xi = X; m = np.abs(xv) < 1500
                    if m.sum() < 20: continue
                    tv, tfl, _ = T[n]; chi = np.array([np.sum((xf[m] - np.interp(xv[m] - s, tv, tfl)) ** 2 * xi[m]) for s in S]); i = int(np.argmin(chi))
                    if 0 < i < len(S) - 1:
                        a, b, _ = np.polyfit(S[i - 1:i + 2], chi[i - 1:i + 2], 2)
                        if a > 0: res[n] = (-b / (2 * a), np.sqrt(max(chi[i] / (m.sum() - 1), 1) / a))
                vals = [(v, e) for v, e in res.values() if np.isfinite(v)]; cons, ce, nl = np.nan, np.nan, 0
                if len(vals) >= 2:
                    med = np.median([v for v, _ in vals]); ok = np.array([(v, e) for v, e in vals if abs(v - med) <= max(3 * e, 40)])
                    if len(ok) >= 2:
                        nl = len(ok); cons = ok[:, 0].mean(); ce = max(ok[:, 0].std(ddof=1) / np.sqrt(nl), np.median(ok[:, 1]) / np.sqrt(nl), 8)
                rows.append(dict(sdss_id=sid, field=int(r.field), mjd=int(r.mjd), exp=x.name, mjd_mid=round(t, 5), **{f"v_{n}": round(v, 1) for n, (v, e) in res.items()},
                                 **{f"e_{n}": round(e, 1) for n, (v, e) in res.items()}, v=round(cons, 1) if np.isfinite(cons) else np.nan, e=round(ce, 1) if np.isfinite(ce) else np.nan, n_lines=nl))
            h.close()
        g = pd.DataFrame(rows); g = g[np.isfinite(g.v)] if len(g) else g; summ = dict(sdss_id=sid, status="ok", n_files=len(files), n_exp=len(g))
        if len(g) >= 2:
            wts = 1 / g.e ** 2; mu = np.sum(wts * g.v) / wts.sum(); chi2 = float(np.sum(((g.v - mu) / g.e) ** 2))
            vv, ee = g.v.values, g.e.values; dv = np.abs(vv[:, None] - vv[None, :]); sg = dv / np.sqrt(ee[:, None] ** 2 + ee[None, :] ** 2)
            summ.update(v_mean=round(mu, 1), chi2=round(chi2, 1), chi2r=round(chi2 / (len(g) - 1), 2), dv_max=round(float(dv.max()), 1), sig_max=round(float(sg.max()), 1),
                        span_d=round(float(g.mjd_mid.max() - g.mjd_mid.min()), 3))
        return rows, summ
    except Exception as e:
        return [], dict(sdss_id=sid, status=f"error {str(e)[:80]}")
    finally:
        subprocess.run(["rm", "-rf", tmp])
if __name__ == "__main__":
    S_ = pd.read_csv(sys.argv[1], dtype={"sdss_id": str}); V = pd.read_csv(sys.argv[2], dtype={"sdss_id": str}); out = sys.argv[3]; nw = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    os.makedirs(os.path.join(out, "tmp"), exist_ok=True); fs, fe = os.path.join(out, "summary.csv"), os.path.join(out, "exposures.csv")
    done = set(pd.read_csv(fs, dtype={"sdss_id": str}).sdss_id) if os.path.exists(fs) else set()
    todo = [s for s in S_.sdss_id if s not in done]; print(len(todo), "to do", flush=True); R, E = [], []
    with ThreadPoolExecutor(nw) as ex:
        for i, (rows, summ) in enumerate(ex.map(lambda s: one(s, V[V.sdss_id == s], out), todo)):
            E += rows; R.append(summ)
            if (i + 1) % 25 == 0 or i + 1 == len(todo):
                pd.DataFrame(E).to_csv(fe, mode="a", header=not os.path.exists(fe), index=False)
                pd.DataFrame(R).to_csv(fs, mode="a", header=not os.path.exists(fs), index=False); E, R = [], []; print(i + 1, "done", flush=True)
