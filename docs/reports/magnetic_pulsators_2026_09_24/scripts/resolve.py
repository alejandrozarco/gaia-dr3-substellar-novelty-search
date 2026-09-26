# Name/coordinate -> Gaia DR3 resolver.
#  1) J-coordinate names (J hhmmss.ss +ddmmss.s) are decoded to J2000 positions -> MWDD local match (PM-propagated) -> Gaia cone.
#  2) Other names: SIMBAD TAP batch (exact ident) -> Gaia DR3 ident; failures -> Sesame -> coordinates -> matching as in 1.
# Every failure is recorded (never silently dropped).
import re, sys, time, json, requests, numpy as np, urllib.parse
sys.path.insert(0, '/tmp/fanout/magpuls/scripts')
from simbad_tap import tap
import mwdd_local, gaia_cone
JRE = re.compile(r'J\s?(\d{2})(\d{2})(\d{2}(?:\.\d+)?)\s*([+\-−])\s*(\d{2})(\d{2})(\d{2}(?:\.\d+)?)')
def jcoord(name):
    m = JRE.search(name.replace('$-$', '-').replace('$+$', '+').replace('−', '-'))
    if not m: return None
    h, mi, s, sg, d, dm, ds = m.groups()
    ra = (int(h) + int(mi) / 60 + float(s) / 3600) * 15
    dec = int(d) + int(dm) / 60 + float(ds) / 3600
    return ra, (-dec if sg in '-−' else dec)
def coord_to_gaia(ra, dec, epoch=2000.0, maxsep=2.0, cone_radius=30.0):
    (i, s), = mwdd_local.match([ra], [dec], epoch, maxsep)
    if i is not None:
        df = mwdd_local.load(); return df.loc[i, 'gaia'], 'mwdd_pos', s
    try:
        sid, s, G = gaia_cone.cone(ra, dec, epoch, cone_radius, maxsep)
    except Exception as e:
        return None, 'HOLE_gaia_cone', None
    return sid, 'gaia_cone', s
def simbad_batch(names):
    out = {}
    names = [n for n in names if n]
    for k in range(0, len(names), 200):
        chunk = names[k:k + 200]
        inl = ",".join("'" + n.replace("'", "''") + "'" for n in chunk)
        q = (f"SELECT i1.id, i2.id, b.main_id, b.ra, b.dec FROM ident AS i1 JOIN basic AS b ON b.oid = i1.oidref "
             f"LEFT JOIN ident AS i2 ON i2.oidref = i1.oidref AND i2.id LIKE 'Gaia DR3 %' WHERE i1.id IN ({inl})")
        cols, rows = tap(q)
        for q_, g, mid, ra, dec in rows:
            out[q_] = dict(gaia=g.replace('Gaia DR3 ', '') if g else None, main_id=mid, ra=ra, dec=dec)
    return out
def sesame(name):
    u = 'https://cds.unistra.fr/cgi-bin/nph-sesame/-oxp/S?' + urllib.parse.quote(name)
    for k in range(3):
        try:
            r = requests.get(u, timeout=60)
            if r.status_code == 200: break
        except Exception: pass
        time.sleep(3)
    else:
        return 'HOLE'
    t = r.text
    m1 = re.search(r'<jradeg>([^<]+)</jradeg>', t); m2 = re.search(r'<jdedeg>([^<]+)</jdedeg>', t); m3 = re.search(r'<oname>([^<]+)</oname>', t)
    if not (m1 and m2): return None
    return dict(ra=float(m1.group(1)), dec=float(m2.group(1)), main_id=m3.group(1) if m3 else None)
def resolve_names(names, epoch_for_jnames=2000.0):
    res = {}
    todo = []
    for n in names:
        jc = jcoord(n)
        if jc and re.search(r'J\s?\d{6}(\.\d+)?\s*[+\-−]\s*\d{6}', n.replace('$-$', '-')):
            g, how, s = coord_to_gaia(jc[0], jc[1], epoch_for_jnames)
            res[n] = dict(gaia=g, how=how, sep=s, ra=jc[0], dec=jc[1])
            if g: continue
        todo.append(n)
    sb = simbad_batch(todo) if todo else {}
    for n in todo:
        if n in sb and sb[n]['gaia']:
            res[n] = dict(gaia=sb[n]['gaia'], how='simbad_ident', sep=None, ra=sb[n]['ra'], dec=sb[n]['dec'], main_id=sb[n]['main_id']); continue
        ss = sesame(n)
        if ss == 'HOLE': res[n] = dict(gaia=None, how='HOLE_sesame'); continue
        if ss is None: res[n] = dict(gaia=None, how='unresolved'); continue
        # SIMBAD J2000 coordinates are epoch J2000 for most objects
        g, how, s = coord_to_gaia(ss['ra'], ss['dec'], 2000.0, 3.0)
        res[n] = dict(gaia=g, how='sesame+' + how, sep=s, ra=ss['ra'], dec=ss['dec'], main_id=ss['main_id'])
        time.sleep(0.3)
    return res
