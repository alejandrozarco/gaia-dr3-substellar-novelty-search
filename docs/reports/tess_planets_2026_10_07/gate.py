"""Novelty gate + dilution check for one candidate. usage: gate.py TIC RA DEC DEPTH TMAG P
Prints a timestamped record per check; writes gate/{tic}.json"""
import sys, json, time, requests, numpy as np
tic, ra, dec, depth, tmag, P = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
ts = lambda: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
out = dict(tic=tic, checks=[])
def rec(name, result):
    out['checks'].append(dict(time=ts(), check=name, result=result)); print(ts(), name, '->', result, flush=True)
# NASA Exoplanet Archive (ps + toi tables, by TIC and cone)
try:
    u = 'https://exoplanetarchive.ipac.caltech.edu/TAP/sync'
    q1 = f"select pl_name,pl_orbper from ps where tic_id='TIC {tic}'"
    r1 = requests.get(u, params=dict(query=q1, format='json'), timeout=60).json()
    q2 = f"select toi,pl_orbper,tfopwg_disp from toi where tid={tic}"
    r2 = requests.get(u, params=dict(query=q2, format='json'), timeout=60).json()
    cd = max(np.cos(np.radians(dec)), 0.05)
    q3 = f"select pl_name from ps where ra between {ra-0.01/cd} and {ra+0.01/cd} and dec between {dec-0.01} and {dec+0.01}"
    r3 = requests.get(u, params=dict(query=q3, format='json'), timeout=60).json()
    rec('NASA Exoplanet Archive ps(TIC)/toi(TIC)/ps(36" cone)', f'{len(r1)}/{len(r2)}/{len(r3)} rows ' + str((r1[:2], r2[:3], r3[:2])))
except Exception as e:
    rec('NASA Exoplanet Archive', 'FAIL ' + str(e)[:80])
# SIMBAD
try:
    from astroquery.simbad import Simbad
    s = Simbad(); s.add_votable_fields('otype')
    from astropy.coordinates import SkyCoord; import astropy.units as un
    t = s.query_region(SkyCoord(ra, dec, unit='deg'), radius=30 * un.arcsec)
    ctl = s.query_object('TOI-700')
    rec('SIMBAD 30" cone (control TOI-700 ok=%s)' % (ctl is not None and len(ctl) > 0),
        'none' if t is None or len(t) == 0 else '; '.join(f"{r['main_id']}[{r['otype']}]" for r in t[:8]))
except Exception as e:
    rec('SIMBAD', 'FAIL ' + str(e)[:80])
# VSX (Python requests)
try:
    r = requests.get('https://www.aavso.org/vsx/index.php', params=dict(view='api.list', ra=ra, dec=dec, radius=0.02, format='json'),
                     timeout=60)
    j = r.json(); v = j.get('VSXObjects', {})
    v = v.get('VSXObject', []) if isinstance(v, dict) else []
    rec('VSX 72" cone', 'none' if not v else '; '.join(f"{x.get('Name')}[{x.get('VariabilityType')},P={x.get('Period')}]" for x in v[:6]))
except Exception as e:
    rec('VSX', 'FAIL ' + str(e)[:80])
# Gaia neighbours within 2 TESS px (42") that could produce the depth
try:
    from astroquery.gaia import Gaia
    Gaia.ROW_LIMIT = 200
    q = (f"select source_id,ra,dec,phot_g_mean_mag,phot_rp_mean_mag,non_single_star,phot_variable_flag,"
         f"distance({ra},{dec},ra,dec)*3600 as sep from gaiadr3.gaia_source where 1=contains(point('icrs',ra,dec),circle('icrs',{ra},{dec},{42/3600}))")
    g = Gaia.launch_job(q).get_results(); g.sort('sep')
    tgt = g[0]
    rows = []
    for x in g[1:]:
        dm = x['phot_rp_mean_mag'] - tgt['phot_rp_mean_mag'] if np.isfinite(x['phot_rp_mean_mag']) else x['phot_g_mean_mag'] - tgt['phot_g_mean_mag']
        need = depth * 10 ** (0.4 * dm)  # eclipse depth needed on the neighbour
        rows.append(f"{x['source_id']} sep={x['sep']:.1f}\" dRP={dm:.2f} needs={need:.3f}{' POSSIBLE' if need < 0.5 else ''}")
    out['gaia_target'] = str(tgt['source_id']); out['target_ruwe_nss'] = int(tgt['non_single_star'])
    rec('Gaia DR3 42" neighbours', f'target {tgt["source_id"]} G={tgt["phot_g_mean_mag"]:.2f} nss={tgt["non_single_star"]} var={tgt["phot_variable_flag"]}; ' + ('; '.join(rows) if rows else 'no neighbours'))
except Exception as e:
    rec('Gaia neighbours', 'FAIL ' + str(e)[:80])
json.dump(out, open(f'gate/{tic}.json', 'w'), indent=1)
