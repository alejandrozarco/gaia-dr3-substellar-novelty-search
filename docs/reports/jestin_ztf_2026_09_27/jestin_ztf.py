"""Blind ZTF period search of the 716 white dwarfs that Jestin+2026 (A&A 712, A243, table A1; Gaia DR3 variable WDs vetted with ZTF) mark
"Variable False". ZTF DR light curves from IRSA (1.5", catflags = 0, magerr < 0.25), fluxes normalised per oid and filter. Joint g+r
Lomb-Scargle 0.5-50 c/d; frequencies within 0.03 c/d of 1, 2 and 3 c/d masked. Per object: top peak, FAP, sinusoid + first-harmonic
amplitudes per band at that peak, r/g amplitude ratio, and the peak nearest the Gaia DR3 vari_spurious_signals GLS frequency (if any)."""
import os, sys, io, time, requests, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
from concurrent.futures import ThreadPoolExecutor
B = os.path.dirname(os.path.abspath(__file__))
def ztf(sid, ra, dec):
    p = f"{B}/ztf/{sid}.csv"
    if os.path.exists(p) and os.path.getsize(p) > 20: return pd.read_csv(p)
    for k in range(4):
        try:
            r = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {ra} {dec} 0.00042", BANDNAME="g,r", FORMAT="csv"), timeout=180)
            if r.status_code == 200 and r.text.startswith("oid"): open(p, "w").write(r.text); return pd.read_csv(io.StringIO(r.text))
        except Exception: pass
        time.sleep(10 * (k + 1))
    return None
FR = np.arange(0.5, 50, 0.00005); MASK = np.ones(len(FR), bool)
for n in (1, 2, 3): MASK &= np.abs(FR - n) > 0.03
def amps(t, y, e, b, f0):
    out = {}
    for band in ("zg", "zr"):
        m = b == band
        if m.sum() < 20: continue
        X = np.vstack([np.ones(m.sum()), np.cos(2*np.pi*f0*t[m]), np.sin(2*np.pi*f0*t[m]), np.cos(4*np.pi*f0*t[m]), np.sin(4*np.pi*f0*t[m])]).T
        W = X / e[m][:, None]; cc = np.linalg.lstsq(W, y[m] / e[m], rcond=None)[0]; cov = np.linalg.inv(W.T @ W)
        chi = np.sum(((y[m] - X @ cc) / e[m]) ** 2) / (m.sum() - 5)
        out[f"A1_{band}"] = 100 * np.hypot(cc[1], cc[2]); out[f"eA1_{band}"] = 100 * np.sqrt(cov[1, 1] * max(chi, 1)); out[f"A2_{band}"] = 100 * np.hypot(cc[3], cc[4]); out[f"n_{band}"] = int(m.sum())
    return out
def one(row):
    try: return one_(row)
    except Exception as ex: return dict(GaiaDR3=row.GaiaDR3, status=f"ERROR {type(ex).__name__}")
def one_(row):
    sid = row.GaiaDR3; d = ztf(sid, row.RA_ICRS, row.DE_ICRS)
    if d is None: return dict(GaiaDR3=sid, status="HOLE")
    d = d[(d.catflags == 0) & (d.magerr < 0.25)]
    if len(d) < 60: return dict(GaiaDR3=sid, status=f"few points {len(d)}")
    t, y, e, b = [], [], [], []
    for (o, f), s in d.groupby(["oid", "filtercode"]):
        if len(s) < 15: continue
        med = np.median(s.mag); fl = 10 ** (-0.4 * (s.mag - med)) - 1; t += list(s.hjd); y += list(fl - np.mean(fl)); e += list(0.921 * s.magerr * (fl + 1)); b += [f] * len(s)
    if len(t) < 60: return dict(GaiaDR3=sid, status="few points after oid cut")
    t, y, e, b = map(np.array, (t, y, e, b)); g = np.isfinite(t) & np.isfinite(y) & np.isfinite(e) & (e > 0); t, y, e, b = t[g], y[g], e[g], b[g]
    if len(t) < 60 or np.ptp(t) < 10: return dict(GaiaDR3=sid, status="few points after finite cut")
    ls = LombScargle(t, y, e); p = ls.power(FR); p[~MASK] = 0
    i = np.argmax(p); f0 = FR[i]; out = dict(GaiaDR3=sid, status="ok", n=len(t), f_top=round(f0, 6), p_top=p[i], fap_top=ls.false_alarm_probability(p[i], minimum_frequency=0.5, maximum_frequency=50))
    q = p.copy(); q[np.abs(FR - f0) < 0.05] = 0; q[np.abs(FR - 2 * f0) < 0.05] = 0; q[np.abs(FR - f0 / 2) < 0.05] = 0; j = np.argmax(q); out.update(f_2nd=round(FR[j], 6), p_2nd=q[j])
    out.update(amps(t, y, e, b, f0))
    fg = row.gls_freq if np.isfinite(row.gls_freq) else np.nan
    if np.isfinite(fg):
        m = np.abs(FR - fg) < 0.05
        if m.sum(): k = np.argmax(np.where(m, p, 0)); out.update(f_gaia=fg, f_near_gaia=round(FR[k], 6), p_near_gaia=p[k])
    if "A1_zg" in out and "A1_zr" in out: out["r_over_g"] = out["A1_zr"] / max(out["A1_zg"], 1e-3)
    return out
if __name__ == "__main__":
    d = pd.read_csv(sys.argv[1], dtype={"GaiaDR3": str}); rows = list(d.itertuples())
    res = []
    with ThreadPoolExecutor(3) as ex:
        for k, r in enumerate(ex.map(one, rows)):
            res.append(r)
            if k % 50 == 0: print(k, flush=True)
    R = pd.DataFrame(res).merge(d, on="GaiaDR3"); R.to_csv(sys.argv[2], index=False); print("done", len(R), R.status.value_counts().to_dict())
