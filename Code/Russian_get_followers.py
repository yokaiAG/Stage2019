
# coding: utf-8

# # <center> Get user graph for `Russian`

# In[1]:


import sys
import util
import json
import time
from twython import Twython


# ### Twitter API credentials
APP_KEY = "AV4KujYNS1y6HdmQ4zXxHw2Tx"
APP_SECRET = "xd2FuFaS5zE1ON407C3U5X0kdEtRJIjH9OMDmgyMmxQCZMFlli"
OAUTH_TOKEN = "1058011325316636672-HkpzhyiOHdJkuwi3FD9QrkMFbuHuVt"
OAUTH_TOKEN_SECRET = "iiD75H9ERtkATnd74pVRBfM7TI189BSmDasYzN2uUO123"


# Get user set from rtu data.
users = list()
for line in open("../Datasets/russian_election2018_rtu.txt"):
    line = line.split()
    users.append(int(line[2]))
    users.append(int(line[3]))

# init
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
FollowGraph = dict()
outfile = "../Datasets/russian_adjList.txt"
error_log = "../Datasets/russian_getfollowers_error_logs.txt"

for i,u in enumerate(users):
    
    # reinit cursor
    cursor = -1
    
    # while there are followers left for this user
    while cursor != 0:
        
        try:
            # get followers
            result = twitter.get_followers_ids(id=u, cursor=cursor)
            ids = result['ids']
            cursor = result['next_cursor']

            # write to out
            with open(outfile, 'a') as out:
                for v in ids:
                    out.write("{} {}\n".format(u,v))

            # wait if API rate limit has been reached
            calls_remaining = int(twitter.get_lastfunction_header('x-rate-limit-remaining'))
            if calls_remaining == 0:
                time_to_wait = 15*60
                start = time.time()
                elapsed_time = 0
                while elapsed_time < time_to_wait:
                    sys.stdout.flush()
                    sys.stdout.write("User {} / {}... Rate limit reached... {} seconds to wait.\r".format(i, len(users), time_to_wait - elapsed_time))
                    time.sleep(1)
                    elapsed_time = time.time() - start
                    
        except:
            with open(error_log, 'a') as out:
                out.write("{} {}\n".format(u, cursor))
            cursor += 1
            continue
