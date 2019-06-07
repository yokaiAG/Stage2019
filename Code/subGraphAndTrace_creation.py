# coding: utf-8

import sys
import util
from operator import itemgetter

# init
adjlist_path = str(sys.argv[1])
trace_path = str(sys.argv[2])
out_path = str(sys.argv[3])
max_nb_follow = int(sys.argv[4])

# import graph 
print("Importing user graph...")
LeadGraph, FollowGraph = util.graph_from_adjList(adjlist_path)
del LeadGraph

# get most followed user among those with <1000 followers
print("Searching for most followed users...")
for (user, nb_follow) in sorted(((u, len(FollowGraph[u])) for u in FollowGraph), key=itemgetter(1), reverse=True):
    if nb_follow < max_nb_follow:
        break
FollowGraph = {u: FollowGraph[u] for u in set(FollowGraph[user]).union({user})}

# write adjlist among her and her followers
print("Writing new adjacency list...")
out = open(out_path + "subAdjlist.txt", "w")
for u in FollowGraph[user]:
    out.write("{} {}\n".format(user, u))
    for v in FollowGraph[u]:
        if v in FollowGraph[user]:
            out.write("{} {}\n".format(u, v))
out.close()
    
# write new trace
print("Getting authors for original twitter trace...")
Author = util.get_authors(trace_path)

print("Writing new twitter trace...")
out = open(out_path + "subTrace.txt", "w")
for line in open(trace_path):
    line_ = line.split()
    uid, rtid = int(line_[2]), int(line_[3])
    if uid in FollowGraph:
        if rtid == -1:
            out.write(line)
        elif rtid in Author:
            if Author[rtid] in FollowGraph:
                out.write(line)
out.close()

print("done!")