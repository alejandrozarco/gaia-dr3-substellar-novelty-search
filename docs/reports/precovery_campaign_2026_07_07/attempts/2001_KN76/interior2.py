import requests, io, csv
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=120):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
    return r.status_code,r.text
adql="SELECT e.exposure,e.mjd,e.depth95,e.fwhm,e.exptime,e.filter FROM nsc_dr2.exposure e WHERE e.exposure IN ('tu2088892','tu2090119','tu2091019','tu2092162')"
sc,txt=q(adql)
print("HTTP",sc)
print(txt[:1500])
