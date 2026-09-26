# Positional pass over all local magnetic-paper sources: decode every J-coordinate name (Jhhmmss.ss+ddmmss.s, any precision >= 1 s)
# and match to pulsator-master Gaia positions propagated over 1998-2020 (tolerance 3"); report the table row for each match.
import re, os, glob, numpy as np, pandas as pd
os.chdir('/tmp/fanout/magpuls')
A = pd.read_csv('raw/puls_gaia_astrometry.csv', dtype={'source_id': str})
P = pd.read_csv('lists/puls_master.csv', dtype={'gaia_dr3': str}).set_index('gaia_dr3')
JRE = re.compile(r'J\s?(\d{2})(\d{2})(\d{2}(?:\.\d+)?)\s*([+\-])\s*(\d{2})(\d{2})(\d{2}(?:\.\d+)?)')
out = []
for d in sorted(glob.glob('/tmp/mwd/arx/*/') + glob.glob('arxmag/*/')):
    key = d.rstrip('/').split('/')[-1]
    if key == '2010.02376': continue
    for f in glob.glob(d + '**/*', recursive=True):
        if not (os.path.isfile(f) and re.search(r'\.(tex|txt|dat|csv|mrt)$', f) and os.path.getsize(f) < 30e6): continue
        raw = open(f, errors='ignore').read().replace('$-$', '-').replace('$+$', '+').replace('−', '-').replace('{-}', '-')
        for row in re.split(r'\\\\|\n', raw):
            for m in JRE.finditer(row):
                h, mi, s, sg, dd, dm, ds = m.groups()
                ra = (int(h) + int(mi) / 60 + float(s) / 3600) * 15; de = int(dd) + int(dm) / 60 + float(ds) / 3600; de = -de if sg == '-' else de
                if abs(de) > 90 or ra >= 360: continue
                near = np.where((np.abs(A.dec.values - de) < 0.01) & (np.abs(((A.ra.values - ra + 180) % 360 - 180) * np.cos(np.radians(de))) < 0.01))[0]
                for j in near:
                    a = A.iloc[j]; best = 1e9
                    for ep in (1998, 2002, 2006, 2010, 2014, 2016, 2020):
                        dt = ep - 2016.0
                        rae = a.ra + (a.pmra if a.pmra == a.pmra else 0) * dt / 3.6e6 / np.cos(np.radians(a.dec)); dee = a.dec + (a.pmdec if a.pmdec == a.pmdec else 0) * dt / 3.6e6
                        best = min(best, np.hypot(((rae - ra + 180) % 360 - 180) * np.cos(np.radians(de)), dee - de) * 3600)
                    # truncated names (1 s precision) can be off by up to ~15" in RA; accept 3" for decimal names, 16" for integer-second names
                    tol = 3.0 if '.' in s else 16.0
                    if best < tol:
                        out.append(dict(gaia_dr3=a.source_id, paper=key, file=os.path.basename(f), jname=m.group(0), sep=round(best, 2), claim=P.claim.get(a.source_id),
                                        row=re.sub(r'\s+', ' ', row.strip())[:300]))
O = pd.DataFrame(out).drop_duplicates(['gaia_dr3', 'paper', 'row'])
O.to_csv('out/tex_jname_posmatch.csv', index=False)
pat = re.compile(r'DAH|DBH|DQH|DZH|DAP|DCP|DXP|DQP|DBP|\bDH\b|magnet|Zeeman|\bMG\b|\bkG\b', re.I)
O['magrow'] = O.row.apply(lambda r: bool(pat.search(r)))
print(len(O), 'positional J-name matches;', O.gaia_dr3.nunique(), 'objects;', O.magrow.sum(), 'rows with magnetic tokens')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 200); pd.set_option('display.max_rows', 200)
print(O[O.magrow][['gaia_dr3', 'claim', 'paper', 'jname', 'sep', 'row']].to_string())
