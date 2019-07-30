# coding: utf-8

"""
arg1 (string): psi list to sort (ex: /home/vendeville/Stage2019/PsiResults/Psis/weibo_emul.txt). 
arg2 (string): outputed file (ex: /home/vendeville/Stage2019/PsiResults/Psis/weibo_emul_sorted.txt).
"""

import sys
from operator import itemgetter

# choose in and out paths
infile = str(sys.argv[1])
outfile = str(sys.argv[2])

# load psis
psi_model = set()
for line in open(infile):
    line = line.split()
    user, psi = int(line[0]), float(line[1])
    psi_model.add((user, psi))

# sort
psi_model = sorted(list(psi_model), key=itemgetter(1), reverse=True)

# save to out
out = open(outfile, 'w')
for user, psi in psi_model:
    out.write("{} {}\n".format(user, psi))
out.close()