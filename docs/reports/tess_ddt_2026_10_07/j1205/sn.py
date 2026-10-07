import numpy as np, warnings; warnings.filterwarnings('ignore')
from astropy.timeseries import LombScargle
rng=np.random.default_rng(1)
D={s:np.load(f'ap_s{s}.npy') for s in [64,99,100,101]}
def pk(t,y,fc,hw=0.03):
    fr=np.arange(fc-hw,fc+hw,0.0002); ls=LombScargle(t,y); p=ls.power(fr); j=p.argmax()
    m=ls.model_parameters(fr[j]); return fr[j],p[j],np.hypot(m[1],m[2])
sets={'S64':[64],'S99':[99],'S100':[100],'S101':[101],'S99-101':[99,100,101]}
for name,ss in sets.items():
    t=np.concatenate([D[s][0] for s in ss]); y=np.concatenate([D[s][1] for s in ss]); tc=np.concatenate([D[s][2] for s in ss])
    tsc=t-tc  # spacecraft-frame time
    hw=0.03 if len(ss)==1 else 0.01
    for f0 in [203.40,206.76]:
        # refine in BJD around sub-Nyquist candidate
        fb,pb,ab=pk(t,y,f0+(0.03 if name=='S64' and f0==203.40 else 0),0.06)
        fm=432.0-fb  # nominal mirror (spacecraft Nyquist 216 c/d exactly for 200 s)
        fm2,pm,am=pk(t,y,fm,0.06)
        # spacecraft frame: both should be equal
        fs,ps,_=pk(tsc,y,fb,0.06); fsm,psm,_=pk(tsc,y,432-fs,0.06)
        # simulation: inject pure sinusoid (amp ab) at fb (sub) or at fm2 (super), same times + noise of residual
        res=[]
        for truth in ['sub','super']:
            r=[]
            for k in range(30):
                ftrue=fb if truth=='sub' else fm2; ph=rng.uniform(0,2*np.pi)
                ys=ab*np.sin(2*np.pi*ftrue*t+ph)+rng.normal(0,np.std(y),len(t))
                r.append(pk(t,ys,fb,0.01)[1]/pk(t,ys,fm2,0.01)[1])
            res.append((np.median(r),np.percentile(r,16),np.percentile(r,84)))
        print(f'{name} f0~{f0}: BJD sub {fb:.4f} P={pb:.5f} A={ab:.3f} | mirror {fm2:.4f} P={pm:.5f} A={am:.3f} | ratio sub/super={pb/pm:.2f} ; s/c-frame ratio={ps/psm:.2f} ; sim ratio if true=sub {res[0][0]:.2f} [{res[0][1]:.2f},{res[0][2]:.2f}], if true=super {res[1][0]:.2f} [{res[1][1]:.2f},{res[1][2]:.2f}]',flush=True)
