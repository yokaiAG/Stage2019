# coding: utf-8

import sys
import util
from operator import itemgetter

# init
adjlist_path = str(sys.argv[1])
trace_path = str(sys.argv[2])
nb_top_users = int(sys.argv[3])

# import graph 
print("Importing user graph...")
LeadGraph, FollowGraph = util.graph_from_adjList(adjlist_path)

# get most followed user and relations among her followers
print("Searching for most followed users...")
i = 0
for (user, nb_follow) in sorted(((u, len(FollowGraph[u])) for u in FollowGraph), key=itemgetter(1), reverse=True):
    print(user, nb_follow)
    i += 1
    if i==nb_top_users:
        break