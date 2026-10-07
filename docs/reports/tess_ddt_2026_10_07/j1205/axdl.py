import json,requests,time,os,tarfile,gzip,io,re
P=json.load(open('sdb_tess_papers.json'))
pats=[b'6130942326140307712',b'21821402',b'120559',b'1205-47',b'1205-4731',b'181.496',b'181.4961',b'12:05:59',b'12 05 59',b'213-067795',b'12055907']
for o in P:
    a=o['ax']
    if not a: continue
    fn=f'ax/{a}.src'
    if not os.path.exists(fn):
        r=requests.get(f'https://arxiv.org/e-print/{a}',timeout=120,headers={'User-Agent':'research-grep'}); open(fn,'wb').write(r.content); time.sleep(3)
    raw=open(fn,'rb').read(); blobs=[]
    try:
        tf=tarfile.open(fileobj=io.BytesIO(raw)); 
        for m in tf.getmembers():
            if m.isfile(): blobs.append((m.name,tf.extractfile(m).read()))
    except Exception:
        try: blobs=[('main',gzip.decompress(raw))]
        except Exception: blobs=[('raw',raw)]
    hits=[(n,p.decode()) for n,b in blobs for p in pats if p in b]
    print(a,o['fa'][:15],len(raw),len(blobs),'HITS' if hits else 'none',hits[:5],flush=True)
