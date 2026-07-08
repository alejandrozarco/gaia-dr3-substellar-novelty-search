"""Independent pixel-centroid validation of the catalog positions (+ photocenter check).
Fetch NOIRLab /svc/cutout of the exact DES ooi frame at the Horizons-predicted position;
Gaia-frame WCS sanity via bright NSC catalog stars on the same cutout; centroid the comet
(photutils) and convert pixel->RA/Dec. Compare to NSC catalog, published DES, Horizons.
Run with the dlvenv python (photutils). Reads raw/measured.json + raw/meas_idxNN.csv.
"""
import warnings; warnings.filterwarnings("ignore")
import io, json, sys, numpy as np, requests
from astropy.io import fits
from astropy.wcs import WCS
from astropy.table import Table
from scipy.optimize import curve_fit

CUTOUT="https://datalab.noirlab.edu/svc/cutout"

def _gauss2d(xy,amp,x0,y0,sx,sy,off):
    x,y=xy; return (amp*np.exp(-((x-x0)**2/(2*sx**2)+(y-y0)**2/(2*sy**2)))+off).ravel()

def gauss_centroid(data, x, y, box=6):
    """2D Gaussian centroid in a box around (x,y). Returns (xc,yc) or None."""
    x,y=int(round(x)),int(round(y))
    if not (box<=x<data.shape[1]-box and box<=y<data.shape[0]-box): return None
    sub=data[y-box:y+box+1, x-box:x+box+1].astype(float)
    yy,xx=np.mgrid[0:sub.shape[0],0:sub.shape[1]]
    off0=np.nanmedian(sub); amp0=np.nanmax(sub)-off0
    try:
        p,_=curve_fit(_gauss2d,(xx,yy),sub.ravel(),
                      p0=[amp0,box,box,2.0,2.0,off0],maxfev=4000)
    except Exception:
        return None
    xc,yc=p[1],p[2]
    if not (0<=xc<sub.shape[1] and 0<=yc<sub.shape[0]): return None
    return (x-box+xc, y-box+yc)

def fetch_inframe_ccd(siaRef, ra, dec):
    """svc/cutout returns the full multi-extension instcal; select the CCD (HDU) whose
    WCS maps (ra,dec) inside the array, with margin for a centroid box."""
    r=requests.get(CUTOUT, params={"siaRef":siaRef,"POS":f"{ra},{dec}","SIZE":"0.02"}, timeout=180)
    r.raise_for_status()
    hdul=fits.open(io.BytesIO(r.content))
    for h in hdul:
        if h.data is None or h.data.ndim!=2: continue
        w=WCS(h.header)
        x,y=w.all_world2pix(ra,dec,0)
        ny,nx=h.data.shape
        if 20<x<nx-20 and 20<y<ny-20:
            return h.data.astype(float), w, h.header.get("EXTNAME")
    raise RuntimeError("predicted position not in-frame on any CCD")

def centroid_at(data, wcs, ra, dec, box=6):
    x,y=wcs.all_world2pix(ra,dec,0)
    c=gauss_centroid(data,float(x),float(y),box=box)
    if c is None: return None
    xc,yc=c
    r2,d2=wcs.all_pix2world(xc,yc,0)
    return float(r2),float(d2),float(xc),float(yc)

def main(indices):
    meas={m["idx"]:m for m in json.load(open("raw/measured.json")) if m["status"]=="CATALOG"}
    out=[]
    for idx in indices:
        m=meas[idx]; siaRef=m["exposure"]+".fits.fz"
        ra_h,dec_h=m["ra_hor"],m["dec_hor"]
        print(f"\n=== idx {idx} {m['obstime']} exp={siaRef} ===",flush=True)
        try:
            data,wcs,extn=fetch_inframe_ccd(siaRef,ra_h,dec_h)
            print(f"  in-frame CCD: {extn}")
        except Exception as e:
            print("  cutout FAIL:",str(e)[:150]); continue
        cd=np.cos(np.radians(dec_h))
        # WCS check via bright NSC stars on this exposure
        try:
            tab=Table.read(f"raw/meas_idx{idx:02d}.csv",format="csv")
            same=tab[[str(e)==m["exposure"] for e in tab["exposure"]]]
            stars=same[(same["class_star"]>0.85)&(same["mag_auto"]<21.0)]
            res=[]
            for s in stars[:8]:
                c=centroid_at(data,wcs,float(s["ra"]),float(s["dec"]),box=9)
                if c: res.append(((c[0]-float(s["ra"]))*3600*cd,(c[1]-float(s["dec"]))*3600))
            if res:
                res=np.array(res); wr=np.hypot(res[:,0],res[:,1])
                print(f"  WCS check ({len(res)} NSC stars): pix-vs-catalog rms={np.sqrt((wr**2).mean()):.3f}\" "
                      f"(dRA {res[:,0].mean():+.3f}, dDec {res[:,1].mean():+.3f})")
        except Exception as e:
            print("  WCS check skipped:",str(e)[:80])
        # centroid comet at Horizons prediction
        c=centroid_at(data,wcs,ra_h,dec_h,box=11)
        if not c: print("  comet centroid FAIL (off-frame)"); continue
        ra_p,dec_p,xc,yc=c
        d_nsc=((ra_p-m["ra_ours"])*3600*cd,(dec_p-m["dec_ours"])*3600)
        d_pub=((ra_p-m["ra_pub"])*3600*cd,(dec_p-m["dec_pub"])*3600)
        d_hor=((ra_p-ra_h)*3600*cd,(dec_p-dec_h)*3600)
        print(f"  pixel RA/Dec = {ra_p:.6f}/{dec_p:.6f}")
        print(f"  pixel - NSC : dRA*cos={d_nsc[0]:+.3f} dDec={d_nsc[1]:+.3f}")
        print(f"  pixel - PUB : dRA*cos={d_pub[0]:+.3f} dDec={d_pub[1]:+.3f}")
        print(f"  pixel - HOR : dRA*cos={d_hor[0]:+.3f} dDec={d_hor[1]:+.3f}")
        out.append(dict(idx=idx,ra_pix=ra_p,dec_pix=dec_p,
            dRA_pix_nsc=round(d_nsc[0],4),dDec_pix_nsc=round(d_nsc[1],4),
            dRA_pix_pub=round(d_pub[0],4),dDec_pix_pub=round(d_pub[1],4),
            dRA_pix_hor=round(d_hor[0],4),dDec_pix_hor=round(d_hor[1],4)))
    json.dump(out,open("raw/pixel_centroids.json","w"),indent=1)
    print(f"\nsaved raw/pixel_centroids.json ({len(out)} epochs)")

if __name__=="__main__":
    idxs=[int(x) for x in sys.argv[1:]] or [23]
    main(idxs)
