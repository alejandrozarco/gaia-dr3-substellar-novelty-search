# VSX API cone (radius 0.003 deg ~ 11") for final candidates. Positive control RR Pic must return.
import requests, json, time
C={'RR Pic (control)':(98.9003,-62.6401),'Gaia19apf 6129723521808742656':(181.04794,-49.82993),'5430557649797803264':(138.66284,-38.56181),'3042753882750748544':(119.75480,-8.17501),
 '5607248786123936384':(104.63022,-31.06063),'6631585605613354368':(280.94190,-62.70252),'5955440827081629568':(264.38318,-43.64065),'5298952292713768576':(140.4551,-61.3128),
 '5813492398419731456':(261.4552,-65.7183),'6036173121152663296':(241.0339,-32.7598),'3538467600619474560':(169.9930,-22.0823),'6184268987981207552':(196.3436,-29.5203),
 '3041858605408672128':(115.7320,-8.2712),'5282634371914454912':(110.4262,-64.0141),'2888241884518643200':(85.1300,-35.9571),'4676030027297506432':(64.0714,-63.7593),
 '3068744791442939904 BD-03 2179':(120.5620,-3.9713),'4658465363442588928 HD 269665':(82.7416,-68.7529),'5610452114472366208':(104.8542,-27.9718)}
out={}
for k,(ra,de) in C.items():
    for a in range(3):
        try:
            r=requests.get('https://www.aavso.org/vsx/index.php',params={'view':'api.list','ra':ra,'dec':de,'radius':0.003,'format':'json'},timeout=60,headers={'User-Agent':'Mozilla/5.0'})
            j=r.json(); break
        except Exception as e: j={'error':str(e)[:80]}; time.sleep(5)
    stars=j.get('VSXObjects',{}).get('VSXObject',[]) if isinstance(j,dict) else []
    if isinstance(stars,dict): stars=[stars]
    out[k]=stars
    print(k,'|',r.status_code if 'r' in dir() else '', '|', [(s.get('Name'),s.get('VariabilityType'),s.get('Period'),s.get('MaxMag'),s.get('MinMag')) for s in stars] if stars else j if 'error' in j else 'NONE')
json.dump(out,open('vsx_api_final.json','w'),indent=1)
