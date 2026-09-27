"""Triage of hot white dwarfs with Gaia DR3 GLS periods of 0.2-3.5 d that are not in findings_register.csv.
Sample (hot_periods_spectra.csv): Gaia DR3 vari_spurious_signals x Gentile Fusillo+2021 (docs/reports/gaia_wd_periods_2026_09_24/data/wd_vspur_gf21.csv),
Pwd > 0.75, TeffH > 40 kK or (BP-RP < -0.35 and M_G < 9.5), GLS 0.25-5 c/d, FAP < 1e-2; with SDSS-V/DESI/LAMOST UHE line measurements.
Per star: Gaia G/BP/RP epoch photometry (DataLink); GLS 0.2-5 c/d on G; G/BP/RP semi-amplitudes (sinusoid + harmonic) at the G peak; RP/BP ratio;
BP-RP vs phase (Spearman against cos 2 pi phase, phase 0 = G maximum); VSX (B/vsx), SIMBAD, Jestin+2026 (J/A+A/712/A243/tablea1), Chen+2020 (J/ApJS/249/18/table2).
Flags: Gaia scan-angle-model significance > 3 or |IPD Spearman| > 0.3 (Holl+2023)."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from astroquery.gaia import Gaia; from astroquery.vizier import Vizier; from astroquery.simbad import Simbad
from astropy.timeseries import LombScargle; from astropy.coordinates import SkyCoord; import astropy.units as u
from scipy.stats import spearmanr
s = pd.read_csv("hot_periods_spectra.csv", dtype={"source_id": str}); s = s[~s.registered.astype(bool)].copy()
tabs = {}
for k0 in range(0, len(s), 40):
    dl = Gaia.load_data(ids=list(s.source_id[k0:k0 + 40]), retrieval_type="EPOCH_PHOTOMETRY", data_release="Gaia DR3", data_structure="INDIVIDUAL", format="csv")
    for k, v in dl.items():
        t = v[0].to_pandas() if hasattr(v[0], "to_pandas") else v[0]; tabs[str(t.source_id.iloc[0])] = t
def fit(t, f, fr, t0):
    X = np.vstack([np.ones_like(t)] + [fn(2 * np.pi * k * fr * (t - t0)) for k in (1, 2) for fn in (np.sin, np.cos)]).T
    c, *_ = np.linalg.lstsq(X, f, rcond=None); r = f - X @ c; cov = np.linalg.inv(X.T @ X) * np.var(r) * len(f) / max(len(f) - 5, 1)
    return np.hypot(c[1], c[2]) / c[0], np.sqrt(cov[1, 1]) / c[0], X @ c
V = Vizier(columns=["**"], row_limit=5); V.TIMEOUT = 120; FR = np.linspace(0.2, 5, 200000); rows = []
for _, r in s.iterrows():
    d = dict(source_id=r.source_id, G=round(r.phot_g_mean_mag, 2), MG=round(r.MG, 2), bp_rp=round(r.bp_rp, 3), TeffH=r.TeffH, sam_sig=round(r.scan_angle_model_ampl_sig_g_fov, 2),
             ipd_rho=round(r.spearman_corr_ipd_g_fov, 2), P_vari_h=round(24 / r.gls_freq_g_fov, 3), sv=r.sv_classification, desi=r.de_specType, lamost=r.la_wdClass, known_uhe=r.known_uhe)
    t = tabs.get(r.source_id)
    if t is not None:
        m = np.isfinite(t.g_transit_time) & (t.g_transit_flux > 0) & (t.variability_flag_g_reject.astype(str).str.lower() != "true")
        tg, fg, eg = t.g_transit_time[m].values, t.g_transit_flux[m].values, t.g_transit_flux_error[m].values
        ls = LombScargle(tg, fg, eg); p = ls.power(FR); k = np.argmax(p); f0 = FR[k]
        d.update(P_h=round(24 / f0, 4), fap=float(f"{ls.false_alarm_probability(p[k], minimum_frequency=0.2, maximum_frequency=5):.2g}"))
        a, e, mod = fit(tg, fg, f0, 0.0); ph = np.linspace(0, 1, 1000); X = np.vstack([np.ones_like(ph)] + [fn(2 * np.pi * k * ph) for k in (1, 2) for fn in (np.sin, np.cos)]).T
        c, *_ = np.linalg.lstsq(np.vstack([np.ones_like(tg)] + [fn(2 * np.pi * k * f0 * tg) for k in (1, 2) for fn in (np.sin, np.cos)]).T, fg, rcond=None); tmax = ph[np.argmax(X @ c)] / f0
        for b, tc, fc, rej in (("G", "g_transit_time", "g_transit_flux", "variability_flag_g_reject"), ("BP", "bp_obs_time", "bp_flux", "variability_flag_bp_reject"), ("RP", "rp_obs_time", "rp_flux", "variability_flag_rp_reject")):
            mm = np.isfinite(t[tc]) & np.isfinite(t[fc]) & (t[fc] > 0) & (t[rej].astype(str).str.lower() != "true")
            if mm.sum() >= 12: a, e, _ = fit(t[tc][mm].values, t[fc][mm].values, f0, 0.0); d[f"A_{b}"] = round(100 * a, 2); d[f"e_{b}"] = round(100 * e, 2)
        mm = np.isfinite(t.bp_flux) & np.isfinite(t.rp_flux) & (t.bp_flux > 0) & (t.rp_flux > 0) & (t.variability_flag_bp_reject.astype(str).str.lower() != "true") & (t.variability_flag_rp_reject.astype(str).str.lower() != "true")
        if mm.sum() >= 12:
            cl = -2.5 * np.log10(t.bp_flux[mm].values / t.rp_flux[mm].values); rho, pp = spearmanr(np.cos(2 * np.pi * ((t.bp_obs_time[mm].values - tmax) * f0)), cl)
            d.update(colour_rho=round(rho, 2), colour_p=float(f"{pp:.2g}"))
    c0 = SkyCoord(r.ra, r.dec, unit="deg")
    try:
        v = V.query_region(c0, radius=5 * u.arcsec, catalog="B/vsx/vsx"); d["vsx"] = "; ".join(f"{x['Name']} {x['Type']} {x['Period']}" for x in v[0]) if len(v) else ""
    except Exception as ex: d["vsx"] = f"ERR {ex}"
    try:
        v = V.query_region(c0, radius=3 * u.arcsec, catalog="J/A+A/712/A243/tablea1"); d["jestin"] = f"var={v[0][0]['Variable']} per={v[0][0]['Periodic']} f={v[0][0]['Freq']}" if len(v) else "not listed"
    except Exception as ex: d["jestin"] = f"ERR {ex}"
    try:
        v = V.query_region(c0, radius=3 * u.arcsec, catalog="J/ApJS/249/18/table2"); d["chen2020"] = f"{v[0][0]['Type']} {v[0][0]['Per']}" if len(v) else ""
    except Exception as ex: d["chen2020"] = f"ERR {ex}"
    try:
        q = Simbad.query_region(c0, radius=5 * u.arcsec); d["simbad"] = f"{q[0]['main_id']} ({q[0]['otype'] if 'otype' in q.colnames else ''})" if q is not None and len(q) else ""
    except Exception as ex: d["simbad"] = f"ERR {ex}"
    rows.append(d); print(d, flush=True)
A = pd.DataFrame(rows); A["RP_BP"] = (A.A_RP / A.A_BP).round(2); A.to_csv("triage.csv", index=False)
