# Get arXiv ids for bibcodes via ADS API (token read by /tmp/fanout/ads.py helper, never printed)
import sys, re; sys.path.insert(0, '/tmp/fanout')
from ads import search
def arxiv_ids(bibcodes):
    out = {}
    for b in bibcodes:
        docs, n = search(f'bibcode:"{b}"', rows=1, fl='bibcode,identifier,title,first_author')
        if docs is None: out[b] = 'HOLE'; continue
        ids = [i for d in docs for i in d.get('identifier', []) if i.lower().startswith('arxiv:')]
        out[b] = ids[0].split(':', 1)[1] if ids else None
    return out
if __name__ == '__main__':
    for b, a in arxiv_ids(sys.argv[1:]).items(): print(b, a)
