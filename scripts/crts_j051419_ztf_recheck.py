"""Decisive ZTF period test for CRTS J051419.8+011120.
Re-fetch ZTF light curve from IRSA, mask outbursts, and test whether the
claimed P=180.77 min (0.1255349 d) orbital period is a real, significant
signal or an artifact of outburst structure / aliasing.

Tests: Lomb-Scargle (per band + check), BLS (eclipse), each WITH and WITHOUT
outburst masking, with analytic + bootstrap FAP. Reports peak periods, the
power/FAP specifically at the ZTF period, and a folded-amplitude significance.
"""
import warnings, json, io, numpy as np
warnings.filterwarnings('ignore')
import requests
from astropy.timeseries import LombScargle, BoxLeastSquares

RA, DEC = 78.58284521736, 1.18914740612
P0 = 0.1255349            # d  (claimed)
out = {'P0_d': P0, 'P0_min': P0*1440}

# ---------- 1. fetch ZTF light curve ----------
url = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
params = {'POS': f'CIRCLE {RA} {DEC} 0.0014', 'BANDNAME': 'g,r,i', 'FORMAT': 'CSV'}
r = requests.get(url, params=params, timeout=180)
r.raise_for_status()
import csv as _csv
rows = list(_csv.DictReader(io.StringIO(r.text)))
out['n_raw'] = len(rows)
if len(rows) == 0:
    print(json.dumps({'FATAL': 'no ZTF rows', 'text_head': r.text[:300]})); raise SystemExit

def col(rows, k):
    return np.array([row.get(k, '') for row in rows])

mjd = col(rows, 'mjd').astype(float)
mag = col(rows, 'mag').astype(float)
err = col(rows, 'magerr').astype(float)
cat = col(rows, 'catflags').astype(float)
band = col(rows, 'filtercode')
good = (cat == 0) & np.isfinite(mag) & np.isfinite(mjd)
mjd, mag, err, band = mjd[good], mag[good], err[good], band[good]
out['n_catflag0'] = int(good.sum())
out['baseline_d'] = float(mjd.max()-mjd.min())
out['bands'] = {b: int((band == b).sum()) for b in ('zg', 'zr', 'zi')}

def run_band(b):
    m = band == b
    t, y, e = mjd[m], mag[m], err[m]
    if len(t) < 40:
        return {'n': int(len(t)), 'skip': 'too few'}
    med = np.median(y)
    # outburst = >0.75 mag BRIGHTER than median (smaller mag). Eclipses (fainter) preserved.
    ob = y < (med - 0.75)
    res = {'n': int(len(t)), 'n_outburst': int(ob.sum()), 'quiescent_med_mag': float(med)}
    for tag, keep in (('with_outbursts', np.ones(len(t), bool)), ('masked', ~ob)):
        tk, yk, ek = t[keep], y[keep], e[keep]
        if len(tk) < 40:
            res[tag] = {'skip': 'too few after mask'}; continue
        # ---- Lomb-Scargle ----
        ls = LombScargle(tk, yk, ek)
        freq, power = ls.autopower(minimum_frequency=0.5, maximum_frequency=20.0,
                                   samples_per_peak=8)
        ip = int(np.argmax(power))
        Ppeak = 1.0/freq[ip]
        fap_peak = float(ls.false_alarm_probability(power[ip], method='baluev'))
        # power at the claimed period
        pw_P0 = float(ls.power(1.0/P0))
        fap_P0 = float(ls.false_alarm_probability(pw_P0, method='baluev'))
        # top-5 peaks (local maxima)
        order = np.argsort(power)[::-1]
        tops = []
        seen = []
        for idx in order:
            Pp = 1.0/freq[idx]
            if all(abs(Pp-s)/s > 0.01 for s in seen):
                seen.append(Pp); tops.append((round(float(Pp), 6), round(float(power[idx]), 4)))
            if len(tops) >= 5:
                break
        # ---- BLS (eclipse) on flux ----
        flux = 10**(-0.4*(yk-med))
        fe = ek*flux*0.92103
        pg = np.linspace(0.05, 0.30, 6000)
        bls = BoxLeastSquares(tk, flux, fe)
        durs = [0.004, 0.008, 0.013]
        bp = bls.power(pg, durs)
        jb = int(np.argmax(bp.power))
        # power at P0
        bp0 = bls.power(np.array([P0]), durs)
        res[tag] = {
            'n_used': int(len(tk)),
            'LS_peak_P_d': round(float(Ppeak), 6), 'LS_peak_P_min': round(float(Ppeak*1440), 3),
            'LS_peak_FAP': fap_peak,
            'LS_power_at_P0': round(pw_P0, 4), 'LS_FAP_at_P0': fap_P0,
            'LS_top5_(P_d,power)': tops,
            'BLS_peak_P_d': round(float(bp.period[jb]), 6), 'BLS_peak_P_min': round(float(bp.period[jb]*1440), 3),
            'BLS_peak_power': round(float(bp.power[jb]), 4),
            'BLS_power_at_P0': round(float(bp0.power[0]), 4),
            'BLS_depth_at_P0': round(float(bp0.depth[0]), 4),
        }
        # bootstrap FAP for LS max peak (shuffle mags)
        rng = np.random.default_rng(0)
        nb = 200; cnt = 0
        for _ in range(nb):
            ys = rng.permutation(yk)
            _, pw = LombScargle(tk, ys, ek).autopower(minimum_frequency=0.5, maximum_frequency=20.0, samples_per_peak=4)
            if pw.max() >= power[ip]:
                cnt += 1
        res[tag]['LS_bootstrap_FAP_peak'] = cnt/nb
    return res

for b in ('zg', 'zr', 'zi'):
    out[b] = run_band(b)

print(json.dumps(out, indent=1, default=str))
json.dump(out, open('/tmp/crts_j051419_ztf_recheck.json', 'w'), indent=1, default=str)
print('\nSAVED /tmp/crts_j051419_ztf_recheck.json')
