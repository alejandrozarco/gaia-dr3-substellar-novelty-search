import s3fs, os
fs=s3fs.S3FileSystem(anon=True)
pats=['qr2/spectral_wcs/cal-wcs-v4-2025-254','qr3/epsf/cal-epsf-v1-2026-191','qr3/epsf/cal-epsf-v2-2026-191','qr2/solid_angle_pixel_map/cal-sapm-v2-2025-164','qr3/l3_flux_corrections/cal-flxc-v1-2026-191','qr3/spectral_wcs/cal-swcs-v5-2026-191']
for p in pats:
    for f in fs.find('nasa-irsa-spherex/'+p):
        out='cal/'+os.path.basename(f)
        if not os.path.exists(out): fs.get(f,out); print(out,flush=True)
