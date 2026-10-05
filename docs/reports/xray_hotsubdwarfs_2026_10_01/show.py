from astropy.table import Table
import numpy as np, sys
M=Table.read('s07_props.ecsv')
for c in M.colnames:
    if hasattr(M[c],'filled'):
        try: M[c]=M[c].filled(np.nan)
        except Exception: M[c]=M[c].filled('')
def f(x,fm):
    try: return (fm%x) if np.isfinite(x) else '  nan'
    except Exception: return ' -- '
def show(S,title):
    print('##',title,len(S))
    print(f"{'GaiaDR3':>20s} {'name':22s} {'ot':4s} {'G':>5s} {'BR':>5s} {'d':>5s} {'ruwe':>5s} {'Fx':>8s} {'DL':>6s} {'sep':>4s} {'logLx':>5s} {'LxLb':>6s} {'FxFo':>6s} {'G-J':>5s} {'J-H':>5s} {'G-W1':>5s} {'W1W2':>5s} vflag/vari ; vsx")
    for r in S:
        print(f"{r['GaiaEDR3']:20d} {str(r['simbad'])[:22]:22s} {str(r['otype']):4s} {r['phot_g_mean_mag']:5.2f} {r['bp_rp']:5.2f} {f(r['r_med_geo'],'%5.0f')} {r['ruwe']:5.2f} {r['Fx']:8.1e} {r['DetLike0']:6.0f} {r['sepX']:4.1f} {f(np.log10(r['Lx']),'%5.1f')} {f(r['logLxLbol'],'%6.2f')} {r['logFxFopt']:6.2f} {f(r['G_J'],'%5.2f')} {f(r['J_H'],'%5.2f')} {f(r['G_W1'],'%5.2f')} {f(r['W1_W2'],'%5.2f')} {str(r['phot_variable_flag'])[:4]}/{r['vari']} ; {str(r['vsx'])[:40]}")
if __name__=='__main__':
    show(M[~M['known_cv'].astype(bool)],'gate survivors')
    K=M[M['known_cv'].astype(bool)]
    print('known CV ref: median logLx',np.nanmedian(np.log10(K['Lx'])),'median G-W1',np.nanmedian(K['G_W1']),'median logFxFopt',np.nanmedian(K['logFxFopt']), 'median LxLbol', np.nanmedian(K['logLxLbol']))
