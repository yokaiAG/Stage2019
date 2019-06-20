import sys
import util

# argv
trace_path = str(sys.argv[1])
adjlist_path = str(sys.argv[2])

# get authors
print("Getting authors...")
Author = util.get_authors(trace_path)

################################################################
##################### OURSIN VS REAL GRAPH #####################
################################################################

# edges dict
edges = dict()

# get oursin edges
print("Getting oursin graph...")
LeadGraph_oursin, FollowGraph_oursin = util.graph_from_trace(trace_path, False, Author)
del FollowGraph_oursin
print("Converting oursin to edge list...")
edges['oursin'] = { (u,v) for v in LeadGraph_oursin for u in LeadGraph_oursin[v] }
del LeadGraph_oursin

# get real graph
print("Getting real graph edges...")
edges['real'] = set()
for line in open(adjlist_path):
    line = line.split()
    lead, follow = int(line[0]), int(line[1])
    edges['real'].add((lead, follow))

# comparison nb edges
nb_edges = dict()
for graph in edges:
    nb_edges[graph] = len(edges[graph])
    print("Nb edges {} : {}".format(graph, nb_edges[graph]))

# comparison edges in common
for graph in edges:
    for graph2 in edges:
        if graph != graph2:
            prop = len(edges[graph].intersection(edges[graph2])) / nb_edges[graph]
            print("Prop edges from {} present in {} : {}".format(graph, graph2, prop))



################################################################
##################### CASCADE VS REAL GRAPH #####################
################################################################

del edges['oursin']

# get cascade edges
print("Getting cascade graph...")
LeadGraph, FollowGraph = util.graph_from_trace(trace_path, True, Author)
del FollowGraph
print("Converting oursin to edge list...")
edges['cascade'] = { (u,v) for v in LeadGraph for u in LeadGraph[v] }
del LeadGraph

# comparison nb edges
nb_edges = dict()
for graph in edges:
    nb_edges[graph] = len(edges[graph])
    print("Nb edges {} : {}".format(graph, nb_edges[graph]))

# comparison edges in common
for graph in edges:
    for graph2 in edges:
        if graph != graph2:
            prop = len(edges[graph].intersection(edges[graph2])) / nb_edges[graph]
            print("Prop edges from {} present in {} : {}".format(graph, graph2, prop))


################################################################
##################### CASCADE VS OURSIN #####################
################################################################

del edges['real']

# get oursin edges
print("Getting oursin graph...")
LeadGraph_oursin, FollowGraph_oursin = util.graph_from_trace(trace_path, False, Author)
del FollowGraph_oursin
print("Converting oursin to edge list...")
edges['oursin'] = { (u,v) for v in LeadGraph_oursin for u in LeadGraph_oursin[v] }
del LeadGraph_oursin

# comparison nb edges
nb_edges = dict()
for graph in edges:
    nb_edges[graph] = len(edges[graph])
    print("Nb edges {} : {}".format(graph, nb_edges[graph]))

# comparison edges in common
for graph in edges:
    for graph2 in edges:
        if graph != graph2:
            prop = len(edges[graph].intersection(edges[graph2])) / nb_edges[graph]
            print("Prop edges from {} present in {} : {}".format(graph, graph2, prop))