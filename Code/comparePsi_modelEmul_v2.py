
# coding: utf-8

# # <center>Short paper preparation</center>

# In[42]:

import sys
import numpy as np
from time import time
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
from operator import itemgetter
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset
mpl.rcParams.update({'font.size': 14})
mpl.rc('text', usetex = True)
mpl.rc('font', family = 'serif')


psiemul = str(sys.argv[1])
psimodel = str(sys.argv[2])
outpath = str(sys.argv[3])
nb_top_influencers = 20
if not outpath.endswith("/"):
    outpath += "/"
outfile = open(outpath + "compare_psimodelemul_v2.txt")

# Load influences into dicts.
Psi = {'emul':dict(), 'model':dict()}

for line in open(psiemul):
    line = line.split()
    user, psi = int(line[0]), float(line[1])
    if psi > 0:
        Psi['emul'][user] = psi

for line in open(psimodel):
    line = line.split()
    user, psi = int(line[0]), float(line[1])
    if psi > 0:
        Psi['model'][user] = psi


print("Memes users model et emul ? {}".format(set(Psi['model'].keys()) == set(Psi['emul'].keys()))


# ### 3.1 Correlations
outdegs = list()
lambdas = list()
nus = list()
psis_model = list()
psis_emul = list()

for u in Psi['model']:
    outdegs.append(G.out_degree[u])
    lambdas.append(Lambda[u])
    nus.append(Nu[u])
    psis_model.append(Psi['model'][u])
    psis_emul.append(Psi['emul'][u])

outdegs = np.array(outdegs).reshape(-1,1)
lambdas = np.array(lambdas).reshape(-1,1)
nus = np.array(nus).reshape(-1,1)
psis_model = np.array(psis_model).reshape(-1,1)
psis_emul = np.array(psis_emul).reshape(-1,1)

# outdeg
corr = np.corrcoef(np.concatenate((outdegs, psis_model), axis=1), rowvar=False)[0,1]
outfile.write("Correlation coeff between outdeg and psi_model : {}\n".format(corr))
# lambda
corr = np.corrcoef(np.concatenate((lambdas, psis_model), axis=1), rowvar=False)[0,1]
outfile.write("Correlation coeff between lambda and psi_model : {}\n".format(corr))
# nu
corr = np.corrcoef(np.concatenate((nus, psis_model), axis=1), rowvar=False)[0,1]
outfile.write("Correlation coeff between nu and psi_model : {}\n".format(corr))
# psis
corr = np.corrcoef(np.concatenate((psis_emul, psis_model), axis=1), rowvar=False)[0,1]
outfile.write("Correlation coeff between psi_emul and psi_model : {}\n".format(corr))
    


# ### 3.2 Influences distribution
# main plot
fig, ax = plt.subplots()

# labels and legend
plt.xlabel(r"$\psi$")
plt.ylabel(r"Nb. users with $\Psi \geq \psi$".format(origin))

# to remember first plot for zoom
old = True

for origin, psis in Psi.items():

    # on compte les occurences
    values = np.array(sorted(psis.values()))
    unique, counts = np.unique(values, return_counts=True)

    # on cumule
    cumul = np.flip(np.cumsum(np.flip(counts)))

    # plot
    if origin=='emul':
        origin = 'trace'
    ax.loglog(unique, cumul, label=r"{}".format(origin))
    
    # compute alpha value
    values = values[values > 0]
    n = values.shape[0]
    minval = np.min(values)
    alpha = 1 + n / (n * np.log(minval) + np.sum(np.log(values)))
    outfile.write("alpha for psi_{} : {}\n".format(origin, alpha))
    
    # remember first plot
    if old:
        old_unique = unique
        old_cumul = cumul
        old_origin = origin
        old = False
    
# save & show
ax.legend(loc='best', shadow=True)
plt.savefig(outpath + "psi_cumdistrib_log.pdf", dpi=300)
plt.show()
plt.close()


# ### 3.3 Regression $\Psi_{model}$ en fct de $\Psi_{emul}$

# Full.

# In[138]:


# init
fig, ax = plt.subplots()

# main scatter and line
ax.scatter(psis_emul, psis_model, c='blue', s=1.5) # label=r"$(\Psi_{emul}, \Psi_{model})$"
ax.plot(psis_emul, psis_emul, c='red', ls='-.', label=r"$y = x$")
plt.xlim(0, 0.02)
plt.ylim(0, 0.04)

# labels and legends
plt.xlabel(r"$\Psi_{emul}$")
plt.ylabel(r"$\Psi_{model}$")
plt.legend(loc='upper left', shadow=True)

# zoom
axins = zoomed_inset_axes(ax, 7, loc='upper center') # init
axins.scatter(psis_emul, psis_model, c='blue', s=1.5, alpha=0.25) # scatter
axins.plot(psis_emul, psis_emul, c='red', ls='-.', label=r"$y = x$") # line y=x
x1, x2, y1, y2 = 0, 0.001, 0, 0.0015 # specify the limits
axins.set_xlim(x1, x2) # apply the x-limits
axins.set_ylim(y1, y2) # apply the y-limits
plt.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")

# end
plt.show()
plt.savefig(outpath + "psis_y=x_full")
plt.close()


# ## 4. Stats for top influencers
i = 0

outfile.write("user \t psi_em   psi_model   rank_emul   rank_model   outdeg \t lambda\n")
outfile.write("-------------------------------------------------------------------\n")
for user,psi_emul in sorted(Psi['emul'].items(), key=itemgetter(1), reverse=True)[:nb_top_influencers]:
    rank_emul = i+1
    psi_model = Psi['model'][user]
    rank_model = sorted(Psi['model'].items(), key=itemgetter(1), reverse=True).index((user,psi_model))+1
    outfile.write(user, psi_emul, psi_model, rank_emul, rank_model, G.out_degree(user), Lambda[user], sep='\t')
    outfile.write("\n-------------------------------------------------------------------\n")
    i += 1

outfile.close()