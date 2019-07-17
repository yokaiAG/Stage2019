
# coding: utf-8
# IMPORTS 
import util
import math
import numpy as np
import sys
from numba import jit

# INIT
data_path = str(sys.argv[1])
adjList_path = str(sys.argv[2])
cascade = False

# Author dict creation if not RTU
print("Author dict creation...")
Author = util.get_authors(data_path)

# GET LAMBDAS MUS AND GRAPH
print("Getting lambdas and mus...")
Rtweet, Rrtweet, total_time = util.get_activity(data_path, cascade, Author, divide_by_time=True, retweeted=False)
print("Getting leaders and followers...")
LeadGraph, FollowGraph = util.graph_from_adjList(adjList_path)

# get common users between trace and real graph
# we remove users with 0 activity or 0 edges
print("Getting common users between graph and trace...")
common_users = set()
for u in Rtweet:
    if u in Rrtweet and u in LeadGraph and u in FollowGraph:
        if Rtweet[u]==0 and Rrtweet[u]==0:
            continue
        elif LeadGraph[u]==set() and FollowGraph[u]==set():
            continue
        else:
            common_users.add(u)
N = len(common_users)

# eliminate users that are not common between graph and twitter trace
print("Filtering common users...")
Rtweet = { u: Rtweet[u] for u in common_users }
Rrtweet = { u: Rrtweet[u] for u in common_users }
LeadGraph = { u: LeadGraph[u].intersection(common_users) for u in common_users }
FollowGraph = { u: FollowGraph[u].intersection(common_users) for u in common_users }

# save lambdas, mus, user graph to out! for common users only
print("Writing to out...")
lambdas = open("weibo_input/lambdas.txt", "w")
mus = open("weibo_input/mus.txt", "w")
lead2follow = open("weibo_input/leadgraph.txt", "w")
follow2lead = open("weibo_input/followgraph.txt", "w")
for i,u in enumerate(common_users):
    sys.stdout.flush()
    sys.stdout.write(">>> user {} / {}...".format(i, N))
    lambdas.write("{} {}\n".format(u, Rtweet[u]))
    mus.write("{} {}\n".format(u, Rrtweet[u]))
    for v in LeadGraph[u]:
        lead2follow.write("{} {}\n".format(v,u))
        follow2lead.write("{} {}\n".format(u,v))
lambdas.close()
mus.close()
lead2follow.close()
follow2lead.close()
del common_users

# ### Build matrix A in sparse format
def som_sparse(Lvec,Mvec,Lead):
    Som = {} 
    for user in Lvec:
        Som[user] = 0
        for leader in Lead[user]:
            Som[user] += np.float32(Lvec[leader]+Mvec[leader])
        Som[user] = np.float32(Som[user])
    return Som


# fill A function
@jit
def fill_A_sparse(Lvec,Mvec,Lead,Som):
    A = {}
    # We consider that Lead[j] contains the set of leaders of node j.
    #
    for user in Lvec:
        A[user] = {}
        for leader in Lead[user]:
            A[user][leader] = np.float32(Mvec[leader]/Som[user])
    return A


@jit
def fill_A_trans_sparse(Lvec,Mvec,Lead,Som):
    A_trans = {}
    # This is the A transpose that we will use also later.
    # A_trans is a dictionary. The keys are the columns of matrix form A. 
    # Each key shows the non-zero elements of A for this column.
    # We consider that Lead[j] contains the set of leaders of node j.
    #
    for user in Lvec:
        A_trans[user] = {}
    for user in Lvec:
        for leader in Lead[user]:
            A_trans[leader][user] = np.float32(Mvec[leader]/Som[user])
    return A_trans

# ### Build matrix C in sparse format
@jit
def fill_C_sparse(Lvec,Mvec):
    C = {}
    for user in Lvec:
        C[user] = 0
        if Lvec[user]+Mvec[user]>0:
            C[user] = np.float32(Mvec[user]/(Lvec[user]+Mvec[user]))
    return C


# Calculation of the general input: dictionary Som and the three dictionaries A, A-trans, C for the matrices.
print("Computing Som...")
Som = som_sparse(Rtweet,Rrtweet,LeadGraph)
print("Writing Som to out...")
with open("weibo_input/Som.txt", "w") as out:
    for key in Som:
        out.write("{} {}\n".format(key, Som[key]))

print("Computing A...")
A = fill_A_sparse(Rtweet,Rrtweet,LeadGraph,Som)
print("Writing A to out...")
with open("weibo_input/A.txt", "w") as out:
    for key in A:
        out.write("{} {}\n".format(key, A[key]))

print("Computing A_trans...")
A_trans = fill_A_trans_sparse(Rtweet,Rrtweet,LeadGraph,Som)
print("Writing A_trans to out...")
with open("weibo_input/A_trans.txt", "w") as out:
    for key in A_trans:
        out.write("{} {}\n".format(key, A_trans[key]))

print("Computing C...")
C = fill_C_sparse(Rtweet,Rrtweet)
print("Writing C to out...")
with open("weibo_input/C.txt", "w") as out:
    for key in C:
        out.write("{} {}\n".format(key, C[key]))

print()
print("FINISH")