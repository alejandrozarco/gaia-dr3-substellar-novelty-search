import requests
u="https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/cadcbin/ssos/ssosclf.pl"
base=dict(lang="en",object="2002 KW14",search="bynameHorizons",epoch1="2017-05-01",epoch2="2017-08-20")
for fmt in ["tsv"]:
    p=dict(base); p["format"]=fmt
    r=requests.get(u,params=p,timeout=120)
    print("format=",fmt,r.status_code,len(r.text), r.text.splitlines()[0][:60] if r.text else "")
    if r.status_code==200 and r.text.startswith("Image"):
        open("ssois_2017.tsv","w").write(r.text); print("SAVED TSV")
