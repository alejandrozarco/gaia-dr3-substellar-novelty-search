import warnings,pickle,math,subprocess,urllib.parse,json; warnings.filterwarnings("ignore")
import numpy as np
from scipy.optimize import minimize_scalar, least_squares
P,t,f,e=pickle.load(open("fold.pkl","rb"))
# --- Gaia orbit timing parameters ---
q="SELECT t_periastron,period,eccentricity,a_thiele_innes,b_thiele_innes,f_thiele_innes,g_thiele_innes FROM gaiadr3.nss_two_body_orbit WHERE source_id=1593152388271709824"
u="https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=json&QUERY="+urllib.parse.quote(q)
tp,Po,eo,A,B,F,G=json.loads(subprocess.run(["curl","-sL","--max-time","120",u],capture_output=True,text=True).stdout)["data"][0]
Tp_btjd=2457389.0+tp-2457000.0          # Gaia t_periastron is in days from J2016.0 = JD 2457389.0
uu=(A*A+B*B+F*F+G*G)/2; vv=A*G-B*F; a=math.sqrt(uu+math.sqrt(uu*uu-vv*vv)); cosi=vv/a**2
w_plus_O=math.atan2(B-F,A+G); w_minus_O=math.atan2(-B-F,A-G)
om=((w_plus_O+w_minus_O)/2)%(2*math.pi)
print(f"Gaia outer orbit: P={Po:.2f} d  e={eo:.3f}  T_peri=BTJD {Tp_btjd:.2f}  a_phot={a:.3f} mas  i={math.degrees(math.acos(cosi)):.1f} deg  omega={math.degrees(om):.1f} deg (+/-180 ambiguity)")
# --- eclipse timing per TESS segment: fit the global template with a free time shift ---
ph=((t-t[0])/P)%1.0; nb=200
cen=(np.arange(nb)+0.5)/nb; tmpl=np.array([np.median(f[(ph>=k/nb)&(ph<(k+1)/nb)]) for k in range(nb)])
def model(tt,dt): x=((tt-dt-t[0])/P)%1.0; return np.interp(x,cen,tmpl,period=1.0)
gaps=np.where(np.diff(t)>5)[0]; edges=[0]+list(gaps+1)+[len(t)]
segs=[]
for a0,b0 in zip(edges[:-1],edges[1:]):
    tt,ff,ee=t[a0:b0],f[a0:b0],e[a0:b0]
    if len(tt)<300: continue
    chi=lambda dt: np.sum(((ff-model(tt,dt))/ee)**2)
    grid=np.linspace(-0.02,0.02,801); c=[chi(g) for g in grid]; g0=grid[int(np.argmin(c))]
    r=minimize_scalar(chi,bounds=(g0-0.001,g0+0.001),method="bounded"); c0=r.fun
    red=c0/(len(tt)-1)
    # 1-sigma from delta-chi2 = red (errors rescaled to reduced chi2 = 1)
    s=1e-5; lo=r.x
    while chi(lo)-c0<red and s<0.01: lo-=s; s*=1.3
    s=1e-5; hi=r.x
    while chi(hi)-c0<red and s<0.01: hi+=s; s*=1.3
    segs.append((np.mean(tt),r.x*86400,(hi-lo)/2*86400,len(tt)))
print(f"\n{len(segs)} TESS segments; eclipse-time shift vs a single linear ephemeris (seconds):")
T=np.array([s[0] for s in segs]); O=np.array([s[1] for s in segs]); S=np.array([s[2] for s in segs])
for s in segs: print(f"   BTJD {s[0]:8.1f}  O-C {s[1]:+8.1f} +/- {s[2]:5.1f} s   ({s[3]} pts)")
# linear-only fit (period correction) vs linear + Gaia-shaped LTTE
def kep(M,e):
    E=M.copy()
    for _ in range(50): E=E-(E-e*np.sin(E)-M)/(1-e*np.cos(E))
    return E
def ltte_shape(tt,w):
    M=2*np.pi*(tt-Tp_btjd)/Po; E=kep(np.mod(M,2*np.pi),eo)
    nu=2*np.arctan2(math.sqrt(1+eo)*np.sin(E/2),math.sqrt(1-eo)*np.cos(E/2))
    return (1-eo**2)/(1+eo*np.cos(nu))*np.sin(nu+w)+eo*np.sin(w)
def fit(with_ltte,w=None):
    def res(p):
        m=p[0]+p[1]*(T-T.mean())
        if with_ltte: m=m+p[2]*ltte_shape(T,w)
        return (O-m)/S
    p0=[0,0]+([0] if with_ltte else [])
    r=least_squares(res,p0); return r, np.sum(r.fun**2)
r0,c0=fit(False)
print(f"\nlinear ephemeris only: chi2 = {c0:.1f} for {len(T)-2} dof")
for lab,w in (("omega_Gaia",om),("omega_Gaia+180",om+math.pi)):
    r1,c1=fit(True,w)
    J=r1.jac; cov=np.linalg.pinv(J.T@J); ea=math.sqrt(cov[2,2])
    print(f"+ Gaia-shaped LTTE ({lab}): chi2 = {c1:.1f} for {len(T)-3} dof;  amplitude {r1.x[2]:+.1f} +/- {ea:.1f} s  ({abs(r1.x[2])/ea:.1f} sigma)")
m_tot_guess=2.5; a_out=(m_tot_guess*(Po/365.25)**2)**(1/3)
print(f"\nexpected |amplitude| if the EB pair is ~half the system mass: a_pair sin i / c ~ {a_out*0.5*math.sin(math.acos(cosi))*499.0:.0f} s")
