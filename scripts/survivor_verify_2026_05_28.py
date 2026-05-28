"""Verify the survivor re-vet agent's two factual conflicts with the dossiers:
  (1) HD 157033 archival RV: 4 dated epochs spanning 71 km/s, or not?
  (2) 5406907 Gaia RV variability: present (dossier) or absent (agent)?
Plus Gaia RV stats + NSS solution type for all 4 survivors.
"""
import warnings, json; warnings.filterwarnings('ignore')
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u

SIDS = {'3155543': 3155543945892767232, 'hd157033': 4111149395881722496,
        '5406907': 5406907085973524224, '5858574': 5858574810404752256}
out = {}
ids = ','.join(str(s) for s in SIDS.values())

# (A) Gaia gaia_source RV variability stats
gs = Gaia.launch_job(
    "SELECT source_id, ra, dec, phot_g_mean_mag, ruwe, radial_velocity, "
    "radial_velocity_error, rv_nb_transits, rv_chisq_pvalue, rv_renormalised_gof, "
    "rv_amplitude_robust FROM gaiadr3.gaia_source WHERE source_id IN (%s)" % ids).get_results()
out['gaia_source'] = {int(r['source_id']): {c: (None if str(r[c])=='--' else str(r[c])) for c in gs.colnames} for r in gs}

# (B) NSS solution type + spectroscopic TI (C,H) for the 3 with NSS rows
nss = Gaia.launch_job(
    "SELECT source_id, nss_solution_type, period, eccentricity, parallax, significance, "
    "a_thiele_innes, b_thiele_innes, f_thiele_innes, g_thiele_innes, "
    "c_thiele_innes, h_thiele_innes FROM gaiadr3.nss_two_body_orbit WHERE source_id IN (%s)" % ids).get_results()
out['nss'] = {int(r['source_id']): {c: (None if str(r[c])=='--' else str(r[c])) for c in nss.colnames} for r in nss}

# (C) HD 157033 archival RV — GALAH DR3 (single epoch) + APOGEE DR17 allStar (VHELIO_AVG, VSCATTER, NVISITS)
hd = [r for r in gs if int(r['source_id']) == 4111149395881722496][0]
co = SkyCoord(float(hd['ra'])*u.deg, float(hd['dec'])*u.deg)
V = Vizier(row_limit=20, columns=['**'])
for label, cat in [('GALAH_DR3', 'III/284'), ('APOGEE_DR17', 'III/286'), ('GALAH_DR4', 'III/290')]:
    try:
        r = V.query_region(co, radius=5*u.arcsec, catalog=cat)
        if r is None or len(r) == 0:
            out['hd157033_'+label] = 'NO MATCH'
        else:
            t = r[0]
            rvlike = [c for c in t.colnames if any(k in c.lower() for k in ('rv','vhelio','vscat','nvis','hrv','vrad','helio','mjd','jd','date'))]
            out['hd157033_'+label] = {'tab': t.meta.get('name',''), 'rv_cols': rvlike,
                                      'rows': [{c: str(row[c]) for c in (rvlike or t.colnames[:12])} for row in t]}
    except Exception as e:
        out['hd157033_'+label+'_err'] = str(e)[:150]

print(json.dumps(out, indent=1, default=str)[:7000])
json.dump(out, open('/tmp/survivor_verify.json', 'w'), indent=1, default=str)
print('\nSAVED /tmp/survivor_verify.json')
