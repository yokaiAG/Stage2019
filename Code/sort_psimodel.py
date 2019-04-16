
# coding: utf-8

# In[1]:

import sys
from operator import itemgetter

infile = str(sys.argv[1])
outfile = str(sys.argv[2])

# load psis
psi_model = list()
for line in open(infile):
    line = line.split()
    user, psi = int(line[0]), float(line[1])
    psi_model.append((user, psi))

# sort
psi_model = sorted(psi_model, key=itemgetter(1), reverse=True)

# write to out
out = open(outfile, 'w')
for user, psi in psi_model:
    out.write("{} {}\n".format(user, psi))
out.close()
