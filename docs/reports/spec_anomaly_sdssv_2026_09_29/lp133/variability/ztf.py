import requests, io, numpy as np
from astropy.table import Table
ra0,dec0,pmra,pmdec=211.79318389854885,55.15819632693748,-60.39384961937155,181.49465178481682
dt=2020.5-2016.0  # ZTF mid-epoch
ra=ra0+pmra*dt/3.6e6/np.cos(np.radians(dec0)); dec=dec0+pmdec*dt/3.6e6
def get(ra,dec,rad,extra=""):
    u=f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE {ra} {dec} {rad/3600}&FORMAT=csv{extra}"
    r=requests.get(u,timeout=300); return r
# probe known object (positive control): use Gaia-bright star nearby? use generic known: AM Her
pc=get(274.05493,49.86792,3); print("probe AM Her rows", len(pc.text.splitlines())-1)
r=get(ra,dec,3); open("ztf_raw.csv","w").write(r.text)
t=Table.read(io.StringIO(r.text),format="csv"); print("rows",len(t))
for f in ["zg","zr","zi"]:
    m=t["filtercode"]==f; g=m&(t["catflags"]==0)
    print(f,"all",m.sum(),"catflags0",g.sum(),"oids",set(t["oid"][m]))
# distances of oids at epoch per point
