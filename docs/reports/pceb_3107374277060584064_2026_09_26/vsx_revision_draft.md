# VSX revision draft: Gaia DR3 3107374277060584064 (VSX OID 3195181)

Status: draft, not submitted (user action). Existing VSX entry (checked 2026-09-26): type WD, 17.13-17.34 G, spectral type O,
discoverer Gaia collaboration, no period.

## Values to submit (revision)

| field | value |
|---|---|
| Name | Gaia DR3 3107374277060584064 (unchanged) |
| Other names | WDJ064438.09-004550.51 |
| Type | R (reflection effect; hot white dwarf + irradiated companion) |
| Magnitude range | 17.41 - 17.70 r (ZTF, 2018-2024, binned phased light curve; single points 17.37-17.81) |
| Period | 0.5928858 d |
| Epoch | BJD_TDB 2459300.1744 (maximum light, ZTF r) |
| Spectral type | leave as is |
| File | `pceb_summary.png` |

## Remarks (to submit)

Reflection-effect light curve with a period of 0.5928858 d (14.229 h) in ZTF g and r (2018-2024, semi-amplitude about 11% in r and 4% in g) and in Gaia DR3 G epoch photometry.
The same period is in the CoRoT light curves of CoRoT 102743730 (IRa01, LRa01 and LRa06, 2007-2012). That CoRoT star is the G = 16.2 neighbour 4.1" away, whose aperture includes this star.
The neighbour is constant in ZTF.
Period from a joint CoRoT and ZTF fit.
SDSS-V DR20 spectra (4 visits, 2021) show a hot white dwarf (He II 4686 absorption) with H-alpha, H-beta and Ca II triplet emission, whose velocity changes with orbital phase.

## Notes (not for submission)
- Magnitude range: re-derived from ztf_WD.csv (10 phase bins of the joint ephemeris): r bins 17.409-17.702, g 17.052-17.176.
- Epoch: ZTF r maximum from the public table (the earlier BMJD 59300.28308 used a wrong CoRoT time zero point; corrected 2026-09-26). CoRoT times are BJD(TT); ZTF times are HJD. The difference (< 1 min)
  is below the period precision.
- Ferreira Lopes+2025 (J/A+A/703/A32) list the CoRoT period for the F8 IV star (0.592812 d). Consider noting this with the
  moderator.
- Object journal: `docs/object_journals/3107374277060584064.md`.
