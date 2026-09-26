# Reverse check of magnetic papers available only as LaTeX: grep every magnetic-paper source for every pulsator alias
# (Gaia DR3/DR2 ids, SIMBAD identifiers, short J names from J2000 and 2016.0 positions, Jhhmmss+ddmmss). Writes out/tex_grep_hits.csv
import re, os, sys, glob, json, numpy as np, pandas as pd
sys.path.insert(0, '/tmp/fanout/magpuls/scripts'); os.chdir('/tmp/fanout/magpuls')
A = pd.read_csv('raw/puls_gaia_astrometry.csv', dtype={'source_id': str, 'dr2_ids': str})
S = json.load(open('raw/puls_simbad_ids.json'))  # gaia3 -> list of SIMBAD identifiers
def jnames(ra, dec):
    out = set()
    h = ra / 15; hh = int(h); mm = int((h - hh) * 60); ss = (h - hh - mm / 60) * 3600
    sg = '+' if dec >= 0 else '-'; ad = abs(dec); dd = int(ad); dm = int((ad - dd) * 60); ds = (ad - dd - dm / 60) * 3600
    out.add(f'J{hh:02d}{mm:02d}{sg}{dd:02d}{dm:02d}'); out.add(f'J{hh:02d}{mm:02d}{int(ss):02d}{sg}{dd:02d}{dm:02d}{int(ds):02d}')
    return out
alias = {}
for _, r in A.iterrows():
    al = {r.source_id}
    al |= {x for x in str(r.dr2_ids).split(';') if x and x != 'nan'}
    for ep in (2000.0, 2016.0):
        dt = ep - 2016.0
        pmra = 0 if r.pmra != r.pmra else r.pmra; pmde = 0 if r.pmdec != r.pmdec else r.pmdec
        al |= jnames(r.ra + pmra * dt / 3.6e6 / np.cos(np.radians(r.dec)), r.dec + pmde * dt / 3.6e6)
    for sid in S.get(r.source_id, []):
        s = re.sub(r'\s+', ' ', sid.strip())
        if s.startswith(('Gaia', 'TIC', '2MASS', 'WISE', 'AllWISE', 'UCAC', 'USNO', 'PS1', 'SSTSL2', 'LEHPM', 'ATO J', 'ZTF J', 'Cl*', '[')): continue
        if len(s) >= 5: al.add(s.replace('V* ', '').replace('NAME ', ''))
    alias[r.source_id] = al
srcdirs = sorted(glob.glob('/tmp/mwd/arx/*/') + glob.glob('arxmag/*/'))
skip = {'2010.02376'}   # Vincent+2020 is a pulsator paper
hits = []
for d in srcdirs:
    key = d.rstrip('/').split('/')[-1]
    if key in skip: continue
    txt = ''
    for f in glob.glob(d + '**/*', recursive=True):
        if os.path.isfile(f) and re.search(r'\.(tex|txt|dat|csv|bbl|mrt)$', f) and os.path.getsize(f) < 30e6:
            txt += '\n' + open(f, errors='ignore').read()
    t2 = txt.replace('$-$', '-').replace('$+$', '+').replace('$', '').replace('−', '-').replace('~', ' ').replace('\\,', '')
    t3 = re.sub(r'\s+', ' ', t2)
    for g, al in alias.items():
        for a in al:
            if len(a) < 6: continue
            # word-boundary style search (avoid J1234+5678 matching inside longer names is intended: we want both)
            pat = re.escape(a).replace('\\ ', '\\s?')
            for m in re.finditer(pat, t3):
                pre = t3[max(0, m.start() - 1):m.start()]
                post = t3[m.end():m.end() + 1]
                if a.isdigit() and ((pre and pre.isdigit()) or (post and post.isdigit())): continue
                ctx = t3[max(0, m.start() - 150): m.end() + 150]
                hits.append(dict(gaia_dr3=g, paper=key, alias=a, context=ctx))
                break
H = pd.DataFrame(hits)
H.to_csv('out/tex_grep_hits.csv', index=False)
print(len(H), 'hits;', H.gaia_dr3.nunique() if len(H) else 0, 'objects')
if len(H): print(H.groupby('paper').gaia_dr3.nunique().to_string())
