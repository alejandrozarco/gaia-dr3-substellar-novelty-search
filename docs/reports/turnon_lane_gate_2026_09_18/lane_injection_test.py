#!/usr/bin/env python3
"""END-TO-END LANE TEST: inject synthetic turn-ons into REAL ZTF cadences.

Astra's critique E4/E8: two dwarf-nova recoveries validate the FILTERS on two bright
examples; they say nothing about completeness across amplitude, turn-on date or depth.
This measures the lane's actual recovery fraction using the real observing dates and
real per-frame limiting magnitudes, and the IDENTICAL classifier from turnon_pilot2.py.

A synthetic source is 'detected' on a frame only if it clears the same quality cut the
pipeline applies (mag <= limitmag - 0.3), with photometric noise scaled to the margin.
"""
import csv, glob, math, random, statistics, collections

random.seed(20260918)
ZTF_ERR_FLOOR = 0.03

def load_cadences():
    """Real (mjd, filter, limitmag) sequences from downloaded light curves."""
    cads=[]
    for fn in ('/tmp/c2.csv','/tmp/lc_test.csv','/tmp/eb.csv','/tmp/lc1.csv'):
        try: rows=list(csv.DictReader(open(fn)))
        except Exception: continue
        ep=[(float(r['mjd']),r['filtercode'],float(r['limitmag']))
            for r in rows if r.get('limitmag') and float(r['limitmag'])>0 and r['catflags']=='0']
        if len(ep)>=40: cads.append((fn,sorted(ep)))
    return cads

def simulate(cad, m_faint, m_bright, t_on, band='zr'):
    """Return the epochs the pipeline would SEE for this synthetic source."""
    seen=[]
    for mjd,f,lim in cad:
        if f!=band: continue
        m_true = m_faint if mjd < t_on else m_bright
        margin = lim - m_true
        if margin < 0.3:          # same cut as good_epoch()
            continue
        # noise grows as the source approaches the limit
        sig = max(ZTF_ERR_FLOOR, 0.2*math.exp(-(margin-0.3)))
        seen.append((mjd, m_true + random.gauss(0,sig)))
    return seen

def classify(seen, nsc_r):
    """The pipeline's own logic (post-duty-veto-removal)."""
    if len(seen) < 3: return 'ZTF_SPARSE'
    mags=sorted(m for _,m in seen)
    bright=mags[max(0,int(0.05*len(mags)))]
    thr=bright+1.0
    nights=collections.defaultdict(list)
    for mj,m in seen: nights[int(mj)].append(m)
    bn=[n for n,ms in nights.items() if min(ms)<thr]
    duty=len(bn)/len(nights)
    be=[mj for mj,m in seen if m<thr]
    span=max(be)-min(be) if be else 0
    amp=nsc_r-bright
    if len(bn)<2: return 'SINGLE_NIGHT'
    if amp<=2.5:  return 'NO_TURNON'
    if span<=30 and duty<=0.9: return 'SHORT_SPAN'
    return 'CANDIDATE_SUSTAINED' if duty>0.9 else 'CANDIDATE_OUTBURST'

cads=load_cadences()
print(f"real ZTF cadences loaded: {len(cads)}")
for fn,ep in cads:
    zr=[e for e in ep if e[1]=='zr']
    if zr:
        lims=[l for _,_,l in zr]
        print(f"  {fn.split('/')[-1]:14s} zr epochs={len(zr):4d} median limitmag={statistics.median(lims):.2f}")

NSC_R = 23.0
print(f"\n=== RECOVERY of a SUSTAINED turn-on (archival NSC r={NSC_R}) ===")
print("rows = brightness the source reaches; cols = turn-on date; 60 trials each\n")
dates=[('pre-ZTF',58000),('2019',58500),('2021',59200),('2023',60000)]
print(f"{'reaches':>9} {'amp':>5} " + " ".join(f"{d[0]:>10}" for d in dates))
for m_bright in (18.5,19.0,19.5,20.0,20.3,20.5,21.0):
    row=[]
    for _,t_on in dates:
        ok=0
        for _ in range(60):
            fn,cad=random.choice(cads)
            seen=simulate(cad,NSC_R,m_bright,t_on)
            if classify(seen,NSC_R).startswith('CANDIDATE'): ok+=1
        row.append(f"{100*ok/60:9.0f}%")
    print(f"{'r='+format(m_bright,'.1f'):>9} {NSC_R-m_bright:5.1f} " + " ".join(row))

print(f"\n=== RECOVERY of an OUTBURST (dwarf-nova-like), 30-day events ===")
def simulate_outburst(cad,m_faint,m_bright,n_out,dur=30,band='zr'):
    mjds=[e[0] for e in cad if e[1]==band]
    if not mjds: return []
    lo,hi=min(mjds),max(mjds)
    starts=[random.uniform(lo,hi) for _ in range(n_out)]
    seen=[]
    for mjd,f,lim in cad:
        if f!=band: continue
        m_true=m_bright if any(s<=mjd<s+dur for s in starts) else m_faint
        if lim-m_true<0.3: continue
        sig=max(ZTF_ERR_FLOOR,0.2*math.exp(-(lim-m_true-0.3)))
        seen.append((mjd,m_true+random.gauss(0,sig)))
    return seen
print(f"{'reaches':>9} " + " ".join(f"{n:>3} outbursts" for n in (1,2,4,8)))
for m_bright in (18.0,19.0,19.5,20.0):
    row=[]
    for n_out in (1,2,4,8):
        ok=0
        for _ in range(60):
            fn,cad=random.choice(cads)
            seen=simulate_outburst(cad,NSC_R,m_bright,n_out)
            if classify(seen,NSC_R).startswith('CANDIDATE'): ok+=1
        row.append(f"{100*ok/60:11.0f}%")
    print(f"{'r='+format(m_bright,'.1f'):>9} " + " ".join(row))
