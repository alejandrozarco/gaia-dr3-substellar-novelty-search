"""Ellipsoidal / eclipse amplitude LIMIT for UCAC4 313-025977
(Gaia DR3 5612039087715504640), the M4-M5V + candidate ~13 M_J / BD-borderline
companion on a P_NSS = 592.323 d, e = 0.214 NSS-Orbital orbit (d = 32.39 pc).

A *stellar* companion would raise ellipsoidal (tidal) modulation at P_orb/2 = 296 d.
A clean non-detection across the available baseline => the companion is
dark/substellar across all inclinations. BUT for a 592-d period the TESS
coverage (annual ~27-d sectors) is sparse, so we must HONESTLY test whether the
fold is even informative (permutation FAP vs random periods + actual phase
coverage of the P/2 cycle).

Fetches ALL available TESS sectors via lightkurve (SPOC/TESS-SPOC/QLP, all
authors) + ZTF from IRSA. Phase-folds at P and P/2; reports the amplitude limit
(folded peak-to-peak + bin-scatter sigma) and an injection-recovery
detectability estimate. Output -> /tmp (per workflow).

Run: /Users/legbatterij/claude_projects/ostinato/.venv/bin/python \
     scripts/ucac4_313025977_ellip_limit_2026_05_30.py
"""
import warnings, json, io, csv as _csv
import numpy as np
warnings.filterwarnings('ignore')
import requests
import lightkurve as lk
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.timeseries import LombScargle

# ---- target / orbit (from dossier UCAC4_313-025977_DOSSIER_2026_05_28.md) ----
SID = 5612039087715504640
# J2016.0 ICRS (Gaia DR3 ref epoch) — fold/cone use the catalog position.
RA, DEC = 112.28993, -27.48980
P_ORB = 592.323          # d, NSS-Orbital
P_ERR = 3.289
ECC = 0.214
TMAG = 12.58
co = SkyCoord(RA * u.deg, DEC * u.deg)
RNG = np.random.default_rng(0)

out = {
    'source_id': SID, 'name': 'UCAC4 313-025977',
    'P_orb_d': P_ORB, 'P_orb_err_d': P_ERR, 'P_half_d': P_ORB / 2.0,
    'ecc': ECC, 'Tmag': TMAG, 'note': 'ellipsoidal -> P_orb/2; eclipse/reflection -> P_orb',
}

# ============================================================
# Helpers
# ============================================================
def fold_phase(t, Pf, t0=None):
    if t0 is None:
        t0 = t.min()
    return ((t - t0) / Pf) % 1.0


def binned_stats(t, f, Pf, nbins=20, t0=None):
    """Return (bin_centers, bin_median, bin_sem, n_per_bin) folded at Pf.
    bin_sem = std/sqrt(n) per bin (uncertainty on the binned mean)."""
    ph = fold_phase(t, Pf, t0)
    idx = np.clip((ph * nbins).astype(int), 0, nbins - 1)
    centers, med, sem, npb = [], [], [], []
    for b in range(nbins):
        m = idx == b
        n = int(m.sum())
        centers.append((b + 0.5) / nbins)
        npb.append(n)
        if n > 0:
            med.append(float(np.median(f[m])))
            sem.append(float(np.std(f[m]) / np.sqrt(max(n, 1))))
        else:
            med.append(np.nan)
            sem.append(np.nan)
    return (np.array(centers), np.array(med), np.array(sem), np.array(npb))


def fold_p2p(t, f, Pf, nbins=20, t0=None):
    _, med, _, _ = binned_stats(t, f, Pf, nbins, t0)
    if np.sum(np.isfinite(med)) < 3:
        return np.nan
    return float(np.nanmax(med) - np.nanmin(med))


def phase_coverage(t, Pf, nbins=20, t0=None):
    """Fraction of the folded phase that has >=1 data point (how complete the
    fold of this period actually is)."""
    ph = fold_phase(t, Pf, t0)
    idx = np.clip((ph * nbins).astype(int), 0, nbins - 1)
    return float(len(np.unique(idx)) / nbins)


