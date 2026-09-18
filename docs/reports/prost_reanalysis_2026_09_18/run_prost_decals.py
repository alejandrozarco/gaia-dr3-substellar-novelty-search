import warnings, pandas as pd
warnings.filterwarnings("ignore")
from scipy.stats import gamma, halfnorm, uniform
from astro_prost.associate import associate_sample
from astro_prost.helpers import SnRateAbsmag
objs = pd.DataFrame({
 "name":["R950_unreportedSN","R637_SNII_cand","R016_hostless_blue","R512_mundane_SN"],
 "RA":  [334.249623, 332.391259, 306.748024, 313.226506],
 "Dec": [-18.207948, -14.869900, -11.818564, -14.840435]})
priors = {"offset": uniform(loc=0, scale=10), "absmag": uniform(loc=-30, scale=20),
          "z": halfnorm(loc=0.0001, scale=0.5)}
likes  = {"offset": gamma(a=0.75), "absmag": SnRateAbsmag(a=-30, b=-10)}
res = associate_sample(objs, name_col="name", coord_cols=("RA","Dec"), priors=priors, likes=likes,
                       catalogs=["decals"], parallel=False, verbose=1, save=False, cat_cols=False)
res.to_csv("prost_decals.csv", index=False)
c=["name","best_cat","host_total_posterior","none_posterior","host_ra","host_dec",
   "host_offset_mean","host_redshift_mean","host_absmag_mean","host_2_total_posterior"]
print("\n=== DECaLS-only (has photo-z + absmag support) ===")
print(res[c].to_string(index=False))
