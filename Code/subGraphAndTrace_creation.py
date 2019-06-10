# coding: utf-8

import sys
import util
from operator import itemgetter

# init
adjlist_path = str(sys.argv[1])
trace_path = str(sys.argv[2])
out_path = str(sys.argv[3])
max_nb_retweetd = int(sys.argv[4])
cascade = False

print()
print("adjlist path : ", adjlist_path)
print("trace path : ", trace_path)
print("out path : ", out_path)
print("max nb retweeted : ", max_nb_retweetd)
print("cascade : ", cascade)

# get authors
print("Getting authors for original twitter trace...")
Author = util.get_authors(trace_path)

# get most retweeted user
print("Searching for most retweeted user with maximum {} retweeted events...".format(max_nb_retweetd))
nb_tweets, nb_retweets, nb_retweeted, total_time = util.get_activity(trace_path, cascade, Author, divide_by_time=False, retweeted=True)
del nb_tweets, nb_retweets, total_time
for (user, nb_rtd) in sorted(nb_retweeted.items(), key=itemgetter(1), reverse=True):
    if nb_rtd < max_nb_retweetd:
        break

# import graph 
print("Importing user graph...")
LeadGraph, FollowGraph = util.graph_from_adjList(adjlist_path)
del LeadGraph
users = set(FollowGraph[user]).union({user})

# restrict user graph
print("Restricting user graph to users of interest...")
FollowGraph = {u: FollowGraph[u] for u in users}

# write new trace and delete users that are not present in the trace
print("Writing new twitter trace...")
trace_users = set()
out = open(out_path + "subTrace.txt", "w")
nb_lines = 0
for line in open(trace_path):
    line_ = line.split()
    uid, rtid = int(line_[2]), int(line_[3])
    if uid in users:
        trace_users.add(uid)
        if rtid == -1:
            out.write(line)
            nb_lines += 1
        elif rtid in Author:
            if Author[rtid] in users:
                out.write(line)
                nb_lines += 1
                trace_users.add(Author[rtid])
out.close()
print("Nb lines in new trace : {}".format(nb_lines))

print("Restricting graph to active users among users of interest...")
users = set(trace_users)
del trace_users
print("Nb users of interest : ", len(users))

# write adjlist among her and her followers
print("Writing new adjacency list...")
out = open(out_path + "subAdjlist.txt", "w")
nb_lines = 0
for u in users:
    for v in FollowGraph[u]:
        if v in users:
            out.write("{} {}\n".format(u, v))
            nb_lines += 1
out.close()
print("Nb lines in new adjlist : {}".format(nb_lines))

# end
print("\nFinish !")