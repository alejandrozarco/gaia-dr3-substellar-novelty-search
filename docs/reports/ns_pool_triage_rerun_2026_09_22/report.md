# Tier-1 NS pool — archival-RV second-method triage

_2026-05-28. Sources processed: **161**._

## Headline
- **44/161** Tier-1 NS have ANY archival RV second-method data (LAMOST LRS/MRS, APOGEE DR17, RAVE DR6, GALAH DR3).
- **19/161** have >=2 epochs at >=2 distinct orbital phases (eligible for an NSS-locked Keplerian fit).

## Verdict distribution
- CORROBORATED: 2
- REFUTED: 2
- INCONCLUSIVE: 40
- NO_ARCHIVAL_RV: 117

## Archive coverage (sources with >=1 epoch)
- LAMOST_LRS: 20
- LAMOST_MRS: 16
- APOGEE_visits: 8
- RAVE: 11
- GALAH_DR3: 0

## CORROBORATED (2)
| source_id | P_d | M2 | sig | ruwe | epochs | K1(km/s) | evidence |
|---|---|---|---|---|---|---|---|
| 2127900555635640832 | 303.4 | 1.52 | 41 | 2.7 | 4 | 16.5+/-0.1 | constant-RV null rejected (p=0.00e+00), K1=16.5+/-0.1 km/s (206.2sigma), spectroscopic f(M)=0.137 vs astrometric f_phot=0.329 (ratio 0.42) |
| 3378588057203660160 | 999.4 | 1.90 | 12 | 4.7 | 50 | 17.1+/-0.1 | constant-RV null rejected (p=0.00e+00), K1=17.1+/-0.1 km/s (231.1sigma), spectroscopic f(M)=0.421 vs astrometric f_phot=0.499 (ratio 0.84) |

## REFUTED (2)
| source_id | P_d | M2 | sig | ruwe | epochs | K1(km/s) | evidence |
|---|---|---|---|---|---|---|---|
| 2129927539681151872 | 541.0 | 1.35 | 29 | 3.8 | 6 | 192.3+/-43.5 | spectroscopic f(M)=230.66 >> astrometric f_phot=0.252 (ratio 916.7) with K1 at 4.4 sigma |
| 1379150557507688960 | 1351.1 | 1.27 | 22 | 20.2 | 4 | 250.0+/-12.5 | spectroscopic f(M)=2172.70 >> astrometric f_phot=0.279 (ratio 7787.1) with K1 at 20.0 sigma |

