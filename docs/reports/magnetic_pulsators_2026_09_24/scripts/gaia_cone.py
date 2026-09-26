# Per-object Gaia DR3 cone search at ESA TAP (sync) with PM propagation to the input epoch. Returns best (source_id, sep, G) or raises (HOLE).
import requests, time, numpy as np
URL = 'https://gea.esac.esa.int/tap-server/tap/sync'
def gaia_q(adql, timeout=120, tries=3):
    err = None
    for k in range(tries):
        try:
            r = requests.post(URL, data=dict(REQUEST='doQuery', LANG='ADQL', FORMAT='json', QUERY=adql), timeout=timeout)
            if r.status_code == 200:
                j = r.json(); return [c['name'] for c in j['metadata']], j['data']
            err = f'HTTP {r.status_code} {r.text[:200]}'
        except Exception as e:
            err = repr(e)
        time.sleep(5)
    raise RuntimeError('Gaia TAP HOLE: ' + str(err))
def cone(ra, dec, epoch=2000.0, radius=30.0, maxsep=3.0):
    q = (f"SELECT source_id, ra, dec, pmra, pmdec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE "
         f"1=CONTAINS(POINT('ICRS',ra,dec), CIRCLE('ICRS',{ra},{dec},{radius/3600.}))")
    cols, rows = gaia_q(q)
    best = None
    for sid, gra, gde, pmra, pmde, G in rows:
        dt = epoch - 2016.0; pmra = pmra or 0.0; pmde = pmde or 0.0
        rae = gra + pmra * dt / 3.6e6 / np.cos(np.radians(gde)); dee = gde + pmde * dt / 3.6e6
        s = np.hypot((rae - ra) * np.cos(np.radians(dec)), dee - dec) * 3600
        if best is None or s < best[1]: best = (str(sid), s, G)
    if best is None or best[1] > maxsep: return (None, best[1] if best else None, best[2] if best else None)
    return best
