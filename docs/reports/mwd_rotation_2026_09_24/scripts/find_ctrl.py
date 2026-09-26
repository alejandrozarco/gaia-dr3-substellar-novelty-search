import json, re
d = json.load(open('/tmp/mwd/mwdd/table.json'))['data']
want = ['J0150+2835','J0748+1125','J1105+5225','J1630+2724','J2223+2319','J2257+0755','J0006+3104','J0856+1611','J1018+0111','J1543+3021','J1029+1127','J0718+3731','J1852+1833','J1628+2332','J0153+1808','J2332+2658','J1707+3532','J1659+4401','J0050-0326']
def todeg(r):
    ra = [float(x) for x in r['icrsra'].split()]; ds = r['icrsdec'].strip()
    sg = -1 if ds.startswith('-') else 1; de = [abs(float(x)) for x in ds.replace('+','').replace('-','').split()]
    return 15*(ra[0]+ra[1]/60+ra[2]/3600), sg*(de[0]+de[1]/60+de[2]/3600)
def wdeg(w):
    h, m = int(w[1:3]), int(w[3:5]); sg = -1 if w[5] == '-' else 1; dd, dm = int(w[6:8]), int(w[8:10])
    return 15*(h + (m+0.5)/60), sg*(dd + (dm+0.5)/60)
targets = {w: wdeg(w) for w in want}
hits = {w: [] for w in want}
for r in d:
    try: ra, de = todeg(r)
    except Exception: continue
    for w, (wr, wd) in targets.items():
        if abs(ra - wr) < 0.4 and abs(de - wd) < 0.02:
            if 'H' in r['spectype'] or 'P' in r['spectype'] or 'Q' in r['spectype'] or r['spectype'] == '' or True:
                hits[w].append((r, ra, de))
for w in want:
    wr, wd = targets[w]
    for r, ra, de in hits[w]:
        # J-name check: truncated hhmm / ddmm must match
        h = ra/15; hh = int(h); mm = int((h-hh)*60); sg = '-' if de < 0 else '+'; ad = abs(de); dd = int(ad); dm = int((ad-dd)*60)
        jn = f"J{hh:02d}{mm:02d}{sg}{dd:02d}{dm:02d}"
        if jn != w: continue
        print(w, r['gaiaedr3'], r['wdid'][:28].ljust(28), r['spectype'].ljust(8), 'G=', r['G'][:5], f"{ra:.5f} {de:.5f}", 'np=', r['number_periods'], 'T=', r['teff'], 'M=', r['mass'])
