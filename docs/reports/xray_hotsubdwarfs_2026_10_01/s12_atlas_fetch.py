import os, json, requests, time
tok=open(os.path.expanduser('~/.config/atlas/token')).read().strip()
H={'Authorization':f'Token {tok}','Accept':'application/json'}
tasks=json.load(open('atlas/tasks.json')); done=0; pend=0
for gid,url in tasks.items():
    fn=f'atlas/{gid}.txt'
    if os.path.exists(fn): done+=1; continue
    r=requests.get(url,headers=H,timeout=60)
    if r.status_code!=200: print(gid,'status',r.status_code); continue
    j=r.json()
    if j.get('finishtimestamp') and j.get('result_url'):
        t=requests.get(j['result_url'],headers=H,timeout=120)
        if t.status_code==200 and len(t.text.splitlines())>1: open(fn,'w').write(t.text); done+=1
        else: print(gid,'empty result',t.status_code,len(t.text))
    elif j.get('finishtimestamp'): print(gid,'finished, no result:',str(j.get('error_msg'))[:100]); 
    else: pend+=1
print('done',done,'pending',pend,'of',len(tasks))
