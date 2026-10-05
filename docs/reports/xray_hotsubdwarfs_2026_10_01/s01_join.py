# Culpan+2022 hot-subdwarf candidates (J/A+A/662/A40/hotsd) x eRASS:3 DR2 main Gaia-NWAY counterparts (J/A+A/712/A171/dr2mg), by Gaia source_id.
import pyvo, time
from astropy.table import Table
tap=pyvo.dal.TAPService('https://tapvizier.cds.unistra.fr/TAPVizieR/tap')
q='''SELECT h.GaiaEDR3, h.RA_ICRS, h.DE_ICRS, h.GLON, h.GLAT, h.Plx, h.e_Plx, h."Gmag", h."GMAG", h."BP-RP", h."E(BP/RP)c", h.RUWE, h.pm, h.e_EFlux,
 e.IAUName, e.RA_ICRS AS RAx, e.DE_ICRS AS DEx, e.posErr, e.Ext, e.ExtLike, e.DetLike0, e.MLRate1, e.s_MLRate1, e.MLFlux1, e.s_MLFlux1, e.MLExp1, e.FlagOpt,
 e.FSpSNR, e.FSpBPS, e.FSpSCL, e.FSpLGA, e.FSpGCCons, e.UId5XMM, e.UIdCSC, e.UId2RXS, e.UIdDR1, e.UIdHard,
 e.SepGDR3ERO, e.pany, e.pi, e.matchflag, e.psingle, e.Pstar, e.PQSO, e.PGal, e.GDR3Xpr
 FROM "J/A+A/662/A40/hotsd" AS h JOIN "J/A+A/712/A171/dr2mg" AS e ON h.GaiaEDR3 = e.GaiaDR3'''
t0=time.time(); r=tap.run_sync(q, maxrec=100000).to_table(); print(len(r), time.time()-t0)
r.meta['description']='Culpan+2022 hotsd x eRASS:3 DR2 dr2mg (Gaia NWAY counterparts), joined on Gaia source_id; all matchflags; query run '+time.strftime('%Y-%m-%dT%H:%MZ',time.gmtime())
r.write('s01_culpan_x_dr2mg.ecsv',overwrite=True)
import numpy as np
print('matchflag', np.unique(r['matchflag'],return_counts=True))
print('pany>0.5', (r['pany']>0.5).sum(), 'pany>0.5 & mf1', ((r['pany']>0.5)&(r['matchflag']==1)).sum())
print('HD49798', r[r['GaiaEDR3']==5562023884304074240]['IAUName','pany','pi','matchflag','MLFlux1'])
