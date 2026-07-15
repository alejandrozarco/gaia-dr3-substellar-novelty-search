#!/usr/bin/env python
"""Archival catalog stack for Rubin diaObject 170587115976392822 at (326.82833, -13.4747).
All outputs saved as CSV in this dir. Sync TAP queries, no auth needed."""
import requests, sys, io

RA, DEC = 326.82833, -13.4747
OUT = '/tmp/rubin_pilot/forensics/170587115976392822'

def tap(name, url, adql, fmt='csv', extra=None):
    params = {'REQUEST': 'doQuery', 'LANG': 'ADQL', 'FORMAT': fmt, 'QUERY': adql}
    if extra: params.update(extra)
    try:
        r = requests.get(url, params=params, timeout=120)
        ok = r.status_code == 200 and not r.text.lstrip().startswith('<')
        fn = f'{OUT}/{name}.csv'
        open(fn, 'w').write(r.text)
        nrows = max(0, len([l for l in r.text.strip().splitlines() if l.strip()]) - 1)
        print(f'{name}: status={r.status_code} rows={nrows}')
        if not ok: print('  head:', r.text[:200].replace(chr(10),' '))
    except Exception as e:
        print(f'{name}: ERR {repr(e)[:150]}')

# Gaia DR3 within 10"
tap('gaia_dr3_cone', 'https://gea.esac.esa.int/tap-server/tap/sync', f"""
SELECT source_id, ra, dec, parallax, parallax_error, pmra, pmdec,
       phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, ruwe,
       phot_variable_flag, classprob_dsc_combmod_quasar, classprob_dsc_combmod_galaxy,
       DISTANCE(POINT('ICRS', ra, dec), POINT('ICRS', {RA}, {DEC}))*3600 AS sep_as
FROM gaiadr3.gaia_source
WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {RA}, {DEC}, 10./3600))
ORDER BY sep_as""")

# Legacy Survey DR10 tractor within 10"
DL = 'https://datalab.noirlab.edu/tap/sync'
tap('ls_dr10_tractor', DL, f"""
SELECT ls_id, ra, dec, type, flux_g, flux_r, flux_i, flux_z,
       mag_g, mag_r, mag_i, mag_z, mag_w1, mag_w2,
       shape_r, sersic, pmra, pmdec, parallax, ref_cat, ref_id,
       q3c_dist(ra, dec, {RA}, {DEC})*3600 AS sep_as
FROM ls_dr10.tractor
WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, 10./3600)
ORDER BY sep_as""")

# NSC DR2 object (mean props + variability) within 10"
tap('nsc_dr2_object', DL, f"""
SELECT id, ra, dec, gmag, rmag, imag, zmag, umag, vmag, ymag,
       grms, rrms, irms, zrms, ndet, nphot, mjd AS mjd_mean, deltamjd, class_star,
       variable10sig, nsigvar,
       q3c_dist(ra, dec, {RA}, {DEC})*3600 AS sep_as
FROM nsc_dr2.object
WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, 10./3600)
ORDER BY sep_as""")

# CatWISE2020 within 10" (IRSA)
IRSA = 'https://irsa.ipac.caltech.edu/TAP/sync'
tap('catwise2020_cone', IRSA, f"""
SELECT source_name, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, pmra, pmdec
FROM catwise_2020
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {RA}, {DEC}, 0.00278))=1""")

# AllWISE within 10"
tap('allwise_cone', IRSA, f"""
SELECT designation, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, w3mpro, w4mpro
FROM allwise_p3as_psd
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {RA}, {DEC}, 0.00278))=1""")

# PS1 DR2 mean within 10" (MAST catalogs API, not TAP)
try:
    r = requests.get('https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv',
                     params={'ra': RA, 'dec': DEC, 'radius': 10/3600.,
                             'columns': '[objID,raMean,decMean,gMeanPSFMag,rMeanPSFMag,iMeanPSFMag,zMeanPSFMag,yMeanPSFMag,iMeanKronMag,nDetections,ng,nr,ni,nz,ny,qualityFlag]',
                             'pagesize': 50}, timeout=120)
    open(f'{OUT}/ps1_dr2_mean.csv', 'w').write(r.text)
    print('ps1_dr2_mean: status=', r.status_code, 'rows=', max(0, len(r.text.strip().splitlines())-1))
except Exception as e:
    print('ps1_dr2_mean ERR', repr(e)[:150])
