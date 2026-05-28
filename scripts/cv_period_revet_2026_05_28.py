"""Re-vet 4 CV "orbital period + eclipse" discoveries from a BUGGY photometry
pipeline.

The original pipeline folded OUTBURST-INCLUDING light curves (outbursts inject
power across all frequencies) and measured eclipse depths as the per-cycle
MINIMUM of noise-dominated cadences (per-cadence S/N < 1), manufacturing
spurious deep "eclipses" and spurious periods.

This script applies the SAME rigorous method validated on the falsified 5th
object (CRTS J051419.8+011120) to the remaining 4 targets:

  1. Re-fetch ZTF light curve from IRSA (cone 0.0014 deg, g/r/i, catflags==0).
  2. Per band: mask outbursts (>0.75 mag BRIGHTER than per-band median).
     Report n_quiescent + per-cadence S/N (quiescent median flux / median
     flux error, in linear flux).
  3. Lomb-Scargle on outburst-masked data, freq 0.5-20/d: peak period, its
     analytic (baluev) + bootstrap FAP, top-5 peaks (flag 1-sidereal-day
     aliases ~0.997/0.499/0.333/0.25 d), and power+FAP at the claimed period.
  4. BLS on outburst-masked flux: best period PER BAND (do bands agree with
     each other and with claimed P?) + power/depth at the claimed period.
  5. TESS (if a sector exists): fetch the actual SPOC/TESS-SPOC/QLP light
     curve, mask outbursts, fold at claimed P, binned deepest-dip significance
     with a permutation FAP over random periods. Report per-cadence S/N.
  6. VERDICT per target: SURVIVES / NOT_SUPPORTED / AMBIGUOUS.

Adapted from /tmp/crts_ztf_recheck.py and /tmp/crts_spoc_recheck.py.

Usage:
    python cv_period_revet_2026_05_28.py            # all 4 targets
    python cv_period_revet_2026_05_28.py <shortname> # one target
"""
import warnings, json, io, sys, csv as _csv
import numpy as np
warnings.filterwarnings('ignore')
import requests
from astropy.timeseries import LombScargle, BoxLeastSquares

# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------
TARGETS = [
    {'short': 'sdss1549', 'name': 'SDSS J154953.41+173939.0',
     'ra': 237.473, 'dec': 17.661, 'P_min': 116.68, 'cls': 'NL',
     'eclipse_claim': None},
    {'short': 'sdss0919', 'name': 'SDSS J091935.66+502825.1',
     'ra': 139.899, 'dec': 50.474, 'P_min': 93.51, 'cls': 'DN (S21 superoutburst)',
     'eclipse_claim': None},
    {'short': 'crts1518', 'name': 'CRTS J151836.0-054803',
     'ra': 229.650, 'dec': -5.801, 'P_min': 24.64, 'cls': 'DN (brightest ~16.5 mag; possible 1/7 alias of ~172 min)',
     'eclipse_claim': None},
    {'short': 'sdss1604', 'name': 'SDSS J160419.02+161548.5',
     'ra': 241.079, 'dec': 16.263, 'P_min': 128.80, 'cls': 'SU UMa',
     'eclipse_claim': 0.23},
]

SIDEREAL_ALIASES = [0.99727, 0.49863, 0.33242, 0.24932]  # 1,1/2,1/3,1/4 sidereal day


def is_sidereal_alias(P_d, tol=0.01):
    return any(abs(P_d - a) / a < tol for a in SIDEREAL_ALIASES)


# ---------------------------------------------------------------------------
# 1. ZTF fetch
# ---------------------------------------------------------------------------
def fetch_ztf(ra, dec):
    url = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
    params = {'POS': f'CIRCLE {ra} {dec} 0.0014', 'BANDNAME': 'g,r,i', 'FORMAT': 'CSV'}
    r = requests.get(url, params=params, timeout=180)
    r.raise_for_status()
    rows = list(_csv.DictReader(io.StringIO(r.text)))
    return rows, r.text


def col(rows, k):
    return np.array([row.get(k, '') for row in rows])


