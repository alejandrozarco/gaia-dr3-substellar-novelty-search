import sys,warnings; warnings.filterwarnings('ignore')
import requests
c=sys.argv[1]
# list tables via VizieR TAP and grep full table dumps in tsv via asu-tsv
r=requests.get('https://vizier.cds.unistra.fr/viz-bin/asu-tsv',params={'-source':c,'-out.all':'','-out.max':'unlimited','-oc.form':'dec'},timeout=150)
txt=r.text; nrow=sum(1 for l in txt.split('\n') if l and not l.startswith('#'))
hits=[p for p in ['21821402','6130942326140307712','120559','181.496','181.4960','-47.527','47 31 37'] if p in txt]
tabs=[l for l in txt.split('\n') if l.startswith('#Table')]
print(c,r.status_code,'bytes',len(txt),'lines',nrow,'tables',len(tabs),'| HITS '+str(hits) if hits else '| none',flush=True)
