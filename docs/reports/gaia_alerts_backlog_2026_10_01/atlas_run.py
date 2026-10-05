import os, time, requests, pandas as pd, io
tok=open(os.path.expanduser('~/.config/atlas/token')).read().strip()
H={'Authorization':f'Token {tok}','Accept':'application/json'}; B='https://fallingstar-data.com/forcedphot'
s=pd.read_csv('short.csv')
urls={}
for r in s.itertuples():
    if os.path.exists(f'atlas/{r.Name}.csv'): continue
    while True:
        q=requests.post(f'{B}/queue/',headers=H,data=dict(ra=r.RAdeg,dec=r.DEdeg,mjd_min=57000.,send_email=False),timeout=60)
        if q.status_code==201: urls[r.Name]=q.json()['url']; break
        if q.status_code==429: time.sleep(int(q.json().get('detail','x 10').split()[-2]) if False else 15); continue
        print(r.Name,'queue fail',q.status_code,q.text[:200],flush=True); break
print('queued',len(urls),flush=True)
while urls:
    for n,u in list(urls.items()):
        q=requests.get(u,headers=H,timeout=60)
        if q.status_code!=200: continue
        j=q.json()
        if j.get('finishtimestamp'):
            if j.get('result_url'):
                t=requests.get(j['result_url'],headers=H,timeout=120).text
                open(f'atlas/{n}.csv','w').write(t); print(n,'ok',t.count('\n'),flush=True)
            else: print(n,'no result',j.get('error_msg'),flush=True)
            requests.delete(u,headers=H,timeout=60); urls.pop(n)
        time.sleep(1)
    time.sleep(20)
print('done',flush=True)