# ---------------------------------------------------------------------------
# 3+4. per-band LS + BLS, masked vs unmasked
# ---------------------------------------------------------------------------
def run_band(b, mjd, mag, err, band, P0):
    m = band == b
    t, y, e = mjd[m], mag[m], err[m]
    if len(t) < 40:
        return {'n': int(len(t)), 'skip': 'too few'}
    med = np.median(y)
    # outburst = >0.75 mag BRIGHTER than median (smaller mag). Eclipses (fainter) preserved.
    ob = y < (med - 0.75)
    # per-cadence S/N in LINEAR flux on QUIESCENT data
    keepq = ~ob
    yq, eq = y[keepq], e[keepq]
    medq = np.median(yq)
    flux_q = 10 ** (-0.4 * (yq - medq))
    ferr_q = eq * flux_q * 0.92103          # d(flux) = 0.4 ln10 * flux * dmag
    snr_cadence = float(np.median(flux_q) / np.median(ferr_q)) if len(yq) else None
    res = {'n': int(len(t)), 'n_outburst': int(ob.sum()),
           'n_quiescent': int(keepq.sum()),
           'quiescent_med_mag': float(medq),
           'per_cadence_SNR_quiescent': snr_cadence}
    for tag, keep in (('with_outbursts', np.ones(len(t), bool)), ('masked', ~ob)):
        tk, yk, ek = t[keep], y[keep], e[keep]
        if len(tk) < 40:
            res[tag] = {'skip': 'too few after mask'}
            continue
        # ---- Lomb-Scargle ----
        ls = LombScargle(tk, yk, ek)
        freq, power = ls.autopower(minimum_frequency=0.5, maximum_frequency=20.0,
                                   samples_per_peak=8)
        ip = int(np.argmax(power))
        Ppeak = 1.0 / freq[ip]
        try:
            fap_peak = float(ls.false_alarm_probability(power[ip], method='baluev'))
        except Exception:
            fap_peak = None
        pw_P0 = float(ls.power(1.0 / P0))
        try:
            fap_P0 = float(ls.false_alarm_probability(pw_P0, method='baluev'))
        except Exception:
            fap_P0 = None
        # top-5 distinct peaks
        order = np.argsort(power)[::-1]
        tops, seen = [], []
        for idx in order:
            Pp = 1.0 / freq[idx]
            if all(abs(Pp - s) / s > 0.01 for s in seen):
                seen.append(Pp)
                tops.append({'P_d': round(float(Pp), 6), 'P_min': round(float(Pp * 1440), 3),
                             'power': round(float(power[idx]), 4),
                             'sidereal_alias': bool(is_sidereal_alias(Pp))})
            if len(tops) >= 5:
                break
        # ---- BLS on flux ----
        flux = 10 ** (-0.4 * (yk - med))
        fe = ek * flux * 0.92103
        # period grid spans well below + above the claimed P
        pgrid_min = max(0.01, P0 * 0.3)
        pg = np.linspace(pgrid_min, max(0.30, P0 * 4), 8000)
        bls = BoxLeastSquares(tk, flux, fe)
        # transit durations MUST be shorter than the minimum period in the grid
        durs = [d for d in (0.003, 0.006, 0.010, 0.015) if d < pgrid_min * 0.9]
        if not durs:
            durs = [pgrid_min * 0.3, pgrid_min * 0.6]
        bp = bls.power(pg, durs)
        jb = int(np.argmax(bp.power))
        # at the claimed period, durations must also be < P0
        durs0 = [d for d in durs if d < P0 * 0.9] or [P0 * 0.1, P0 * 0.3]
        bp0 = bls.power(np.array([P0]), durs0)
        res[tag] = {
            'n_used': int(len(tk)),
            'LS_peak_P_d': round(float(Ppeak), 6), 'LS_peak_P_min': round(float(Ppeak * 1440), 3),
            'LS_peak_FAP': fap_peak,
            'LS_peak_is_sidereal_alias': bool(is_sidereal_alias(Ppeak)),
            'LS_power_at_P0': round(pw_P0, 4), 'LS_FAP_at_P0': fap_P0,
            'LS_top5': tops,
            'BLS_peak_P_d': round(float(bp.period[jb]), 6),
            'BLS_peak_P_min': round(float(bp.period[jb] * 1440), 3),
            'BLS_peak_power': round(float(bp.power[jb]), 4),
            'BLS_power_at_P0': round(float(bp0.power[0]), 4),
            'BLS_depth_at_P0': round(float(bp0.depth[0]), 4),
        }
        # bootstrap FAP for LS max peak (shuffle mags)
        rng = np.random.default_rng(0)
        nb = 200
        cnt = 0
        for _ in range(nb):
            ys = rng.permutation(yk)
            _, pw = LombScargle(tk, ys, ek).autopower(minimum_frequency=0.5,
                                                       maximum_frequency=20.0,
                                                       samples_per_peak=4)
            if pw.max() >= power[ip]:
                cnt += 1
        res[tag]['LS_bootstrap_FAP_peak'] = cnt / nb
    return res


