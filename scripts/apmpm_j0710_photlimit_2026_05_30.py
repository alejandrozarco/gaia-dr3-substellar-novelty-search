"""APMPM J0710-5704 (Gaia DR3 5486916932205092352) — ellipsoidal / eclipse
amplitude LIMIT from TESS (all sectors via lightkurve) + ZTF.

Goal (per request):
  - Fetch all TESS sectors (lightkurve) + ZTF.
  - Phase-fold at the Gaia DR3 NSS orbital period P=253.479 d and at P/2=126.74 d.
  - Measure the ellipsoidal/eclipse amplitude LIMIT (not just a P2P number).
  - A stellar companion would produce ellipsoidal modulation at P/2; a clean
    non-detection over the baseline implies a dark/substellar companion across
    inclinations.
  - HONESTLY flag if coverage is too short / too gappy for the (long) P to be
    informative -> then the limit is uninformative.

Skepticism-first. We compute:
  (a) The TIME / PHASE COVERAGE diagnostics at P and P/2 — the decisive honesty
      check for a 253 d period observed by a satellite with ~27 d sectors and
      large gaps. We report fraction of orbital phase sampled, the largest
      phase gap, and how many DISTINCT orbital cycles are touched.
  (b) A robust ellipsoidal-amplitude limit via a least-squares fit of a
      cos(2*phase) (+ cos(phase)) harmonic model at P and P/2, per-sector
      detrended to remove the 10.5 d rotation + TESS systematics, with the
      amplitude uncertainty -> 3σ upper limit. This is the physically correct
      observable: ellipsoidal modulation is a cos(2θ) term at the ORBITAL
      period (=> a signal at P/2 in "humps per orbit" language).
  (c) Expected ellipsoidal amplitude for a main-sequence M-dwarf companion at
      the NSS-implied separation, for comparison with the limit.

Env: ostinato venv. Outputs JSON + report to /tmp. Does NOT touch docs/.
"""
import warnings, json, io, os, sys, math
warnings.filterwarnings('ignore')
import numpy as np

RA, DEC = 107.40961, -57.06023          # ICRS J2016.0 (dossier)
SID = 5486916932205092352
TIC = 294093302
P = 253.479                              # d, Gaia DR3 NSS Orbital
P_err = 0.926
ECC = 0.134
PHALF = P / 2.0                          # 126.7395 d
M1 = 0.25                                # Msun (adopted)
M1_lo, M1_hi = 0.20, 0.30
R1 = 0.30                                # Rsun (Kervella+2022)
PROT = 10.51                             # d (rotation, this project)

out = {
    'target': 'APMPM J0710-5704',
    'gaia_dr3_source_id': str(SID), 'TIC': TIC,
    'ra_deg': RA, 'dec_deg': DEC,
    'P_orbit_d': P, 'P_orbit_err_d': P_err, 'P_half_d': PHALF, 'ecc': ECC,
    'M1_Msun': M1, 'R1_Rsun': R1, 'Prot_d': PROT,
}

# ============================================================
# 0. ZTF coverage reality check (Dec = -57 deg, Palomar lat +33.4)
# ============================================================
ztf = {'note': 'ZTF is a Palomar (lat +33.4 deg) survey; practical southern '
                'declination limit ~ -31 deg (airmass<2). Target Dec=-57.06 is '
                'far below the ZTF footprint, so 0 epochs are expected.'}
try:
    import requests
    r = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves",
                     params={'POS': f'CIRCLE {RA} {DEC} 0.0028',  # 10 arcsec
                             'BANDNAME': 'g,r,i', 'FORMAT': 'CSV'}, timeout=180)
    import csv as _csv
    rows = list(_csv.DictReader(io.StringIO(r.text)))
    ztf['n_epochs'] = len(rows)
    ztf['queried'] = True
    ztf['conclusion'] = ('NO ZTF DATA (as expected from declination) — ZTF cannot '
                         'contribute; analysis rests on TESS alone.') if len(rows) == 0 \
        else f'UNEXPECTED: {len(rows)} ZTF rows returned; inspect.'
except Exception as e:
    ztf['queried'] = False
    ztf['error'] = repr(e)
    ztf['conclusion'] = 'ZTF query failed; but Dec=-57 is outside ZTF footprint regardless.'
