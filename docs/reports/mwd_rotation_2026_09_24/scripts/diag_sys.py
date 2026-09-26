# Diagnose the 0.966 c/d (lunar alias) systematic: correlate normalised flux with limitmag, airmass, lunar phase.
import sys, os, json, numpy as np
sys.path.insert(0, 'scripts'); import rotlib as RL
from astropy.time import Time
from astropy.coordinates import get_body, get_sun, SkyCoord
import astropy.units as u
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
for sid in sys.argv[1:]:
    rec = META[sid]
    rows, by = RL.read_oids(f'ztf/{sid}.csv'); ot = RL.oid_table(by, rec); tset = set(o['oid'] for o in ot if o['sep'] < 1.5)
    D = RL.load_lc([r for r in rows if r['oid'] in tset], float(rec['ra']), float(rec['dec']))
    print(sid, rec.get('name', ''))
    for b in ('zg', 'zr'):
        d = D[b]; t = Time(d['mjd'], format='mjd')
        # lunar phase angle proxy: elongation of moon from sun
        sun = get_sun(t); moon = get_body('moon', t)
        elong = sun.separation(moon).deg  # 0 new, 180 full
        tgt = SkyCoord(float(rec['ra']) * u.deg, float(rec['dec']) * u.deg)
        msep = moon.separation(tgt).deg
        f = d['f']
        for lab, x in (('limitmag', d['limitmag']), ('airmass', d['airmass']), ('moon_elong', elong), ('moon_sep', msep)):
            r = np.corrcoef(x, f)[0, 1]
            # binned relation
            q = np.percentile(x, [0, 20, 40, 60, 80, 100]); ib = np.clip(np.digitize(x, q[1:-1]), 0, 4)
            med = [np.median(f[ib == i]) for i in range(5)]
            print(f"  {b} {lab:10s} r={r:+.3f}  quintile medians: " + " ".join(f"{m:.4f}" for m in med))