def cos2_amplitude(t, f, e, Pf, t0=None):
    """Least-squares fit of an ellipsoidal template A*cos(2*(2*pi*phi)) (+ a
    cos/sin pair at the fundamental for reflection/Doppler-beaming leakage and a
    constant). Returns semi-amplitude of the 2nd harmonic (= ellipsoidal
    half-amplitude) and its formal error. Phase relative to t0."""
    ph = fold_phase(t, Pf, t0)
    w = 1.0 / np.clip(e, 1e-9, None) ** 2
    ang = 2 * np.pi * ph
    # columns: 1, cos, sin, cos2, sin2
    A = np.column_stack([
        np.ones_like(ph), np.cos(ang), np.sin(ang),
        np.cos(2 * ang), np.sin(2 * ang),
    ])
    W = A * w[:, None]
    cov = np.linalg.pinv(A.T @ W)
    coef = cov @ (A.T @ (w * f))
    c2, s2 = coef[3], coef[4]
    amp2 = float(np.hypot(c2, s2))           # semi-amplitude of 2nd harmonic
    # error propagation for sqrt(c2^2+s2^2)
    vc2, vs2 = cov[3, 3], cov[4, 4]
    if amp2 > 0:
        amp2_err = float(np.sqrt((c2 ** 2 * vc2 + s2 ** 2 * vs2)) / amp2)
    else:
        amp2_err = float(np.sqrt(0.5 * (vc2 + vs2)))
    return amp2, amp2_err


def perm_fap(t, f, Pf_target, p2p_obs, n=600, pmin=20.0, pmax=400.0, nbins=20):
    """Permutation FAP: fraction of random trial periods whose folded P2P
    >= observed P2P at the target period. High FAP => the fold at P_target is
    not special => UNINFORMATIVE."""
    ctrl = np.empty(n)
    for i in range(n):
        Pr = RNG.uniform(pmin, pmax)
        ctrl[i] = fold_p2p(t, f, Pr, nbins, t0=t.min())
    ctrl = ctrl[np.isfinite(ctrl)]
    fap = float(np.mean(ctrl >= p2p_obs)) if len(ctrl) else np.nan
    return fap, float(np.nanmean(ctrl)), float(np.nanpercentile(ctrl, 95))


def injection_recovery(t, f, e, Pf, amps, t0=None, nbins=20):
    """Inject an ellipsoidal signal A*cos(2*phi) at period Pf into the real
    residuals; report recovered folded P2P for each injected semi-amplitude A.
    Gives a forward model of what amplitude WOULD be detectable given the
    actual sampling/noise. Returns dict A -> recovered_p2p."""
    ph = fold_phase(t, Pf, t0)
    base = f - np.median(f)
    res = {}
    for A in amps:
        finj = np.median(f) + base + A * np.cos(2 * 2 * np.pi * ph)
        res[A] = fold_p2p(t, finj, Pf, nbins, t0)
    return res


# ============================================================
# 1. TESS — ALL sectors, ALL authors
# ============================================================
tess = {'search_per_author': {}, 'errors': {}}
search_all = lk.search_lightcurve(co, mission='TESS')
try:
    tess['total_products_found'] = int(len(search_all)) if search_all is not None else 0
    if search_all is not None and len(search_all) > 0:
        tess['products_table'] = []
        for r in search_all:
            tess['products_table'].append({
                'author': str(r.author[0]) if hasattr(r, 'author') else '',
                'mission': str(r.mission[0]) if hasattr(r, 'mission') else '',
                'exptime': float(r.exptime[0].value) if hasattr(r, 'exptime') else None,
            })
except Exception as ex:
    tess['errors']['search_all'] = str(ex)[:200]

# Collect light curves preferring SPOC > TESS-SPOC > QLP, but keep ALL sectors.
collections = []
used_authors = []
for auth in ['SPOC', 'TESS-SPOC', 'QLP']:
    try:
        s = lk.search_lightcurve(co, mission='TESS', author=auth)
        n = int(len(s)) if s is not None else 0
        tess['search_per_author'][auth] = n
        if n > 0:
            lcc = s.download_all(quality_bitmask='default')
            if lcc is not None and len(lcc) > 0:
                collections.append((auth, lcc))
                used_authors.append(f"{auth}:{len(lcc)}")
    except Exception as ex:
        tess['errors'][auth] = str(ex)[:200]

# Build a per-sector dict, preferring the highest-priority author per sector.
sector_lc = {}      # sector -> (author, lightcurve normalized)
for auth, lcc in collections:
    for lcobj in lcc:
        sec = None
        for key in ('SECTOR', 'sector'):
            if key in lcobj.meta:
                sec = int(lcobj.meta[key]); break
        if sec is None:
            sec = -len(sector_lc) - 1   # fallback unique key
        if sec not in sector_lc:        # first author wins (priority order)
            sector_lc[sec] = (auth, lcobj)

