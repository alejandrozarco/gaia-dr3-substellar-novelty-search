import requests, pandas as pd, re, time, json, datetime
from concurrent.futures import ThreadPoolExecutor
t=pd.read_csv('gates.csv').set_index('Name')
L=open('vizall_list.txt').read().split()
def one(n):
    r=t.loc[n]
    for k in range(3):
        try:
            x=requests.get('https://vizier.cds.unistra.fr/viz-bin/asu-tsv',params={'-c':f'{r.RAdeg:.6f} {r.DEdeg:+.6f}','-c.rs':2,'-out.max':1,'-out.add':'_r'},timeout=400)
            if x.ok and 'CatalogsExamined' in x.text: break
        except Exception: time.sleep(10)
    else: return n,None
    open(f'vizraw/{n}.txt','w').write(x.text)
    cats=[]; cur=None; title=''; ndata=0; state=0
    def flush():
        if cur and ndata>0: cats.append((cur,title))
    for line in x.text.splitlines():
        if line.startswith('#RESOURCE') or line.startswith('#Table'):
            flush(); cur=None; ndata=0; state=0
        if line.startswith('#Name: ') and '/' in line: cur=line[7:].strip()
        elif line.startswith('#Title: '): title=line[8:].strip()[:90]
        elif line.startswith('---'): state=1
        elif state==1 and line.strip() and not line.startswith('#'): ndata+=1
    flush()
    return n,cats
res=dict(ThreadPoolExecutor(4).map(one,L))
json.dump(res,open('vizall.json','w'),indent=0)
skip=re.compile(r'^(I/|II/|IV/|V/1[45]|VI/|B/denis|B/vsx|J/ApJ/867/105|J/ApJ/751/52|J/A\+A/638/A21|J/MNRAS/458/3479)')
for n,c in res.items():
    if c is None: print(n,'QUERYFAIL'); continue
    keep=sorted(set((a.rsplit('/',1)[0] if a.count('/')>2 else a,b) for a,b in c if not skip.match(a)))
    print(n,len(c),'|', ' ;; '.join(f'{a}: {b}' for a,b in keep))