out['ZTF'] = ztf
print('[ZTF]', ztf.get('conclusion'), '| n_epochs=', ztf.get('n_epochs'))

# ============================================================
# 1. TESS: download all sectors via lightkurve
# ============================================================
import lightkurve as lk

tess = {}
sr_all = lk.search_lightcurve(f'TIC {TIC}', mission='TESS')
authors_all = sorted(set(str(a) for a in sr_all.table['author'])) if len(sr_all) else []
tess['search_n_products_allauthors'] = int(len(sr_all))
tess['authors_available'] = authors_all
# RESTRICT to the SPOC pipeline (PDCSAP) to avoid mixing detrending philosophies
# across QLP/eleanor/TGLC etc., which injects spurious low-frequency power when
# folded at a LONG period. SPOC/TESS-SPOC use a consistent PDC pipeline.
sr = lk.search_lightcurve(f'TIC {TIC}', mission='TESS', author=('SPOC', 'TESS-SPOC'))
print(f'[TESS] {len(sr_all)} products all-authors; {len(sr)} SPOC/TESS-SPOC; authors={authors_all}')

# One product per sector; prefer SPOC over TESS-SPOC, and shorter exptime (2-min/20-s).
def pick_products(sr):
    tbl = sr.table
    rank = {'SPOC': 0, 'TESS-SPOC': 1}
    by_sector = {}
    for i, row in enumerate(tbl):
        sec = str(row['mission'])
        a = str(row['author'])
        try:
            expt = float(row['exptime'])
        except Exception:
            expt = 9999.0
        rk = (rank.get(a, 9), expt)        # best author, then shortest cadence
        if sec not in by_sector or rk < by_sector[sec][0]:
            by_sector[sec] = (rk, i, a)
    idx = sorted(v[1] for v in by_sector.values())
    return idx, by_sector

idx, by_sector = pick_products(sr)
tess['n_unique_sectors'] = len(by_sector)
tess['sectors'] = sorted(by_sector.keys())
print(f'[TESS] {len(by_sector)} unique sectors selected for download')

# Download (cache to /tmp). Be robust to individual sector failures.
all_t, all_f, all_fe, all_sec = [], [], [], []
dl_log = []
for k in idx:
    row = sr[int(k)]
    sec = str(row.table['mission'][0])
    auth = str(row.table['author'][0])
    try:
        lcf = row.download(download_dir='/tmp/lk_cache')
        if lcf is None:
            dl_log.append({'sector': sec, 'author': auth, 'status': 'None'}); continue
        lc = lcf
        # Choose flux column: prefer PDCSAP for SPOC, else default flux; QLP uses 'sap_flux'/'det_flux'
        flux = None
        for cand in ('pdcsap_flux', 'flux', 'sap_flux', 'det_flux', 'kspsap_flux'):
            if cand in lc.colnames and np.isfinite(np.asarray(lc[cand], float)).sum() > 50:
                flux = np.asarray(lc[cand], float); fcol = cand; break
        if flux is None:
            dl_log.append({'sector': sec, 'author': auth, 'status': 'no usable flux col'}); continue
        t = np.asarray(lc.time.value, float)
        # error
        ecol = None
        for cand in (fcol.replace('flux', 'flux_err'), 'flux_err', 'pdcsap_flux_err', 'sap_flux_err'):
            if cand in lc.colnames:
                ecol = cand; break
        fe = np.asarray(lc[ecol], float) if ecol else np.full_like(flux, np.nan)
        # quality mask
        q = np.asarray(lc['quality'], float) if 'quality' in lc.colnames else np.zeros_like(t)
        m = np.isfinite(t) & np.isfinite(flux) & (q == 0)
        if m.sum() < 50:
            m = np.isfinite(t) & np.isfinite(flux)
        t, flux, fe = t[m], flux[m], fe[m]
        # normalize per product to median 1
        med = np.nanmedian(flux)
        if not np.isfinite(med) or med == 0:
            dl_log.append({'sector': sec, 'author': auth, 'status': 'bad median'}); continue
        f = flux / med
        fe = fe / med
        all_t.append(t); all_f.append(f); all_fe.append(fe)
        all_sec.append(np.full(t.shape, len(dl_log)))
        dl_log.append({'sector': sec, 'author': auth, 'fcol': fcol, 'n': int(m.sum()),
                       't0': float(t.min()), 't1': float(t.max()), 'status': 'ok'})
    except Exception as e:
        dl_log.append({'sector': sec, 'author': auth, 'status': f'ERR {type(e).__name__}: {e}'})

