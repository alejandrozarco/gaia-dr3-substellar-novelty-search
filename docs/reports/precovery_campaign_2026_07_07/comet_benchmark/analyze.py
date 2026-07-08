"""Assemble benchmark_table.csv + three-way comparison stats + photocenter (sunward) projection."""
import json, csv, numpy as np

meas=json.load(open("raw/measured.json"))
sun={r["idx"]:r for r in csv.DictReader(open("raw/horizons_sunward.csv"))}

def proj_sunward(dE,dN,antiSunPA):
    """Project offset (East,North arcsec) onto SUNWARD unit vector (PA=antiSunPA+180)."""
    pa=np.radians(antiSunPA+180.0)
    u_e,u_n=np.sin(pa),np.cos(pa)            # sunward unit (E,N)
    p_e,p_n=np.sin(pa+np.pi/2),np.cos(pa+np.pi/2)  # perpendicular
    return dE*u_e+dN*u_n, dE*p_e+dN*p_n       # (sunward, perp) components

rows=[]
for m in meas:
    if m["status"]!="CATALOG":
        rows.append(m); continue
    s=sun[str(m["idx"])]
    aspa=float(s["sunTargetPA"])
    # ours-vs-Horizons and published-vs-Horizons, projected sunward
    sun_o,perp_o=proj_sunward(m["dRA_ours_hor"],m["dDec_ours_hor"],aspa)
    # published - horizons
    cd=np.cos(np.radians(m["dec_hor"]))
    dRA_pub_hor=(m["ra_pub"]-m["ra_hor"])*3600*cd
    dDec_pub_hor=(m["dec_pub"]-m["dec_hor"])*3600
    sun_p,perp_p=proj_sunward(dRA_pub_hor,dDec_pub_hor,aspa)
    row=dict(
      idx=m["idx"], obstime=m["obstime"], band=m["band"], exposure=m["exposure"],
      dt_frame_mid_s=m["dt_frame_mid_s"], r_helio_au=s["r_helio_au"], delta_au=s["delta_au"],
      antiSunPA_deg=round(aspa,1),
      ra_ours=round(m["ra_ours"],6), dec_ours=round(m["dec_ours"],6),
      ra_pub=round(m["ra_pub"],6), dec_pub=round(m["dec_pub"],6),
      ra_hor=round(m["ra_hor"],6), dec_hor=round(m["dec_hor"],6),
      mag_ours=m["mag_ours"], mag_pub=m["mag_pub"], fwhm_ours=m["fwhm_ours"],
      comp_star_fwhm=m.get("comp_star_fwhm"), class_star_ours=m["class_star_ours"],
      sep_pred_as=m["sep_pred_as"],
      dRA_ours_pub=m["dRA_ours_pub"], dDec_ours_pub=m["dDec_ours_pub"],
      dRA_ours_hor=m["dRA_ours_hor"], dDec_ours_hor=m["dDec_ours_hor"],
      dRA_pub_hor=round(dRA_pub_hor,4), dDec_pub_hor=round(dDec_pub_hor,4),
      ours_sunward_as=round(sun_o,4), ours_perp_as=round(perp_o,4),
      pub_sunward_as=round(sun_p,4), pub_perp_as=round(perp_p,4),
      ra3sig=m["ra3sig"], dec3sig=m["dec3sig"])
    rows.append(row)

cat=[r for r in rows if r.get("exposure")]
fieldnames=list(cat[0].keys())
with open("benchmark_table.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fieldnames); w.writeheader()
    for r in cat: w.writerow(r)
print(f"wrote benchmark_table.csv ({len(cat)} epochs)")

def stats(vals):
    a=np.array(vals,float); return a.mean(), np.sqrt((a**2).mean()), np.abs(a).max(), a.std(ddof=1)

print("\n================ THREE-WAY COMPARISON (arcsec) ================")
for label,ra_k,dec_k in [("OURS - PUBLISHED (same frame)","dRA_ours_pub","dDec_ours_pub"),
                         ("OURS - JPL Horizons (O-C)","dRA_ours_hor","dDec_ours_hor"),
                         ("PUBLISHED - JPL Horizons (O-C)","dRA_pub_hor","dDec_pub_hor")]:
    mra,rra,xra,sra=stats([r[ra_k] for r in cat])
    mde,rde,xde,sde=stats([r[dec_k] for r in cat])
    tot=np.sqrt(np.array([r[ra_k] for r in cat])**2+np.array([r[dec_k] for r in cat])**2)
    print(f"\n{label}  (N={len(cat)})")
    print(f"  dRA*cos : mean={mra:+.3f}  rms={rra:.3f}  max|{xra:.3f}|")
    print(f"  dDec    : mean={mde:+.3f}  rms={rde:.3f}  max|{xde:.3f}|")
    print(f"  total sep: mean={tot.mean():.3f}  rms={np.sqrt((tot**2).mean()):.3f}  max={tot.max():.3f}")

print("\n================ PHOTOCENTER (sunward projection, arcsec) ================")
print("  (+ = displaced toward Sun; - = anti-sunward/tailward)")
print(" idx  r_AU  antiSunPA  ours_sunward ours_perp  pub_sunward")
for r in cat:
    print(f" {r['idx']:>3} {float(r['r_helio_au']):5.2f}   {r['antiSunPA_deg']:6.1f}     {r['ours_sunward_as']:+.3f}     {r['ours_perp_as']:+.3f}    {r['pub_sunward_as']:+.3f}")
so=np.array([r["ours_sunward_as"] for r in cat]); po=np.array([r["ours_perp_as"] for r in cat])
sp=np.array([r["pub_sunward_as"] for r in cat])
print(f"\n  OURS sunward: mean={so.mean():+.3f} +/- {so.std(ddof=1)/np.sqrt(len(so)):.3f} (SE)  rms={np.sqrt((so**2).mean()):.3f}")
print(f"  OURS perp   : mean={po.mean():+.3f} +/- {po.std(ddof=1)/np.sqrt(len(po)):.3f} (SE)  rms={np.sqrt((po**2).mean()):.3f}")
print(f"  PUB  sunward: mean={sp.mean():+.3f} +/- {sp.std(ddof=1)/np.sqrt(len(sp)):.3f} (SE)")
# trend with heliocentric distance
r_au=np.array([float(r["r_helio_au"]) for r in cat])
A=np.vstack([r_au,np.ones_like(r_au)]).T
slope,icpt=np.linalg.lstsq(A,so,rcond=None)[0]
print(f"  OURS sunward vs r_helio: slope={slope:+.3f} arcsec/AU (sunward bias grows as r decreases if slope<0)")
EOF=None
