import os
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
p=os.path.expanduser("~/claude_projects/gaia-recovered-2026-05-27/docs/reports/rubin_pilot_2026_07_14/forensics/170587115976392822/photometry_master_mjd.csv")
d=pd.read_csv(p)
bad=d.note.astype(str).str.contains("ASTEROID",case=False,na=False)
print(f"excluded as suspect single-epoch measurements: {bad.sum()} rows")
d=d[~bad & (d.band!="W1")]

# REVISION 7: flag the withdrawn maximum rather than silently drop it
WD_MJD=59218.0779
wd=d[(d.mjd-WD_MJD).abs()<0.01]
d_ok=d[(d.mjd-WD_MJD).abs()>=0.01]

bcol={"g":"#2b7a3d","zg":"#2b7a3d","r":"#c0392b","zr":"#c0392b","i":"#6c3483","zi":"#6c3483","z":"#b7950b","i(LSST)":"#6c3483"}
fig,ax=plt.subplots(figsize=(13,6.6),facecolor="white")
dec=d_ok[d_ok.source=="DECam/NSC-DR2"]
ax.errorbar(dec.mjd,dec.mag,yerr=dec.magerr,fmt="s",ms=9,mfc="none",mew=1.6,color="#1a5276",lw=0,elinewidth=1,
            label="DECam / NSC DR2 (deep, r/g/z)",zorder=5)
for src,mark,size in [("ZTF-DR","o",4.5),("ZTF-alert/ALeRCE",".",3)]:
    for b,g in d_ok[d_ok.source==src].groupby("band"):
        ax.errorbar(g.mjd,g.mag,yerr=g.magerr.fillna(0),fmt=mark,ms=size,color=bcol.get(b,"k"),
                    alpha=.7,lw=0,elinewidth=.4,label=f"{'ZTF DR' if src=='ZTF-DR' else 'ZTF alerts'} {b}")
ru=d_ok[d_ok.source=="Rubin/Fink-flag"]
ax.plot(ru.mjd,ru.mag,"*",ms=17,color="k",label="Rubin/LSST (Fink flag 2026-07)",zorder=6)

# withdrawn point, shown and labelled
if len(wd):
    ax.plot(wd.mjd,wd.mag,"x",ms=13,mew=2.4,color="#7f8c8d",zorder=7,
            label="withdrawn (shallowest frame, sharp +0.68)")

# pre-2018 faint state: LS DR10 coadd
ax.axvspan(56400,58000,color="#d6eaf8",alpha=.5,zorder=0)
ax.axhline(23.12,xmin=0,xmax=0.30,color="#1a5276",ls="--",lw=1.2,zorder=3)
ax.text(57200,23.55,"pre-2018 faint state\nLS DR10 coadd r = 23.12 ± 0.08",ha="center",fontsize=9.5,color="#1a5276")
ax.annotate("turn-on between\n2017-08-22 and 2018-06-16",xy=(58285,21.3),xytext=(58120,19.9),fontsize=9,
            arrowprops=dict(arrowstyle="->",lw=.9))
ax.annotate("adopted maximum r = 18.34\n2024-09-21 (limitmag 21.04)",xy=(60577,18.34),xytext=(59100,17.45),fontsize=9,
            arrowprops=dict(arrowstyle="->",lw=.9))
ax.annotate("MJD 58372 DECam pair\nr = 23.13 / 22.03, 13 min apart\n— UNRESOLVED",xy=(58372,22.6),xytext=(58650,22.9),
            fontsize=8.2,color="#873600",arrowprops=dict(arrowstyle="->",lw=.8,color="#873600"))

# yearly zr medians: the state changes
yr={2019:19.72,2020:18.89,2021:18.63,2022:20.61,2023:19.31,2024:19.00,2025:21.33}
mj={2019:58700,2020:59050,2021:59400,2022:59780,2023:60130,2024:60500,2025:60850}
ax.plot([mj[k] for k in sorted(yr)],[yr[k] for k in sorted(yr)],"-",color="#e67e22",lw=2.0,alpha=.85,
        zorder=8,label="annual zr median (state changes)")

ax.set_ylim(24.2,16.6); ax.set_xlabel("MJD"); ax.set_ylabel("magnitude (AB)")
ax.set_title("ZTF19abxfaon = Rubin diaObject 170587115976392822 — 13 yr archival record; in no variability catalogue\n"
             "observed range ≈ 4.8 mag (23.12 → 18.34); repeated ~2-mag state changes since 2018, never returning to the pre-2018 level",
             fontsize=10.5)
ax.grid(alpha=.25); ax.legend(fontsize=7.6,ncol=2,loc="lower left",framealpha=.95)
sec=ax.secondary_xaxis("top"); sec.set_xticks([56600,57300,58000,58700,59400,60100,60800,61300])
sec.set_xticklabels(["2013","2015","2017","2019","2021","2023","2025","2026"],fontsize=9)
out=os.path.expanduser("~/claude_projects/gaia-recovered-2026-05-27/docs/reports/vsx_bycatch_2026_09_18/vsx_ZTF19abxfaon_lightcurve.png")
plt.tight_layout(); plt.savefig(out,dpi=140)
print("saved:",out)
