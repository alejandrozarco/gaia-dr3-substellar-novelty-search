"""Injection-recovery on real QLP light curves with the exact search.py analyse().
usage: inject.py SECTOR QUEUE NSTARS NINJ_PER_STAR OUT"""
import sys, os, csv, numpy as np
os.environ.setdefault('NB', '200')
sys.argv_saved = sys.argv[:]
SEC = int(sys.argv[1]); QF = sys.argv[2]; NS = int(sys.argv[3]); NI = int(sys.argv[4]); OUT = sys.argv[5]
sys.argv = ['search.py', str(SEC), QF, '0', '0']
import search
rng = np.random.default_rng(42)
tics = np.loadtxt(QF, delimiter=',', skiprows=1, usecols=0, dtype=np.int64)
tics = rng.choice(tics, size=min(NS, len(tics)), replace=False)
done = set()
if os.path.exists(OUT):
    for r in csv.DictReader(open(OUT)): done.add(int(r['tic']))
fh = open(OUT, 'a'); w = None
for tic in tics:
    if int(tic) in done: continue
    raw = search.fetch(int(tic))
    if raw is None or raw == 'ERR': continue
    base, _ = search.analyse(int(tic), raw)
    if base.get('status') not in ('ok', 'nopeak'): continue
    for k in range(NI):
        P = float(np.exp(rng.uniform(np.log(0.6), np.log(13))))
        T0 = 4206.0 + rng.uniform(0, P)
        rs = base.get('rstar') or 1.0
        try: rs = float(rs)
        except Exception: rs = 1.0
        if not (0.1 < rs < 3): rs = 1.0
        dur = 0.54 * (P / 365.25) ** (1 / 3) * rs * rng.uniform(0.5, 1.0)  # days, solar-density scaling, random b
        dur = max(dur, 0.025)
        dep = float(np.exp(rng.uniform(np.log(100e-6), np.log(5000e-6))))
        r, _ = search.analyse(int(tic), raw, inj=(P, T0, dur, dep))
        rec = 0
        if r.get('status') == 'ok':
            for h in (1, 2, 0.5, 3, 1 / 3):
                if abs(r['P'] / (P * h) - 1) < 0.005:
                    dph = abs(((r['T0'] - T0 + 0.5 * P) % P) - 0.5 * P)
                    if dph < max(dur, r['dur']) or h != 1:
                        rec = h; break
        row = dict(tic=int(tic), tmag=base.get('tmag'), mad=base.get('mad'), Pinj=P, T0inj=T0, durinj=dur, depinj=dep,
                   Pfound=r.get('P'), snr=r.get('snr'), sde=r.get('sde'), nev=r.get('nev'), oe=r.get('oe_sig'),
                   sec=r.get('sec_snr'), rec=rec, base_snr=base.get('snr'), base_P=base.get('P'))
        if w is None:
            w = csv.DictWriter(fh, list(row.keys()))
            if not done: w.writeheader()
        w.writerow(row); fh.flush()
    del raw
