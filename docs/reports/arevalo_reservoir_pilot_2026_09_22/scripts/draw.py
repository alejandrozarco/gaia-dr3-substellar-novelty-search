import subprocess,urllib.parse,time,csv,io,json
def tap(q):
    u="http://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync?request=doQuery&lang=adql&format=csv&query="+urllib.parse.quote(q)
    for k in range(4):
        p=subprocess.run(["curl","-sL","--max-time","600",u],capture_output=True,text=True)
        if p.returncode==0 and p.stdout.strip() and "ERROR" not in p.stdout[:400]: return p.stdout
        time.sleep(5*(k+1))
    raise SystemExit("TAP FAILED: "+p.stdout[:300])
T='"J/A+A/705/A247/catalog"'; COLS='recno, OID, RAJ2000, DEJ2000, magMean, Std, Pvar, nEpochs, predClass'
BASE="predClass='nonvar-star' AND magMean BETWEEN 14.5 AND 19.5 AND nEpochs>=80"
sets={"reservoir":(f"{BASE} AND Pvar>=0.99 AND Std>=0.04","MOD(recno,220)=13"),
      "control":(f"{BASE} AND Pvar<0.5","MOD(recno,8000)=13")}
for name,(cond,samp) in sets.items():
    n=tap(f"SELECT COUNT(*) FROM {T} WHERE {cond}").strip().splitlines()[-1]
    rows=list(csv.DictReader(io.StringIO(tap(f"SELECT {COLS} FROM {T} WHERE {cond} AND {samp}"))))
    seen=set(); tg=[]
    for r in rows:                                 # one entry per star (OIDs are per band/field)
        key=(round(float(r["RAJ2000"])*3600/2),round(float(r["DEJ2000"])*3600/2))
        if key in seen: continue
        seen.add(key)
        tg.append(dict(source_id=f"AREV_{r['OID']}",ra=float(r["RAJ2000"]),dec=float(r["DEJ2000"]),g=float(r["magMean"]),
                       std=float(r["Std"]),pvar=float(r["Pvar"]),sample=name))
    json.dump(tg,open(f"targets_{name}.json","w"))
    print(f"{name:10s}: parent population {n:>10s}   drawn {len(rows):5d}   unique stars {len(tg):5d}")