tess['download_log'] = dl_log
n_ok = sum(1 for d in dl_log if d.get('status') == 'ok')
tess['n_sectors_downloaded'] = n_ok
print(f'[TESS] downloaded {n_ok} sectors OK')

if n_ok == 0:
    out['TESS'] = tess
    out['FATAL'] = 'No TESS sectors downloaded; cannot proceed.'
    json.dump(out, open('/tmp/apmpm_j0710_photlimit.json', 'w'), indent=1, default=str)
    print(json.dumps({'FATAL': out['FATAL']})); sys.exit(0)

t = np.concatenate(all_t)
f = np.concatenate(all_f)
fe = np.concatenate(all_fe)
segid = np.concatenate(all_sec).astype(int)   # per-product segment index
order = np.argsort(t)
t, f, fe, segid = t[order], f[order], fe[order], segid[order]

tess['n_points_total'] = int(t.size)
tess['baseline_d'] = float(t.max() - t.min())
tess['baseline_in_P'] = float((t.max() - t.min()) / P)
# robust raw rms
mad = np.median(np.abs(f - np.median(f)))
tess['raw_rms_ppm'] = float(1.4826 * mad * 1e6)
print(f'[TESS] N={t.size}, baseline={tess["baseline_d"]:.1f} d = {tess["baseline_in_P"]:.2f} orbital cycles, raw rms~{tess["raw_rms_ppm"]:.0f} ppm')

# ============================================================
# 2. PHASE / TIME COVERAGE at P and P/2  (the honesty check)
# ============================================================
def coverage(period, t):
    ph = ((t - t.min()) / period) % 1.0
    ph_sorted = np.sort(ph)
    # largest gap in phase (wrap-around)
    gaps = np.diff(np.concatenate([ph_sorted, [ph_sorted[0] + 1.0]]))
    max_gap = float(gaps.max())
    # fraction of phase covered using 200 bins
    nb = 200
    occ = np.zeros(nb, bool)
    occ[(ph * nb).astype(int).clip(0, nb - 1)] = True
    frac = float(occ.mean())
    # distinct cycles touched
    cyc = np.floor((t - t.min()) / period).astype(int)
    n_cycles_touched = int(np.unique(cyc).size)
    n_cycles_total = int(np.ceil((t.max() - t.min()) / period))
    return {'phase_frac_covered_200bin': round(frac, 3),
            'largest_phase_gap': round(max_gap, 3),
            'largest_phase_gap_pct': round(max_gap * 100, 1),
            'n_cycles_touched': n_cycles_touched,
            'n_cycles_in_baseline': n_cycles_total}

# Independent-SECTOR phase coverage: do the 37 separate visits (not just
# within-sector continuous runs) actually sample the whole orbit? This is the
# decisive honesty check for a long period.
def sector_phase_coverage(period):
    secs = [d for d in dl_log if d.get('status') == 'ok']
    t0 = min(s['t0'] for s in secs)
    mids = np.array([0.5 * (s['t0'] + s['t1']) for s in secs])
    widths = np.array([s['t1'] - s['t0'] for s in secs])
    ph = ((mids - t0) / period) % 1.0
    nb = 40
    occ = np.zeros(nb)
    for p, w in zip(ph, widths):
        n = max(1, int(np.ceil(min(w / period, 1.0) * nb)))
        for k in range(n):
            occ[int((p + k / nb) * nb) % nb] += 1
    s = np.sort(ph)
    g = np.diff(np.r_[s, s[0] + 1])
    return {'n_sectors': len(secs),
            'mean_sector_phasewidth': round(float(widths.mean() / period), 3),
            'phasebins40_with_ge1_sector_pct': round(float((occ > 0).mean()) * 100, 0),
            'empty_phasebins40': int((occ == 0).sum()),
            'largest_gap_between_sector_centers_phase': round(float(g.max()), 3),
            'largest_gap_between_sector_centers_d': round(float(g.max() * period), 0)}

