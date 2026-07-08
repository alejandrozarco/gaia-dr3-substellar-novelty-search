import json, re
raw = json.load(open("mpc_getobs_raw.json"))
# raw is list; each has OBS80 multiline
lines=[]
for rec in [raw[0]]:
    ob = rec.get("OBS80") or ""
    for ln in ob.split("\n"):
        if ln.strip(): lines.append(ln)
# write raw obs80
open("mpc_obs80.txt","w").write("\n".join(lines)+"\n")

def parse_line(ln):
    # cols: desig(1-12) ...; date at cols 16-32 (0-based 15..32); RA 33-44; DEC 45-56; mag ~65-70; band 71; stn last 3
    # OBS80 fixed format
    try:
        yr=int(ln[15:19]); mo=int(ln[20:22]); day=float(ln[23:32])
    except:
        return None
    stn=ln[77:80].strip()
    band=ln[70:71]
    note2=ln[14:15]
    mag=ln[65:70].strip()
    return dict(y=yr,m=mo,d=day,stn=stn,band=band,note2=note2,mag=mag,raw=ln)

obs=[]
for ln in lines:
    p=parse_line(ln)
    if p and p['note2'] not in ('s',):  # skip satellite pos 's' lines
        obs.append(p)

# compute decimal-year sortable and jd approx
from datetime import datetime, timedelta
def to_jd(y,m,d):
    # d is day.fraction
    di=int(d); frac=d-di
    dt=datetime(y,m,di)+timedelta(days=frac)
    a=(14-dt.month)//12; yy=dt.year+4800-a; mm=dt.month+12*a-3
    jdn=dt.day+((153*mm+2)//5)+365*yy+yy//4-yy//100+yy//400-32045
    jd=jdn+(dt.hour-12)/24+dt.minute/1440+dt.second/86400+dt.microsecond/86400e6
    return jd
for o in obs:
    o['jd']=to_jd(o['y'],o['m'],o['d'])
obs.sort(key=lambda o:o['jd'])
json.dump(obs, open("obs_parsed_fresh.json","w"), indent=0)

print("N optical obs (excl sat 's'):", len(obs))
print("ARC START:", obs[0]['y'],obs[0]['m'],round(obs[0]['d'],3),"stn",obs[0]['stn'],"jd",round(obs[0]['jd'],3))
print("ARC END:  ", obs[-1]['y'],obs[-1]['m'],round(obs[-1]['d'],3),"stn",obs[-1]['stn'],"jd",round(obs[-1]['jd'],3))
from collections import Counter
print("stations:", Counter(o['stn'] for o in obs))
print("years:", sorted(set(o['y'] for o in obs)))
# any obs in 2016+, in 2017?
for yr in [2016,2017,2018]:
    yy=[o for o in obs if o['y']==yr]
    print(f"  obs in {yr}: {len(yy)}", [(o['m'],round(o['d'],2),o['stn']) for o in yy][:10])
# W84?
w84=[o for o in obs if o['stn']=='W84']
print("W84 (CTIO-DECam) obs in arc:", len(w84), [(o['y'],o['m'],round(o['d'],2)) for o in w84])
