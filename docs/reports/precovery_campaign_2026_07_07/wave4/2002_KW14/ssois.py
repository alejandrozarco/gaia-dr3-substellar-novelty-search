import requests
# CADC SSOIS by-name resolver (Horizons ephemeris), TSV output, DECam era window
base="https://www.canfar.net/cadc-ssois/ssosclf.pl"
alts=[
 "https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/cadcbin/ssos/ssosclf.pl",
 "https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/ssois/ssosclf.pl",
]
params=dict(lang="en", object="2002 KW14", search="bynameHorizons",
            epoch1="2017 05 01", epoch2="2017 08 20", eunits="none",
            extres="no", xxx="", format="tsv")
for u in alts:
    try:
        r=requests.get(u, params=params, timeout=90)
        print(u, r.status_code, len(r.text))
        print(r.text[:400])
        if r.status_code==200 and "Image" in r.text and "Datalink" in r.text:
            open("ssois_2017.tsv","w").write(r.text); print("SAVED", u); break
    except Exception as e:
        print("ERR",u,e)
