import os,time,requests,json
tok=open(os.path.expanduser('~/.config/atlas/token')).read().strip(); H={'Authorization':f'Token {tok}','Accept':'application/json'}
urls=json.load(open('atlas_keep.json'))
while urls:
    for n,u in list(urls.items()):
        q=requests.get(u,headers=H,timeout=60)
        if q.status_code!=200: continue
        j=q.json()
        if j.get('finishtimestamp'):
            if j.get('result_url'):
                t=requests.get(j['result_url'],headers=H,timeout=120).text; open(f'atlas/{n}.csv','w').write(t); print(n,'ok',t.count('\n'),flush=True)
            else: print(n,'no result',j.get('error_msg'),flush=True)
            requests.delete(u,headers=H,timeout=60); urls.pop(n)
        time.sleep(1)
    time.sleep(30)
print('done',flush=True)
