# Rotation-period pipeline for ZTF DR24 light curves (lane: /tmp/fanout/rotation).
# Flux space, catflags==0, per field/ccd/quadrant/filter median normalisation, BJD_TDB at mid-exposure
# (ZTF 'mjd' = exposure START in UTC, verified against the 'hjd' column: HJD_UTC(mjd)-hjd = -15.0 s = -exptime/2).
import csv, json, math
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.timeseries import LombScargle

GEO = EarthLocation.from_geocentric(0, 0, 0, unit="m")
FMIN, FMAX, OFAC = 0.05, 300.0, 5.0


def gaia_pos_at(rec, jyear):
    """Gaia DR3 (epoch 2016.0) position propagated linearly to epoch jyear (deg)."""
    ra, dec = float(rec["ra"]), float(rec["dec"])
    pmra = float(rec["pmra"] or 0); pmdec = float(rec["pmdec"] or 0)
    dt = jyear - 2016.0
    return ra + pmra * dt / 3.6e6 / math.cos(math.radians(dec)), dec + pmdec * dt / 3.6e6


def sep_as(ra1, de1, ra2, de2):
    return 3600 * math.degrees(math.acos(min(1, math.sin(math.radians(de1)) * math.sin(math.radians(de2)) +
                                              math.cos(math.radians(de1)) * math.cos(math.radians(de2)) * math.cos(math.radians(ra1 - ra2)))))


def read_oids(fn):
    rows = list(csv.DictReader(open(fn)))
    by = {}
    for r in rows:
        by.setdefault(r["oid"], []).append(r)
    return rows, by


def oid_table(by, rec):
    """Per-oid summary: filter, n, median position, separation from the PM-propagated Gaia position at the oid's median epoch."""
    out = []
    for oid, R in by.items():
        mjd = np.array([float(r["mjd"]) for r in R])
        jy = Time(np.median(mjd), format="mjd").jyear
        ra0, de0 = gaia_pos_at(rec, jy)
        ra = np.median([float(r["ra"]) for r in R]); de = np.median([float(r["dec"]) for r in R])
        good = [r for r in R if int(r["catflags"]) == 0]
        mag = np.median([float(r["mag"]) for r in good]) if good else np.nan
        out.append(dict(oid=oid, filt=R[0]["filtercode"], n=len(R), n_good=len(good), ra=ra, dec=de, sep=sep_as(ra, de, ra0, de0),
                        mag=float(mag), field=R[0]["field"], ccd=R[0]["ccdid"], qid=R[0]["qid"]))
    return sorted(out, key=lambda x: (x["sep"], -x["n"]))


def bjd_mid(mjd_start, exptime, ra, dec):
    c0 = SkyCoord(ra * u.deg, dec * u.deg)
    t = Time(mjd_start + exptime / 2 / 86400.0, format="mjd", scale="utc", location=GEO)
    return (t.tdb + t.light_travel_time(c0)).jd


def load_lc(rows_of_oids, ra, dec, magerr_max=0.3, clip=5.0, detrend=True):
    """Normalised flux light curve per band from a list of ZTF rows (already restricted to the chosen oids)."""
    D = {}
    for band in ("zg", "zr", "zi"):
        R = [r for r in rows_of_oids if r["filtercode"] == band and int(r["catflags"]) == 0 and float(r["magerr"]) < magerr_max]
        if len(R) < 10:
            continue
        mjd = np.array([float(r["mjd"]) for r in R]); m = np.array([float(r["mag"]) for r in R]); e = np.array([float(r["magerr"]) for r in R])
        ex = np.array([float(r["exptime"]) for r in R])
        key = np.array([f"{r['field']}_{r['ccdid']}_{r['qid']}" for r in R])
        f = 10 ** (-0.4 * (m - np.median(m))); ef = f * e / 1.0857362
        for k in np.unique(key):
            s = np.median(f[key == k]); f[key == k] /= s; ef[key == k] /= s
        mad = 1.4826 * np.median(np.abs(f - 1))
        ok = np.abs(f - 1) < clip * max(mad, 1e-4)
        if detrend and ok.sum() >= 60:
            # remove the sky-brightness/depth systematic (flux vs limitmag; diagnosed on the negative controls: ~1-2% in g,
            # lunar-phase correlated, aliases to 1 +- 1/29.5 c/d) with a binned-median curve in limitmag, then a linear airmass term
            L = np.array([float(r["limitmag"]) for r in R]); X = np.array([float(r["airmass"]) for r in R])
            q = np.unique(np.percentile(L[ok], np.linspace(0, 100, 11)))
            if len(q) >= 4:
                ib = np.clip(np.digitize(L, q[1:-1]), 0, len(q) - 2)
                cen = np.array([np.median(L[ok & (ib == i)]) if np.sum(ok & (ib == i)) > 5 else np.nan for i in range(len(q) - 1)])
                med = np.array([np.median(f[ok & (ib == i)]) if np.sum(ok & (ib == i)) > 5 else np.nan for i in range(len(q) - 1)])
                g = np.isfinite(cen) & np.isfinite(med)
                if g.sum() >= 3:
                    trend = np.interp(L, cen[g], med[g])
                    f = f / trend; ef = ef / trend
            A = np.vstack([np.ones(ok.sum()), X[ok] - 1.3]).T
            c, *_ = np.linalg.lstsq(A, f[ok], rcond=None)
            tr = c[0] + c[1] * (X - 1.3)
            f = f / tr; ef = ef / tr
            mad = 1.4826 * np.median(np.abs(f - 1))
            ok = np.abs(f - 1) < clip * max(mad, 1e-4)
        t = bjd_mid(mjd[ok], ex[ok], ra, dec)
        extra = {k: np.array([float(r[k]) for r, o in zip(R, ok) if o]) for k in ("airmass", "limitmag", "mag", "magerr")}
        extra["expid"] = np.array([int(r["expid"]) for r, o in zip(R, ok) if o])
        extra["filefracday"] = np.array([r["filefracday"] for r, o in zip(R, ok) if o])
        extra["field"] = np.array([r["field"] for r, o in zip(R, ok) if o]); extra["ccdid"] = np.array([r["ccdid"] for r, o in zip(R, ok) if o])
        extra["qid"] = np.array([r["qid"] for r, o in zip(R, ok) if o])
        D[band] = dict(t=t, f=f[ok], e=ef[ok], key=key[ok], mjd=mjd[ok], n_raw=len(R), n=int(ok.sum()), rms=float(np.std(f[ok])),
                       med_err=float(np.median(ef[ok])), med_mag=float(np.median(m)), **extra)
    return D


