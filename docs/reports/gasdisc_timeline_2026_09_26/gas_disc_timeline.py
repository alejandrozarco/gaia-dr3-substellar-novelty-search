"""Ca II triplet emission of known and new gaseous-disc white dwarfs in every public spectrum: SDSS/BOSS/DESI (SPARCL), SDSS-V visits,
LAMOST DR11 LRS (local WD catalogue match, 3 arcsec), ESO X-shooter VIS and UVES red-arm phase-3 spectra covering 8450-8700 A.
Per spectrum: gas_disc_epochs.norm (quadratic continuum 8330-8830 A, Ca II/O I windows masked, resampled to the SDSS-V grid) and
measure (summed EW over +-900 km/s of the three lines, with formal error), plus the S/N per resampled pixel, cover_min (smallest
fraction of valid pixels in the three +-900 km/s windows), cont_med and cont_rms (median and robust scatter of the normalised flux
outside the windows over 8350-8830 A) and the Gaussian fit
centroid/FWHM where EW > 5 sigma. ESO wavelengths: air -> vacuum; UVES ADP wavelengths in Angstrom (TUNIT checked).
Input targets.csv (name, gaia); output timeline.csv; per-target failures are recorded as HOLE rows."""
import sys, os, io, gzip, json, subprocess, requests, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts"))
import gas_disc_epochs as GE
from astropy.io import fits
from astropy.time import Time
CACHE = "/tmp/hotdq/lane_gastime/cache"; os.makedirs(CACHE, exist_ok=True)
sw = pd.read_csv("/tmp/hotdq/lane_gasdisc/sw_all.csv", dtype=str)
lam = pd.read_csv("/tmp/hotdq/lane_lamost/lamost_dr11_wd.csv", dtype={"ObsID": str})
def gaia_pos(ids):
    q = "SELECT source_id, ra, dec, pmra, pmdec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(ids) + ")"
    r = requests.post("https://gea.esac.esa.int/tap-server/tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=300)
    return pd.read_csv(io.StringIO(r.text), dtype={"source_id": str}).set_index("source_id")
def eso(ra, dec):
    q = ("SELECT dp_id, instrument_name, t_min, em_min, em_max FROM ivoa.ObsCore WHERE instrument_name IN ('XSHOOTER','UVES') AND "
         f"em_min < 8.45E-7 AND em_max > 8.70E-7 AND CONTAINS(POINT('ICRS',s_ra,s_dec),CIRCLE('ICRS',{ra},{dec},0.003))=1")
    t = pd.read_csv(io.StringIO(requests.post("https://archive.eso.org/tap_obs/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=300).text))
    out = []
    for r in t.itertuples():
        path = os.path.join(CACHE, f"{r.dp_id}.fits")
        if not os.path.exists(path):
            subprocess.run(["curl", "-sL", "-m", "900", "-o", path, f"https://dataportal.eso.org/dataportal_new/file/{r.dp_id}"])
        try:
            h = fits.open(path); d = h[1].data; unit = str(h[1].header.get("TUNIT1", "")).lower()
            w = np.asarray(d["WAVE"][0], float) * (10 if "nm" in unit else 1); f = np.asarray(d["FLUX"][0], float)
            e = np.asarray(d["ERR"][0], float) if "ERR" in d.columns.names else np.asarray(d["ERR_REDUCED"][0], float)
        except Exception as ex:
            out.append(dict(dataset=f"ESO {r.instrument_name}", identifier=r.dp_id, date="", mjd=r.t_min, hole=f"read {type(ex).__name__}")); continue
        out.append(dict(dataset=f"ESO {r.instrument_name}", identifier=r.dp_id, date=Time(r.t_min, format="mjd").iso[:10], mjd=round(float(r.t_min), 3),
                        w=GE.air_to_vac(w), f=f, iv=np.where(e > 0, 1 / np.where(e > 0, e, 1) ** 2, 0)))
    return out
def lamost(ra, dec):
    sep = np.hypot((lam.RAJ2000 - ra) * np.cos(np.radians(dec)), lam.DEJ2000 - dec) * 3600; hit = lam[sep < 3]; out = []
    for r in hit.itertuples():
        raw = b""
        for rel in ("v1.1", "v2.0"):
            try: raw = requests.get(f"https://www.lamost.org/dr11/{rel}/spectrum/fits/{r.ObsID}", timeout=120).content
            except Exception: raw = b""
            if len(raw) > 5000: break
        if len(raw) < 5000: out.append(dict(dataset="LAMOST DR11", identifier=r.ObsID, date=str(r._7), mjd=np.nan, hole="download")); continue
        d = fits.open(io.BytesIO(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw))[1].data[0]
        ok = d["ANDMASK"] == 0
        out.append(dict(dataset="LAMOST DR11", identifier=r.ObsID, date=str(r._7), mjd=float(r.MJD), w=np.asarray(d["WAVELENGTH"], float),
                        f=np.asarray(d["FLUX"], float), iv=np.asarray(d["IVAR"], float) * ok))
    return out
if __name__ == "__main__":
    tg = pd.read_csv(sys.argv[1], dtype=str); pos = gaia_pos(tg.gaia.tolist()); rows = []
    for t in tg.itertuples():
        p = pos.loc[t.gaia]; ra, dec = float(p.ra), float(p.dec); spectra = []
        s_id = sw[sw.gaia_dr3_source_id == t.gaia].sdss_id
        for label, fn in (("SPARCL", lambda: GE.sparcl_spectra(ra, dec)), ("ESO", lambda: eso(ra, dec)), ("LAMOST", lambda: lamost(ra, dec)),
                          ("SDSS-V", lambda: GE.sdssv_spectra(s_id.iloc[0])[1] if len(s_id) else [])):
            try: spectra += fn()
            except Exception as ex: rows.append(dict(name=t.name, gaia=t.gaia, dataset=label, hole=f"{type(ex).__name__}: {str(ex)[:80]}"))
        for s in spectra:
            row = dict(name=t.name, gaia=t.gaia, dataset=s["dataset"], identifier=s["identifier"], date_utc=s["date"], mjd=s["mjd"])
            if "hole" in s: row["hole"] = s["hole"]; rows.append(row); continue
            try:
                n, v = GE.norm(s["w"], s["f"], s["iv"]); ok = (v > 0) & np.isfinite(n)
                if ok.sum() < 100: row["hole"] = "no Ca II coverage"; rows.append(row); continue
                ew, e, _, _ = GE.measure(n, v, np.zeros(len(GE.W)))
                cov = min(float(np.mean(((v > 0) & np.isfinite(n))[np.abs(GE.W / l - 1) * GE.C < 900])) for l in GE.CAT)
                cw = (np.abs(GE.W - 8590) < 240) & ~GE.WIN & ok; cmed = float(np.median(n[cw])) if cw.sum() > 20 else np.nan
                crms = float(1.4826 * np.median(np.abs(n[cw] - cmed))) if cw.sum() > 20 else np.nan
                row.update(snr_pix=round(float(np.median(np.sqrt(v[ok]))), 1), ew_A=ew, ew_err_A=e, cover_min=round(cov, 2), cont_med=round(cmed, 3), cont_rms=round(crms, 3))
                if ew > 5 * e:
                    try: vg, fw = GE.gauss_fit(n, v); row.update(v_gauss_kms=vg, fwhm_gauss_kms=fw)
                    except Exception: pass
            except Exception as ex: row["hole"] = f"measure {type(ex).__name__}"
            rows.append(row)
        print(t.name, len(spectra), "spectra", flush=True)
    pd.DataFrame(rows).to_csv(sys.argv[2], index=False); print("TIMELINE_DONE", flush=True)