## INCONCLUSIVE with >=2 archival epochs (21) — follow-up priority
| source_id | P_d | M2 | sig | epochs_any | phaseable | distinct_phase | reason |
|---|---|---|---|---|---|---|---|
| 348572609373952768 | 775.0 | 1.20 | 116 | 3 | 3 | 2 | chi2/dof=0.009 with dof=1 is a weak statistic (few epochs); K1 detected at only 0.0 sigma (<3) |
| 4589512133070332032 | 745.3 | 1.21 | 97 | 2 | 2 | 1 | 2 phaseable epoch(s), 1 distinct phase bin(s); RV span across epochs = 0.48 km/s — too few distinct phases for a locked fit (1593152 standard) |
| 350365844119482368 | 527.7 | 1.28 | 84 | 2 | 2 | 1 | 2 phaseable epoch(s), 1 distinct phase bin(s); RV span across epochs = 0.39 km/s — too few distinct phases for a locked fit (1593152 standard) |
| 1277223188209612544 | 499.6 | 1.30 | 69 | 5 | 5 | 3 | chi2/dof=0.419 with dof=2 is a weak statistic (few epochs); K1 detected at only 3.0 sigma (<3) |
| 2052738181284248192 | 643.1 | 1.28 | 67 | 2 | 2 | 2 | chi2/dof=0.000 with dof=1 is a weak statistic (few epochs); K1 detected at only 0.0 sigma (<3); constant-RV null not strongly rejected (p=0.156) |
| 811261052394634240 | 1037.4 | 1.74 | 65 | 9 | 9 | 3 | K1 detected at only 1.8 sigma (<3) |
| 897510244874198656 | 248.8 | 1.28 | 65 | 4 | 4 | 2 | chi2/dof=0.290 with dof=1 is a weak statistic (few epochs); K1 detected at only 0.0 sigma (<3) |
| 4582499727085787904 | 243.4 | 1.25 | 59 | 4 | 4 | 2 | chi2/dof=0.256 with dof=1 is a weak statistic (few epochs); K1 detected at only 0.0 sigma (<3) |
| 4607062438892147456 | 245.5 | 1.33 | 49 | 2 | 2 | 1 | 2 phaseable epoch(s), 1 distinct phase bin(s); RV span across epochs = 0.15 km/s — too few distinct phases for a locked fit (1593152 standard) |
| 42521348758696192 | 578.4 | 1.24 | 48 | 2 | 2 | 2 | chi2/dof=0.000 with dof=1 is a weak statistic (few epochs); K1 detected at only 0.0 sigma (<3) |
| 1315399022199887616 | 615.3 | 1.35 | 47 | 2 | 2 | 1 | 2 phaseable epoch(s), 1 distinct phase bin(s); RV span across epochs = 5.09 km/s — too few distinct phases for a locked fit (1593152 standard) |
| 3151205105506859136 | 1038.2 | 1.23 | 47 | 2 | 2 | 1 | 2 phaseable epoch(s), 1 distinct phase bin(s); RV span across epochs = 0.41 km/s — too few distinct phases for a locked fit (1593152 standard) |
| 3155543945892767232 | 543.3 | 1.33 | 41 | 2 | 2 | 2 | chi2/dof=0.000 with dof=1 is a weak statistic (few epochs); K1 detected at only 0.0 sigma (<3) |
| 345412574298262656 | 652.6 | 1.32 | 39 | 4 | 4 | 2 | chi2/dof=0.000 with dof=1 is a weak statistic (few epochs); K1 detected at only 2.7 sigma (<3) |
| 5723238196178723200 | 879.0 | 1.20 | 37 | 3 | 3 | 2 | chi2/dof=0.000 with dof=1 is a weak statistic (few epochs) |
| 826299038567583744 | 1164.8 | 1.54 | 28 | 11 | 11 | 5 | insufficient evidence to corroborate or refute |
| 3455517071870718208 | 680.5 | 1.29 | 23 | 3 | 3 | 2 | chi2/dof=0.220 with dof=1 is a weak statistic (few epochs); K1 detected at only 0.0 sigma (<3); constant-RV null not strongly rejected (p=0.250) |
| 479672397275709952 | 1354.5 | 1.47 | 16 | 2 | 2 | 1 | 2 phaseable epoch(s), 1 distinct phase bin(s); RV span across epochs = 0.28 km/s — too few distinct phases for a locked fit (1593152 standard) |
| 3111209476696494592 | 860.9 | 1.38 | 16 | 3 | 3 | 2 | chi2/dof=0.002 with dof=1 is a weak statistic (few epochs); K1 detected at only 0.0 sigma (<3); constant-RV null not strongly rejected (p=0.997) |
| 150223078247389568 | 1143.3 | 1.43 | 15 | 2 | 2 | 2 | chi2/dof=0.000 with dof=1 is a weak statistic (few epochs); K1 detected at only 0.0 sigma (<3); constant-RV null not strongly rejected (p=0.460) |
| 2133587229775941504 | 431.1 | 1.63 | 14 | 3 | 3 | 2 | chi2/dof=0.140 with dof=1 is a weak statistic (few epochs); K1 detected at only 0.0 sigma (<3); constant-RV null not strongly rejected (p=0.433) |

## Astrometric-quality flags
- ruwe > 1.4: 161/161
- NSS significance < 20: 26/161