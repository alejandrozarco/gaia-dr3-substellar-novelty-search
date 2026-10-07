import requests,os,json
tok=open(os.path.expanduser('~/.config/ads/token')).read().strip().split('=')[-1].strip().strip('"')
H={'Authorization':'Bearer '+tok}
q='abs:("hot subdwarf" OR "hot subdwarfs" OR sdB OR sdBV OR sdO OR "blue large-amplitude pulsator" OR BLAP) AND abs:(TESS) AND year:2019-2026 AND (abs:(pulsat* OR variab* OR periodic* OR "light curve*") )'
docs=[];start=0
while True:
    r=requests.get('https://api.adsabs.harvard.edu/v1/search/query',params=dict(q=q,fl='bibcode,title,identifier,first_author',rows=200,start=start),headers=H,timeout=60).json()
    docs+=r['response']['docs']; start+=200
    if start>=r['response']['numFound']: break
out=[]
for d in docs:
    ax=[i.replace('arXiv:','') for i in d.get('identifier',[]) if i.startswith('arXiv:')]
    out.append(dict(b=d['bibcode'],fa=d.get('first_author',''),t=d.get('title',[''])[0],ax=ax[0] if ax else None))
json.dump(out,open('sdb_tess_papers.json','w'),indent=0)
print(len(out),'papers',sum(1 for o in out if o['ax']),'with arXiv')
for o in out: print(o['b'],o['fa'][:20],o['ax'],o['t'][:70])
