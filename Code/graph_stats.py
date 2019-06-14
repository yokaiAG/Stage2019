import sys
import util

# argvs
data_path = str(sys.argv[1])
out_path = str(sys.argv[2])
cascade = bool(int(sys.argv[3]))
truegraph = bool(int(sys.argv[4]))
print()

# load authors and graph
if truegraph:
    print("Loading user graph...")
    LeadGraph, FollowGraph = util.graph_from_adjList(data_path)
else:
    print("Getting authors...")
    Author = util.get_authors(data_path)
    print("Loading user graph...")
    LeadGraph, FollowGraph = util.graph_from_trace(data_path, cascade, Author)

# compute stats
print("Computing stats...")
nb_nodes = len(LeadGraph)
print("------ nb nodes ok")
nb_edges = 0
for l in LeadGraph.values():
    nb_edges += len(l)
print("------ nb edges ok")
mean_deg = 2 * nb_edges / nb_nodes
print("------ mean deg ok")
max_indeg = max((len(l) for l in LeadGraph.values()))
print("------ max indeg ok")
max_outdeg = max((len(l) for l in FollowGraph.values()))
print("------ max outdeg ok")

# write to out
out = open(out_path + "simple_graph_stats.txt", 'w')
out.write("nb nodes : {}\n".format(nb_nodes))
out.write("nb edges : {}\n".format(nb_edges))
out.write("mean deg : {}\n".format(mean_deg))
out.write("max indeg : {}\n".format(max_indeg))
out.write("max outdeg : {}\n".format(max_outdeg))

# end
out.close()
print("\nFinish !\n")