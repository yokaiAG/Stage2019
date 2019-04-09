
# coding: utf-8

# # <center> Utilitary functions </center>

# In[ ]:


""" 
Load dataset :
data_path, out_path, RTU, truegraph = load_data(dataset, cascade)

Get activity :
lambda, mu, total_time = get_activity(data_path, RTU, cascade, divide_by_time=True, retweeted=False):

Get graph in networkx format :
G = get_nx_graph(data_path, RTU, cascade, truegraph)

Get graph in dicts format :
LeadGraph, FollowGraph = get_graph(data_path, RTU, cascade, truegraph)
"""


import networkx as nx


# ## Get dataset

# In[1]:


def load_data(dataset, cascade=False):
    
    """ Choose dataset between (string):
    wcano, russian_rtu, russian_rtid, weibo_rtu, weibo_rtid, tdn10, tdn11, tdnT, test_rtu, test_rtid
    Returns : data_path (=adjacencylist in case of truegraph), out_path, RTU, truegraph
    """

    # wcano
    if dataset == 'wcano':
        data_path = "../Datsets/wcano/tweets.tronques.sorted22n.txt"
        out_path = "../DataAnalysis/wcano/"
        RTU = False
        truegraph = False

    # russian
    elif dataset == 'russian_rtu':
        data_path = "../Datasets/russian/russian_election_2018_rtu.txt"
        out_path = "../DataAnalysis/russian/"
        RTU = True
        truegraph = False
    elif dataset == 'russian_rtid':
        data_path = "../Datasets/russian/russian_election_2018_rtid.txt"
        out_path = "../DataAnalysis/russian/"
        RTU = False
        truegraph = False

    # weibo
    elif dataset == 'weibo_rtu':
        data_path = "../Datasets/weibo/total_rtu.txt"
        out_path = "../DataAnalysis/weibo/"
        RTU = True
        truegraph = False
    elif dataset == 'weibo_rtid':
        data_path = "../Datasets/weibo/total_rtid.txt"
        out_path = "../DataAnalysis/wdeibo/"
        RTU = False
        truegraph = False

    # tdn
    elif dataset == 'tdn10':
        data_path = "../Datasets/tdn/tdn10/tweets2010_clean.txt"
        out_path = "../DataAnalysis/tdn/tdn10/"
        RTU = True
        truegraph = False
    elif dataset == 'tdn11':
        data_path = "../Datasets/tdn/tdn11/tweets2011_clean.txt"
        out_path = "../DataAnalysis/tdn/tdn11/"
        RTU = True
        truegraph = False
    elif dataset == 'tdnT':
        data_path = "../Datasets/tdn/tdnT/adjacency_list.txt"
        out_path = "../DataAnalysis/tdn/tdnT/"
        RTU = False
        truegraph = True

    # test
    elif dataset == 'test_rtu':
        data_path = "../Datasets/test/test_rtu.txt"
        out_path = "../DataAnalysis/test/"
        RTU = True
        truegraph = False
    elif dataset == 'test_rtid':
        data_path = "../Datasets/test/test_rtid.txt"
        out_path = "../DataAnalysis/test/"
        RTU = False
        truegraph = False

    else:
        print("Non existing dataset.")
        return None
        
    return data_path, out_path, RTU, truegraph


# ## Get $\lambda, \mu$

# In[2]:


def get_activity(data_path, RTU, cascade, divide_by_time=True, retweeted=False):
    
    """ returns lambda, mu, total_time
    if retweeted : returns lambda, mu, nu, total_time
    if not divide_by_time : ntweet, nrtweet, nrtweetd instead of lambda, mu, nu """
    
    users = set()
    count = {'tweets':dict(), 'retweets':dict(), 'retweeted':dict()}
    tweets = open(data_path, 'r')

    if RTU:

        # parcourt tweets
        for i,tweet in enumerate(tweets):
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
                if rtu not in users:
                    users.add(rtu)
                    count['tweets'][rtu], count['retweets'][rtu], count['retweeted'][rtu] = 0, 0, 1
                else:
                    count['retweeted'][rtu] += 1

            # on enregistre le ts du 1er tweet
            if i==0:
                firstT = ts

    else:

        # si cascade on doit recréer le LastPublisher dict
        if cascade:
            LastPublisher = dict()
            for tweet in tweets:
                tweet = tweet.split()
                twid, uid = int(tweet[0]), int(tweet[2])
                LastPublisher[twid] = uid

        # sinon on recrée le author dict
        else:
            Author = dict()
            for tweet in tweets:
                tweet = tweet.split()
                twid, uid = int(tweet[0]), int(tweet[2])
                Author[twid] = uid

        # parcourt tweets
        tweets.seek(0)
        for i,tweet in enumerate(tweets):
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
    tweets.close()
    
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

# In[3]:


