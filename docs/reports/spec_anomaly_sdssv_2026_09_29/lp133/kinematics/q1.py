from astroquery.gaia import Gaia
import json
Gaia.ROW_LIMIT=-1
sid=1609392862209121664
q=f"""select * from gaiadr3.gaia_source where source_id={sid}"""
r=Gaia.launch_job(q).get_results()
row={c:(None if hasattr(r[c][0],'mask') and r[c].mask[0] else (r[c][0].item() if hasattr(r[c][0],'item') else str(r[c][0]))) for c in r.colnames}
json.dump(row,open('gaia_row.json','w'),indent=1,default=str)
for k in ['ra','dec','l','b','parallax','parallax_error','parallax_over_error','pmra','pmra_error','pmdec','pmdec_error','pmra_pmdec_corr','parallax_pmra_corr','parallax_pmdec_corr','ruwe','astrometric_excess_noise','astrometric_excess_noise_sig','astrometric_params_solved','astrometric_n_good_obs_al','astrometric_chi2_al','astrometric_gof_al','ipd_gof_harmonic_amplitude','ipd_gof_harmonic_phase','ipd_frac_multi_peak','ipd_frac_odd_win','visibility_periods_used','duplicated_source','phot_bp_rp_excess_factor','phot_g_mean_mag','bp_rp','radial_velocity','radial_velocity_error','non_single_star','phot_variable_flag','ref_epoch']:
    print(k,row.get(k))
for t in ['nss_two_body_orbit','nss_acceleration_astro','nss_non_linear_spectro','nss_vim_fl']:
    try:
        rr=Gaia.launch_job(f"select source_id from gaiadr3.{t} where source_id={sid}").get_results(); print(t,len(rr))
    except Exception as e: print(t,'ERR',e)
# positive control: a known NSS source
rr=Gaia.launch_job("select top 1 source_id from gaiadr3.nss_two_body_orbit").get_results(); print('control nss rows',len(rr))
rr=Gaia.launch_job(f"select * from external.gaiaedr3_distance where source_id={sid}").get_results(); print(rr)