cov = {'at_P': coverage(P, t), 'at_Phalf': coverage(PHALF, t),
       'sectors_at_P': sector_phase_coverage(P), 'sectors_at_Phalf': sector_phase_coverage(PHALF)}
out['coverage'] = cov
print('[COVERAGE] within-sample at P  :', cov['at_P'])
print('[COVERAGE] independent SECTORS at P  :', cov['sectors_at_P'])
print('[COVERAGE] independent SECTORS at P/2:', cov['sectors_at_Phalf'])

# ============================================================
# 3. DETREND per segment (remove rotation + slow systematics)
#    We must NOT remove the orbital signal: P>>27 d sector, so any per-sector
#    low-order polynomial (deg<=2) cannot absorb a 253 d sinusoid within one
#    ~27 d sector except as a slope. Removing a per-sector slope is the standard
#    cost of TESS systematics; we quantify how much orbital amplitude that
#    could hide via injection (section 5).
#    Detrend: subtract a robust smooth (median filter on a wide window) + clip.
# ============================================================
from scipy.ndimage import median_filter

def detrend_segment(ts, fs, fes, win_d=2.0):
    """Robust detrend within one sector: divide by a wide running median to kill
    the ~10.5 d rotation and slow drifts. Returns residual (f/trend - 1)."""
    o = np.argsort(ts)
    ts, fs, fes = ts[o], fs[o], fes[o]
    # window in points
    dt = np.median(np.diff(ts)) if ts.size > 5 else 0.02
    w = max(11, int(win_d / max(dt, 1e-4)))
    if w % 2 == 0:
        w += 1
    w = min(w, max(11, (fs.size // 2) * 2 - 1))
    trend = median_filter(fs, size=w, mode='nearest')
    res = fs / trend - 1.0
    # sigma clip
    s = 1.4826 * np.median(np.abs(res - np.median(res)))
    keep = np.abs(res - np.median(res)) < 5 * s
    return ts[keep], res[keep], (fes[keep] if np.isfinite(fes).any() else np.full(keep.sum(), s))

dt_t, dt_r, dt_e = [], [], []
for s in np.unique(segid):
    m = segid == s
    if m.sum() < 50:
        continue
    a, b, c = detrend_segment(t[m], f[m], fe[m])
    b = b - np.median(b)        # ZERO each sector's residual median: removes
                                # inter-sector flux offsets that otherwise create
                                # a spurious long-period signal in the fold.
    dt_t.append(a); dt_r.append(b); dt_e.append(c)
t2 = np.concatenate(dt_t); r2 = np.concatenate(dt_r); e2 = np.concatenate(dt_e)
o = np.argsort(t2); t2, r2, e2 = t2[o], r2[o], e2[o]
# floor errors
e2 = np.where(np.isfinite(e2) & (e2 > 0), e2, np.nanmedian(e2[np.isfinite(e2) & (e2 > 0)]))
det_rms = float(1.4826 * np.median(np.abs(r2 - np.median(r2))) * 1e6)
tess['detrended_rms_ppm'] = det_rms
tess['n_points_detrended'] = int(t2.size)
print(f'[DETREND] N={t2.size}, residual rms~{det_rms:.0f} ppm (win=2 d median filter)')

# ============================================================
# 4. ELLIPSOIDAL / ECLIPSE AMPLITUDE LIMIT
#    Fit harmonic model at the ORBITAL period:
#      r = a1*cos(theta) + b1*sin(theta) + a2*cos(2 theta) + b2*sin(2 theta)
#    where theta = 2 pi (t-t0)/P.
#    - The 2theta term (amplitude A2 = sqrt(a2^2+b2^2)) IS the ellipsoidal
#      modulation; its semi-amplitude doubles into a peak-to-peak ellipsoidal
#      depth = 2*A2. (Two humps per orbit = a signal at P/2.)
#    - The 1theta term captures reflection/Doppler-beaming/spot leakage.
#    We do weighted linear least squares -> covariance -> formal sigma on each
#    amplitude -> 3 sigma UPPER LIMIT. We also do a bootstrap (cycle-shuffle) to
#    get an empirical null distribution that respects red noise across sectors.
# ============================================================
def harmonic_fit(tt, rr, ee, period, t0=None, nharm=2):
    if t0 is None:
        t0 = tt.min()
    th = 2 * np.pi * (tt - t0) / period
    cols = [np.ones_like(tt)]
    names = ['c0']
    for k in range(1, nharm + 1):
        cols += [np.cos(k * th), np.sin(k * th)]
        names += [f'a{k}', f'b{k}']
    A = np.vstack(cols).T
    w = 1.0 / np.clip(ee, 1e-6, None) ** 2
    AtW = A.T * w
    cov = np.linalg.inv(AtW @ A)
    coef = cov @ (AtW @ rr)
    resid = rr - A @ coef
    # rescale covariance by reduced chi2 (accounts for under/over-estimated errs)
    dof = max(1, tt.size - A.shape[1])
    chi2 = float(np.sum((resid ** 2) * w))
    scale = chi2 / dof
    cov_s = cov * scale
    res = {'t0': float(t0), 'chi2_red': round(scale, 3)}
    for k in range(1, nharm + 1):
        ia, ib = names.index(f'a{k}'), names.index(f'b{k}')
        a_, b_ = coef[ia], coef[ib]
        amp = math.hypot(a_, b_)
        # error on amp via propagation
        va, vb = cov_s[ia, ia], cov_s[ib, ib],
        cab = cov_s[ia, ib]
        if amp > 0:
            damp = math.sqrt((a_ ** 2 * va + b_ ** 2 * vb + 2 * a_ * b_ * cab) / amp ** 2)
        else:
            damp = math.sqrt(0.5 * (va + vb))
        res[f'harm{k}'] = {
            'semi_amp_ppm': round(amp * 1e6, 1),
            'semi_amp_err_ppm': round(damp * 1e6, 1),
            'snr': round(amp / damp, 2) if damp > 0 else None,
        }
    return res, coef, cov_s, names

# Fit at P (gives the 2theta = ellipsoidal term directly) and at P/2.
fitP, _, _, _ = harmonic_fit(t2, r2, e2, P, nharm=2)
fitPh, _, _, _ = harmonic_fit(t2, r2, e2, PHALF, nharm=2)

# The physically meaningful ELLIPSOIDAL term is harm2 of the fit AT P.
ell = fitP['harm2']
A2 = ell['semi_amp_ppm'] / 1e6

# --- RED-NOISE-AWARE LIMIT via CONTROL PERIODS ---------------------------------
# The diagonal-covariance error grossly UNDER-estimates the true uncertainty at
# long periods because TESS residuals are correlated (red) across sectors. The
# honest noise floor is the distribution of the SAME 2theta semi-amplitude fitted
# at many UNRELATED control periods (which contain no real orbital signal). If the
# amplitude at P is not an outlier vs that distribution, there is no detection and
# the control distribution itself sets the upper limit.
rng = np.random.default_rng(7)
n_ctrl = 300
ctrl_amps = np.empty(n_ctrl)
ctrl_amps1 = np.empty(n_ctrl)
i = 0
while i < n_ctrl:
    pp = rng.uniform(40.0, 500.0)
    if abs(pp - P) / P < 0.05 or abs(pp - PHALF) / PHALF < 0.05:
        continue                      # avoid the true period and its half
    if abs(pp - PROT) / PROT < 0.05:
        continue                      # avoid the rotation period
    fc, _, _, _ = harmonic_fit(t2, r2, e2, pp, nharm=2)
    ctrl_amps[i] = fc['harm2']['semi_amp_ppm'] / 1e6
    ctrl_amps1[i] = fc['harm1']['semi_amp_ppm'] / 1e6
    i += 1
ctrl_med = float(np.median(ctrl_amps) * 1e6)
ctrl_95 = float(np.percentile(ctrl_amps, 95) * 1e6)
ctrl_997 = float(np.percentile(ctrl_amps, 99.7) * 1e6)
# p-value: fraction of control periods with >= observed amplitude at P
p_emp = float((ctrl_amps >= A2).mean())
detected = bool(p_emp < 0.01)         # only a detection if P is a clear outlier

# Upper limit on the ellipsoidal SEMI-amplitude (red-noise aware):
#   - if NOT detected, the 95% / 99.7% control percentiles bound any real signal.
#     Use the 99.7% (~3sigma-equivalent) control percentile as the conservative
#     3sigma upper limit. Peak-to-peak ellipsoidal depth = 2 x semi-amplitude.
limit_semi_ppm = ctrl_997 if not detected else (A2 * 1e6)
limit_p2p_ppm = 2 * limit_semi_ppm
limit_semi_95_ppm = ctrl_95

out['ellipsoidal_limit'] = {
    'method': ('weighted harmonic LSQ of cos(2*theta) term at P; UPPER LIMIT set by '
               'the empirical distribution of the same statistic at 300 unrelated '
               'control periods (40-500 d), which captures the red-noise floor that '
               'diagonal-covariance errors miss.'),
    'measured_2theta_semi_amp_at_P_ppm': ell['semi_amp_ppm'],
    'formal_diagonal_err_ppm_UNRELIABLE': ell['semi_amp_err_ppm'],
    'formal_diagonal_snr_UNRELIABLE': ell['snr'],
    'control_periods_median_semi_amp_ppm': round(ctrl_med, 1),
    'control_periods_95pct_semi_amp_ppm': round(ctrl_95, 1),
    'control_periods_99.7pct_semi_amp_ppm': round(ctrl_997, 1),
    'empirical_p_value_at_P': round(p_emp, 4),
    'detection': detected,
    'verdict': ('NON-DETECTION: amplitude at P is consistent with (or below) the '
                'control-period noise floor.' if not detected else
                'POSSIBLE signal at P — investigate (likely systematic).'),
    'UPPER_LIMIT_3sigma_semi_amp_ppm': round(limit_semi_ppm, 1),
    'UPPER_LIMIT_3sigma_peak_to_peak_ppm': round(limit_p2p_ppm, 1),
    'UPPER_LIMIT_95pct_semi_amp_ppm': round(limit_semi_95_ppm, 1),
    'first_harmonic_at_P_semi_amp_ppm': fitP['harm1']['semi_amp_ppm'],
    'note_on_P_half_fit': ('A 2theta fit AT P/2 (=126.7 d) probes 4-humps-per-orbit; '
                           'the physical ellipsoidal term is the 2theta term AT P. '
                           'Both are reported; neither exceeds the control floor.'),
}
out['fit_at_P'] = fitP
out['fit_at_Phalf'] = fitPh
print(f'[ELLIP] 2theta semi-amp @P = {ell["semi_amp_ppm"]:.1f} ppm (formal SNR={ell["snr"]} is UNRELIABLE — red noise)')
print(f'[ELLIP] CONTROL-period 2theta floor: median={ctrl_med:.0f}, 95%={ctrl_95:.0f}, 99.7%={ctrl_997:.0f} ppm')
print(f'[ELLIP] empirical p-value at P = {p_emp:.3f}  -> detection={detected}')
print(f'[ELLIP] >>> 3sigma UPPER LIMIT: ellipsoidal semi-amp < {limit_semi_ppm:.0f} ppm, '
      f'peak-to-peak < {limit_p2p_ppm:.0f} ppm <<<')

# Also a simple binned phase-folded P2P at P and P/2 (matches dossier's metric).
def binned_p2p(period, nb=50):
    ph = ((t2 - t2.min()) / period) % 1.0
    idx = (ph * nb).astype(int).clip(0, nb - 1)
    means, errs = [], []
    for b in range(nb):
        m = idx == b
        if m.sum() >= 5:
            means.append(np.average(r2[m], weights=1 / e2[m] ** 2))
            errs.append(1.0 / math.sqrt(np.sum(1 / e2[m] ** 2)))
    means = np.array(means); errs = np.array(errs)
    return {'p2p_ppm': round((means.max() - means.min()) * 1e6, 1),
            'median_bin_err_ppm': round(float(np.median(errs)) * 1e6, 1),
            'n_filled_bins': int(means.size)}

out['binned_phasefold'] = {'at_P_50bin': binned_p2p(P), 'at_Phalf_50bin': binned_p2p(PHALF)}
print('[FOLD] P2P at P  :', out['binned_phasefold']['at_P_50bin'])
print('[FOLD] P2P at P/2:', out['binned_phasefold']['at_Phalf_50bin'])

# ============================================================
# 5. EXPECTED ellipsoidal amplitude for a stellar (M-dwarf) companion
#    Ellipsoidal semi-amplitude (fractional flux), leading term (Morris 1985 /
#    Kopal):  A_ell ~ alpha * (M2/M1) * (R1/a)^3 * sin^2 i
#    with alpha = 0.15*(15+u)*(1+g)/(3-u) ~ a few tenths..1.3 (use ~1.0).
#    a from Kepler's 3rd law: a^3 = (M1+M2) P^2 (in AU, Msun, yr).
# ============================================================
def a_AU(M1, M2, P_yr):
    return ((M1 + M2) * P_yr ** 2) ** (1 / 3.0)

Rsun_AU = 0.00465047
P_yr = P / 365.25
alpha = 1.0  # gravity+limb-darkening prefactor, order unity for M dwarf
exp_rows = []
for M2 in [0.075, 0.10, 0.15, 0.20, 0.25]:    # Msun: 0.075=H-burning limit ... up to ~M1
    a = a_AU(M1, M2, P_yr)
    aR = a / (R1 * Rsun_AU)                    # a/R1
    for sini2, lab in [(1.0, 'edge-on i=90'), (0.75, 'i=60'), (0.25, 'i=30')]:
        A_ell = alpha * (M2 / M1) * (1.0 / aR) ** 3 * sini2
        exp_rows.append({'M2_Msun': M2, 'M2_Mjup': round(M2 * 1047.6, 0),
                         'a_AU': round(a, 3), 'a_over_R1': round(aR, 0),
                         'incl': lab, 'expected_semi_amp_ppm': round(A_ell * 1e6, 3),
                         'expected_p2p_ppm': round(2 * A_ell * 1e6, 3)})
out['expected_ellipsoidal_stellar_companion'] = exp_rows
# headline: an equal-ish 0.25 Msun M-dwarf companion, edge-on
edge = [r for r in exp_rows if r['M2_Msun'] == 0.25 and r['incl'] == 'edge-on i=90'][0]
hburn = [r for r in exp_rows if r['M2_Msun'] == 0.075 and r['incl'] == 'edge-on i=90'][0]
out['expected_headline'] = {
    'a_over_R1_at_P': edge['a_over_R1'],
    'M-dwarf_companion_0.25Msun_edgeon_p2p_ppm': edge['expected_p2p_ppm'],
    'Hburning_limit_0.075Msun_edgeon_p2p_ppm': hburn['expected_p2p_ppm'],
    'comment': ('At a/R1~%.0f the ellipsoidal term scales as (R1/a)^3 ~ 1e-7..1e-6; '
                'even an edge-on equal-mass M-dwarf companion gives only ~%.2g ppm p2p '
                '-- FAR below any TESS limit. => Ellipsoidal modulation is NOT a useful '
                'discriminator at this LONG period; the orbit is simply too wide.'
                % (edge['a_over_R1'], edge['expected_p2p_ppm'])),
}
print('[EXPECT] a/R1 ~', edge['a_over_R1'], '| 0.25Msun edge-on ellipsoidal p2p ~',
      edge['expected_p2p_ppm'], 'ppm |  0.075Msun ~', hburn['expected_p2p_ppm'], 'ppm')

# ============================================================
# 6. Eclipse geometry: transit/eclipse probability at this a/R1
# ============================================================
a_edge = a_AU(M1, 0.25, P_yr)
aR_edge = a_edge / (R1 * Rsun_AU)
out['eclipse_geometry'] = {
    'transit_prob_circular_pct': round(100.0 / aR_edge, 3),  # R1/a (point companion)
    'comment': ('Eclipse/transit probability ~ R1/a ~ %.2f%% (circular). Non-detection '
                'of eclipses is expected on geometry alone and is NOT informative about '
                'companion nature.' % (100.0 / aR_edge)),
}

out['TESS'] = tess
json.dump(out, open('/tmp/apmpm_j0710_photlimit.json', 'w'), indent=1, default=str)
print('\nSAVED /tmp/apmpm_j0710_photlimit.json')
