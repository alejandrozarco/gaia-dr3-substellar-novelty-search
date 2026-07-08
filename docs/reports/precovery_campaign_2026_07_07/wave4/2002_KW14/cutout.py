import requests
# 032849 _ooi_ product; predicted pos RA 252.078935 Dec -24.789001 (exp4 Horizons)
md5="376f445a63c56fc10d3a337be7d3eed5"
RA,DEC=252.078935,-24.789001
attempts=[
 ("svc cutout", f"https://astroarchive.noirlab.edu/api/svc/cutout?siaRef=c4d_170517_032849_ooi_Y_v1.fits.fz&POS={RA},{DEC}&SIZE=0.02"),
 ("soda sync", f"https://astroarchive.noirlab.edu/api/sia/vohdu?POS=CIRCLE+{RA}+{DEC}+0.01"),
]
for name,u in attempts:
    try:
        r=requests.get(u,timeout=60)
        print(name, r.status_code, r.headers.get('Content-Type'), len(r.content))
        if 'fits' in (r.headers.get('Content-Type') or '') or r.content[:6]==b'SIMPLE':
            open("cutout_032849.fits","wb").write(r.content); print("  saved FITS", len(r.content))
        else:
            print("  body:", r.content[:200])
    except Exception as e:
        print(name,"ERR",e)
