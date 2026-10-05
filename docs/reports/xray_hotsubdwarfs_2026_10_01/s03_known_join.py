import pyvo, time
tap=pyvo.dal.TAPService('https://tapvizier.cds.unistra.fr/TAPVizieR/tap')
q='''SELECT h.Name, h.GaiaEDR3, h.SpClass, h.RA_ICRS, h.DE_ICRS, h.GGAIA, h.Plx, h.e_Plx, h.Teff, h.logg, h.logY, h."E(B-V)", h.J2MASS, h.H2MASS, h.K2MASS, h.W1, h.W2, h.VAPASS,
 e.IAUName, e.posErr, e.Ext, e.DetLike0, e.MLRate1, e.s_MLRate1, e.MLFlux1, e.s_MLFlux1, e.FlagOpt, e.SepGDR3ERO, e.pany, e.pi, e.matchflag, e.UId5XMM, e.UId2RXS, e.UIdDR1
 FROM "J/A+A/662/A40/knownhsd" AS h JOIN "J/A+A/712/A171/dr2mg" AS e ON h.GaiaEDR3 = e.GaiaDR3'''
r=tap.run_sync(q, maxrec=100000).to_table(); print(len(r))
r.meta['description']='Culpan+2022 knownhsd x eRASS:3 DR2 dr2mg joined on Gaia source_id'
r.write('s03_knownhsd_x_dr2mg.ecsv',overwrite=True)
g=r[r['pany']>0.5]; print('pany>0.5',len(g))
g.sort('MLFlux1'); g.reverse()
g['Name','SpClass','GGAIA','Plx','Teff','pany','pi','SepGDR3ERO','DetLike0','MLFlux1','FlagOpt'].pprint(max_lines=100,max_width=200)