def get_nx_graph(data_path, RTU, cascade, truegraph):

    """ returns networkx graph """
    
    G = nx.DiGraph()
    
    # si on étudie un vrai graphe (adjacency list)
    if truegraph:
        for i,line in enumerate(open(data_path, 'r')):
            line = line.split()
            G.add_edge(int(line[0]), int(line[1]))

    # sinon on utilise une trace avec rtu, cascade ou rtid
    else:

        # get data
        tweets = open(data_path, 'r')

        # si on utilise des rtu
        if RTU:
            for tweet in tweets:
                tweet = tweet.split()
                uid, rtu = int(tweet[2]), int(tweet[-1])
                if rtu != -1 :
                    G.add_edge(rtu, uid)

        # si on utilise cascade (avec rtid donc)
        elif cascade:

            # last publisher dict
            LastPublisher = dict()
            for tweet in tweets:
                tweet = tweet.split()
                twid, uid = int(tweet[0]), int(tweet[2])
                LastPublisher[twid] = uid

            # create edges
            tweets.seek(0)
            for tweet in tweets:
                tweet = tweet.split()
                twid, uid, rtid = int(tweet[0]), int(tweet[2]), int(tweet[-1])
                if rtid != -1:
                    if rtid in LastPublisher:
                        G.add_edge(LastPublisher[rtid], uid)
                    LastPublisher[rtid] = uid

        # dernier cas : rtid simple (sans cascade)
        else: 

            # author dict
            Author = dict()
            for tweet in tweets:
                tweet = tweet.split()
                twid, uid = int(tweet[0]), int(tweet[2])
                Author[twid] = uid

            # create edges
            tweets.seek(0)
            for tweet in tweets:
                tweet = tweet.split()
                twid, uid, rtid = int(tweet[0]), int(tweet[2]), int(tweet[-1])
                if rtid != -1:
                    if rtid in Author:
                        G.add_edge(Author[rtid], uid)

        # close
        tweets.close()

    # end
    return G


# ## Get Leadgraph and Followgraph dicts

# In[ ]:


def get_graph(data_path, RTU, cascade, truegraph):
    
    """ returns LeadGraph, FollowGraph (dictionaries)"""

    LeadGraph = dict
    FollowGraph = dict()
    
    # si on étudie un vrai graphe (adjacency list)
    if truegraph:
        for i,line in enumerate(open(data_path, 'r')):
            line = line.split()
            u, v = int(line[0]), int(line[1])
            if u in FollowGraph:
                FollowGraph[u].add(v)
            else:
                FollowGraph[u] = {v}
            if v in LeadGraph:
                LeadGraph[v].add(u)
            else:
                Leadgraph[v] = {u}

    # sinon on utilise une trace avec rtu, cascade ou rtid
    else:

        # get data
        tweets = open(data_path, 'r')

        # si on utilise des rtu
        if RTU:
            for tweet in tweets:
                tweet = tweet.split()
                uid, rtu = int(tweet[2]), int(tweet[-1])
                if rtu != -1 :
                    u, v = rtu, uid
                    if u in FollowGraph:
                        FollowGraph[u].add(v)
                    else:
                        FollowGraph[u] = {v}
                    if v in LeadGraph:
                        LeadGraph[v].add(u)
                    else:
                        Leadgraph[v] = {u}

        # si on utilise cascade (avec rtid donc)
        elif cascade:

            # last publisher dict
            LastPublisher = dict()
            for tweet in tweets:
                tweet = tweet.split()
                twid, uid = int(tweet[0]), int(tweet[2])
                LastPublisher[twid] = uid

            # create edges
            tweets.seek(0)
            for tweet in tweets:
                tweet = tweet.split()
                twid, uid, rtid = int(tweet[0]), int(tweet[2]), int(tweet[-1])
                if rtid != -1:
                    if rtid in LastPublisher:
                        u, v = LastPublisher[rtid], uid
                        if u in FollowGraph:
                            FollowGraph[u].add(v)
                        else:
                            FollowGraph[u] = {v}
                        if v in LeadGraph:
                            LeadGraph[v].add(u)
                        else:
                            Leadgraph[v] = {u}
                    LastPublisher[rtid] = uid

        # dernier cas : rtid simple (sans cascade)
        else: 

            # author dict
            Author = dict()
            for tweet in tweets:
                tweet = tweet.split()
                twid, uid = int(tweet[0]), int(tweet[2])
                Author[twid] = uid

            # create edges
            tweets.seek(0)
            for tweet in tweets:
                tweet = tweet.split()
                twid, uid, rtid = int(tweet[0]), int(tweet[2]), int(tweet[-1])
                if rtid != -1:
                    if rtid in Author:
                        u, v = Author[rtid], uid
                        if u in FollowGraph:
                            FollowGraph[u].add(v)
                        else:
                            FollowGraph[u] = {v}
                        if v in LeadGraph:
                            LeadGraph[v].add(u)
                        else:
                            Leadgraph[v] = {u}

        # close
        tweets.close()

    # end
    return LeadGraph, FollowGraph