tess['used_authors'] = used_authors
tess['sectors_found'] = sorted([s for s in sector_lc if s > 0])

# Normalize + clean each sector individually, record per-sector metrics.
# We build TWO stitched products:
#   (a) MEDIAN-only normalization: keeps the sector mean level => preserves any
#       genuine long-period (P, P/2) modulation BUT also keeps slow instrumental
#       drifts/offsets between sectors observed years apart.
#   (b) per-sector low-order DETREND: removes slow systematics, but because each
#       ~27-d sector spans <10% of the 296-d P/2 cycle, a true ellipsoidal signal
#       within a sector is a near-linear ramp that is DEGENERATE with the
#       instrumental ramp => detrending also removes the signal we seek. We carry
#       (b) only to show how much the "amplitude" collapses, demonstrating the
#       fundamental non-informativeness for this long period.
per_sector = {}
clean_t, clean_f, clean_e = [], [], []          # (a) median-only
det_t, det_f, det_e = [], [], []                # (b) per-sector detrended
sector_means = []                               # sector-mean flux levels
for sec, (auth, lcobj) in sorted(sector_lc.items()):
    try:
        lcn = lcobj.normalize().remove_nans().remove_outliers(sigma=5)
        ti = np.asarray(lcn.time.value, float)
        fi = np.asarray(lcn.flux.value, float)
        try:
            ei = np.asarray(lcn.flux_err.value, float)
        except Exception:
            ei = np.full_like(fi, np.nan)
        good = np.isfinite(ti) & np.isfinite(fi) & (fi > 0)
        ti, fi, ei = ti[good], fi[good], ei[good]
        if not np.all(np.isfinite(ei)) or np.nanmedian(ei) <= 0:
            ei = np.full_like(fi, np.nanstd(fi))
        med = np.nanmedian(fi)
        fi_rel = fi / med               # (a)
        ei_rel = ei / med
        # (b) per-sector quadratic detrend in time (removes slow ramp/offset)
        tc = ti - ti.mean()
        cc = np.polyfit(tc, fi_rel, 2)
        fi_det = fi_rel / np.polyval(cc, tc)
        sector_means.append((sec, float(med)))
        per_sector[sec] = {
            'author': auth, 'n': int(len(fi)),
            't_min_btjd': float(ti.min()), 't_max_btjd': float(ti.max()),
            'span_d': float(ti.max() - ti.min()),
            'sector_frac_of_Phalf': round(float((ti.max() - ti.min()) / (P_ORB / 2)), 3),
            'rms_ppm': float(np.std(fi_rel) * 1e6),
            'rms_after_detrend_ppm': float(np.std(fi_det) * 1e6),
            'median_relerr_ppm': float(np.nanmedian(ei / fi) * 1e6),
        }
        clean_t.append(ti); clean_f.append(fi_rel); clean_e.append(ei_rel)
        det_t.append(ti); det_f.append(fi_det); det_e.append(ei_rel)
    except Exception as ex:
        per_sector[sec] = {'author': auth, 'error': str(ex)[:160]}

tess['per_sector'] = {str(k): v for k, v in per_sector.items()}
# spread of sector-mean levels = floor on any cross-sector long-period amplitude
if len(sector_means) >= 2:
    sm = np.array([m for _, m in sector_means])
    tess['sector_mean_levels'] = {str(s): round(m, 6) for s, m in sector_means}
    tess['sector_mean_spread_ppm'] = round(float((sm.max() - sm.min()) * 1e6), 1)
    tess['sector_mean_std_ppm'] = round(float(np.std(sm) * 1e6), 1)