# ---------------------------------------------------------------------------
# 5. TESS SPOC fold + permutation FAP
# ---------------------------------------------------------------------------
def dip_stat(tq, rq, P, nbins=28):
    ph = ((tq - tq.min()) / P) % 1.0
    idx = np.clip((ph * nbins).astype(int), 0, nbins - 1)
    bm = np.array([np.mean(rq[idx == b]) if np.any(idx == b) else np.nan for b in range(nbins)])
    bn = np.array([np.sum(idx == b) for b in range(nbins)])
    ooe = np.nanmedian(bm)
    db = int(np.nanargmin(bm))
    deepest = bm[db]
    depth = (ooe - deepest) / ooe
    scat = np.std(rq)
    sig = (ooe - deepest) / (scat / np.sqrt(max(bn[db], 1)))
    return depth, sig, db, ooe, scat, int(bn[db])


def run_tess(tgt):
    import lightkurve as lk
    name = tgt['name']
    P_d = tgt['P_min'] / 1440.0
    out = {'P_claimed_d': P_d, 'P_claimed_min': tgt['P_min']}
    # coordinate-based search (CV designations are not always TIC-resolvable)
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    coord = SkyCoord(tgt['ra'], tgt['dec'], unit='deg')
    try:
        sr = lk.search_lightcurve(coord, mission='TESS', radius=21 * u.arcsec)
    except Exception as ex:
        return {'no_tess': f'search failed: {str(ex)[:160]}', **out}
    if sr is None or len(sr) == 0:
        return {'no_tess': 'no TESS light curve products found', **out}
    try:
        out['search'] = [f"{row['author']}|S{row['mission'].split()[-1]}|exp={row['exptime']}"
                         for row in sr.table]
    except Exception:
        out['search'] = str(sr)[:500]

    # pick best product: prefer SPOC 120s, then TESS-SPOC, then QLP. Prefer short exp.
    lc = None
    used = None
    authors = list(sr.table['author'])
    # rank candidate rows
    def author_rank(a):
        return {'SPOC': 0, 'TESS-SPOC': 1, 'QLP': 2}.get(a, 3)
    exptimes = np.asarray(sr.table['exptime'].value, float) if hasattr(sr.table['exptime'], 'value') else np.asarray(sr.table['exptime'], float)
    rank = sorted(range(len(authors)), key=lambda i: (author_rank(authors[i]), exptimes[i]))
    for i in rank:
        try:
            lc = sr[int(i)].download()
            if lc is not None:
                used = f"{authors[i]} exp={exptimes[i]}s"
                break
        except Exception as ex:
            out.setdefault('dl_errs', []).append(f"{authors[i]}: {str(ex)[:120]}")
    if lc is None:
        return {'no_tess': 'no TESS product downloadable', **out}
    out['used_product'] = used

    flux = None
    for c in ('pdcsap_flux', 'sap_flux', 'flux'):
        if c in lc.colnames and np.isfinite(np.asarray(lc[c].value, float)).sum() > 100:
            flux = np.asarray(lc[c].value, float)
            out['flux_col'] = c
            break
    if flux is None:
        return {'no_tess': 'no usable flux column', **out}
    t = np.asarray(lc.time.value, float)
    ferr = np.asarray(lc['flux_err'].value, float) if 'flux_err' in lc.colnames else np.full_like(flux, np.nan)
    m = np.isfinite(flux) & np.isfinite(t)
    t, flux, ferr = t[m], flux[m], ferr[m]
    out['n_total'] = int(len(flux))
    out['exptime_s'] = float(np.median(np.diff(np.sort(t))) * 86400)

    # running-median trend (window >> eclipse). Use 0.5 d, but cap so it stays
    # well above the claimed period.
    order = np.argsort(t)
    t, flux, ferr = t[order], flux[order], ferr[order]
    win = max(0.3, min(0.5, P_d * 6))
    trend = np.empty_like(flux)
    lo = hi = 0
    for i in range(len(t)):
        while t[lo] < t[i] - win / 2:
            lo += 1
        while hi < len(t) and t[hi] <= t[i] + win / 2:
            hi += 1
        trend[i] = np.median(flux[lo:hi])
    qbase = np.percentile(trend, 20)
    out['quiescent_baseline_flux'] = float(qbase)
    out['per_cadence_relerr_median'] = float(np.nanmedian(ferr / np.maximum(flux, 1e-9)))
    out['per_cadence_SNR_quiescent'] = (float(qbase / np.nanmedian(ferr))
                                        if np.isfinite(np.nanmedian(ferr)) else None)

    ob = trend > 1.4 * qbase
    qmask = ~ob
    resid = flux / trend
    tq, rq = t[qmask], resid[qmask]
    out['n_quiescent'] = int(qmask.sum())
    out['n_outburst'] = int(ob.sum())
    if len(tq) < 200:
        out['warn'] = 'few quiescent cadences'

    depth, sig, db, ooe, scat, nin = dip_stat(tq, rq, P_d)

    # refine the period over a +/-0.3% window (the look-elsewhere boost)
    def refined_sig(Pc, frac=0.003, ng=121):
        grid = np.linspace(Pc * (1 - frac), Pc * (1 + frac), ng)
        ss = [dip_stat(tq, rq, Pg)[1] for Pg in grid]
        j = int(np.argmax(ss))
        return float(grid[j]), float(ss[j])

    P_best, sig_best = refined_sig(P_d)
    depth_b = dip_stat(tq, rq, P_best)[0]

    # permutation FAP over random periods spanning the CV regime.
    # CRITICAL: compute TWO nulls so the comparison is apples-to-apples.
    #   (a) raw: fold at random P, take deepest bin (compare to at_claimed_P sig)
    #   (b) refined: ALSO refine each random center over +/-0.3% before taking
    #       the deepest bin (compare to the refined sig). Without this, an
    #       optimized period looks falsely significant against an un-optimized
    #       null -- the exact min-of-noise trap.
    rng = np.random.default_rng(1)
    ntr = 2000
    plo, phi = max(0.02, P_d * 0.5), P_d * 2.0
    null_raw = np.array([dip_stat(tq, rq, rng.uniform(plo, phi))[1] for _ in range(ntr)])
    fap_claim = float(np.mean(null_raw >= sig))
    # refined null (fewer trials -- each is 121x more work)
    ntr_ref = 400
    null_ref = np.array([refined_sig(rng.uniform(plo, phi))[1] for _ in range(ntr_ref)])
    fap_best_refined = float(np.mean(null_ref >= sig_best))

    out['fold'] = {
        'at_claimed_P': {'binned_depth': float(depth), 'deepest_bin_sigma': float(sig),
                         'n_in_deepbin': nin, 'OOE_level': float(ooe),
                         'per_cadence_scatter': float(scat), 'permutation_FAP': fap_claim},
        'refined_pm0.3pct': {'P_best_d': P_best, 'P_best_min': P_best * 1440,
                             'binned_depth': float(depth_b), 'deepest_bin_sigma': sig_best,
                             # apples-to-apples FAP: random centers ALSO refined +/-0.3%
                             'permutation_FAP_refined_null': fap_best_refined,
                             'refined_null_sigma_mean': float(np.mean(null_ref)),
                             'refined_null_sigma_p99': float(np.percentile(null_ref, 99))},
        'null_sigma_mean': float(np.mean(null_raw)), 'null_sigma_p99': float(np.percentile(null_raw, 99)),
        'random_period_range_d': [plo, phi],
    }
    return out


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------
def decide_verdict(tgt, ztf, tess):
    P0 = tgt['P_min'] / 1440.0
    reasons = []
    bands = [b for b in ('zg', 'zr', 'zi') if b in ztf and 'masked' in ztf[b]]
    # masked-LS FAP at claimed period (take the most favorable = smallest across bands)
    fap_at_P0 = []
    ls_peak_aliases = []
    bls_peaks = []
    ls_peaks = []
    snrs = []
    for b in bands:
        mk = ztf[b]['masked']
        if mk.get('LS_FAP_at_P0') is not None:
            fap_at_P0.append(mk['LS_FAP_at_P0'])
        ls_peak_aliases.append(mk.get('LS_peak_is_sidereal_alias'))
        bls_peaks.append(mk.get('BLS_peak_P_d'))
        ls_peaks.append(mk.get('LS_peak_P_d'))
        if ztf[b].get('per_cadence_SNR_quiescent') is not None:
            snrs.append(ztf[b]['per_cadence_SNR_quiescent'])
    best_fap = min(fap_at_P0) if fap_at_P0 else None

    # Do BLS bands agree with each other and the claimed P?
    def agree(p, q, tol=0.03):
        if p is None or q is None:
            return False
        # accept direct, 2x, 0.5x, and beat-alias matches
        for f in (1, 2, 0.5, 1 / 3, 3):
            if abs(p - q * f) / (q * f) < tol:
                return True
        return False
    bls_band_agree = False
    if len(bls_peaks) >= 2:
        bls_band_agree = all(agree(bls_peaks[0], bp) for bp in bls_peaks[1:])
    bls_match_claim = any(agree(bp, P0) for bp in bls_peaks if bp is not None)

    # LS peak near claimed P in any band?
    ls_match_claim = any(agree(lp, P0) for lp in ls_peaks if lp is not None)

    # TESS dip significance / FAP at claimed P
    tess_verdict = 'none'
    tess_fap = None          # FAP at the exact claimed P (raw null)
    tess_fap_refined = None  # apples-to-apples FAP for the +/-0.3%-refined peak
    tess_snr = None
    if tess and 'fold' in tess:
        tess_fap = tess['fold']['at_claimed_P']['permutation_FAP']
        tess_snr = tess.get('per_cadence_SNR_quiescent')
        sig = tess['fold']['at_claimed_P']['deepest_bin_sigma']
        null_mean = tess['fold']['null_sigma_mean']
        ref = tess['fold']['refined_pm0.3pct']
        tess_fap_refined = ref.get('permutation_FAP_refined_null')
        sig_ref = ref.get('deepest_bin_sigma')
        ref_null_mean = ref.get('refined_null_sigma_mean')
        # A real eclipse must beat BOTH tests: low FAP at the claimed P AND,
        # when the period is optimized over +/-0.3%, still beat random periods
        # optimized the SAME way (refined null). The min-of-noise trap is a
        # refined peak that random periods match -> refined FAP near 1.
        real_at_claim = (tess_fap is not None and tess_fap < 0.01 and sig > null_mean + 2)
        real_refined = (tess_fap_refined is not None and tess_fap_refined < 0.01)
        if real_at_claim or real_refined:
            tess_verdict = (f'real dip (sig@P={sig:.1f}, FAP@P={tess_fap:.3f}; '
                            f'refined sig={sig_ref:.1f}, refined-null FAP={tess_fap_refined:.3f})')
        else:
            tess_verdict = (f'min-of-noise (sig@P={sig:.1f} vs null_mean={null_mean:.1f}, FAP@P={tess_fap:.3f}; '
                            f'refined sig={sig_ref:.1f} vs refined-null_mean={ref_null_mean:.1f}, '
                            f'refined-null FAP={tess_fap_refined:.3f})')
    elif tess and 'no_tess' in tess:
        tess_verdict = 'no TESS data'

    # ---- decision ----
    median_snr = float(np.median(snrs)) if snrs else None

    # Strong NOT_SUPPORTED signals
    if best_fap is not None and best_fap > 0.5:
        reasons.append(f'masked-LS FAP at claimed P = {best_fap:.2g} (>0.5; period vanishes when outbursts masked)')
    if all(ls_peak_aliases) and ls_peak_aliases:
        reasons.append('all masked-LS peaks are 1-sidereal-day aliases')
    if len(bls_peaks) >= 2 and not bls_band_agree:
        reasons.append(f'BLS best periods disagree across bands ({[round(b,4) if b else None for b in bls_peaks]} d)')
    if not bls_match_claim and not ls_match_claim:
        reasons.append('neither LS nor BLS peak matches the claimed period in any band')

    survives_signals = []
    if best_fap is not None and best_fap < 0.01:
        survives_signals.append(f'masked-LS FAP at claimed P = {best_fap:.2g}')
    if ls_match_claim:
        survives_signals.append('LS peak matches claimed P')
    if bls_band_agree and bls_match_claim:
        survives_signals.append('BLS bands agree and match claimed P')
    if tess_verdict.startswith('real dip'):
        survives_signals.append(tess_verdict)

    # eclipse claim handling
    eclipse_ok = None
    if tgt['eclipse_claim'] is not None:
        if tess_verdict.startswith('real dip'):
            eclipse_ok = True
        elif tess and 'fold' in tess:
            eclipse_ok = False
            reasons.append(f'claimed {int(tgt["eclipse_claim"]*100)}% eclipse is min-of-noise in TESS ({tess_verdict})')

    # final
    strong_against = (best_fap is not None and best_fap > 0.5) or (all(ls_peak_aliases) and len(ls_peak_aliases) > 0)
    strong_for = (best_fap is not None and best_fap < 0.001 and (ls_match_claim or (bls_band_agree and bls_match_claim)))

    if strong_for and (eclipse_ok is not False):
        verdict = 'SURVIVES'
    elif strong_against or (not survives_signals and reasons):
        verdict = 'NOT_SUPPORTED'
    elif survives_signals and not strong_against:
        verdict = 'AMBIGUOUS'
    else:
        verdict = 'AMBIGUOUS'

    return {
        'verdict': verdict,
        'reasons': reasons,
        'survives_signals': survives_signals,
        'masked_LS_FAP_at_claimed_P_best': best_fap,
        'median_per_cadence_SNR_ztf': median_snr,
        'bls_band_agree': bls_band_agree,
        'bls_match_claim': bls_match_claim,
        'ls_match_claim': ls_match_claim,
        'all_ls_peaks_sidereal_alias': bool(all(ls_peak_aliases)) if ls_peak_aliases else None,
        'tess_verdict': tess_verdict,
        'tess_permutation_FAP_at_claimed_P': tess_fap,
        'tess_permutation_FAP_refined_apples_to_apples': tess_fap_refined,
        'tess_per_cadence_SNR': tess_snr,
        'eclipse_claim': tgt['eclipse_claim'],
        'eclipse_real': eclipse_ok,
    }


