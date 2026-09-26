# Reverse check: SnowWhite (SDSS-V BOSS) probabilities for every published pulsator (and NOV) Gaia DR3 id. Positive control: J2159+5102.
import requests, io, os, time, pandas as pd
os.chdir('/tmp/fanout/magpuls')
P = pd.read_csv('lists/puls_master.csv', dtype={'gaia_dr3': str})
ids = sorted(P.gaia_dr3)
cols = "sdss_id, gaia_dr3_source_id, classification, p_da, p_dah, p_dahe, p_dbh, p_mwd, p_db, p_dq, p_hotdq, p_cv, p_da_ms, teff, logg, snr, telescope, n_visits, min_mjd, max_mjd"
out = []; holes = 0
for k in range(0, len(ids), 150):
    sql = f"SELECT {cols} FROM snow_white_boss_star WHERE gaia_dr3_source_id IN ({','.join(ids[k:k+150])})"
    for t in range(3):
        try:
            r = requests.get('https://skyserver.sdss.org/dr20/SkyServerWS/SearchTools/SqlSearch', params=dict(cmd=sql, format='csv'), timeout=180)
            if r.status_code == 200 and r.text.startswith('#Table'): break
        except Exception as e: pass
        time.sleep(5)
    else:
        holes += 1; print('HOLE chunk', k); continue
    txt = r.text.split('\n', 1)[1]
    if txt.strip():
        out.append(pd.read_csv(io.StringIO(txt), dtype={'gaia_dr3_source_id': str}))
S = pd.concat(out, ignore_index=True) if out else pd.DataFrame()
S.to_csv('out/snowwhite_pulsators.csv', index=False)
print('chunks failed', holes, 'SnowWhite rows', len(S), 'unique stars', S.gaia_dr3_source_id.nunique() if len(S) else 0)
S['p_mag'] = S[['p_dah', 'p_dahe', 'p_dbh', 'p_mwd']].sum(axis=1)
m = P.set_index('gaia_dr3')
S['claim'] = S.gaia_dr3_source_id.map(m['claim']); S['names'] = S.gaia_dr3_source_id.map(m['names']).str[:50]
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
print(S.sort_values('p_mag', ascending=False)[['gaia_dr3_source_id', 'claim', 'classification', 'p_da', 'p_dah', 'p_dahe', 'p_mwd', 'p_mag', 'snr', 'n_visits', 'names']].head(40).to_string())
