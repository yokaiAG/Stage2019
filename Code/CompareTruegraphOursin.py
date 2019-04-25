import sys
import util
from time import time


# args
dataset_oursin = str(sys.argv[1])
dataset_realgraph = str(sys.argv[2])
out = open(str(sys.argv[3]), "w")
cascade = False


# oursin graph
print("Loading oursin data...")
data_path, RTU, truegraph = util.load_data(dataset_oursin, cascade)
print("Creating author dict...")
Author = util.get_authors(data_path)
print("Creating oursin graph...")
LeadGraph_oursin, FollowGraph_oursin = util.get_graph(data_path, RTU, cascade, truegraph, Author=Author)
print()

########### TEST real graph TEST
# print("Loading real graph data...")
# data_path, RTU, truegraph = "../Datasets/test/test_graph.txt", False, True
# print("Creating real graph...")
# LeadGraph_real, FollowGraph_real = util.get_graph(data_path, RTU, cascade, truegraph, Author=None)
# print()
###########

# real graph
print("Loading real graph data...")
data_path, RTU, truegraph = util.load_data(dataset_realgraph, cascade)
print("Creating real graph...")
LeadGraph_real, FollowGraph_real = util.get_graph(data_path, RTU, cascade, truegraph, Author=None)
print()


# compare nodes
oursin_users = set(LeadGraph_oursin.keys())
real_users = set(LeadGraph_real.keys())
common_users = oursin_users.intersection(real_users)

print("Comparing nodes...")
oursin_users_in_real_prop =  len(common_users) / len(oursin_users)
print("Proportion of users from oursin in real graph : {}".format(oursin_users_in_real_prop))
out.write("Proportion of users from oursin in real graph : {}\n".format(oursin_users_in_real_prop))

print("Comparing nodes...")
real_users_in_oursin_prop = len(common_users) / len(real_users)
print("Proportion of users from real in oursin graph : {}".format(real_users_in_oursin_prop))
out.write("Proportion of users from real in oursin graph : {}\n".format(real_users_in_oursin_prop))
print()

del oursin_users, real_users


# compare edges
print("Comparing edges among common users...")
oursin_edges_in_real_prop = 0
i = 0
for u in common_users:
    for v in LeadGraph_oursin[u]:
        if v in common_users and v in LeadGraph_real[u]:
            oursin_edges_in_real_prop += 1
        i += 1
oursin_edges_in_real_prop /= i
print("Proportion of edges in oursin present in real : {}".format(oursin_edges_in_real_prop))
out.write("Proportion of edges in oursin present in real : {}\n".format(oursin_edges_in_real_prop))

print("Comparing edges among common users...")
real_edges_in_oursin_prop = 0
i = 0
for u in common_users:
    for v in LeadGraph_real[u]:
        if v in common_users and v in LeadGraph_oursin[u]:
            real_edges_in_oursin_prop += 1
        i += 1   
real_edges_in_oursin_prop /= i
print("Proportion of edges in real present in oursin : {}".format(real_edges_in_oursin_prop))
out.write("Proportion of edges in real present in oursin : {}".format(real_edges_in_oursin_prop))


# end
out.close()