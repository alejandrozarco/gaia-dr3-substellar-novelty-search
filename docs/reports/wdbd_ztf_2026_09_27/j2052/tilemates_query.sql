-- Astro Data Lab TAP (desi_dr1): all spectra on J2052's tile and petal (tile 20836, petal_loc 8, night 20210523) -> tilemates.csv
SELECT f.targetid, f.fiber, z.spectype, z.subtype, z.z, z.coadd_numexp FROM desi_dr1.fiberassign AS f JOIN desi_dr1.ztile AS z
ON z.targetid=f.targetid AND z.tileid=f.tileid WHERE f.tileid=20836 AND f.petal_loc=8
