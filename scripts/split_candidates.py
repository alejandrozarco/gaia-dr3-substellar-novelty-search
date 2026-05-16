"""Split novelty_candidates.csv into substellar candidates + cascade byproducts.

Splits the 11 rows into:
  * novelty_candidates.csv (9 rows) — true substellar candidates only
  * cascade_byproducts.csv (2 rows) — HD 75426 (mass-ambiguous, posterior straddles BD/star
    boundary) and HD 120954 (apparent stellar-mass companion, by-product of methodology
    side-effect on Gaia NSS Acceleration)

The split addresses external-review feedback that the headline candidate file
shouldn't blur the substellar story with mass-ambiguous and clearly-stellar cases.
"""
import polars as pl

REPO = "/tmp/gaia-novelty-publication"
df = pl.read_csv(f"{REPO}/novelty_candidates.csv")
print(f"Loaded {df.height} rows from novelty_candidates.csv")

# Byproducts: HD 75426 (mass-ambiguous) and HD 120954 (apparent stellar)
BYPRODUCT_NAMES = {"HD 75426", "HD 120954"}

byproducts = df.filter(pl.col("name").is_in(BYPRODUCT_NAMES))
novelty = df.filter(~pl.col("name").is_in(BYPRODUCT_NAMES))

print(f"  novelty (substellar):       {novelty.height} rows")
print(f"    {novelty['name'].to_list()}")
print(f"  byproducts (stellar/ambig): {byproducts.height} rows")
print(f"    {byproducts['name'].to_list()}")

novelty.write_csv(f"{REPO}/novelty_candidates.csv")
byproducts.write_csv(f"{REPO}/cascade_byproducts.csv")
print(f"\nWrote {REPO}/novelty_candidates.csv ({novelty.height} rows)")
print(f"Wrote {REPO}/cascade_byproducts.csv ({byproducts.height} rows)")
