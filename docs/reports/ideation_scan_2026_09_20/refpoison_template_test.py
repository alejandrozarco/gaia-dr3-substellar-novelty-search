#!/usr/bin/env python3
"""GATE ZERO for the reference-poisoned outburster lane.

The lane claims: a dwarf nova in outburst DURING its own quadrant's ZTF reference
window contaminates that reference, so difference imaging subtracts the outburst
away and the object never alerts.

Before any search, the standing rule requires the pipeline to recover KNOWN objects
on its own configuration. This measures, on VSX dwarf novae that fall in <=30 d
reference windows:
  (a) what fraction have ZTF DR epochs inside their own reference window at all
  (b) of those, what fraction are >=1.0 mag brighter in-window than out-of-window
      (i.e. the reference really is poisoned)
ZTF DR photometry is PSF photometry on SCIENCE images, so it reports total flux and
is not itself biased by the reference - that is what makes this test possible.
"""
import csv, io, json, math, random, statistics, subprocess, threading, time
from concurrent.futures import ThreadPoolExecutor

templates = json.load(open('refpoison_templates.json'))
random.seed(20260920); random.shuffle(templates)
N = 80
sample = templates[:N]
_lk = threading.Lock(); _last = [0.0]
def throttle(gap=0.9):
    with _lk:
        dt = time.time() - _last[0]
        if dt < gap: time.sleep(gap - dt)
        _last[0] = time.time()

def lc(ra, dec, tries=3):
    url = ("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?"
           f"POS=CIRCLE%20{ra:.6f}%20{dec:.6f}%200.00042&BAD_CATFLAGS_MASK=32768&FORMAT=CSV")
    for k in range(tries):
        throttle()
        p = subprocess.run(["curl","-sL","--max-time","90",url],capture_output=True,text=True)
        if p.returncode == 0 and "oid" in p.stdout:
            return list(csv.DictReader(io.StringIO(p.stdout)))
        time.sleep(3*(k+1))
    return None

def test(t):
    rows = lc(t['ra'], t['dec'])
    if rows is None: return dict(name=t['name'], status='QUERY_ERROR')
    v = [r for r in rows if r['catflags']=='0' and r['filtercode']=='zr']
    if len(v) < 30: return dict(name=t['name'], status='SPARSE', n=len(v))
    mj = [float(r['mjd']) for r in v]; mg = [float(r['mag']) for r in v]
    inw  = [m for j,m in zip(mj,mg) if t['mjd_start'] <= j <= t['mjd_end']]
    outw = [m for j,m in zip(mj,mg) if not (t['mjd_start'] <= j <= t['mjd_end'])]
    if not outw: return dict(name=t['name'], status='NO_OUT', n=len(v))
    out_med = statistics.median(outw)
    rec = dict(name=t['name'], type=t['type'], n=len(v), n_in=len(inw), n_out=len(outw),
               out_med=round(out_med,3), span=t['span'], nframes=t['nframes'])
    if not inw:
        rec['status'] = 'NO_EPOCHS_IN_WINDOW'; return rec
    in_med = statistics.median(inw); in_bright = min(inw)
    rec.update(in_med=round(in_med,3), in_bright=round(in_bright,3),
               delta_med=round(out_med-in_med,3), delta_bright=round(out_med-in_bright,3))
    rec['status'] = 'POISONED' if (out_med-in_med) >= 1.0 else (
                    'PARTIAL' if (out_med-in_bright) >= 1.0 else 'CLEAN')
    return rec

print(f"testing {len(sample)} VSX dwarf novae in <=30 d reference windows", flush=True)
res=[]
with ThreadPoolExecutor(max_workers=3) as ex:
    for i,r in enumerate(ex.map(test, sample),1):
        res.append(r)
        if i%20==0: print(f"  {i}/{len(sample)}", flush=True)
json.dump(res, open('refpoison_gate0.json','w'), indent=1)
import collections
c=collections.Counter(r['status'] for r in res)
print("\nSTATUS:", dict(c))
usable=[r for r in res if r['status'] in ('POISONED','PARTIAL','CLEAN','NO_EPOCHS_IN_WINDOW')]
withep=[r for r in res if r['status'] in ('POISONED','PARTIAL','CLEAN')]
print(f"\n(a) have ZTF epochs inside their own reference window: {len(withep)}/{len(usable)} = "
      f"{100*len(withep)/max(len(usable),1):.0f}%")
pois=[r for r in res if r['status']=='POISONED']
part=[r for r in res if r['status']=='PARTIAL']
print(f"(b) of those, reference POISONED (in-window median >=1.0 mag brighter): "
      f"{len(pois)}/{len(withep)} = {100*len(pois)/max(len(withep),1):.0f}%")
print(f"    PARTIAL (brightest in-window epoch >=1.0 mag brighter): {len(part)}")
if pois:
    print("\n  poisoned templates:")
    for r in sorted(pois,key=lambda x:-x['delta_med'])[:12]:
        print(f"    {r['name'][:26]:26s} {r['type'][:6]:6s} in={r['in_med']:.2f} out={r['out_med']:.2f} "
              f"delta={r['delta_med']:+.2f} n_in={r['n_in']} window={r['span']}d/{r['nframes']}fr")
