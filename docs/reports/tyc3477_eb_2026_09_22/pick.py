import subprocess,urllib.parse,csv,io
def tap(q):
    u="http://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync?request=doQuery&lang=adql&format=csv&query="+urllib.parse.quote(q)
    return list(csv.DictReader(io.StringIO(subprocess.run(["curl","-sL","--max-time","400",u],capture_output=True,text=True).stdout)))
T='"III/286/catalog"'; C="APOGEE,Tel,Field,Teff,logg,\"[M/H]\",SNR,Nvis,s_HRV,FWHMCC,HRV"
sel={"F":"Teff BETWEEN 6000 AND 6250 AND logg BETWEEN 3.8 AND 4.1 AND \"[M/H]\" BETWEEN -0.65 AND -0.35",
     "K":"Teff BETWEEN 4300 AND 4500 AND logg BETWEEN 4.5 AND 4.8 AND \"[M/H]\" BETWEEN -0.4 AND 0.0"}
for k,cond in sel.items():
    rows=tap(f"SELECT TOP 8 {C} FROM {T} WHERE {cond} AND SNR>300 AND Nvis>=3 AND s_HRV<0.3 AND Tel='apo25m' ORDER BY SNR DESC")
    print(f"=== {k} template candidates ===")
    for r in rows: print("   ",{c:r[c] for c in r})
