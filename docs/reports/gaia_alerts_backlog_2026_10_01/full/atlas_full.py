import os, time, requests, pandas as pd, json, datetime
tok=open(os.path.expanduser('~/.config/atlas/token')).read().strip()
H={'Authorization':f'Token {tok}','Accept':'application/json'}; B='https://fallingstar-data.com/forcedphot'
t=pd.read_csv('gates.csv'); t=t[t.survive].reset_index(drop=True)
# positive control first: Gaia24deb (pilot UG with known ATLAS outbursts)
todo=[('CTRL_Gaia24deb',132.88327,-9.77135)]+[(r.Name,r.RAdeg,r.DEdeg) for r in t.itertuples() if not os.path.exists(f'atlas/{r.Name}.csv')]
def now(): return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
pending={}; MAX=8
def req(f,*a,**k):
    for i in range(6):
        try: return f(*a,headers=H,timeout=120,**k)
        except Exception as e: print('net',e.__class__.__name__,flush=True); time.sleep(30)
    return None
while todo or pending:
    while todo and len(pending)<MAX:
        n,a,d=todo[0]
        q=req(requests.post,f'{B}/queue/',data=dict(ra=a,dec=d,mjd_min=57000.,send_email=False))
        if q is not None and q.status_code==201: pending[n]=q.json()['url']; todo.pop(0); print(now(),'queued',n,flush=True)
        elif q is not None and q.status_code==429: time.sleep(20); break
        else: print(n,'queue fail',None if q is None else (q.status_code,q.text[:100]),flush=True); time.sleep(30); break
    for n,u in list(pending.items()):
        q=req(requests.get,u)
        if q is None or q.status_code!=200: continue
        j=q.json()
        if j.get('finishtimestamp'):
            if j.get('result_url'):
                r=req(requests.get,j['result_url'])
                if r is not None: open(f'atlas/{n}.csv','w').write(r.text); print(now(),n,'ok',r.text.count('\n'),flush=True)
            else: print(n,'no result',j.get('error_msg'),flush=True)
            req(requests.delete,u); pending.pop(n)
        time.sleep(1)
    time.sleep(15)
print('END',now(),flush=True)
