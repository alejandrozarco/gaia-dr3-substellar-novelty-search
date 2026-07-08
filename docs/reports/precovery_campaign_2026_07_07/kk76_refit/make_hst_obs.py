import math
PACK = "88268K01K76K"  # packed number(5)+packed prov desig(7), from MPC arc

# (utc_jd, ra_deg, dec_deg, Xkm, Ykm, Zkm)  geocentric equatorial J2000 HST position
DET = [
 (2453857.857090, 253.861466, -22.186202, -6826.769438, -677.028023, -1088.684669),
 (2453857.860793, 253.861387, -22.186194, -6039.022821, -2723.620806, -2092.558089),
 (2453857.864497, 253.861323, -22.186188, -4522.832183, -4442.351924, -2843.690040),
 (2453857.868201, 253.861260, -22.186182, -2461.602245, -5625.786012, -3251.223107),
]
SIG = "0.16x0.10"  # RA x Dec arcsec (referee-mandated)

def jd_to_cal(jd):
    jd += 0.5
    Z=math.floor(jd); F=jd-Z
    if Z<2299161: A=Z
    else:
        al=math.floor((Z-1867216.25)/36524.25); A=Z+1+al-math.floor(al/4)
    B=A+1524; C=math.floor((B-122.1)/365.25); D=math.floor(365.25*C)
    E=math.floor((B-D)/30.6001)
    day=B-D-math.floor(30.6001*E)+F
    month=E-1 if E<14 else E-13
    year=C-4716 if month>2 else C-4715
    return year,month,day

def date_field(jd):
    y,m,d=jd_to_cal(jd)
    return f"{y:4d} {m:02d} {d:08.5f}"   # e.g. '2006 05 02.357292' (17 chars)

def ra_field(ra):
    h=ra/15.0; hh=int(h); r=(h-hh)*60; mm=int(r); ss=(r-mm)*60
    return f"{hh:02d} {mm:02d} {ss:05.2f}"

def dec_field(dec):
    s='-' if dec<0 else '+'; a=abs(dec); dd=int(a); r=(a-dd)*60; mm=int(r); ss=(r-mm)*60
    return f"{s}{dd:02d} {mm:02d} {ss:04.1f}"

def axis(v):
    sign='-' if v<0 else '+'
    return f"{sign} {abs(v):9.4f} "   # 12 chars: sign, space, %9.4f (9), trailing space

def main_line(jd,ra,dec):
    line=list(" "*80)
    line[0:12]=PACK
    line[13]=' '        # note1
    line[14]='S'        # satellite obs type
    df=date_field(jd)
    line[15:15+len(df)]=df
    raf=ra_field(ra); line[32:32+len(raf)]=raf
    decf=dec_field(dec); line[44:44+len(decf)]=decf
    line[77:80]='250'
    return "".join(line)

def sat_line(jd,X,Y,Z):
    line=list(" "*80)
    line[0:12]=PACK
    line[14]='s'
    df=date_field(jd)
    line[15:15+len(df)]=df
    line[32]='1'        # units = km
    fx=axis(X); fy=axis(Y); fz=axis(Z)
    line[34:46]=fx
    line[46:58]=fy
    line[58:70]=fz
    line[77:80]='250'
    return "".join(line)

out=[]
for jd,ra,dec,X,Y,Z in DET:
    out.append(f"#Sigmas {SIG}")
    out.append(main_line(jd,ra,dec))
    out.append(sat_line(jd,X,Y,Z))

open("hst4.obs","w").write("\n".join(out)+"\n")
ruler="".join(str(i%10) for i in range(80))
print(ruler)
for l in out: print(l)