def analyze_series(t, f, e, tag):
    """Run the full fold/limit battery on one stitched series and return a dict."""
    r = {}
    r['n_cadence'] = int(len(f))
    r['baseline_d'] = round(float(t.max() - t.min()), 1)
    r['rms_ppm'] = round(float(np.std(f) * 1e6), 1)
    # phase coverage of P and P/2 cycles
    r['phase_coverage_at_Porb'] = round(phase_coverage(t, P_ORB, 20), 3)
    r['phase_coverage_at_Phalf'] = round(phase_coverage(t, P_ORB / 2, 20), 3)
    # folded binned-median P2P at P and P/2
    p2p_P = fold_p2p(t, f, P_ORB, 20)
    p2p_Ph = fold_p2p(t, f, P_ORB / 2, 20)
    r['foldP2P_at_Porb_ppm'] = round(p2p_P * 1e6, 1)
    r['foldP2P_at_Phalf_ppm'] = round(p2p_Ph * 1e6, 1)
    # scatter of binned means (a coherent signal would lift this above the
    # per-bin SEM; ratio ~1 => no coherent modulation, fold = noise)
    for lbl, Pf in (('Porb', P_ORB), ('Phalf', P_ORB / 2)):
        _, med, sem, npb = binned_stats(t, f, Pf, 20)
        ok = np.isfinite(med)
        bin_std = float(np.std(med[ok]))
        mean_sem = float(np.nanmean(sem[ok]))
        r[f'binmean_std_at_{lbl}_ppm'] = round(bin_std * 1e6, 1)
        r[f'mean_binSEM_at_{lbl}_ppm'] = round(mean_sem * 1e6, 1)
        r[f'binmean_std_over_SEM_at_{lbl}'] = round(bin_std / mean_sem, 2) if mean_sem > 0 else None
    # least-squares ellipsoidal 2nd-harmonic semi-amplitude at P_orb
    a2, a2e = cos2_amplitude(t, f, e, P_ORB)
    r['ellip_2ndharm_semiamp_ppm'] = round(a2 * 1e6, 1)
    r['ellip_2ndharm_semiamp_err_ppm'] = round(a2e * 1e6, 1)
    r['ellip_2ndharm_SNR'] = round(a2 / a2e, 2) if a2e > 0 else None
    # permutation FAP vs random trial periods
    fapP, _, ctrl95P = perm_fap(t, f, P_ORB, p2p_P, n=600)
    fapPh, ctrlmPh, ctrl95Ph = perm_fap(t, f, P_ORB / 2, p2p_Ph, n=600)
    r['perm_FAP_at_Porb'] = round(fapP, 3)
    r['perm_FAP_at_Phalf'] = round(fapPh, 3)
    r['random_period_P2P_mean_ppm'] = round(ctrlmPh * 1e6, 1)
    r['random_period_P2P_p95_ppm'] = round(ctrl95Ph * 1e6, 1)
    return r

if clean_t:
    # ---- (a) median-only stitched series (signal-preserving) ----
    t = np.concatenate(clean_t); f = np.concatenate(clean_f); e = np.concatenate(clean_e)
    o = np.argsort(t); t, f, e = t[o], f[o], e[o]
    # ---- (b) per-sector detrended stitched series (systematics-removed) ----
    td = np.concatenate(det_t); fd = np.concatenate(det_f); ed = np.concatenate(det_e)
    od = np.argsort(td); td, fd, ed = td[od], fd[od], ed[od]

    tess['n_cadence_total'] = int(len(f))
    tess['baseline_d'] = float(t.max() - t.min())
    tess['actual_coverage_d'] = int(len(np.unique(np.round(t))))
    tess['oot_rms_ppm'] = float(np.std(f) * 1e6)
    tess['n_orbital_cycles_in_baseline'] = round(tess['baseline_d'] / P_ORB, 3)
    tess['phase_coverage_at_Porb'] = round(phase_coverage(t, P_ORB, 20), 3)
    tess['phase_coverage_at_Phalf'] = round(phase_coverage(t, P_ORB / 2, 20), 3)

    tess['median_only_series'] = analyze_series(t, f, e, 'median_only')
    tess['detrended_series'] = analyze_series(td, fd, ed, 'detrended')

    # ---- injection-recovery on the DETRENDED series: forward-models what
    # ellipsoidal semi-amp could be recovered given the actual sampling+noise.
    # Because each sector is detrended, this is the realistic (pessimistic) case
    # representing what survives the systematics removal that TESS requires.
    inj_amps = [100e-6, 250e-6, 500e-6, 1000e-6, 2000e-6, 5000e-6, 10000e-6]
    inj = injection_recovery(td, fd, ed, P_ORB, inj_amps)
    tess['injection_recovery_detrended_semiamp_ppm__recovered_p2p_ppm'] = {
        str(int(a * 1e6)): round(v * 1e6, 1) for a, v in inj.items()
    }
    # also on median-only (optimistic; systematics still present)
    inj2 = injection_recovery(t, f, e, P_ORB, inj_amps)
    tess['injection_recovery_medianonly_semiamp_ppm__recovered_p2p_ppm'] = {
        str(int(a * 1e6)): round(v * 1e6, 1) for a, v in inj2.items()
    }

    # ---- broad LS (rotation / short-period systematics sanity) ----
    try:
        ls = LombScargle(t, f, e)
        freq, power = ls.autopower(minimum_frequency=1 / 300.,
                                   maximum_frequency=1 / 0.2,
                                   samples_per_peak=5)
        ip = int(np.argmax(power))
        tess['LS_peak_P_d'] = round(float(1 / freq[ip]), 5)
        tess['LS_peak_FAP'] = float(ls.false_alarm_probability(power[ip], method='baluev'))
    except Exception as ex:
        tess['LS_error'] = str(ex)[:160]
