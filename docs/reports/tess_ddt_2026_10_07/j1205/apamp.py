import warnings,sys; warnings.filterwarnings('ignore')
from pixmap import pixlcs, fit
import numpy as np
from astropy.timeseries import LombScargle
for s,f0 in [(64,203.4295),(99,203.398),(100,203.403),(101,206.7635),(101,203.4085)]:
    t,F,im,x,y,w,ny,nx=pixlcs(s)
    yy,xx=np.mgrid[:ny,:nx]; r=np.hypot(xx-x,yy-y).ravel()
    for rad in [1.0,1.5,2.0]:
        sel=r<=rad; L=F[:,sel].sum(1); z,sig=fit(t,L[:,None],f0)
        # target flux in aperture: PSF frac est from gaussian sigma 0.85
        print(f'S{s} f={f0} rad={rad} npix={sel.sum()} amp={abs(z[0]):.2f}+-{sig[0]:.2f} e/s  ap median={np.median(im.ravel()[sel]*1):.0f}/pix rms={np.std(L):.1f} e/s')
