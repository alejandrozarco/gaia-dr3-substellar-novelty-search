import time, json, requests, pandas as pd, numpy as np, datetime
v=pd.read_csv('vet_short.csv'); s=pd.read_csv('short.csv')
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0 (research script)'
def vsx(a,d,r=30):
    for k in range(5):
        try:
            t=S.get('https://www.aavso.org/vsx/index.php',params=dict(view='api.list',ra=a,dec=d,radius=r/3600,format='json'),timeout=120)
            if t.ok and t.text.startswith('{'):
                it=t.json().get('VSXObjects',{}); it=it.get('VSXObject',[]) if isinstance(it,dict) else []
                return it if isinstance(it,list) else [it]
            print('bad',t.status_code,t.text[:80])
        except Exception as e: print('exc',e)
        time.sleep(10*(k+1))
    return None
print('control', vsx(325.67854,43.58617)[0]['Name'])
for i,r in v[v.vsx=='FAIL'].iterrows():
    p=s[s.Name==r.Name].iloc[0]; ts=datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%MZ')
    x=vsx(p.RAdeg,p.DEdeg)
    v.loc[i,'vsx']='FAIL' if x is None else json.dumps([(y.get('Name'),y.get('VariabilityType'),round(3600*np.hypot((float(y['RA2000'])-p.RAdeg)*np.cos(np.radians(p.DEdeg)),float(y['Declination2000'])-p.DEdeg),1)) for y in x])
    v.loc[i,'vsx_ts']=ts; print(r.Name,v.loc[i,'vsx'],flush=True); time.sleep(3)
v.to_csv('vet_short.csv',index=False)
