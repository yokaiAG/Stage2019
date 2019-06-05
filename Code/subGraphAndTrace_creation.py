# coding: utf-8

import sys
import util
from operator import itemgetter

# init
adjlist_path = str(sys.argv[1])
trace_path = str(sys.argv[2])

# import graph 
LeadGraph, FollowGraph = util.graph_from_adjList(adjlist_path)

# get most followed user and relations among her followers
most_influential_user = max(((u, len(FollowGraph[u])) for u in FollowGraph), key=itemgetter(1))
print(most_influential_user)