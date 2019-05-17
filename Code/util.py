# coding: utf-8

""" 
->>> Get authors/last Publisher dict:
Author = get_authors(data_path)

->>> Get activity :
lambda, mu, total_time = get_activity(data_path, cascade, Author, divide_by_time=True, retweeted=False)

->>> Get graph in networkx format :
G = nxgraph_from_trace(data_path, cascade, Author=Author)
ou
G = nxgraph_from_adjList(data_path)

->>> Get graph in dicts format :
LeadGraph, FollowGraph = graph_from_trace(data_path, cascade, Author)
ou
LeadGraph, FollowGraph = graph_from_adjList(data_path)
"""


import networkx as nx


# ## Create author dict
def get_authors(data_path):
    Author = dict()
    for tweet in open(data_path):
        tweet = tweet.split()
        twid, uid = int(tweet[0]), int(tweet[2])
        Author[twid] = uid
    return Author

# ## Get $\lambda, \mu$
def get_activity(data_path, cascade, Author, divide_by_time=True, retweeted=False):
    
    """ returns lambda, mu, total_time
    if retweeted : returns lambda, mu, nu, total_time
    if not divide_by_time : ntweet, nrtweet, nrtweetd instead of lambda, mu, nu """
    
    users = set()
    count = {'tweets':dict(), 'retweets':dict(), 'retweeted':dict()}

    # si cascade le author dict est en fait un LastPublisher dict
    if cascade:
        LastPublisher = dict(Author)
        del Author

    # parcourt tweets
    for i,tweet in enumerate(open(data_path)):
        tweet = tweet.split()
        ts, uid, rtid = int(tweet[1]), int(tweet[2]), int(tweet[-1])

        # si user non connu on crée des nouvelles entrées de dictionnaire
        if uid not in users:
            users.add(uid)
            count['tweets'][uid], count['retweets'][uid], count['retweeted'][uid] = 0, 0, 0

        # si tweet original update nb_tweets
        if rtid == -1:
            count['tweets'][uid] += 1

        # si retweet update nb_retweets et nb_retweeted (si retweeted user connu)
        else:
            count['retweets'][uid] += 1
            if cascade:
                if rtid in LastPublisher:
                    rtu = LastPublisher[rtid]
                    if rtu in users:
                        count['retweeted'][rtu] += 1
                    else:
                        users.add(rtu)
                        count['tweets'][rtu], count['retweets'][rtu], count['retweeted'][rtu] = 0, 0, 1
                LastPublisher[rtid] = uid
            else:
                if rtid in Author:
                    rtu = Author[rtid]
                    if rtu in users:
                        count['retweeted'][rtu] += 1
                    else:
                        users.add(rtu)
                        count['tweets'][rtu], count['retweets'][rtu], count['retweeted'][rtu] = 0, 0, 1

        # on enregistre le ts du 1er tweet
        if i==0:
            firstT = ts

    # end
    total_time = ts - firstT
    
    if divide_by_time:
        for activity_type in count:
            for u in count[activity_type]:
                count[activity_type][u] /= total_time
    
    # return
    if retweeted:
        return count['tweets'], count['retweets'], count['retweeted'], total_time
    else:
        return count['tweets'], count['retweets'], total_time

# ## Get networkx graph from adjacency_list
def nxgraph_from_adjList(data_path):
    """ returns networkx graph """
    G = nx.DiGraph()
    for line in open(data_path, 'r'):
        line = line.split()
        G.add_edge(int(line[0]), int(line[1]))
    return G

# ## Get networkx graph from trace
def nxgraph_from_trace(data_path, cascade, Author):

    """ returns networkx graph """
    G = nx.DiGraph()

    # si on utilise cascade
    if cascade:
        LastPublisher = dict(Author)
        del Author
        for tweet in open(data_path, 'r'):
            tweet = tweet.split()
            uid, rtid = int(tweet[2]), int(tweet[-1])
            if uid not in G.nodes:
                G.add_node(uid)
            if rtid != -1:
                if rtid in LastPublisher:
                    G.add_edge(LastPublisher[rtid], uid)
                LastPublisher[rtid] = uid

    # rtid simple (sans cascade)
    else:
        for tweet in open(data_path, 'r'):
            tweet = tweet.split()
            uid, rtid = int(tweet[2]), int(tweet[-1])
            if uid not in G.nodes:
                G.add_node(uid)
            if rtid != -1:
                if rtid in Author:
                    G.add_edge(Author[rtid], uid)

    # end
    return G

# ## Get Leadgraph and Followgraph dicts from adjacency list
def graph_from_adjList(data_path):
    
    """ returns LeadGraph, FollowGraph (dictionaries)"""

    # init
    LeadGraph = dict()
    FollowGraph = dict()

    # process
    for line in open(data_path, 'r'):
        line = line.split()
        u, v = int(line[0]), int(line[1])
        if u in FollowGraph:
            FollowGraph[u].add(v)
        else:
            FollowGraph[u] = {v}
        if v in LeadGraph:
            LeadGraph[v].add(u)
        else:
            LeadGraph[v] = {u}
        if u not in LeadGraph:
            LeadGraph[u] = set()
        if v not in FollowGraph:
            FollowGraph[v] = set()

    # end
    return LeadGraph, FollowGraph

    # ## Get Leadgraph and Followgraph dicts from trace

def graph_from_trace(data_path, cascade,  Author):
    
    """ returns LeadGraph, FollowGraph (dictionaries)"""

    LeadGraph = dict()
    FollowGraph = dict()
    
    # cascade
    if cascade:
        # last publisher dict
        LastPublisher = dict(Author)
        del Author
        # create edges
        for tweet in open(data_path, 'r'):
            tweet = tweet.split()
            uid, rtid = int(tweet[2]), int(tweet[-1])
            if uid not in LeadGraph:
                LeadGraph[uid] = set()
            if uid not in FollowGraph:
                FollowGraph[uid] = set()
            if rtid != -1:
                if rtid in LastPublisher:
                    rtu = LastPublisher[rtid]
                    LeadGraph[uid].add(rtu)
                    if rtu not in LeadGraph:
                        LeadGraph[rtu] = set()
                    if rtu not in FollowGraph:
                        FollowGraph[rtu] = set()
                    FollowGraph[rtu].add(uid)
                LastPublisher[rtid] = uid

    # rtid simple (sans cascade)
    else: 
        # create edges
        for tweet in open(data_path, 'r'):
            tweet = tweet.split()
            uid, rtid = int(tweet[2]), int(tweet[-1])
            if uid not in LeadGraph:
                LeadGraph[uid] = set()
            if uid not in FollowGraph:
                FollowGraph[uid] = set()
            if rtid != -1 and rtid in Author:
                rtu = Author[rtid]
                LeadGraph[uid].add(rtu)
                if rtu not in LeadGraph:
                    LeadGraph[rtu] = set()
                if rtu not in FollowGraph:
                    FollowGraph[rtu] = set()
                FollowGraph[rtu].add(uid)

    # end
    return LeadGraph, FollowGraph