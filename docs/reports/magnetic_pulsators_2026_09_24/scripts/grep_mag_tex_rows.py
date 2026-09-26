# Row-level version: for each alias hit, take the enclosing table row (tex row delimited by \\ or a text line), and flag magnetic tokens in that row only.
import re, os, sys, glob, json, numpy as np, pandas as pd
os.chdir('/tmp/fanout/magpuls')
exec(open('scripts/grep_mag_tex.py').read().split("srcdirs = ")[0])   # reuse alias construction
srcdirs = sorted(glob.glob('/tmp/mwd/arx/*/') + glob.glob('arxmag/*/'))
pat = re.compile(r'DAH|DBH|DQH|DZH|DAP|DCP|DXP|DQP|DBP|\bDH\b|magnet|Zeeman|\bMG\b|\bkG\b|polari|\\mg\b|\\bbs|\\ssz', re.I)
hits = []
for d in srcdirs:
    key = d.rstrip('/').split('/')[-1]
    if key == '2010.02376': continue
    for f in glob.glob(d + '**/*', recursive=True):
        if not (os.path.isfile(f) and re.search(r'\.(tex|txt|dat|csv|bbl|mrt)$', f) and os.path.getsize(f) < 30e6): continue
        raw = open(f, errors='ignore').read().replace('$-$', '-').replace('$+$', '+').replace('−', '-').replace('~', ' ').replace('\\,', '')
        # rows: split on tex row ends and newlines
        rows = re.split(r'\\\\|\n', raw)
        for g, al in alias.items():
            for a in al:
                if len(a) < 6: continue
                rx = re.compile(r'(?<![0-9A-Za-z])' + re.escape(a).replace('\\ ', '\\s?') + r'(?![0-9])')
                for row in rows:
                    if a[:4] not in row: continue
                    if rx.search(row):
                        hits.append(dict(gaia_dr3=g, paper=key, file=os.path.basename(f), alias=a, row=re.sub(r'\s+', ' ', row.strip())[:400], magrow=bool(pat.search(row))))
H = pd.DataFrame(hits).drop_duplicates(['gaia_dr3', 'paper', 'row'])
H.to_csv('out/tex_grep_rows.csv', index=False)
P = pd.read_csv('lists/puls_master.csv', dtype={'gaia_dr3': str}).set_index('gaia_dr3')
M = H[H.magrow].copy(); M['claim'] = M.gaia_dr3.map(P['claim'])
print(len(H), 'row hits;', len(M), 'magnetic-token rows;', M.gaia_dr3.nunique(), 'objects')
for (g, paper), x in M.groupby(['gaia_dr3', 'paper']):
    print(f"## {g} [{x.claim.iloc[0]}] {paper}/{x.file.iloc[0]} alias={x.alias.iloc[0]}")
    for rw in x.row.head(3): print('     ', rw[:330])
