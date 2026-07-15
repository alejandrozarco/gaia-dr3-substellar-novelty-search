import requests, os
pw = open(os.path.expanduser('~/.config/ztf_zfps/userpass')).read().strip()
email = 'alexander@ch.tudelft.nl'
r = requests.get('https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi',
    auth=('ztffps', 'dontgocrazy!'),
    params={'ra': 326.82833, 'dec': -13.4747,
            'jdstart': 2458194.5, 'jdend': 2461235.5,
            'email': email, 'userpass': pw}, timeout=180)
print('status', r.status_code)
print(r.text.replace(pw, '****')[:800])
