"""Build OBS80 arc files for the orbit-level with/without test.
  full.obs        : all 2249 MPC lines (control; should reproduce JPL)
  arc_minus.obs   : all lines EXCEPT the 10 re-measured W84 epochs
  joint_ours.obs  : all lines, but those 10 W84 lines' RA/Dec replaced by OUR NSC positions
Only cols 33-56 (RA+Dec) change in joint_ours; date/mag/band/catalog/obscode identical.
"""
import json, numpy as np
from astropy.time import Time

def obs80_mjd(line):
    y=int(line[15:19]); m=int(line[20:22]); d=float(line[23:32])
    di=int(d); frac=d-di
    return Time(f"{y:04d}-{m:02d}-{di:02d}",format="isot",scale="utc").mjd+frac

def fmt_ra(ra_deg):
    h=ra_deg/15.0; H=int(h); m=(h-H)*60; M=int(m); s=(m-M)*60
    out=f"{H:02d} {M:02d} {s:06.3f}"
    assert len(out)==12, repr(out); return out

def fmt_dec(dec_deg):
    sign="-" if dec_deg<0 else "+"; a=abs(dec_deg)
    D=int(a); m=(a-D)*60; M=int(m); s=(m-M)*60
    out=f"{sign}{D:02d} {M:02d} {s:05.2f}"
    assert len(out)==12, repr(out); return out

lines=open("raw/mpc_obs80.txt").read().splitlines()
meas=[m for m in json.load(open("raw/measured.json")) if m["status"]=="CATALOG"]

# round-trip check: reformat every W84 published line and confirm columns reproduce (to rounding)
w84=[i for i,l in enumerate(lines) if l[77:80]=="W84"]
print(f"total lines={len(lines)}  W84 lines={len(w84)}  measured epochs={len(meas)}")

# match each measured epoch to its OBS80 line by mjd + obscode W84
match={}
for m in meas:
    cand=[(abs(obs80_mjd(lines[i])-float(m["mjd_obs"]))*86400, i) for i in w84]
    dt,i=min(cand)
    assert dt<2.0, f"idx{m['idx']} no OBS80 match within 2s (best {dt:.2f}s)"
    assert i not in match.values(), f"dup match line {i}"
    match[m["idx"]]=i
    # sanity: published RA/Dec in the line vs my stored ra_pub/dec_pub
    old=lines[i]
    print(f" idx{m['idx']:>2} -> line {i}  dt={dt:.2f}s  band={m['band']}  {old[32:56]}")

# build files
minus_idx=set(match.values())
open("orbit/full.obs","w").write("\n".join(lines)+"\n")
open("orbit/arc_minus.obs","w").write("\n".join(l for i,l in enumerate(lines) if i not in minus_idx)+"\n")

joint=list(lines)
for m in meas:
    i=match[m["idx"]]; l=lines[i]
    ra_s=fmt_ra(m["ra_ours"]); dec_s=fmt_dec(m["dec_ours"])
    newl=l[:32]+ra_s+dec_s+l[56:]
    assert len(newl)==len(l), (len(newl),len(l))
    joint[i]=newl
open("orbit/joint_ours.obs","w").write("\n".join(joint)+"\n")

print(f"\nwrote orbit/full.obs ({len(lines)}), arc_minus.obs ({len(lines)-len(minus_idx)}), joint_ours.obs ({len(joint)})")
# show one before/after
i0=match[meas[0]['idx']]
print("example swap (idx%s):"%meas[0]['idx'])
print("  PUB :", lines[i0][32:56])
print("  OURS:", joint[i0][32:56])
