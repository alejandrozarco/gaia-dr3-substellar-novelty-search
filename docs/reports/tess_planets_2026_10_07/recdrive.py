import pandas as pd, os, subprocess, time
while True:
    os.system('venv/bin/python triage.py 0105 0 > /dev/null 2>&1; venv/bin/python vet_lc.py 0105 > /dev/null 2>&1')
    c=pd.read_csv('shortlist_s0105_vet.csv')
    c=c[c.toi.isna() & ~c.sinusoid.fillna(False).astype(bool) & ~c.half_bad.fillna(False).astype(bool)]
    c['gapfl']=(c.frac_after_gap>0.4)
    c=c.sort_values(['gapfl','prio','snr'],ascending=[True,True,False])
    todo=[r for _,r in c.iterrows() if not os.path.exists(f'rec/{int(r.tic)}.json')]
    if not todo:
        if os.path.exists('STOP_REC'): break
        time.sleep(120); continue
    r=todo[0]
    with open('recdrive.log','a') as fh:
        fh.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())} start {int(r.tic)} P={r.P:.5f}\n"); fh.flush()
        try:
            subprocess.run(['venv/bin/python','recover.py',str(int(r.tic)),str(r.P),str(r.T0),str(r.dur),'105'],stdout=fh,stderr=subprocess.STDOUT,timeout=1500)
        except Exception as e:
            fh.write(f'fail {e}\n'); open(f'rec/{int(r.tic)}.json','w').write('{"error":"timeout"}')
