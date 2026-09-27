# Southern short-period white dwarfs: Gaia BP/RP amplitudes, infrared excess, TESS

- `select.py` -> `sample.csv` (28 stars): Pwd > 0.75, Gaia DR3 GLS 3-40 c/d, FAP < 1e-3, Dec < -28.
- `gaia_ep.py` -> `south_amp.csv`: Gaia DR3 epoch photometry; sinusoid + harmonic at the GLS frequency in G, BP, RP; RP/BP amplitude ratio.
- `ir_south.py` -> `south_ir.csv`: CatWISE2020 W1/W2 and VHS DR5 J/Ks excess against Montreal pure-H photometry (Table_DA) at GF21 Teff/log g, scaled at Gaia G; companion M_W1; TESS sector count.
- `tess_ffi.py <source_id> <gaia_freq>`: TESScut 7x7 px FFI light curves (sectors listed in the output), per-sector and joint Lomb-Scargle; `tess_*.png`.