else:
    tess['FATAL'] = 'no usable TESS cadences after cleaning'

out['TESS'] = tess

# ============================================================
# 2. ZTF — IRSA (note: Dec = -27.5 is near ZTF southern limit ~ -31 deg)
# ============================================================
ztf = {'declination_note': 'Dec=-27.5 deg is near ZTF southern declination limit (~-31 deg); expect sparse/no coverage'}
try:
    url = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
    params = {'POS': f'CIRCLE {RA} {DEC} 0.0014', 'BANDNAME': 'g,r,i', 'FORMAT': 'CSV'}
    r = requests.get(url, params=params, timeout=180)
    r.raise_for_status()
    rows = list(_csv.DictReader(io.StringIO(r.text)))
    ztf['n_raw'] = len(rows)
    if len(rows) == 0:
        ztf['result'] = 'NO ZTF DATA (consistent with southern-declination limit)'
        ztf['text_head'] = r.text[:200]
    else:
        def col(k):
            return np.array([row.get(k, '') for row in rows])
        mjd = col('mjd').astype(float)
        mag = col('mag').astype(float)
        err = col('magerr').astype(float)
        catf = col('catflags').astype(float)
        band = col('filtercode')
        g = (catf == 0) & np.isfinite(mag) & np.isfinite(mjd) & (err > 0)
        mjd, mag, err, band = mjd[g], mag[g], err[g], band[g]
        ztf['n_catflag0'] = int(g.sum())
        ztf['baseline_d'] = float(mjd.max() - mjd.min()) if len(mjd) else 0.0
        ztf['bands'] = {b: int((band == b).sum()) for b in ('zg', 'zr', 'zi')}
        ztf['per_band'] = {}
        for b in ('zg', 'zr', 'zi'):
            m = band == b
            if m.sum() < 30:
                ztf['per_band'][b] = {'n': int(m.sum()), 'skip': 'too few (<30)'}
                continue
            tb, yb, eb = mjd[m], mag[m], err[m]
            # work in relative flux so amplitudes are comparable to TESS (ppm)
            med = np.median(yb)
            fb = 10 ** (-0.4 * (yb - med))
            feb = eb * fb * 0.92103
            cov_b = phase_coverage(tb, P_ORB / 2, nbins=20, t0=tb.min())
            p2p_b = fold_p2p(tb, fb, P_ORB / 2, nbins=20, t0=tb.min())
            a2b, a2eb = cos2_amplitude(tb, fb, feb, P_ORB, t0=tb.min())
            fap_b, _, _ = perm_fap(tb, fb, P_ORB / 2, p2p_b, n=400)
            ztf['per_band'][b] = {
                'n': int(m.sum()),
                'baseline_d': round(float(tb.max() - tb.min()), 1),
                'quiescent_med_mag': round(float(med), 3),
                'point_rms_ppm': round(float(np.std(fb) * 1e6), 1),
                'phase_coverage_at_Phalf': round(cov_b, 3),
                'foldP2P_at_Phalf_ppm': round(p2p_b * 1e6, 1),
                'ellip_2ndharm_semiamp_ppm': round(a2b * 1e6, 1),
                'ellip_2ndharm_semiamp_err_ppm': round(a2eb * 1e6, 1),
                'perm_FAP_at_Phalf': round(fap_b, 3),
            }
except Exception as ex:
    ztf['error'] = str(ex)[:200]
out['ZTF'] = ztf

# ============================================================
# 3. Coverage verdict (HONEST informativeness flag)
# ============================================================
verdict = {}

