"""White dwarf + irradiated companion search: GF21 white dwarfs (Pwd > 0.75) with a Gaia DR3 vari_spurious_signals GLS frequency > 3 c/d
(FAP < 0.05), Dec > -28. ZTF light curves (IRSA, 1.5", catflags = 0, magerr < 0.25). Per object: Lomb-Scargle of g+r jointly (offsets per
filter) over 0.5-50 c/d; best peak within 0.05 c/d of the Gaia frequency (or of 2f, f/2); sinusoid + first harmonic per filter at that
frequency; r/g amplitude ratio. Irradiation candidates: significant in both bands, r/g >= 1.5."""
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
def one(row):
    sid = row.source_id; d = ztf(sid, row.ra, row.dec)
    if d is None: return dict(source_id=sid, status="HOLE")
    d = d[(d.catflags == 0) & (d.magerr < 0.25)]
    if len(d) < 60: return dict(source_id=sid, status=f"few points {len(d)}")
    t, y, e, b = [], [], [], []
    for (o, f), s in d.groupby(["oid", "filtercode"]):
        if len(s) < 15: continue
        med = np.median(s.mag); fl = 10 ** (-0.4 * (s.mag - med)) - 1; t += list(s.hjd); y += list(fl - np.mean(fl)); e += list(0.921 * s.magerr * (fl + 1)); b += [f] * len(s)
    t, y, e, b = map(np.array, (t, y, e, b)); fg = row.gls_freq_g_fov
    fr = np.arange(0.5, 50, 0.00005); ls = LombScargle(t, y, e); p = ls.power(fr); top = fr[np.argmax(p)]
    best = None
    for c in (fg, 2 * fg, fg / 2, fg + 1, fg - 1):
        m = np.abs(fr - c) < 0.05
        if m.sum() and (best is None or p[m].max() > best[1]): best = (fr[m][np.argmax(p[m])], p[m].max(), c / fg)
    f0 = best[0]; out = dict(source_id=sid, status="ok", f_gaia=fg, f_ztf=round(f0, 6), rel=best[2], top_peak=round(top, 5), fap=ls.false_alarm_probability(best[1], minimum_frequency=0.5, maximum_frequency=50))
    for band in ("zg", "zr"):
        m = b == band
        if m.sum() < 20: continue
        X = np.vstack([np.ones(m.sum()), np.cos(2*np.pi*f0*t[m]), np.sin(2*np.pi*f0*t[m]), np.cos(4*np.pi*f0*t[m]), np.sin(4*np.pi*f0*t[m])]).T
        cc = np.linalg.lstsq(X / e[m][:, None], y[m] / e[m], rcond=None)[0]; cov = np.linalg.inv((X / e[m][:, None]).T @ (X / e[m][:, None]))
        chi = np.sum(((y[m] - X @ cc) / e[m]) ** 2) / (m.sum() - 5)
        out[f"A1_{band}"] = 100 * np.hypot(cc[1], cc[2]); out[f"eA1_{band}"] = 100 * np.sqrt(cov[1, 1] * max(chi, 1)); out[f"A2_{band}"] = 100 * np.hypot(cc[3], cc[4]); out[f"n_{band}"] = int(m.sum())
    if "A1_zg" in out and "A1_zr" in out: out["r_over_g"] = out["A1_zr"] / max(out["A1_zg"], 1e-3)
    return out
if __name__ == "__main__":
    d = pd.read_csv(sys.argv[1], dtype={"source_id": str}); rows = list(d.itertuples())
    with ThreadPoolExecutor(3) as ex: res = list(ex.map(one, rows))
    R = pd.DataFrame(res).merge(d, on="source_id"); R.to_csv(sys.argv[2], index=False); print("done", len(R), R.status.value_counts().to_dict())
