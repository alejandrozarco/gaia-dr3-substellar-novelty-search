import requests,os,sys,json
tok=open(os.path.expanduser('~/.config/ads/token')).read().strip()
H={'Authorization':'Bearer '+tok}
for q in sys.argv[1:]:
    r=requests.get('https://api.adsabs.harvard.edu/v1/search/query',headers=H,params={'q':q,'fl':'bibcode,author,year,title,pub,volume,page','rows':5})
    print('Q:',q)
    for d in r.json().get('response',{}).get('docs',[]):
        print('  ',d.get('bibcode'),'|',(d.get('author') or [''])[0],'+%d'%(len(d.get('author') or [])-1),'|',d.get('year'),'|',(d.get('title') or [''])[0][:110],'|',d.get('volume'),d.get('page'))
