import pandas as pd, requests, time, os
s=pd.read_csv('g2_novsxviz.csv'); S=requests.Session()
bad=[]
for n in s.Name:
    f=f'glc/{n}.csv'
    if os.path.exists(f) and os.path.getsize(f)>50: continue
    ok=False
    for k in range(3):
        try:
            r=S.get(f'http://gsaweb.ast.cam.ac.uk/alerts/alert/{n}/lightcurve.csv',timeout=60)
            if r.status_code==200 and r.text.startswith(n) and r.text.count('\n')>3:
                open(f,'w').write(r.text); ok=True; break
        except Exception: pass
        time.sleep(3)
    if not ok: bad.append(n)
    time.sleep(0.3)
print('fail',len(bad),bad[:20])
