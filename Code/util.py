
# coding: utf-8

""" 
Load dataset :
data_path, RTU, truegraph = load_data(dataset, cascade)

Get authors/last Publisher dict:
Author = get_authors(data_path)

Get activity :
lambda, mu, total_time = get_activity(data_path, RTU, cascade, divide_by_time=True, retweeted=False, Author=Author)

Get graph in networkx format :
G = get_nx_graph(data_path, RTU, cascade, truegraph, Author=Author)

Get graph in dicts format :
LeadGraph, FollowGraph = get_graph(data_path, RTU, cascade, truegraph, Author=Author)
"""


import networkx as nx


# ## Get dataset
def load_data(dataset, cascade=False):
    
    """ Choose dataset between (string):
    wcano, russian_rtu, russian_rtid, weibo_rtu, weibo_rtid, tdn10, tdn11, tdnT, test_rtu, test_rtid
    Returns : data_path (=adjacencylist in case of truegraph), out_path, RTU, truegraph
    """

    # wcano
    if dataset == 'wcano':
        data_path = "../Datasets/wcano/tweets.tronques.sorted22n.txt"
        RTU = False
        truegraph = False

    # russian
    elif dataset == 'russian_rtu':
        data_path = "../Datasets/russian/russian_election_2018_rtu.txt"
        RTU = True
        truegraph = False
    elif dataset == 'russian_rtid':
        data_path = "../Datasets/russian/russian_election_2018_rtid.txt"
        RTU = False
        truegraph = False

    # weibo
    elif dataset == 'weibo_rtu':
        data_path = "../Datasets/weibo/total_rtu.txt"
        RTU = True
        truegraph = False
    elif dataset == 'weibo_rtid':
        data_path = "../Datasets/weibo/total_rtid.txt"
        RTU = False
        truegraph = False
    elif dataset == 'weibo_T':
        data_path = "../Datasets/weibo/true_adjacency_list.txt"
        RTU = False
        truegraph = True

    # tdn
    elif dataset == 'tdn10':
        data_path = "../Datasets/tdn/tweets2010_clean.txt"
        RTU = True
        truegraph = False
    elif dataset == 'tdn11':
        data_path = "../Datasets/tdn/tweets2011_clean.txt"
        RTU = True
        truegraph = False
    elif dataset == 'tdnT':
        data_path = "../Datasets/tdn/tdnT_adjacency_list.txt"
        RTU = False
        truegraph = True

    # test
    elif dataset == 'test_rtu':
        data_path = "../Datasets/test/test_rtu.txt"
        RTU = True
        truegraph = False
    elif dataset == 'test_rtid':
        data_path = "../Datasets/test/test_rtid.txt"
        RTU = False
        truegraph = False

    else:
        print("Non existing dataset.")
        return None
        
    return data_path, RTU, truegraph


# ## Create author dict
def get_authors(data_path):
    Author = dict()
    for tweet in open(data_path):
        tweet = tweet.split()
        twid, uid = int(tweet[0]), int(tweet[2])
        Author[twid] = uid
    return Author


# ## Get $\lambda, \mu$
def get_activity(data_path, RTU, cascade, divide_by_time=True, retweeted=False,  Author=None):
    
    """ returns lambda, mu, total_time
    if retweeted : returns lambda, mu, nu, total_time
    if not divide_by_time : ntweet, nrtweet, nrtweetd instead of lambda, mu, nu """
    
    users = set()
    count = {'tweets':dict(), 'retweets':dict(), 'retweeted':dict()}

    if RTU:

        # parcourt tweets
        for i,tweet in enumerate(open(data_path)):
            tweet = tweet.split()
            ts, uid, rtu = int(tweet[1]), int(tweet[2]), int(tweet[-1])

            # si user non connu on crée des nouvelles entrées de dictionnaire
            if uid not in users:
                users.add(uid)
                count['tweets'][uid], count['retweets'][uid], count['retweeted'][uid] = 0, 0, 0

            # si tweet original update nb_tweets
            if rtu == -1:
                count['tweets'][uid] += 1

            # si retweet update nb_retweets et nb_retweeted, ajoute rtu à users
            else:
                count['retweets'][uid] += 1
                if rtu in Author.values(): # si rtu est un noeud du graphe d'utilisateurs
                    if rtu not in users:
                        users.add(rtu)
                        count['tweets'][rtu], count['retweets'][rtu], count['retweeted'][rtu] = 0, 0, 1
                    else:
                        count['retweeted'][rtu] += 1

            # on enregistre le ts du 1er tweet
            if i==0:
                firstT = ts

    else:

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


# ## Get networkx graph
def get_nx_graph(data_path, RTU, cascade, truegraph, Author=None):

    """ returns networkx graph """
    
    G = nx.DiGraph()
    
    # si on étudie un vrai graphe (adjacency list)
    if truegraph:
        for line in open(data_path, 'r'):
            line = line.split()
            G.add_edge(int(line[0]), int(line[1]))

    # sinon on utilise une trace avec rtu, cascade ou rtid
    else:

        # si on utilise des rtu
        if RTU:
            for tweet in open(data_path, 'r'):
                tweet = tweet.split()
                uid, rtu = int(tweet[2]), int(tweet[-1])
                if uid not in G.nodes:
                    G.add_node(uid)
                if rtu != -1 and rtu in Author.values():
                    G.add_edge(rtu, uid)

        # si on utilise cascade (avec rtid donc)
        elif cascade:
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

        # dernier cas : rtid simple (sans cascade)
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


# ## Get Leadgraph and Followgraph dicts
def get_graph(data_path, RTU, cascade, truegraph,  Author=None):
    
    """ returns LeadGraph, FollowGraph (dictionaries)"""

    LeadGraph = dict()
    FollowGraph = dict()
    
    # si on étudie un vrai graphe (adjacency list)
    if truegraph:
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

    # si rtu
    elif RTU:
        for tweet in open(data_path, 'r'):
            tweet = tweet.split()
            uid, rtu = int(tweet[2]), int(tweet[-1])
            if uid not in LeadGraph:
                LeadGraph[uid] = set()
            if uid not in FollowGraph:
                FollowGraph[uid] = set()
            if rtu != -1 and rtu in Author.values():
                LeadGraph[uid].add(rtu)
                if rtu not in LeadGraph:
                    LeadGraph[rtu] = set()
                if rtu not in FollowGraph:
                    FollowGraph[rtu] = set()
                FollowGraph[rtu].add(uid)

    # si on utilise cascade (avec rtid donc)
    elif cascade:
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

    # dernier cas : rtid simple (sans cascade)
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