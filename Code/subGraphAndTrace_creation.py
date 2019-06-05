# coding: utf-8

import sys
import util
from operator import itemgetter

# init
adjlist_path = str(sys.argv[1])
trace_path = str(sys.argv[2])

# import graph 
print("Importing user graph...")
LeadGraph, FollowGraph = util.graph_from_adjList(adjlist_path)

# get most followed user and relations among her followers
print("Searching for most followed user...")
most_followed_user = max(((u, len(FollowGraph[u])) for u in FollowGraph), key=itemgetter(1))
print("Most followed user and her number of followers : ", most_followed_user)