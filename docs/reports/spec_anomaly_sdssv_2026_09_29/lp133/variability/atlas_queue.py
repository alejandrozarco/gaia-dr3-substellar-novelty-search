"""Queue ATLAS forced photometry for LP 133-754 (Gaia DR3 1609392862209121664) at epoch 2021.0 position; token never printed."""
import os, json, requests, numpy as np
tok=open(os.path.expanduser("~/.config/atlas/token")).read().strip()
H={"Authorization":f"Token {tok}","Accept":"application/json"}; BASE="https://fallingstar-data.com/forcedphot"
ra0,dec0,pmra,pmdec=211.79318389854885,55.15819632693748,-60.39384961937155,181.49465178481682
dt=2021.0-2016.0
ra=ra0+pmra*dt/3.6e6/np.cos(np.radians(dec0)); dec=dec0+pmdec*dt/3.6e6
print("pos2021",ra,dec)
r=requests.post(f"{BASE}/queue/",headers=H,data=dict(ra=f"{ra:.6f}",dec=f"{dec:.6f}",mjd_min=57000,send_email=False),timeout=120)
print(r.status_code); j=r.json(); print({k:j.get(k) for k in ("url","id","ra","dec","mjd_min","timestamp")})
json.dump({k:j.get(k) for k in ("url","id","ra","dec","mjd_min","timestamp")},open("atlas_job.json","w"))
