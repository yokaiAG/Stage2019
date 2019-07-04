
# coding: utf-8

# # <center> Simulator (custom)</center>

# This code is used to create synthetic twitter datasets according to the model. We create a user graph and choose an activity pair $(\lambda,\mu)$ for each user . From there we can generate events of tweeting/retweeting where each user $i$ tweets with rate $\lambda_i$ and retweets from his newsfeed with rate $\mu_i$. The output consists of two `.txt` files, one being the adjacency list of the user graph and the other the list of tweets.

# In[4]:

import sys
import util
import numpy as np
import networkx as nx
import random as random
from time import time
from operator import itemgetter
from random import choice

# args
N = str(sys.argv[1])

# Choose out folder where the results will be written.
out_folder = "../Datasets/Newman/"


# ## Setting parameters
# the number of events `nb_events` and the activity rates. The latter are in the form of two lists of length $N$: `Lambda` and `Mu` where `Lambda[i]` is the posting rate of user $i$ and `Mu[i]` is her reposting rate.
w = 0.1
nb_events = 40*w*N*(N-1)

Lambda = [0.1 for n in range(N)]
Mu = [0.1 for n in range(N)]

# ## 1. User graph creation
# We represent the user graph with a dictionary `Followers` where `Followers[i]` is the set of leaders of user $i$.
print("Generating user graph...")

# example: graph Erdös-Rényi of parameter w
Followers = {i:set() for i in range(N)}
for i in range(N):
    for j in range(N):
        if j != i and np.random.random() < w:
            Followers[i].add(j)
print("Number of edges: ", sum([len(Followers[i]) for i in range(N)]))


# Write adjacency list on file.
graph_out = open(out_folder + "adjList_scaleTest.txt", "w")
for i in Followers:
    for j in Followers[i]:
        graph_out.write("{} {}\n".format(i,j))
graph_out.close()


# ## 2. Events creation

# We generate a list `events` where the $i^{th}$ entry corresponds to the $i^{th}$ event occurring on the network. Each event is described as a tuple `twid timestamp userid rtid`, with
# - `twid` is the unique id of the tweet, $\in \{1, \ldots, nb\_events\}$
# - `timestamp` is the instant of occurence (seconds since the beginning)
# - `userid` is the unique id $\in \{1, \ldots, N\}$ of the (re)tweeting user
# - `rtid` is the id of the original tweet in case of retweet, else is set to -1.

print("Generating trace...")


news = {i:list() for i in range(N)} # initialization of the newsfeeds
M = 1 # newsfeeds max size
next_twid = 1 # id of the next post
time = 0 # time since the beginning
Events = list() # list of events (output)

while len(Events) < nb_events:
    
    # generate exponential variates of scale 1/lambda, 1/mu for each user
    posting_time = np.random.exponential([1/x for x in Lambda], N)
    reposting_time = np.random.exponential([1/x for x in Mu], N)
    
    # get closest posting time and reposting time ---> next event will be the closest between both
    min_post = np.min(posting_time)
    min_repost = np.min(reposting_time)
    
    # if the next event is a post
    if min_post < min_repost:
        time += min_post
        user = np.argmin(posting_time)
        new_post = (next_twid, time, user, -1) # create new post
    
    # if repost
    elif min_repost < min_post:
        time += min_repost
        user = np.argmin(reposting_time)
        if len(news[user]) == 0: # skip step if nothing to repost in the user's newsfeed
            continue
        else:
            retweeted = choice(news[user]) # choose what to retweet
            if retweeted[-1] == -1: # get original id
                rtid = retweeted[0]
            else:
                rtid = retweeted[-1]
            new_post = (next_twid, time, user, rtid) # create new_post
            
            
    # append new post to the events list and update next_twid
    Events.append(new_post)
    next_twid += 1

    # update newfeeds for followers of active user
    for j in Followers[user]:
        if len(news[j]) == M: # remove something at random if newsfeed is full
            news[j].remove(choice(news[j]))
        news[j].append(new_post) # add new post to newsfeed


