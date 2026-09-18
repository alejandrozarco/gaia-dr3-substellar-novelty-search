import warnings, pandas as pd, numpy as np
warnings.filterwarnings("ignore")
from scipy.stats import gamma, halfnorm, uniform
from astro_prost.associate import associate_sample
from astro_prost.helpers import SnRateAbsmag

objs = pd.DataFrame({
 "name":["R950_unreportedSN","R637_SNII_cand","R016_hostless_blue","R822_ZTF19abxfaon_CV","R512_mundane_SN"],
 "RA":  [334.249623, 332.391259, 306.748024, 326.828330, 313.226506],
 "Dec": [-18.207948, -14.869900, -11.818564, -13.474700, -14.840435]})
print(objs.to_string(index=False)); print()

priors = {"offset": uniform(loc=0, scale=10),
          "absmag": uniform(loc=-30, scale=20),
          "z": halfnorm(loc=0.0001, scale=0.5)}
likes  = {"offset": gamma(a=0.75), "absmag": SnRateAbsmag(a=-30, b=-10)}

res = associate_sample(objs, name_col="name", coord_cols=("RA","Dec"), priors=priors, likes=likes,
                       catalogs=["glade","decals","panstarrs"],
                       parallel=False, verbose=1, save=False, cat_cols=True)
res.to_csv("prost_results.csv", index=False)
print("\n=== COLUMNS ===")
print([c for c in res.columns])
