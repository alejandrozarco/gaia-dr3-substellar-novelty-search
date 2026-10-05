"""Forced ePSF photometry on SPHEREx QR2 L2 cutouts (npz sections fetched from S3).

Model per frame (pixel values converted to uJy/pixel):
    D_j = sum_k F_k * P(x_j - x_k, y_j - y_k) + b0 + b1*dx + b2*dy
with P the QR3 ePSF (recommended for QR2 too) of the detector zone nearest the target,
evaluated on native pixels and normalised to unit sum.  ZODI layer subtracted first.
Pixels with photometry-mask flags are excluded (Expl. Suppl. sec 3.3 list + OVERFLOW).
Fluxes are then multiplied by the QR3 l3_flux_corrections factor at the target pixel
(multiplicative correction for pre-QR3 data, puts QR2 on the DR1/QR3 gain scale).
Wavelength = CWAVE (QR2 spectral_wcs v4, the version used for QR2) at the target pixel.
"""
import numpy as np, glob, os, warnings, logging
warnings.filterwarnings('ignore')
from astropy.io import fits
from astropy.wcs import WCS
from astropy.table import Table
from scipy.interpolate import RectBivariateSpline
logging.getLogger('astropy').setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
CAL = os.path.join(HERE, 'cal')
ARCSEC2_SR = (np.pi / 180 / 3600) ** 2
# photometry mask bits (Expl. Suppl. 3.3; QR2 headers only define a subset) + OVERFLOW
MASKBITS = [1, 2, 6, 9, 10, 11, 15, 17]
MASK = sum(1 << b for b in MASKBITS)
SOURCEBIT = 1 << 21

_cal = {}
def cal(det):
    if det in _cal: return _cal[det]
    g = lambda pat: fits.getdata(glob.glob(os.path.join(CAL, pat))[0], 1)
    cw = fits.open(glob.glob(os.path.join(CAL, f'spectral_wcs_D{det}_*wcs-v4*'))[0])
    epf = 'epsf_D3_spx_cal-epsf-v2-2026-191.fits' if det == 3 else f'epsf_D{det}_spx_cal-epsf-v1-2026-191.fits'
    et = Table(fits.getdata(os.path.join(CAL, epf), 1))
    c = dict(cwave=cw['CWAVE'].data, cband=cw['CBAND'].data,
             sapm=g(f'solid_angle_pixel_map_D{det}_*'), flxc=g(f'l3_flux_corrections_D{det}_*'), epsf=et)
    _cal[det] = c
    return c

def load(fn):
    d = np.load(fn)
    hdr = fits.Header.fromstring(str(d['hdr']))
    return dict(im=d['im'].astype(float), fl=d['fl'], va=d['va'].astype(float), zo=d['zo'].astype(float),
                x0=int(d['x0']), y0=int(d['y0']), hdr=hdr, fn=fn)

class EPSF:
    def __init__(self, arr, ovs=5):
        n = arr.shape[0]; c = (n - 1) / 2
        u = (np.arange(n) - c) / ovs
        self.half = c / ovs
        self.sp = RectBivariateSpline(u, u, arr, kx=3, ky=3)  # arr[y, x]
    def stamp(self, dx, dy):
        """dx,dy: arrays of (pixel centre - source) offsets, native pixels. Returns unnormalised values."""
        out = np.zeros(np.shape(dx))
        ok = (np.abs(dx) <= self.half) & (np.abs(dy) <= self.half)
        if ok.any():
            out[ok] = self.sp.ev(dy[ok], dx[ok])
        return np.clip(out, 0, None)
    def norm_model(self, X, Y, xs, ys):
        # normalise with a full stamp around the source so truncation by the fit region doesn't bias
        gx, gy = np.meshgrid(np.arange(np.floor(xs) - 4, np.floor(xs) + 6), np.arange(np.floor(ys) - 4, np.floor(ys) + 6))
        s = self.stamp(gx - xs, gy - ys).sum()
        return self.stamp(X - xs, Y - ys) / s

def zone_psf(c, xp, yp):
    t = c['epsf']
    i = np.argmin((t['XCENTER'] - xp) ** 2 + (t['YCENTER'] - yp) ** 2)
    return EPSF(np.array(t['EPSF'][i]).reshape(33, 33)), int(i), float(t['NEFF_MEAN'][i])

def prepare(fr, ra, dec, itarget=0, rfit=6.0):
    hdr = fr['hdr']; det = int(hdr['DETECTOR']); c = cal(det)
    w = WCS(hdr)
    xs, ys = w.all_world2pix(np.asarray(ra), np.asarray(dec), 0)
    xt, yt = xs[itarget], ys[itarget]
    ixt, iyt = int(round(xt)), int(round(yt))
    if not (3 <= ixt < 2037 and 3 <= iyt < 2037): return None
    ny, nx = fr['im'].shape
    Y, X = np.mgrid[0:ny, 0:nx]; X = X + fr['x0']; Y = Y + fr['y0']
    om = c['sapm'][Y, X] * ARCSEC2_SR * 1e12        # uJy per (MJy/sr) per pixel
    data = (fr['im'] - fr['zo']) * om
    var = fr['va'] * om ** 2
    r = np.hypot(X - xt, Y - yt)
    good = (r <= rfit) & np.isfinite(data) & np.isfinite(var) & (var > 0) & ((fr['fl'] & MASK) == 0)
    psf, zone, neff = zone_psf(c, xt, yt)
    return dict(fr=fr, det=det, c=c, xs=xs, ys=ys, xt=xt, yt=yt, ixt=ixt, iyt=iyt, X=X, Y=Y, data=data, var=var,
                r=r, good=good, psf=psf, zone=zone, neff=neff, itarget=itarget, rfit=rfit, n=len(xs))