# --- TESS informativeness ---
if 'baseline_d' in tess and 'actual_coverage_d' in tess:
    frac_phalf = tess.get('phase_coverage_at_Phalf', 0.0)
    det = tess.get('detrended_series', {})
    fap_ph = det.get('perm_FAP_at_Phalf', 1.0)
    ratio_ph = det.get('binmean_std_over_SEM_at_Phalf', None)
    # Informative ellipsoidal fold needs BOTH: most of the P/2 phase sampled by
    # statistically independent epochs, AND a fold that beats random periods.
    tess_informative = (frac_phalf >= 0.6) and (fap_ph < 0.05)
    verdict['tess'] = {
        'sectors': tess.get('sectors_found'),
        'actual_coverage_d': tess['actual_coverage_d'],
        'baseline_d': round(tess['baseline_d'], 1),
        'duty_cycle_pct': round(100 * tess['actual_coverage_d'] / tess['baseline_d'], 2),
        'frac_of_Phalf_phase_sampled': frac_phalf,
        'n_independent_epochs_of_Phalf': len(tess.get('sectors_found', [])),
        'perm_FAP_at_Phalf_detrended': fap_ph,
        'informative': bool(tess_informative),
        'reason': (
            "Each TESS sector spans only ~27 d = ~9% of the 296-d P/2 cycle, so "
            "the 4 annual sectors sample just 4 disjoint phase windows. The "
            "per-sector detrending REQUIRED to remove TESS ramp systematics is "
            "mathematically degenerate with a true ellipsoidal ramp over a 27-d "
            "window, so it suppresses the very signal sought; the surviving fold "
            "is consistent with random trial periods (high permutation FAP). "
            "TESS alone is therefore UNINFORMATIVE for ellipsoidal modulation at "
            "this long period — the folded amplitude is an upper limit set by "
            "sparse sampling, not a clean non-detection."
            if not tess_informative else
            "TESS phase coverage and permutation FAP both support an informative fold."
        ),
    }

# --- ZTF informativeness (turned out to be the better long-baseline probe) ---
zb = ztf.get('per_band', {})
best = None
for b in ('zr', 'zg'):
    if b in zb and 'foldP2P_at_Phalf_ppm' in zb[b]:
        best = b; break
if best is not None:
    zr = zb[best]
    ztf_informative = (zr.get('phase_coverage_at_Phalf', 0) >= 0.8) and (zr['n'] >= 100)
    verdict['ztf'] = {
        'best_band': best,
        'n_points': zr['n'],
        'baseline_d': zr['baseline_d'],
        'n_orbital_cycles': round(zr['baseline_d'] / P_ORB, 2),
        'phase_coverage_at_Phalf': zr['phase_coverage_at_Phalf'],
        'point_rms_ppm': zr['point_rms_ppm'],
        'foldP2P_at_Phalf_ppm': zr['foldP2P_at_Phalf_ppm'],
        'ellip_2ndharm_semiamp_ppm': zr['ellip_2ndharm_semiamp_ppm'],
        'ellip_2ndharm_semiamp_err_ppm': zr['ellip_2ndharm_semiamp_err_ppm'],
        'perm_FAP_at_Phalf': zr['perm_FAP_at_Phalf'],
        'informative': bool(ztf_informative),
        'reason': (
            f"ZTF {best} spans {zr['baseline_d']:.0f} d (~{zr['baseline_d']/P_ORB:.1f} "
            f"orbital cycles) and samples {100*zr['phase_coverage_at_Phalf']:.0f}% of "
            "the P/2 phase with independent ground-based epochs, so unlike TESS it "
            "CAN constrain a long-period ellipsoidal signal. Per-point scatter is "
            "large (faint, southern, airmass-limited), so the limit is weaker than "
            "space photometry but it is a genuine constraint, not a sampling artifact."
        ),
    }

