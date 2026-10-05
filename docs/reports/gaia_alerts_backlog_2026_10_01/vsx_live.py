import pandas as pd, requests, time, json, sys, datetime
s=pd.read_csv('g2_novsxviz.csv')
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0 (research script)'
def vsx(a,d,r=15):
    for k in range(4):
        try:
            t=S.get('https://www.aavso.org/vsx/index.php',params=dict(view='api.list',ra=a,dec=d,radius=r/3600,format='json'),timeout=60)
            if t.status_code==200 and t.text.startswith('{'):
                j=t.json(); it=j.get('VSXObjects',{})
                it=it.get('VSXObject',[]) if isinstance(it,dict) else []
                return it if isinstance(it,list) else [it]
        except Exception as e: pass
        time.sleep(5*(k+1))
    return None
ctl=vsx(325.67854,43.58617)
print('control', ctl and ctl[0]['Name'], datetime.datetime.utcnow().isoformat(),flush=True)
assert ctl and ctl[0]['Name']=='SS Cyg'
out=[]
for i,r in s.iterrows():
    it=vsx(r.RAdeg,r.DEdeg)
    if i%100==0:
        c=vsx(325.67854,43.58617); print(i,'ctl',bool(c),flush=True)
    out.append(dict(Name=r.Name, vsx_status='FAIL' if it is None else ('HIT' if it else 'NONE'),
        vsx=json.dumps([(x.get('Name'),x.get('VariabilityType'),x.get('RA2000'),x.get('Declination2000')) for x in (it or [])])))
    time.sleep(0.5)
pd.DataFrame(out).to_csv('vsx_live.csv',index=False)
print('done',datetime.datetime.utcnow().isoformat(), pd.DataFrame(out).vsx_status.value_counts().to_dict())
