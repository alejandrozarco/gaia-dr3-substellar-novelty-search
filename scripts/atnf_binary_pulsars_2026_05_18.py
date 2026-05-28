"""Pull ATNF Pulsar Catalogue (Manchester+ 2005, B/psr) — extract binary
subset with orbital periods.

Outputs the binary pulsars partitioned by companion-mass class (medM):
  - substellar (medM < 0.05 M_sun) — 37 sources
  - M-dwarf (0.08 <= medM < 0.5)   — 154 sources
  - WD       (0.5 <= medM < 1.4)
  - NS-NS    (1.2 <= medM < 3.0)
  - HMXB     (medM >= 3.0)

These are LEAK-FREE positive labels for the cascade — radio timing
confirms the companion mass, independent of Gaia astrometry.

Output: data/intermediate/atnf_binary_pulsars_2026_05_18.csv
"""
from __future__ import annotations
import sys
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')
import polars as pl
from astroquery.vizier import Vizier

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def main():
    v = Vizier(columns=['**'], row_limit=-1)
    tabs = v.get_catalogs('B/psr')
    if not tabs or len(tabs) == 0:
        print('Failed to retrieve B/psr')
        return 1
    t = tabs[0]
    df = t.to_pandas()
    print(f'ATNF total: {len(df)} pulsars')

    binmask = df['PB'].notna()
    binaries = df[binmask].copy()
    print(f'Binary pulsars (with PB): {binmask.sum()}')

    binaries['PB_d'] = binaries['PB']
    print(f'PB range: {binaries["PB_d"].min():.4f} - {binaries["PB_d"].max():.2f} d')
    print(f'medM range: {binaries["medM"].min():.3f} - {binaries["medM"].max():.2f} M_sun')

    keep = ['PSRJ','RAJ2000','DEJ2000','pmRA','pmDE','Plx','PB','A1','Ecc','OM',
            'medM','minM','BINCOMP','Dist','Assoc']
    keep = [c for c in keep if c in binaries.columns]
    out_df = pl.from_pandas(binaries[keep].reset_index(drop=True))

    out_path = ROOT / 'data' / 'intermediate' / 'atnf_binary_pulsars_2026_05_18.csv'
    out_df.write_csv(out_path)
    print(f'\nSaved {len(out_df)} binary pulsars -> {out_path}')

    n_sub = (binaries['medM'] < 0.05).sum()
    n_md = ((binaries['medM'] >= 0.08) & (binaries['medM'] < 0.5)).sum()
    n_wd = ((binaries['medM'] >= 0.5) & (binaries['medM'] < 1.4)).sum()
    n_ns = ((binaries['medM'] >= 1.2) & (binaries['medM'] < 3.0)).sum()
    n_bh = (binaries['medM'] >= 3.0).sum()
    print(f'\nMass-class partition:')
    print(f'  Substellar (medM < 0.05): {n_sub}')
    print(f'  M-dwarf    (0.08-0.5)   : {n_md}')
    print(f'  WD         (0.5-1.4)    : {n_wd}')
    print(f'  NS-NS      (1.2-3.0)    : {n_ns}')
    print(f'  HMXB-mass  (>= 3.0)     : {n_bh}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
