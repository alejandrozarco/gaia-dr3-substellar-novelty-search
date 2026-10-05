import pyvo, numpy as np, collections
s=pyvo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")
ra,dec=305.66064,39.19732
q=f"""SELECT a.uri, p.planeid, p.obsid, p.energy_bandpassname, p.time_bounds_lower, p.time_bounds_upper, p.provenance_version
FROM spherex.artifact a JOIN spherex.plane p ON a.planeid=p.planeid
WHERE 1=CONTAINS(POINT('ICRS',{ra},{dec}),p.poly) ORDER BY p.time_bounds_lower"""
t=s.search(q).to_table()
print(len(t)); print(t[:3])
rel=[u.split('/')[3] if 'spherex' in u else u for u in t['uri']]
print(collections.Counter([u.split('/')[3] for u in t['uri']]))
print(collections.Counter(zip([u.split('/')[3] for u in t['uri']],t['energy_bandpassname'])))
t.write('tap_frames.ecsv',overwrite=True)
