# Per-visit H-alpha emission screen of the SDSS-V DR20 white-dwarf visit spectra (2026-09-28)

Sample: the 50,886 SnowWhite-classified objects of the gas-disc screen (targets.csv: sdss_id, Gaia DR3 id, class, G, parallax, BP-RP, M_G, Teff).
Store: raw mwmVisit-0.8.1 files kept unaltered in a persistent directory outside the repository (`spectra_store/sdssv_dr20/visit/<xx>/<yy>/`), with index.csv (visits, telescopes, MJDs, S/N per object). Built by build_store.py (SAS, six parallel downloads, resumable).
Stage 1 (extract_halpha.py): per visit, 6400-6750 A on a 1e-4 dex grid, XCSAO shift undone for in-stack visits, straight-line normalisation through the 6405-6440 and 6700-6745 A medians; inverse-variance coadd. Saved per object (halpha_store).
Stage 2 (screen_halpha.py): photospheric template from the 40 nearest neighbours in BP-RP (same class group, |dBP-RP| < 0.2, coadd S/N > 8), split into a bluer and a redder half; for DA-group stars the object is fitted as 1 + a(t1-1) + b(t2-1) over pixel shifts of +-2, with upward residuals within 80 A of H-alpha excluded from the fit; other groups use the plain median. Per-pixel error = quadrature sum of the visit error and a template term (0.15 x neighbour scatter for DA, 0.05 x otherwise). Matched filters on the residual: narrow (Gaussian sigma 1.5/3/6 A, -600..+600 km/s) and broad (sigma 3/6/10/15 A, -3000..+3000 km/s), per visit and on the coadd; EW per visit at the coadd velocity and its chi2.
Controls (recovered): DAHe Gaia DR3 3656469211440196736 (sdss_id 78995796; broad channel z 18 in the coadd, 15-16 per visit), DAHe 1428562506980546688 (61248548; z 4-5 at coadd S/N 9), reflection-effect emitter WDJ064438.09-004550.51 (74709777; per-visit z up to 24, EW chi2 20).
Calibration (first 700 DA, template version with fit): null z_coadd p90 5.2, p99 14.8; 2-A injected emission recovered at z > 5 in 41 % (coadd S/N 5-10), 77 % (10-20), 94 % (20-40), 98 % (> 40). The DA null tail contains real emitters (red DA-labelled composites with M-dwarf chromospheric emission).
Outputs: screen_full.csv, screen_inject2.csv, plots/ (vetting figures) in the store directory; vetted results are journaled per object.

## T2 tier vetting (2026-09-28 evening)
- 95 T2 objects (persistent but weak); 40 remain after the locus, nebular and field-night cuts (candidates_clean.csv).
- Velocity consistency: real stellar emission sits near the white dwarf's rest velocity at the same velocity in every visit. Keeping |v_coadd| <= 250 km/s and per-visit velocity spread <= 150 km/s leaves 13 (results/t2_physical.csv). The other 27 have velocities up to +-600 km/s that jump between visits.
- Per-visit profiles (results/t2_physical_halpha.png): in 11 of 13 the signal is a one-to-two-pixel spike in a single visit (cosmic-ray pattern) with nothing in the other visit. sdss_id 67709640 and 67709813 show the feature in the same visit (MJD 60463, same plate), which points to a night-level artefact. One marginal case: sdss_id 88344739 (Gaia DR3 4328334690765259264, G 18.1) has a weak narrow core in both visits (MJD 60106/60107, z 6.9/9.6, v -25/-150 km/s). It is too weak to call and is not journaled.
- Result: the T2 tier yields no emission-line candidates.

## T3-single tier vetting (2026-09-28 evening)
- 63 objects with one visit, so no persistence test. A cosmic ray is one to two pixels wide; requiring a resolved line (sigma >= 3 A over >= 4 px), |v| <= 250 km/s, no ringing and no nebular lines leaves 11 (results/t3_wide.csv).
- Field-night test (results/t3_wide_fieldnight.csv): eight of the 11 sit on fields where 16-43% of the other stars on the same night also show H-alpha emission (sky or diffuse nebular light).
- The three on clean fields (results/t3_clean_three.png): sdss_id 89550297 shows no emission core in the spectrum (template artefact). sdss_id 62082609 (G 15.4) has a narrow core at line centre, but only two comparison stars share its field-night, so sky cannot be excluded. sdss_id 79252920 is V379 Vir, a known polar with a brown-dwarf donor: a recovery.
- Result: no new candidates from the T3-single tier; one known magnetic CV recovered.