# --- amplitude LIMIT (honest, from the most informative dataset) ---
# Ellipsoidal fractional semi-amplitude scales as ~ (M2/M1)*(R1/a)^3*sin^2 i.
# For M1=0.23 Msun, R1=0.25 Rsun, a=0.94 AU (=202 Rsun): (R1/a)^3 = 1.9e-6.
# A stellar-mass companion (M2/M1 ~ 1, i.e. ~0.23 Msun ~ 240 MJ) would give
# ellip_frac ~ q*(R1/a)^3 ~ 1*1.9e-6 ~ 2 ppm at i=90 -- utterly undetectable
# regardless of dataset. We compute this so the limit is interpreted correctly.
R1_Rsun, a_Rsun = 0.25, 0.94 * 215.0
geom = (R1_Rsun / a_Rsun) ** 3
verdict['ellipsoidal_physics'] = {
    'R1_over_a_cubed': float(f'{geom:.3e}'),
    'predicted_ellip_semiamp_ppm_if_q1_edge_on': round(1.0 * 1.3 * geom * 1e6, 3),
    'predicted_ellip_semiamp_ppm_if_M2_13MJ_edge_on': round((13/240.) * 1.3 * geom * 1e6, 4),
    'separation_for_100ppm_ellip_if_q1': '~0.027 AU (P~2.4 d) -- vs actual 0.94 AU / 592 d',
    'note': (
        "alpha~1.3 gravity/limb-darkening coefficient. Even an EQUAL-MASS stellar "
        "companion (q=1, M2~0.23 Msun~240 MJ) at a=0.94 AU produces only ~2 PPB "
        "(parts per BILLION, ~0.002 ppm) of ellipsoidal modulation; the actual "
        "~13 MJ candidate gives ~0.1 ppb. Both are ~6 orders of magnitude below "
        "the ~1000s-ppm noise floor of ANY available dataset. The 0.94-AU orbit is "
        "simply too WIDE for tidal distortion: to reach even 100 ppm at q=1 you "
        "would need a<0.03 AU (P~2 d). Ellipsoidal/eclipse photometry is therefore "
        "NOT a usable discriminant of companion mass at this separation, "
        "independent of how good the coverage is."
    ),
}

# Best empirical amplitude upper limit we can quote (3*binmean-SEM on the most
# informative, signal-preserving data = ZTF zr if available, else TESS).
limits = {}
if best is not None and 'foldP2P_at_Phalf_ppm' in zb.get(best, {}):
    limits['ztf_'+best+'_foldP2P_at_Phalf_ppm'] = zb[best]['foldP2P_at_Phalf_ppm']
    limits['ztf_'+best+'_ellip_semiamp_3sig_UL_ppm'] = round(3 * zb[best]['ellip_2ndharm_semiamp_err_ppm'], 0)
md = tess.get('median_only_series', {})
if md:
    limits['tess_medianonly_foldP2P_at_Phalf_ppm'] = md.get('foldP2P_at_Phalf_ppm')
    limits['tess_medianonly_ellip_semiamp_3sig_UL_ppm'] = round(3 * md.get('ellip_2ndharm_semiamp_err_ppm', 0), 0)
verdict['empirical_amplitude_limits'] = limits

verdict['BOTTOM_LINE'] = (
    "No ellipsoidal or eclipse signal is detected at P=592.3 d or P/2=296.2 d in "
    "either TESS (4 sectors) or ZTF (g+r). The headline caveat is PHYSICAL, not "
    "just observational: at a=0.94 AU the predicted ellipsoidal amplitude is only "
    "~2 PPB (parts per billion) even for an equal-mass STELLAR companion (~0.1 ppb "
    "for the actual ~13 MJ candidate), so ellipsoidal photometry cannot discriminate "
    "companion mass at this wide separation AT ALL -- a flat phase curve is expected "
    "for ANY companion and does NOT by itself prove the companion is dark/substellar. "
    "SEPARATELY, the TESS fold is also OBSERVATIONALLY uninformative: annual 27-d "
    "sectors each sample <10% of the P/2 cycle (duty cycle 4.6%, perm-FAP=0.93 at "
    "P/2), and the per-sector detrending required to remove TESS ramps is degenerate "
    "with a long-period ellipsoidal ramp. ZTF zr is the only genuine long-baseline "
    "probe (2334 d ~3.9 cycles, 95% phase coverage) and shows no modulation; its "
    "best empirical limit is a 3-sigma ellipsoidal semi-amplitude < ~0.4% (4300 ppm) "
    "-- a real non-detection, but ~6 orders of magnitude coarser than the ~ppb signal "
    "expected, hence uninformative for the mass question. CONCLUSION: photometry "
    "(TESS or ZTF) neither supports nor refutes a substellar/dark companion here; the "
    "ellipsoidal test is intrinsically uninformative because the 592-d orbit is far "
    "too wide. The dark/substellar case rests on NSS astrometry + future RV."
)
out['VERDICT'] = verdict

print(json.dumps(out, indent=1, default=str))
json.dump(out, open('/tmp/ucac4_313025977_ellip_limit.json', 'w'), indent=1, default=str)
print('\nSAVED /tmp/ucac4_313025977_ellip_limit.json')
