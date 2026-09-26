# Select non-magnetic DA negative controls from SnowWhite (SDSS DR20): p_da high, magnetic probs ~0, Teff outside ZZ Ceti strip,
# G similar to targets (17.3-18.8), ZTF sky (dec > -20), then require MWDD spectype == 'DA' (not DAH) and no Gaia neighbour < 5" brighter than G+2.
import requests, csv, io, json, sys
SQL = ("SELECT TOP 400 sdss_id, gaia_dr3_source_id, ra, dec, g_mag, classification, p_da, p_dah, p_dahe, p_mwd, p_dbh, p_cv, teff, logg, snr "
       "FROM snow_white_boss_star WHERE classification = 'DA' AND p_da > 0.97 AND (p_dah + p_dahe + p_mwd + p_dbh) < 0.005 "
       "AND teff > 16000 AND teff < 35000 AND g_mag > 17.3 AND g_mag < 18.8 AND dec > -20 AND snr > 20 ORDER BY snr DESC")
r = requests.get("https://skyserver.sdss.org/dr20/SkyServerWS/SearchTools/SqlSearch", params=dict(cmd=SQL, format="csv"), timeout=300)
print("HTTP", r.status_code)
lines = [l for l in r.text.splitlines() if not l.startswith("#")]
rows = list(csv.DictReader(io.StringIO("\n".join(lines))))
print("rows", len(rows))
mw = {x.get('gaiaedr3'): x for x in json.load(open('/tmp/mwd/mwdd/table.json'))['data'] if x.get('gaiaedr3')}
good = []
for x in rows:
    m = mw.get(x['gaia_dr3_source_id'])
    if m is None or m['spectype'].strip() != 'DA': continue
    good.append((x, m))
print("with MWDD spectype DA:", len(good))
for x, m in good[:25]:
    print(x['gaia_dr3_source_id'], x['ra'][:9], x['dec'][:9], 'g=%.2f' % float(x['g_mag']), 'Teff=%s' % x['teff'][:6], 'snr=%s' % x['snr'][:5], m['wdid'][:25], 'MWDD T=', m['teff'])
json.dump([x for x, m in good], open('data/neg_ctrl_candidates.json', 'w'), indent=1)