def combine(D, bands=("zg", "zr", "zi"), min_n=30):
    bs = [b for b in bands if b in D and D[b]["n"] >= min_n]
    t = np.concatenate([D[b]["t"] for b in bs]); f = np.concatenate([D[b]["f"] for b in bs]); e = np.concatenate([D[b]["e"] for b in bs])
    bb = np.concatenate([np.full(D[b]["n"], b) for b in bs])
    o = np.argsort(t)
    return t[o], f[o], e[o], bb[o], bs


def freq_grid(t, fmin=FMIN, fmax=FMAX, ofac=OFAC):
    T = t.max() - t.min()
    df = 1.0 / (ofac * T)
    return np.arange(fmin, fmax, df), df


def periodogram(t, f, e, freq):
    ls = LombScargle(t, f, e)
    p = ls.power(freq, method="fast", assume_regular_frequency=True, method_kwds=dict(trig_sum_kwds=dict(oversampling=3)))
    return ls, p


def top_peaks(freq, p, n=10, min_sep=None):
    if min_sep is None:
        min_sep = 5 * (freq[1] - freq[0])
    # local maxima
    lm = np.where((p[1:-1] > p[:-2]) & (p[1:-1] >= p[2:]))[0] + 1
    lm = lm[np.argsort(p[lm])[::-1]]
    out = []
    for i in lm:
        if all(abs(freq[i] - freq[j]) > min_sep for j in out):
            out.append(i)
        if len(out) == n:
            break
    return out


def refine_peak(ls, f0, df, n=201):
    fr = np.linspace(f0 - 2 * df, f0 + 2 * df, n)
    p = ls.power(fr, method="slow")
    i = np.argmax(p)
    return fr[i], p[i]


def sine_fit(t, f, e, freq, nharm=1):
    cols = [np.ones_like(t)]
    for k in range(1, nharm + 1):
        cols += [np.sin(2 * np.pi * k * freq * t), np.cos(2 * np.pi * k * freq * t)]
    X = np.vstack(cols).T
    w = 1 / e
    b, *_ = np.linalg.lstsq(X * w[:, None], f * w, rcond=None)
    cov = np.linalg.inv((X * w[:, None]).T @ (X * w[:, None]))
    # scale covariance by reduced chi2 (conservative)
    res = f - X @ b
    chi2r = np.sum((res / e) ** 2) / max(1, len(t) - X.shape[1])
    cov *= max(1.0, chi2r)
    A = math.hypot(b[1], b[2])
    # amplitude error (first harmonic)
    J = np.array([b[1], b[2]]) / max(A, 1e-12)
    eA = math.sqrt(max(0.0, J @ cov[1:3, 1:3] @ J))
    phase = math.atan2(b[2], b[1])
    return dict(A=A, eA=eA, phase=phase, b=b, chi2r=chi2r, model=X @ b)


def window_peaks(t, freq, n=12):
    W = LombScargle(t, np.ones_like(t), fit_mean=False, center_data=False).power(freq, method="fast", assume_regular_frequency=True, method_kwds=dict(trig_sum_kwds=dict(oversampling=3)))
    idx = top_peaks(freq, W, n=n, min_sep=0.02)
    return W, [(float(freq[i]), float(W[i])) for i in idx]


def alias_notes(f0, wpk, tol=0.003):
    """Flag f0 if it coincides with a strong spectral-window peak or its harmonics, or with a known systematics frequency family:
    k x (1 sidereal/solar day) and k +- 1/29.53 d (lunar sky-brightness aliases), k +- 1/365.25 d (seasonal), for k <= 300 c/d."""
    notes = []
    for w, pw in wpk:
        if pw < 0.05: continue
        for k in (1, 2, 3):
            if abs(f0 - k * w) < tol * k:
                notes.append(f"f0 ~ {k}x window peak {w:.4f} c/d (W={pw:.2f})")
    for day, lab in ((1.0, "solar day"), (1.0027379, "sidereal day")):
        k = round(f0 / day)
        for off, olab in ((0.0, ""), (1 / 29.53, " +- lunar"), (1 / 365.25, " +- 1/yr")):
            for sgn in ((1,) if off == 0 else (1, -1)):
                for kk in (k - 1, k, k + 1):
                    if kk < 0: continue
                    if abs(f0 - (kk * day + sgn * off)) < tol:
                        notes.append(f"f0 ~ {kk} x {lab}{olab}")
    if f0 < 0.2:
        notes.append("f0 < 0.2 c/d: long-period regime, seasonal/lunar systematics dominate in ZTF")
    return sorted(set(notes))
