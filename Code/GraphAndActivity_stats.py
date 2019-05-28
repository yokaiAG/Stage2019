
# coding: utf-8

# # <center> Graph and Activity stats from dataset

# Imports.

# In[1]:


import os
import sys
import util
from time import time
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from IPython import get_ipython


# Choose dataset and edit `out_path`. <b> Attention ! </b> Si `truegraph` la liste d'adjacence doit être au format $leader follower$.

# In[2]:


data_path = str(sys.argv[1])
out_path = str(sys.argv[2])
cascade = bool(int(sys.argv[3]))
truegraph = bool(int(sys.argv[3]))


# Open outfile (and create out folder if necessary).

# In[3]:


graph_stats = open(out_path + "graph_stats.txt", 'w')


# Author dict creation.

# In[4]:


if truegraph:
    Author = None
else:
    Author = util.get_authors(data_path)


# ### Graph construction
# Construit un graphe nx à partir du dataset.

# In[5]:


if truegraph:
    G = util.nxgraph_from_adjList(data_path)
else:
    G = util.nxgraph_from_trace(data_path, cascade, Author)


# ### Basic stats

# In[6]:


get_ipython().run_cell_magic('capture', 'cap', 'print("Number of nodes: {}".format(G.number_of_nodes()))\nprint("Number of edges: {}".format(G.number_of_edges()))')


# In[7]:


print(cap)
graph_stats.write(cap.stdout+'\n')


# ### Degrees stats

# Les degrés.

# In[8]:


deg = {'degrees': [x[1] for x in G.degree()], 
       'in_degrees': [x[1] for x in G.in_degree()],
       'out_degrees': [x[1] for x in G.out_degree()]}


# Calcul des stats.

# In[9]:


get_ipython().run_cell_magic('capture', 'cap', '\nfor d_type in deg.keys():\n    d = deg[d_type]\n    print("----- Stats for {} -----".format(d_type))\n    print("Mean: ", np.mean(d))\n    print("Median: ", np.median(d))\n    print("Min: ", np.min(d))\n    print("Max: ", np.max(d))\n    for percent in [25, 75, 90, 95, 99]:\n        print("{}% <= {}".format(percent, np.percentile(d, percent)))\n    print()')


# Print and save.

# In[10]:


print(cap)
graph_stats.write(cap.stdout+'\n')


# ### Degrees distribution
# On affiche et on enregistre la distribution des degrés.

# In[11]:


for d_type in deg.keys():
    
    # on récupère les degrés
    d = np.array(sorted(deg[d_type]))
    
    # on compte les occurences
    nb_occ = np.bincount(d)
    nb_occ = nb_occ[nb_occ > 0]

    # on récupère les valeurs uniques de d
    d = np.unique(d)

    # plot
    plt.loglog(d, nb_occ, color='blue')
    
    # save & show
    plt.savefig(out_path + d_type + "_distrib_log.pdf")
    plt.show()
    plt.close()


# ### Connected components basic stats

# In[12]:


get_ipython().run_cell_magic('capture', 'cap', '\nstart = time()\ncc_sizes = {\'weakly\': [len(c) for c in nx.weakly_connected_components(G)],\n            \'strongly\': [len(c) for c in nx.strongly_connected_components(G)]}\n\nprint("Number of weakly connected components: {} (calculated in {})"\n      .format(len(cc_sizes[\'weakly\']), time()-start))\nprint("Number of strongly connected components: {} (calculated in {})"\n      .format(len(cc_sizes[\'strongly\']), time()-start))')


# In[13]:


print(cap)
graph_stats.write(cap.stdout+'\n')


# ### Connected components sizes stats

# In[14]:


get_ipython().run_cell_magic('capture', 'cap', '\nfor s_type in cc_sizes.keys():\n    s = cc_sizes[s_type]\n    print("----- Stats for {} connected components sizes -----".format(s_type))\n    print("Mean: ", np.mean(s))\n    print("Median: ", np.median(s))\n    print("Min: ", np.min(s))\n    print("Max: ", np.max(s))\n    for percent in [25, 75, 90, 95, 99]:\n        print("{}% <= {}".format(percent, np.percentile(s, percent)))\n    print()')


# In[15]:


print(cap)
graph_stats.write(cap.stdout+'\n')


# ### Connected components sizes distrib
# Encore une fois on ne garde que les valeurs <p%tile.

# In[16]:


for s_type in cc_sizes.keys():

    # on récupère les valeurs
    d = np.array(sorted(cc_sizes[s_type]))
    
    # on compte les occurences
    nb_occ = np.bincount(d)
    nb_occ = nb_occ[nb_occ > 0]

    # on récupère les valeurs uniques de d
    d = np.unique(d)

    # plot
    plt.loglog(d, nb_occ, color='blue')
    
    # save & show
    plt.savefig(out_path + "{}_connected_components_sizes_distrib_log.pdf".format(s_type))
    plt.show()
    plt.close()


# ### Custom wedge metric

# <center>
# $\frac{\sum_{\text{user }i}LF - L \cap F}{\sum_{\text{user }i}LF - L \cap F + \frac{1}{2}(L(L-1) + F(F-1))} = \frac{2\sum_{\text{user }i}LF - L \cap F}{\sum_{\text{user }i}(L+F)^2-L-F-2L \cap F}$
# </center>

# In[17]:


numerator = 0
denominator = 0

for i in G.nodes:
    leaders = set(G.predecessors(i))
    followers = set(G.successors(i))
    friends = leaders.intersection(followers)
    if len(leaders) + len(followers) < 2:
        continue
    if leaders==followers and len(leaders)==1:
        continue
    L = len(leaders)
    F = len(followers)
    LintF = len(friends)
    numerator += L*F - LintF
    denominator += (L+F)**2 - L - F - 2*LintF

if denominator != 0:
    wedge_metric = 2 * numerator / denominator
else:
    wedge_metric = 0


# In[18]:


print("Wedge_metric : ", wedge_metric)
graph_stats.write("Wedge_metric : {}".format(wedge_metric))


# ### Close graph_stats

# In[19]:


graph_stats.close()


# # Activity

# ### Nb tweets/retweets/retweeted stats

# On compte le nb de tweets, retweets et retweeted par utilisateur.

# In[20]:


count = dict()
count['tweets'], count['retweets'], count['retweeted'], total_time = util.get_activity(
    data_path, cascade, Author, divide_by_time=False, retweeted=True)


# On affiche et on enregistre.

# In[21]:


get_ipython().run_cell_magic('capture', 'cap', '\nfor count_type in count.keys():\n    c = np.array([*count[count_type].values()])\n    print("----- Stats for {} per user -----".format(count_type))\n    print("Total: ", c.sum())\n    print("Mean: ", np.mean(c))\n    print("Median: ", np.median(c))\n    print("Min: ", np.min(c))\n    maximum = np.max(c)\n    print("Max: {} (user {})".format(maximum, [u for u in count[\'tweets\'] if count[count_type][u]==maximum]))\n    for percent in [25, 75, 90, 95, 99]:\n        print("{}% <= {}".format(percent, np.percentile(c, percent)))\n    print("Nb users with at least 1: ", c[c>0].shape[0])\n    print("Nb users with 0: ", c[c==0].shape[0])\n    print()')


# In[22]:


print(cap)
with open(out_path + "tweetsRetweets_stats.txt", 'w') as out:
    out.write(cap.stdout)
out.close()


# ### Nb tweets/retweets/retweeted distrib

# In[23]:


for count_type in count.keys():
   
    # on récupère les valeurs
    d = np.array(sorted([*count[count_type].values()]))
    
    # on compte les occurences
    nb_occ = np.bincount(d)
    nb_occ = nb_occ[nb_occ > 0]

    # on récupère les valeurs uniques de d
    d = np.unique(d)

    # plot
    plt.loglog(d, nb_occ, color='blue')
    
    # save & show
    plt.savefig(out_path + "number_of_{}_distrib_log.pdf".format(count_type))
    plt.show()
    plt.close()


# ### $\lambda, \mu, \nu$ stats

# In[24]:


activity = {'lambda': np.array([*count['tweets'].values()]) / total_time, 
            'mu': np.array([*count['retweets'].values()]) / total_time, 
            'nu': np.array([*count['retweeted'].values()]) / total_time}


# In[25]:


get_ipython().run_cell_magic('capture', 'cap', '\nfor act_type in activity.keys():\n    c = activity[act_type]\n    print("----- Stats for {} -----".format(act_type))\n    print("Mean: ", np.mean(c))\n    print("Median: ", np.median(c))\n    print("Min: ", np.min(c))\n    maximum = np.max(c)\n    print("Max: ", np.max(c))\n    for percent in [25, 75, 90, 95, 99]:\n        print("{}% <= {}".format(percent, np.percentile(c, percent)))\n    print("Nb users with >0: ", c[c>0].shape[0])\n    print("Nb users with 0: ", c[c==0].shape[0])\n    print()')


# In[26]:


print(cap)
with open(out_path + "activity_stats.txt", 'w') as out:
    out.write(cap.stdout)
out.close()

