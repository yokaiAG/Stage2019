"""
arg1 (string): trace path (ex: /home/vendeville/Stage2019/Datasets/weibo_rtid.txt)
arg2 (string): adjcaency list path (ex: /home/vendeville/Stage2019/Datasets/weibo_adjList.txt)
arg3 (string): out_path. where to write results (ex: /home/vendeville/Stage2019/DataAnalysis/weibo). 
Outputed files are: 
    1) out_path + _outdeg_cumdistrib.eps (cumulative distribution for out-degrees)
    2) out_path + _indeg_cumdistrib.eps (cumulative distribution for in-degrees)
"""

import sys
import util
import matplotlib as mpl
import matplotlib.pyplot as plt
from operator import itemgetter
mpl.rcParams.update({'font.size': 14})
mpl.rc('text', usetex = True)
mpl.rc('font', family = 'serif')

# argvs
trace_path = str(sys.argv[1])
adjlist_path = str(sys.argv[2])
out_path = str(sys.argv[3])

# authors
print("Getting authors...")
Author = util.get_authors(trace_path)

# get degrees list
outdeg = dict()
indeg = dict()

# oursin
print("Getting degrees for oursin...")
LeadGraph, FollowGraph = util.graph_from_trace(trace_path, False, Author)
outdeg['urchin'] = [len(FollowGraph[u]) for u in FollowGraph]
indeg['urchin'] = [len(LeadGraph[u]) for u in LeadGraph]

# cascade
print("Getting degrees for cascade...")
LeadGraph, FollowGraph = util.graph_from_trace(trace_path, True, Author)
outdeg['cascade'] = [len(FollowGraph[u]) for u in FollowGraph]
indeg['cascade'] = [len(LeadGraph[u]) for u in LeadGraph]

# real graph
print("Getting degrees for truegraph...")
LeadGraph, FollowGraph = util.graph_from_adjList(adjlist_path)
outdeg['real'] = [len(FollowGraph[u]) for u in FollowGraph]
indeg['real'] = [len(LeadGraph[u]) for u in LeadGraph]

# clean for memory
del Author, LeadGraph, FollowGraph, trace_path, adjlist_path

# plot style
colors = {'urchin': 'blue', 'cascade':'red', 'real':'green'}
linestyle = {'urchin': ':', 'cascade':'--', 'real':'-.'}

# compute outdeg cumul distrib
for graph in outdeg:
    print("Outdeg distribution for {}...".format(graph))

    print("--> Cumul...")
    # on récupère les valeurs
    outdeg_unique = sorted(set(outdeg[graph]))
    
    # on compte les occurences
    cumul = list()
    for val in outdeg_unique:
        cumul.append(len([x for x in outdeg[graph] if x>=val]))

    # plot
    print("--> Plot...")
    plt.loglog(outdeg_unique, cumul, ls=linestyle[graph], label=graph)
    plt.xlabel(r"Out-degree $\delta_{out}$")
    plt.ylabel(r"Number of users with out-degree $\geq \delta_{out}$")

# clean
del outdeg, outdeg_unique

# save & show
print("Saving...")
plt.savefig(out_path + "_outdeg_cumdistrib.eps")
plt.close()

# compute indeg cumul distrib
for graph in indeg:
    print("Outdeg distribution for {}...".format(graph))

    print("--> Cumul...")
    # on récupère les valeurs
    indeg_unique = sorted(set(indeg[graph]))
    
    # on compte les occurences
    cumul = list()
    for val in indeg_unique:
        cumul.append(len([x for x in indeg[graph] if x>=val]))

    # plot
    print("--> Plot...")
    plt.loglog(indeg_unique, cumul, ls=linestyle[graph], label=graph)
    plt.xlabel(r"In-degree $\delta_{in}$")
    plt.ylabel(r"Number of users with In-degree $\geq \delta_{in}$")

# save & show
print("Saving...")
plt.savefig(out_path + "_indeg_cumdistrib.eps")
plt.close()