import requests
u="https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/cadcbin/ssos/ssosclf.pl"
variants=[
 dict(lang="en",object="2002 KW14",search="bynameHorizons",epoch1="2017-05-01",epoch2="2017-08-20",eunits="arcseconds",extres="yes",xxx="Search"),
 dict(lang="en",object="307251",search="bynameHorizons",epoch1="2017-05-01",epoch2="2017-08-20",eunits="arcseconds",extres="yes",xxx="Search"),
 dict(lang="en",object="2002 KW14",search="bynameHorizons",epoch1="2017-05-01",epoch2="2017-08-20"),
]
for i,p in enumerate(variants):
    try:
        r=requests.get(u, params=p, timeout=120)
        print(i, r.status_code, len(r.text), "| header:", r.text.splitlines()[0][:80] if r.text else "")
        if r.status_code==200 and "Image" in r.text:
            open(f"ssois_v{i}.tsv","w").write(r.text)
            nlines=len([l for l in r.text.splitlines() if l.strip()])
            print("   SAVED lines=",nlines)
    except Exception as e:
        print(i,"ERR",e)
