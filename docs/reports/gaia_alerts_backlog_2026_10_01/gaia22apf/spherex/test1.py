import numpy as np, glob, sxphot as S
from astropy.table import Table
from astropy.coordinates import SkyCoord
t=Table.read('scene_sources.ecsv')
c0=SkyCoord(305.66064,39.19732,unit='deg'); r=SkyCoord(t['ra'],t['dec'],unit='deg').separation(c0).arcsec
sel=(r<1)|((t['K']<15.0)&(r<60))|((t['K']<16.0)&(r<15))
src=t[sel]; print(len(src), list(src['name'][:6]))
ib=list(src['name']).index('J202237.40+391159.3')
fs=sorted(glob.glob('cut/*.npz'))
import random; random.seed(1)
for fn in random.sample(fs,12):
    fr=S.load(fn)
    o=S.fit_frame(fr,src)
    if o is None: print('none'); continue
    # flipped psf test
    det=o['det']
    psf0=S.EPSF.__init__
    sh=S.centroid_shift(fr,src,ib)
    o2=S.fit_frame(fr,src,shift=sh[:2])
    print(det, f"{o['wave']:.3f} chi2r={o['chi2r']:.2f} -> shift {sh[0]:+.2f},{sh[1]:+.2f} chi2r={o2['chi2r']:.2f} | tgt {o['flux'][0]:.1f}+-{o['eflux'][0]:.1f} -> {o2['flux'][0]:.1f} nb {o2['flux'][2]:.1f} s16 {o2['flux'][ib]:.0f} fq={o2['fq']:.2f} npix={o2['npix']} nsrc={o2['nsrc']} fc={o2['fcorr']:.3f} fwhm={o2['psf_fwhm']:.2f} neff={o2['neff']:.2f}")
