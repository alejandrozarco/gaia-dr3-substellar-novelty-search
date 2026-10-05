import os
import sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.image as im, subprocess
out=sys.argv[1]; L=sys.argv[2:]
subprocess.run([os.path.expanduser('~/claude_projects/ostinato/.venv/bin/python'),'plot1.py']+L)
fig,ax=plt.subplots(4,3,figsize=(27,24))
for a in ax.ravel(): a.axis('off')
for a,n in zip(ax.ravel(),L): a.imshow(im.imread(f'lc/{n}.png'))
plt.tight_layout(); plt.savefig(out,dpi=45)
