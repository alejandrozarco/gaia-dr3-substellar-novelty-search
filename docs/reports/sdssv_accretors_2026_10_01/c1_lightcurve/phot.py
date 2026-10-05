"""Forced PSF photometry on ZTF scimrefdiffimg cutouts at C1 = Gaia DR3 2101985070870393856
(RA 290.516500 Dec +42.259050) + controls. Joint 2-PSF fit with KIC 6773282 (Gaia DR3 2101985070870394368, 2.56").
Fluxes: DN in diff image -> uJy via MAGZP (AB, 23.9). Output: forced_lc_raw.csv"""
import numpy as np, pandas as pd, glob, os, warnings
from astropy.io import fits
from astropy.wcs import WCS, FITSFixedWarning
from scipy.ndimage import shift as ndshift
warnings.simplefilter('ignore', FITSFixedWarning)
W='.'
meta=pd.read_csv(f'{W}/sci_meta.tbl')
g=pd.read_csv(f'{W}/gaia_cone.csv')
def pos_at(row,jd):
    dt=(jd-2457389.0)/365.25  # Gaia DR3 epoch 2016.0
    pmra=0 if np.isnan(row.pmra) else row.pmra; pmde=0 if np.isnan(row.pmdec) else row.pmdec
    return row.ra+pmra*dt/3.6e6/np.cos(np.radians(row.dec)), row.dec+pmde*dt/3.6e6
gs=g.set_index('source_id')
C1=2101985070870393856; KIC=2101985070870394368
STARS={'C1':C1,'KIC6773282':KIC,'ctl_star_G18.30':2101985070870394880,'ctl_star_G18.69':2101985070870393600,'ctl_star_G18.68':2101985036510653696}
BRIGHT2=2101985036510651776  # G=14.68 star for mirror-geometry control
# blank-sky positions: no Gaia source within 9", inside +-45" of C1
rng=np.random.default_rng(1); blanks=[]
cosd=np.cos(np.radians(42.25905))
while len(blanks)<3:
    dx,dy=rng.uniform(-40,40,2)
    ra=290.5165+dx/3600/cosd; de=42.25905+dy/3600
    sep=np.hypot((g.ra-ra)*cosd,(g.dec-de))*3600
    if sep.min()>9 and np.hypot(dx,dy)>12: blanks.append((ra,de))
# astrometric reference stars for per-epoch shift: isolated G<17.8 within 60" (excluding KIC itself is fine; include it)
astro=[s for s in g.source_id if gs.loc[s].phot_g_mean_mag<17.8]
def psfcol(shape,psf,x,y,y0,x0,half):
    n=psf.shape[0]; c=n//2
    canvas=np.zeros((shape[0]+2*n,shape[1]+2*n))
    ix=int(np.floor(x)); iy=int(np.floor(y)); fx=x-ix; fy=y-iy
    p=ndshift(psf,(fy,fx),order=3,mode='constant')
    canvas[iy-c+n:iy-c+n+n, ix-c+n:ix-c+n+n]+=p
    return canvas[n+y0-half:n+y0+half+1, n+x0-half:n+x0+half+1].ravel()
def fit(img,var,psf,xys,cx,cy,half=7,deriv=None,order2=False):
    """Linear LSQ: sum_k a_k PSF(x_k,y_k) [+ dP/dx,dP/dy,lap(P) at deriv=(x,y)] + const, box centred on (cx,cy)."""
    x0=int(round(cx)); y0=int(round(cy))
    if x0-half<0 or y0-half<0 or x0+half+1>img.shape[1] or y0+half+1>img.shape[0]: return None
    sub=img[y0-half:y0+half+1,x0-half:x0+half+1]; v=var[y0-half:y0+half+1,x0-half:x0+half+1]
    cols=[psfcol(img.shape,psf,x,y,y0,x0,half) for (x,y) in xys]
    if deriv is not None:
        x,y=deriv; h=0.3
        px1=psfcol(img.shape,psf,x+h,y,y0,x0,half); px0=psfcol(img.shape,psf,x-h,y,y0,x0,half)
        py1=psfcol(img.shape,psf,x,y+h,y0,x0,half); py0=psfcol(img.shape,psf,x,y-h,y0,x0,half)
        pc=psfcol(img.shape,psf,x,y,y0,x0,half)
        cols += [(px1-px0)/(2*h),(py1-py0)/(2*h)]
        if not order2: cols.append((px1+px0+py1+py0-4*pc)/h**2)
        else:
            pa=psfcol(img.shape,psf,x+h,y+h,y0,x0,half); pb=psfcol(img.shape,psf,x-h,y-h,y0,x0,half)
            pcc=psfcol(img.shape,psf,x+h,y-h,y0,x0,half); pd_=psfcol(img.shape,psf,x-h,y+h,y0,x0,half)
            cols += [(px1+px0-2*pc)/h**2,(py1+py0-2*pc)/h**2,(pa+pb-pcc-pd_)/(4*h*h)]
    cols.append(np.ones(sub.size))
    A=np.array(cols).T; b=sub.ravel(); w=1/v.ravel()
    good=np.isfinite(b)&np.isfinite(w)&(w>0)
    if good.sum()<50: return None
    Aw=A[good]*np.sqrt(w[good])[:,None]; bw=b[good]*np.sqrt(w[good])
    cov=np.linalg.pinv(Aw.T@Aw); p=cov@(Aw.T@bw)
    res=bw-Aw@p; chi=(res**2).sum()/(good.sum()-len(p))
    return p, np.sqrt(np.diag(cov)), chi