# Write events list to `outfolder/trace.txt`. Each line is an entry of the list.
out = open(out_folder + "trace_scaleTest.txt", "w")
for e in Events:
    out.write("{} {} {} {}\n".format(e[0], e[1], e[2], e[3]))
out.close()

print("Done!")
print()


#################################
# NEWMAN
#################################

def flatten(obj):
    if type(obj) == list:
        return [l for L in obj for l in L]
    if type(obj) == dict:
        return [l for i in obj for l in obj[i].values()]

trace_path = "../Datasets/Newman/trace_scaleTest.txt"
graph_path = "../Datasets/Newman/adjList_scaleTest.txt"

print("Getting authors...")
Author = util.get_authors(trace_path)
users = set(Author.values())

print("Getting node pairs...")
n = len(users)
node_pairs = list()
for i in range(n):
    for j in range(n):
        if i != j:
            node_pairs.append((i,j))

print("Computing E and N...")
# init
E = dict()

# read tweets
for i,line in enumerate(open(trace_path)):
    line = line.split()
    uid, rtid = int(line[2]), int(line[3])
    
    # if retweet of known author
    if rtid != -1 and rtid in Author:
        rtu = Author[rtid]
        if rtu != uid: # no self-edges
            if uid in E:
                if rtu in E[uid] and E[uid][rtu]<30:
                    E[uid][rtu] += 1
                else:
                    E[uid][rtu] = 1
            else:
                E[uid] = {rtu: 1}

N = {u: max(flatten(E)) for u in users}

### iteratioooons ###
print()
print("Iterating...\n")
eps = 0.001
repetitions = 1000
max_iter = 100
verbose = False

# at each repetition we save the values of w, a and b
results = {'w':list(), 'a':list(), 'b':list()}

start = time()
for k in range(repetitions):
    
    # we may have divisions by zero
    try:
    
        # random initialization of the parameters
        w = random.uniform(0, 0.2)
        a = random.uniform(0.5, 1)
        b = random.uniform(0, 0.5)
#         w = random.random()
#         a = random.random()
#         b = random.random()
        if verbose:
            print("init values ", w, a, b)
            print()

        # iter
        for l in range(max_iter):
            
            # print state
            sys.stdout.flush()
#             sys.stdout.write("repetition {}/{} --- iteration {}/{} --- elapsed time {:.3f}\r"
#                              .format(k+1, repetitions, l+1, max_iter, time()-start))
            sys.stdout.write("repetition {}/{} --- elapsed time {:.3f}\r"
                             .format(k+1, repetitions, time()-start))

            old_w, old_a, old_b = w, a, b

            # compute Qij
            Q = dict()
            for i in E:
                ni = N[i]
                Q[i] = dict()
                for j in E[i]:
                    eij = E[i][j]
                    qij = w * a**eij * (1-a)**(ni-eij)
                    qij /= w * a**eij * (1-a)**(ni-eij) + (1-w) * b**eij * (1-b)**(ni-eij)
                    Q[i][j] = qij
            
            # update w,a,b
            w = sum(flatten(Q)) / (n*(n-1))
            numerator_a, numerator_b = 0, 0
            denominator_a, denominator_b = 0, 0
            for i in E:
                ni = N[i]
                for j in E[i]:
                    eij = E[i][j]
                    qij = Q[i][j]
                    numerator_a += qij * eij
                    numerator_b += (1-qij) * eij
                    denominator_a += qij * ni
                    denominator_b += (1-qij) * ni
            a = numerator_a / denominator_a
            b = numerator_b / denominator_b
            if verbose:
                print(w,a,b)
                print()
            
            # break if no sufficient evolution after at least one iteration
            # INCOMPLETE
            new_q = np.array(flatten(Q))
            if l>0 and np.linalg.norm(new_q - old_q) < eps:
                if verbose:
                    print(np.abs([a-old_a, b-old_b, w-old_w]))
                break
            
            # register old_q
            old_q = new_q
            
        # add results to results dict
        results['w'].append(w)
        results['a'].append(a)
        results['b'].append(b)
        
    except e:
        print(e)
        continue

print()
print("Newman time: ", time()-start)