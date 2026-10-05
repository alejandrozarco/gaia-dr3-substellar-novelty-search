import time, json, random, datetime, requests, pandas as pd, numpy as np
t=pd.read_csv('targets.csv')
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0 (research script)'
def now(): return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
def vsx(a,d,r=30):
    for k in range(4):
        try:
            q=S.get('https://www.aavso.org/vsx/index.php',params=dict(view='api.list',ra=a,dec=d,radius=r/3600,format='json'),timeout=90)
            if q.ok and q.text.lstrip().startswith('{'):
                it=q.json().get('VSXObjects',{}); it=it.get('VSXObject',[]) if isinstance(it,dict) else []
                return it if isinstance(it,list) else [it]
            print('bad',q.status_code,q.text[:60].replace('\n',' '),flush=True)
        except Exception as e: print('exc',e,flush=True)
        time.sleep(10*(k+1))
    return None
def control():
    c=vsx(274.05458,49.86778,30)
    ok=bool(c) and any(x.get('Name')=='AM Her' for x in c)
    print(now(),'CONTROL AM Her',ok,flush=True); return ok
batch=0; ok=control(); rows=[]
for i,r in t.iterrows():
    if i>0 and i%50==0: batch+=1; ok=control()
    ts=now(); v=vsx(r.RAdeg,r.DEdeg)
    if v is None: st,txt='FAIL',''
    else:
        L=[(x.get('Name'),x.get('VariabilityType'),round(3600*np.hypot((float(x['RA2000'])-r.RAdeg)*np.cos(np.radians(r.DEdeg)),float(x['Declination2000'])-r.DEdeg),1)) for x in v]
        st='HIT' if L else 'NONE'; txt=json.dumps(L)
    rows.append(dict(Name=r.Name,vsx_ts=ts,vsx_status=st,vsx=txt,batch=batch,batch_ctrl_pre=ok))
    print(i,r.Name,st,txt,flush=True)
    pd.DataFrame(rows).to_csv('vsx_full.csv',index=False)
    time.sleep(random.uniform(3,8))
ok2=control()
d=pd.DataFrame(rows)
# a batch is a HOLE if its pre-control or the following control failed
d.to_csv('vsx_full.csv',index=False); print('END',now(),'final ctrl',ok2,d.vsx_status.value_counts().to_dict(),flush=True)
