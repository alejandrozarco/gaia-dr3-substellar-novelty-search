import requests, io, csv, json, math
TAP="https://datalab.noirlab.edu/tap/sync"
def q(a,timeout=300):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':a},timeout=timeout); return r.status_code,r.text
# NEG CONTROL: target pred +1 deg in Dec, on usable exposure 032849
RA0,DEC0=252.0790,-24.7890
NRA,NDEC=RA0, DEC0+1.0   # -23.7890
sc,txt=q(f"""SELECT ra,dec,mjd,mag_auto,filter,fwhm FROM nsc_dr2.meas
WHERE exposure='c4d_170517_032849_ooi_Y_v1'
AND ra BETWEEN {NRA-0.02} AND {NRA+0.02} AND dec BETWEEN {NDEC-0.02} AND {NDEC+0.02}""")
rows=list(csv.DictReader(io.StringIO(txt))) if sc==200 and not txt.startswith('<') else []
def sep(r,r0,d0):
    dra=(float(r['ra'])-r0)*math.cos(math.radians(d0))*3600;dde=(float(r['dec'])-d0)*3600
    return math.hypot(dra,dde)
seps=sorted((sep(r,NRA,NDEC),r) for r in rows)
json.dump(rows, open("negctrl_p1deg.json","w"))
print(f"NEG CTRL +1deg @({NRA:.4f},{NDEC:.4f}) on 032849: {len(rows)} src in 72\" box")
print("  nearest 5 seps:", [round(s,2) for s,_ in seps[:5]])
print("  IN 0.44\" 3-sig ellipse:", sum(1 for s,_ in seps if s<0.44), "(expect 0)")