# ---------------------------------------------------------------------------
# Per-target driver
# ---------------------------------------------------------------------------
def process(tgt):
    P0 = tgt['P_min'] / 1440.0
    out = {'name': tgt['name'], 'short': tgt['short'], 'ra': tgt['ra'], 'dec': tgt['dec'],
           'P_claimed_min': tgt['P_min'], 'P_claimed_d': P0, 'class': tgt['cls'],
           'eclipse_claim': tgt['eclipse_claim']}
    print(f"\n{'='*70}\n{tgt['name']}  P_claim={tgt['P_min']} min ({P0:.6f} d)\n{'='*70}", flush=True)

    # 1. ZTF
    rows, text = fetch_ztf(tgt['ra'], tgt['dec'])
    out['ztf'] = {'n_raw': len(rows)}
    if len(rows) == 0:
        out['ztf']['FATAL'] = 'no ZTF rows'
        out['ztf']['text_head'] = text[:300]
    else:
        mjd = col(rows, 'mjd').astype(float)
        mag = col(rows, 'mag').astype(float)
        err = col(rows, 'magerr').astype(float)
        cat = col(rows, 'catflags').astype(float)
        band = col(rows, 'filtercode')
        good = (cat == 0) & np.isfinite(mag) & np.isfinite(mjd)
        mjd, mag, err, band = mjd[good], mag[good], err[good], band[good]
        out['ztf']['n_catflag0'] = int(good.sum())
        out['ztf']['baseline_d'] = float(mjd.max() - mjd.min()) if good.sum() else 0.0
        out['ztf']['bands'] = {b: int((band == b).sum()) for b in ('zg', 'zr', 'zi')}
        for b in ('zg', 'zr', 'zi'):
            out['ztf'][b] = run_band(b, mjd, mag, err, band, P0)
            r = out['ztf'][b]
            if 'masked' in r:
                mk = r['masked']
                print(f"  {b}: n_q={r['n_quiescent']} S/N={r['per_cadence_SNR_quiescent']:.2f} "
                      f"| masked LS peak={mk['LS_peak_P_min']:.1f}min (alias={mk['LS_peak_is_sidereal_alias']}) "
                      f"FAP@P0={mk['LS_FAP_at_P0']} | BLS={mk['BLS_peak_P_min']:.1f}min", flush=True)
            else:
                print(f"  {b}: {r.get('skip','?')} (n={r.get('n')})", flush=True)

    # 5. TESS
    print("  fetching TESS ...", flush=True)
    try:
        out['tess'] = run_tess(tgt)
    except Exception as ex:
        out['tess'] = {'error': str(ex)[:300]}
    tv = out['tess']
    if 'fold' in tv:
        f = tv['fold']['at_claimed_P']
        print(f"  TESS [{tv.get('used_product')}]: S/N={tv.get('per_cadence_SNR_quiescent')} "
              f"sig@P0={f['deepest_bin_sigma']:.2f} null_mean={tv['fold']['null_sigma_mean']:.2f} "
              f"permFAP={f['permutation_FAP']:.3f}", flush=True)
    else:
        print(f"  TESS: {tv.get('no_tess', tv.get('error','?'))}", flush=True)

    # 6. verdict
    out['decision'] = decide_verdict(tgt, out['ztf'], out['tess'])
    print(f"  >>> VERDICT: {out['decision']['verdict']}", flush=True)
    for rr in out['decision']['reasons']:
        print(f"       - {rr}", flush=True)

    json.dump(out, open(f"/tmp/cv_revet_{tgt['short']}.json", 'w'), indent=1, default=str)
    print(f"  saved /tmp/cv_revet_{tgt['short']}.json", flush=True)
    return out


