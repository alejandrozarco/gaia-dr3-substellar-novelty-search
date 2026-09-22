import json,os,subprocess,urllib.parse,time
tok=open(os.path.expanduser("~/.config/ads/token")).read().strip()
def q(s):
    u="https://api.adsabs.harvard.edu/v1/search/query?q="+urllib.parse.quote(s)+"&fl=bibcode,title,year&rows=10"
    for k in range(3):
        p=subprocess.run(["curl","-sS","--max-time","60","-H",f"Authorization: Bearer {tok}",u],capture_output=True,text=True)
        if p.returncode==0 and p.stdout.strip():
            try: return json.loads(p.stdout)["response"]
            except Exception: pass
        time.sleep(2)
    return None
print("positive control: TYC with a known published EB paper? -> 'KIC 5095269' (circumbinary planet host)")
r=q('full:"KIC 5095269"'); print("   ",r["numFound"] if r else "FAIL","hits\n")
for d in ["TYC 3477-27-1","TIC 161042835","2M14535269+4956476","2MASS J14535269+4956476","1593152388271709824","UCAC4 700-056053","AP J14535269+4956476"]:
    r=q(f'full:"{d}"')
    print(f"  {d:30s} {'QUERY_FAILED' if r is None else str(r['numFound'])+' hit(s)'}"+("" if not r or not r["numFound"] else ": "+"; ".join(x["bibcode"]+" "+(x.get("title") or [''])[0][:50] for x in r["docs"][:4])))
