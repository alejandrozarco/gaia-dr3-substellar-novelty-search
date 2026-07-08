import requests, io, csv, json, math
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=300):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
    return r.status_code,r.text
RA0,DEC0=252.0790,-24.7890
ids=["139366_91157","139366_77340","139366_77339"]
inl=",".join(f"'{i}'" for i in ids)
sc,txt=q(f"""SELECT id,ra,dec,ndet,deltamjd,class_star,gmag,rmag,imag,zmag,ymag,variable
FROM nsc_dr2.object WHERE id IN ({inl})""")
print("=== object (mean) records ===",sc)
print(txt)
def sep(ra,dec):
    dra=(ra-RA0)*math.cos(math.radians(DEC0))*3600;dde=(dec-DEC0)*3600
    return math.hypot(dra,dde),dra,dde
for r in csv.DictReader(io.StringIO(txt)):
    s,dra,dde=sep(float(r['ra']),float(r['dec']))
    print(f"  {r['id']}: mean sep={s:.2f}\"(dRA{dra:+.2f},dDec{dde:+.2f}) ndet={r['ndet']} deltamjd={float(r['deltamjd']):.0f}d var={r['variable']}")