def build_report(results):
    lines = []
    lines.append("# CV period + eclipse re-vetting (2026-05-28)\n")
    lines.append("Re-vetting 4 cataclysmic-variable discoveries from a buggy photometry pipeline "
                 "that folded outburst-including light curves and measured eclipse depths as the "
                 "per-cycle minimum of noise-dominated cadences (per-cadence S/N < 1).\n")
    lines.append("Method (validated on the falsified 5th object CRTS J051419.8+011120): re-fetch ZTF, "
                 "mask outbursts (>0.75 mag brighter than per-band median), Lomb-Scargle + BLS on "
                 "masked data with bootstrap/analytic FAP, and (where a sector exists) fold the actual "
                 "TESS SPOC product at the claimed P with a permutation FAP over random periods.\n")
    lines.append("\n## Verdict table\n")
    lines.append("| target | claimed P (min) | per-cadence S/N | masked-LS FAP at claimed P | bands agree? | TESS verdict | FINAL VERDICT |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in results:
        d = r['decision']
        snr = d['median_per_cadence_SNR_ztf']
        snr_s = f"{snr:.2f}" if snr is not None else "n/a"
        fap = d['masked_LS_FAP_at_claimed_P_best']
        fap_s = f"{fap:.2g}" if fap is not None else "n/a"
        ba = ('yes' if d['bls_band_agree'] and d['bls_match_claim'] else
              ('LS@claim' if d['ls_match_claim'] else 'no'))
        tv = d['tess_verdict']
        lines.append(f"| {r['name']} | {r['P_claimed_min']} | {snr_s} | {fap_s} | {ba} | {tv} | **{d['verdict']}** |")

    # per-target detail
    for r in results:
        d = r['decision']
        lines.append(f"\n## {r['name']}  (claimed P={r['P_claimed_min']} min, class {r['class']})\n")
        z = r['ztf']
        if 'bands' in z:
            lines.append(f"- ZTF: {z['n_catflag0']} catflag0 epochs over {z['baseline_d']:.0f} d; "
                         f"bands {z['bands']}")
        for b in ('zg', 'zr', 'zi'):
            if b in z and 'masked' in z[b]:
                bb = z[b]
                mk = bb['masked']
                wo = bb.get('with_outbursts', {})
                lines.append(f"  - **{b}**: n_quiescent={bb['n_quiescent']}, "
                             f"per-cadence S/N={bb['per_cadence_SNR_quiescent']:.2f}. "
                             f"Masked LS peak={mk['LS_peak_P_min']:.2f} min "
                             f"(alias={mk['LS_peak_is_sidereal_alias']}, FAP={mk['LS_peak_FAP']}); "
                             f"LS power@claimed={mk['LS_power_at_P0']} FAP@claimed={mk['LS_FAP_at_P0']}; "
                             f"bootstrap FAP(peak)={mk.get('LS_bootstrap_FAP_peak')}. "
                             f"BLS peak={mk['BLS_peak_P_min']:.2f} min (power={mk['BLS_peak_power']}); "
                             f"BLS@claimed power={mk['BLS_power_at_P0']} depth={mk['BLS_depth_at_P0']}.")
                # show whether unmasked produced a strong (spurious) peak
                if wo:
                    lines.append(f"    (unmasked-for-comparison: LS peak={wo['LS_peak_P_min']:.1f} min "
                                 f"FAP@claimed={wo['LS_FAP_at_P0']}, BLS@claimed power={wo['BLS_power_at_P0']})")
        t = r['tess']
        if 'fold' in t:
            f = t['fold']
            ref = f['refined_pm0.3pct']
            lines.append(f"- TESS [{t.get('used_product')}], {t['n_total']} cadences, "
                         f"per-cadence S/N={t.get('per_cadence_SNR_quiescent')}. "
                         f"Fold @claimed P: deepest-bin sig={f['at_claimed_P']['deepest_bin_sigma']:.2f}, "
                         f"depth={f['at_claimed_P']['binned_depth']:.3f}, "
                         f"permutation FAP={f['at_claimed_P']['permutation_FAP']:.3f} "
                         f"(null sigma mean={f['null_sigma_mean']:.2f}, p99={f['null_sigma_p99']:.2f}).")
            lines.append(f"  - Refined +/-0.3%: sig={ref['deepest_bin_sigma']:.2f} at "
                         f"P={ref['P_best_min']:.2f} min, but apples-to-apples FAP "
                         f"(random periods refined the SAME way) = {ref['permutation_FAP_refined_null']:.3f} "
                         f"(refined-null mean={ref['refined_null_sigma_mean']:.2f}, "
                         f"p99={ref['refined_null_sigma_p99']:.2f}). A refined peak that random "
                         f"periods match is min-of-noise, not a detection.")
        else:
            lines.append(f"- TESS: {t.get('no_tess', t.get('error','n/a'))}")
        if d['reasons']:
            lines.append("- Reasons against: " + "; ".join(d['reasons']))
        if d['survives_signals']:
            lines.append("- Signals for: " + "; ".join(d['survives_signals']))
        lines.append(f"- **VERDICT: {d['verdict']}**")

    open('/tmp/cv_revet_report.md', 'w').write("\n".join(lines))
    print("\nSAVED /tmp/cv_revet_report.md")


def main():
    sel = sys.argv[1] if len(sys.argv) > 1 else None
    targets = [t for t in TARGETS if (sel is None or t['short'] == sel)]
    results = [process(t) for t in targets]
    if sel is None:
        build_report(results)
    return results


if __name__ == '__main__':
    main()