def fit(P, shift=(0.0, 0.0), free=None, fixed=None, eps=0.0, bgorder=1, nonneg=True, full=True):
    """free: index array of sources fitted freely; fixed: dict {index: flux_uJy (QR2 scale)} subtracted.
    eps: fractional model error added in quadrature to variance (one iteration)."""
    X, Y, good = P['X'], P['Y'], P['good']
    xs = P['xs'] + shift[0]; ys = P['ys'] + shift[1]
    xt, yt, rfit, psf = P['xt'] + shift[0], P['yt'] + shift[1], P['rfit'], P['psf']
    if free is None: free = np.arange(P['n'])
    data = P['data'].copy()
    if fixed:
        for k, f in fixed.items():
            data -= f * psf.norm_model(X, Y, xs[k], ys[k])
    dist = np.hypot(xs - xt, ys - yt)
    cols, names = [], []
    for k in free:
        if dist[k] > rfit + psf.half: continue
        m = psf.norm_model(X, Y, xs[k], ys[k])
        if m[good].sum() < 0.02 and k != P['itarget']: continue
        cols.append(m[good]); names.append(int(k))
    dxg = (X - xt)[good]; dyg = (Y - yt)[good]
    bgc = [np.ones(good.sum())] + ([dxg / rfit, dyg / rfit] if bgorder >= 1 else [])
    A = np.array(cols + bgc).T
    nsrc = len(cols); it = names.index(P['itarget'])
    d = data[good]; var = P['var'][good].copy()
    from scipy.optimize import lsq_linear
    for itn in range(2 if eps > 0 else 1):
        wts = 1 / np.sqrt(var); Aw = A * wts[:, None]; bw = d * wts
        if nonneg:
            lb = np.zeros(A.shape[1]); ub = np.full(A.shape[1], np.inf)
            lb[it] = -np.inf; lb[nsrc:] = -np.inf
            p = lsq_linear(Aw, bw, bounds=(lb, ub), method='bvls').x
        else:
            p = np.linalg.lstsq(Aw, bw, rcond=None)[0]
        if eps > 0 and itn == 0:
            msrc = A[:, :nsrc] @ p[:nsrc]
            var = P['var'][good] + (eps * np.clip(msrc, 0, None)) ** 2
    resid = bw - Aw @ p
    dof = max(good.sum() - A.shape[1], 1)
    chi2r = float((resid ** 2).sum() / dof)
    if not full: return chi2r
    act = np.ones(A.shape[1], bool)
    if nonneg: act[:nsrc] = (p[:nsrc] > 0) | (np.arange(nsrc) == it)
    Aa = Aw[:, act]
    cov = np.linalg.pinv(Aa.T @ Aa)
    err = np.full(A.shape[1], np.nan); err[act] = np.sqrt(np.diag(cov))
    ia = np.where(act)[0]; dd = np.sqrt(np.diag(cov)); cc = cov / np.outer(dd, dd)
    corr = {}
    for a, i in enumerate(ia):
        if i < nsrc: corr[names[i]] = float(cc[list(ia).index(it), a])
    fc = float(P['c']['flxc'][P['iyt'], P['ixt']])
    flux = np.full(P['n'], np.nan); eflux = np.full(P['n'], np.nan)
    for q, k in enumerate(names): flux[k] = p[q] * fc; eflux[k] = err[q] * fc
    model = np.zeros(P['data'].shape); model[good] = A @ p
    r = np.hypot(X - xt, Y - yt)
    sel = good & (r <= 2.5)
    fq = float(np.mean(np.abs(data[sel] - model[sel]) / np.sqrt(P['var'][sel]))) if sel.any() else np.nan
    fl = P['fr']['fl']; near = r <= 2.5
    hdr = P['fr']['hdr']; c = P['c']
    return dict(det=P['det'], mjd=float(hdr['MJD-AVG']), wave=float(c['cwave'][P['iyt'], P['ixt']]),
                band=float(c['cband'][P['iyt'], P['ixt']]), xt=float(xt), yt=float(yt), zone=P['zone'], neff=P['neff'],
                fcorr=fc, flux=flux, eflux=eflux, chi2r=chi2r, npix=int(good.sum()), nsrc=nsrc, names=names, corr=corr,
                fq=fq, flags_near=int(np.bitwise_or.reduce(fl[near].ravel())), nmask_near=int((near & ((fl & MASK) != 0)).sum()),
                psf_fwhm=float(hdr.get('PSF_FWHM', np.nan)), zodi=float(np.nanmedian(P['fr']['zo'])),
                bg=p[nsrc:] * fc, resid=(data - model) * good, data=data)

def solve_shift(fr, ra, dec, ianchor, free_local, rfit=3.0, eps=0.0):
    """Fit a global (dx,dy) WCS correction by minimising chi2 of a fit centred on an anchor star."""
    from scipy.optimize import minimize
    P = prepare(fr, ra, dec, itarget=ianchor, rfit=rfit)
    if P is None: return (0.0, 0.0, np.nan)
    f = lambda s: fit(P, shift=tuple(s), free=free_local, eps=eps, full=False)
    m = minimize(f, [0, 0], method='Nelder-Mead', options=dict(xatol=0.01, fatol=0.01, maxiter=120, initial_simplex=[[0, 0], [0.25, 0], [0, 0.25]]))
    return (float(m.x[0]), float(m.x[1]), float(m.fun))
