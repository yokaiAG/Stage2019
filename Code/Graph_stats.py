
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


# Choose dataset. Si `truegraph` la liste d'adjacence doit être au format $leader follower$.
dataset = str(sys.argv[1])
cascade = bool(int(sys.argv[2]))

data_path, RTU, truegraph = util.load_data(dataset)

# Author dict creation.
if truegraph:
    Author = None
else:
    Author = util.get_authors(data_path)


# ### Graph construction
LeadGraph, FollowGraph = util.get_graph(data_path, RTU, cascade, truegraph, Author)


# Custom wedge metric
numerator = 0
denominator = 0

for i in LeadGraph:
    leaders = LeadGraph[i]
    followers = FollowGraph[i]
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


print("Wedge_metric : ", wedge_metric)