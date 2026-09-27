# Uniform checks of the short-period white dwarfs with red-rising modulations

`companion_deepdive.py <gaia_dr3> <freq_cd> <t_max_bjd>` (run from this folder; needs Table_DA from
https://www.astro.umontreal.ca/~bergeron/CoolingModels/Tables/Table_DA):
- SED fit (GALEX, Pan-STARRS or SkyMapper, Gaia; pure-H colours at log g 7.0; E(B-V) up to the SFD column), radius at d = 1/parallax;
- Gaia DR3 per-transit BP-RP against photometric phase (Spearman);
- orbital separation, Roche-lobe mean density and substellar-point temperature.

Ephemerides: `targets.txt` (sdssv-white-dwarfs-2026 tables/irradiated_companions.csv) and `targets_gaia_ephemeris.txt` (Gaia G fits).
Results: `deepdive_results.csv`.
