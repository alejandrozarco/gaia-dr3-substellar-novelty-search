# White dwarfs in the ZTF periodic-variable catalogue (Chen et al. 2020)

- `xm_chen_table2.py`, `xm_chen_table3.py`: CDS XMatch of Chen+2020 (J/ApJS/249/18 table2, classified; table3, suspected) with Gentile Fusillo+2021 (J/MNRAS/508/3877), 1.5". 95 + 632 matches.
- `combine.py` -> `chen_wd_all.csv` (M_G, BP-RP, period in hours, r/g amplitude ratio).
- `ir.py` -> `short_red_ir.csv`: Pwd > 0.75, P < 6 h, r/g > 1.4, G < 19.5; CatWISE2020 W1/W2 and VHS/2MASS Ks excess against Montreal pure-H synthetic photometry (Table_DA, https://www.astro.umontreal.ca/~bergeron/CoolingModels/Tables/Table_DA) at the GF21 Teff/log g.
- `j2127/`: TESS SPOC 120 s and 20 s light curves of WDJ212738.67+593755.72 (sectors 76, 77, 83, 84); download with astroquery.mast (TIC 2019069807).
