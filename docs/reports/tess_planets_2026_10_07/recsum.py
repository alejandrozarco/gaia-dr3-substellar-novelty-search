import json,glob,numpy as np
for f in sorted([g for g in glob.glob('rec/*.json') if 'lsoo' not in g], key=lambda x: __import__('os').path.getmtime(x)):
    r=json.load(open(f))
    if 'sectors' not in r: print(f,'ERR'); continue
    S=[s for s in r['sectors'] if 'smax' in s]
    if not S: print(r['tic'],'no archival sectors'); continue
    fap=np.array([s['fap_trials'] for s in S]); sm=np.array([s['smax'] for s in S])
    comb=np.sum(sm**2)  # crude
    n_sig=(fap<=0.02).sum()
    print(f"{r['tic']:>10} P={r['P']:.4f} nsec={len(S)} n(FAP<=0.02)={n_sig} min_fap={fap.min():.3f} smax=[{', '.join(f'{x:.1f}' for x in sm)}] phases=[{', '.join(str(round(s['ph_max'],2)) for s in S)}]")
