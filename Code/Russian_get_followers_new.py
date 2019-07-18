# coding: utf-8

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
print("Getting users and errors...")
user2cursor = dict()
for line in open("../Datasets/russian_getfollowers_error_logs.txt"):
    u, err = int(line.split()[0]), int(line.split()[1])
    if u in user2cursor:
        user2cursor[u].add(err)
    else:
        user2cursor[u] = err

# init
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
FollowGraph = dict()
outfile = "../Datasets/russian_adjList_new.txt"
errorfile = "../Datasets/russian_errors_new.txt"

# iterate
for u,cursor in user2cursor.items():
        
    try:
        # get followers
        result = twitter.get_followers_ids(id=u, cursor=cursor)
        sys.stdout.flush()
        sys.stdout.write("User {} ok...\r".format(u))

        # write to out
        with open(outfile, 'a') as out:
            for v in result['ids']:
                out.write("{} {}\n".format(u,v))

        # wait if API rate limit has been reached
        calls_remaining = int(twitter.get_lastfunction_header('x-rate-limit-remaining'))
        if calls_remaining == 0:
            time_to_wait = 15*60 + 5 # add 5 seconds just in case
            start = time.time()
            elapsed_time = 0
            while elapsed_time < time_to_wait:
                sys.stdout.flush()
                sys.stdout.write("User {}... Rate limit reached... {} seconds to wait.\r".format(u, round(time_to_wait - elapsed_time)))
                time.sleep(1)
                elapsed_time = time.time() - start
                
    except Exception as e:
        error_string = "{} {} {}\n".format(u, cursor, e)
        print(error_string)
        with open(errorfile, 'a') as out:
            out.write(error_string)
        continue