def centroid(img,x,y,h=4):
    x=float(x); y=float(y); x0=int(round(x)); y0=int(round(y)); s=img[y0-h:y0+h+1,x0-h:x0+h+1]
    s=s-np.nanmedian(img); s=np.where(np.isfinite(s)&(s>0),s,0)
    yy,xx=np.mgrid[y0-h:y0+h+1,x0-h:x0+h+1]
    if s.shape!=xx.shape or y0-h<0 or x0-h<0: return np.nan,np.nan
    if s.sum()<=0: return np.nan,np.nan
    return (s*xx).sum()/s.sum(),(s*yy).sum()/s.sum()
rows=[]
for i,r in meta.iterrows():
    s=str(r.filefracday); tag=f'{s}_{r.field}_{r.filtercode}_c{r.ccdid:02d}_q{r.qid}'
    fd,fp,fsci=[f'{W}/cut/{tag}_{k}.fits' for k in ('diff','psf','sci')]
    base=dict(tag=tag,jd=r.obsjd,filter=r.filtercode,field=r.field,ccd=r.ccdid,qid=r.qid,infobits=r.infobits,seeing=r.seeing,maglimit=r.maglimit,airmass=r.airmass)
    if not (os.path.exists(fd) and os.path.exists(fp)):
        rows.append({**base,'status':'missing_file'}); continue
    try:
        hd=fits.open(fd); D=[x for x in hd if x.data is not None][0]; dimg=D.data.astype(float); hdr=D.header
        psf=fits.getdata(fp).astype(float); psf/=psf.sum()
        sci=None
        if os.path.exists(fsci):
            hs=fits.open(fsci); S=[x for x in hs if x.data is not None][0]; sci=S.data.astype(float); shdr=S.header
    except Exception as e:
        rows.append({**base,'status':'read_error'}); continue
    w=WCS(hdr); zp=hdr['MAGZP']; gain=hdr.get('GAIN',6.2)
    conv=10**(-0.4*(zp-23.9))  # DN -> uJy
    def pix(ra,de):
        x,y=w.all_world2pix(ra,de,0); return float(x),float(y)
    P={k:pix(*pos_at(gs.loc[v],r.obsjd)) for k,v in STARS.items()}
    # per-epoch astrometric shift from sci image centroids of bright stars (sci WCS == diff WCS frame? use sci's own WCS)
    dxs=[];dys=[]
    if sci is not None:
        ws=WCS(shdr)
        for sid in astro:
            xp,yp=[float(q) for q in ws.all_world2pix(*pos_at(gs.loc[sid],r.obsjd),0)]
            if 6<xp<sci.shape[1]-6 and 6<yp<sci.shape[0]-6:
                cxp,cyp=centroid(sci,xp,yp)
                if np.isfinite(cxp) and abs(cxp-xp)<2 and abs(cyp-yp)<2: dxs.append(cxp-xp); dys.append(cyp-yp)
        kx,ky=[float(q) for q in ws.all_world2pix(*pos_at(gs.loc[KIC],r.obsjd),0)]; kcx,kcy=centroid(sci,kx,ky,h=3)
    sdx=np.median(dxs) if len(dxs)>=3 else 0.0; sdy=np.median(dys) if len(dys)>=3 else 0.0
    # noise model: robust background std of diff + Poisson from sci flux
    finite=np.isfinite(dimg)
    med=np.nanmedian(dimg); mad=1.4826*np.nanmedian(np.abs(dimg-med))
    var=np.full(dimg.shape,mad**2)
    if sci is not None and sci.shape==dimg.shape:
        sb=np.nanmedian(sci); var=var+np.clip(sci-sb,0,None)/gain
    out={**base,'status':'ok','magzp':zp,'uJy_per_DN':conv,'diff_bkg_rms_DN':mad,'astro_dx':sdx,'astro_dy':sdy,'n_astro':len(dxs),
         'kic_cen_dx':(kcx-kx) if sci is not None else np.nan,'kic_cen_dy':(kcy-ky) if sci is not None else np.nan}
    Pc={k:(x+sdx,y+sdy) for k,(x,y) in P.items()}
    c1=Pc['C1']; kic=Pc['KIC6773282']
    mir=(2*kic[0]-c1[0],2*kic[1]-c1[1])  # point mirrored through KIC (same separation, opposite side)
    b2=pix(*pos_at(gs.loc[BRIGHT2],r.obsjd)); b2=(b2[0]+sdx,b2[1]+sdy)
    b2c=(b2[0]+(c1[0]-kic[0]),b2[1]+(c1[1]-kic[1]))
    def put(name,res,k=0):
        if res is None: out[name+'_f']=np.nan; out[name+'_e']=np.nan; out[name+'_chi']=np.nan; return
        p,e,chi=res; out[name+'_f']=p[k]*conv; out[name+'_e']=e[k]*conv; out[name+'_chi']=chi
    j=fit(dimg,var,psf,[c1,kic],*c1); put('C1nodip',j,0); put('KICnodip',j,1)
    jd=fit(dimg,var,psf,[c1,kic],*c1,deriv=kic); put('C1',jd,0); put('KIC',jd,1)
    if jd is not None: out['dip_x']=jd[0][2]*conv; out['dip_y']=jd[0][3]*conv; out['lap']=jd[0][4]*conv
    put('C1o2',fit(dimg,var,psf,[c1,kic],*c1,deriv=kic,order2=True))
    j0=fit(dimg,var,psf,[kic],*c1,deriv=kic); out['chi_noC1']=np.nan if j0 is None else j0[2]
    put('C1single',fit(dimg,var,psf,[c1],*c1))
    off=(c1[0]-kic[0],c1[1]-kic[1])
    ctlpos={'mirrorKIC':(kic[0]-off[0],kic[1]-off[1]),'rot90KIC':(kic[0]-off[1],kic[1]+off[0]),'rot270KIC':(kic[0]+off[1],kic[1]-off[0])}
    for nm,pp in ctlpos.items():
        put(nm,fit(dimg,var,psf,[pp,kic],*pp,deriv=kic)); put(nm+'o2',fit(dimg,var,psf,[pp,kic],*pp,deriv=kic,order2=True)); put(nm+'nodip',fit(dimg,var,psf,[pp,kic],*pp))
    # ring controls at the C1 separation, azimuth measured from the C1 direction; C1 and KIC both fitted
    for az in [90,120,150,180,210,240,270]:
        ca,sa=np.cos(np.radians(az)),np.sin(np.radians(az))
        pp=(kic[0]+ca*off[0]-sa*off[1],kic[1]+sa*off[0]+ca*off[1])
        put(f'ring{az}',fit(dimg,var,psf,[pp,c1,kic],*pp,deriv=kic,order2=True))
    put('mirrorB2',fit(dimg,var,psf,[b2c,b2],*b2c,deriv=b2))
    put('B2',fit(dimg,var,psf,[b2],*b2))
    for k in ['ctl_star_G18.30','ctl_star_G18.69','ctl_star_G18.68']: put(k,fit(dimg,var,psf,[Pc[k]],*Pc[k]))
    for n,(ra,de) in enumerate(blanks):
        x,y=pix(ra,de); put(f'blank{n+1}',fit(dimg,var,psf,[(x+sdx,y+sdy)],x+sdx,y+sdy))
    # science-image joint fit (total flux, not difference) for reference-level anchoring
    if sci is not None and sci.shape==dimg.shape:
        sv=np.full(sci.shape,(1.4826*np.nanmedian(np.abs(sci-np.nanmedian(sci))))**2)+np.clip(sci-np.nanmedian(sci),0,None)/gain
        js=fit(sci,sv,psf,[c1,kic],*c1)
        if js is not None:
            p,e,chi=js; out['sci_C1_f']=p[0]*conv; out['sci_C1_e']=e[0]*conv; out['sci_KIC_f']=p[1]*conv; out['sci_chi']=chi
    rows.append(out)
    if i%200==0: print(i,tag,out.get('C1_f'),out.get('C1_e'),flush=True)
df=pd.DataFrame(rows)
df.to_csv(f'{W}/forced_lc_raw.csv',index=False)
open(f'{W}/blank_positions.txt','w').write('\n'.join(f'{a:.6f} {b:.6f}' for a,b in blanks))
print(df.status.value_counts())
