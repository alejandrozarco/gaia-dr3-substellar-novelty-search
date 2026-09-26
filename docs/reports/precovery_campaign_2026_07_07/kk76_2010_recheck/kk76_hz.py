import os
import subprocess,urllib.parse,re,sys
EL=dict(EPOCH="2453857.5",ECLIP="J2000",EC="0.0187655",QR="41.9051643",TP="2467230.042755",
        OM="86.99310",W="216.16093",IN="1.88308",H="6.3",G="0.15")
def hz(times,center="500@-48"):
    p={"format":"text","COMMAND":"';'","OBJ_DATA":"NO","MAKE_EPHEM":"YES","EPHEM_TYPE":"OBSERVER",
       "CENTER":f"'{center}'","TLIST":" ".join(f"'{t}'" for t in times),"TLIST_TYPE":"JD","TIME_TYPE":"UT",
       "QUANTITIES":"'1'","ANG_FORMAT":"DEG","EXTRA_PREC":"YES","CSV_FORMAT":"YES"}
    p.update({k:f"'{v}'" for k,v in EL.items()})
    u="https://ssd.jpl.nasa.gov/api/horizons.api?"+"&".join(f"{k}={urllib.parse.quote(str(v),safe=chr(39))}" for k,v in p.items())
    out=subprocess.run(["curl","-sL","--max-time","120",u],capture_output=True,text=True).stdout
    if "$$SOE" not in out: print(out[:1500]); sys.exit(1)
    rows=[]
    for l in out.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines():
        f=[x.strip() for x in l.split(",")]; rows.append((f[0],float(f[3]),float(f[4])))
    return rows
if __name__=="__main__":
    import csv,math
    obs=list(csv.DictReader(open(os.path.expanduser("~/claude_projects/gaia-recovered-2026-05-27/docs/reports/precovery_campaign_2026_07_07/wave3/hst_kk76/candidate_astrometry.csv"))))
    from astropy.time import Time
    jds=[Time(o["obsTime_UTC"],scale="utc").jd for o in obs]
    pred=hz([f"{j:.6f}" for j in jds])
    for o,(t,ra,de) in zip(obs,pred):
        dra=(ra-float(o["RA_deg"]))*math.cos(math.radians(de))*3600; dde=(de-float(o["Dec_deg"]))*3600
        print(f"  {o['frame_id']}  measured ({float(o['RA_deg']):.6f},{float(o['Dec_deg']):.6f})  predicted ({ra:.6f},{de:.6f})  O-C = {-dra:+.3f}in, {-dde:+.3f}in")
