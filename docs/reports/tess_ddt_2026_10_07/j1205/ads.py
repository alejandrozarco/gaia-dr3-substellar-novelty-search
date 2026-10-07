import requests,os,glob
p=os.path.expanduser('~/.config/ads'); 
tok=open(p).read().strip() if os.path.isfile(p) else open(glob.glob(p+'/*')[0]).read().strip()
tok=tok.split('=')[-1].strip().strip('"')
H={'Authorization':'Bearer '+tok}
qs=['"J120559.0-473137"','"6130942326140307712"','"21821402"','"TIC 21821402"','"12055907-4731376"','"J120559.08-473138.6"','"213-067795"','"J1205-4731"','"J1205-473"','"J120559-473137"','"J120559.0-473137"','"J1205-47"','"0424-0366067"','"J120559"']
# control
qs=['"AM Her"']+qs
for q in qs:
    for fld in ['full','abs']:
        r=requests.get('https://api.adsabs.harvard.edu/v1/search/query',params=dict(q=f'{fld}:{q}',fl='bibcode,title',rows=50),headers=H,timeout=60).json()
        n=r['response']['numFound']; print(fld,q,n)
        if q!='"AM Her"':
            for d in r['response']['docs']: print('   ',d['bibcode'],d.get('title',[''])[0][:90])
