import sys
import util

# argv
trace_path = str(sys.argv[1])
adjlist_path = str(sys.argv[2])

# get authors
print("Getting authors...")
Author = util.get_authors(trace_path)

# get oursin graph
print("Getting oursin graph...")
LeadGraph_oursin, FollowGraph_oursin = util.graph_from_trace(trace_path, False, Author)
del FollowGraph_oursin

# get cascade graph
print("Getting cascade graph...")
LeadGraph_cascade, FollowGraph_cascade = util.graph_from_trace(trace_path, True, Author)
del FollowGraph_cascade

# get real graph
print("Getting real graph...")
LeadGraph_real = dict()
for i,line in enumerate(open(adjlist_path)):
    if i%1000 == 0:
        sys.stdout.flush()
        sys.stdout.write("Line {}...\r".format(i))
    line = line.split()
    lead, follow = int(line[0]), int(line[1])
    if lead in LeadGraph_oursin and follow in LeadGraph_oursin:
        if follow in LeadGraph_real:
            LeadGraph_real[follow].add(lead)
        else:
            LeadGraph_real[follow] = {lead}

# dict to contain edges lists
edges = dict()

# convert oursin to edge lists
print("Converting oursin to edge list...")
edges['oursin'] = { (u,v) for v in LeadGraph_oursin for u in LeadGraph_oursin[v] }
del LeadGraph_oursin

# convert cascade to edge lists
print("Converting cascade to edge list...")
edges['cascade'] = { (u,v) for v in LeadGraph_cascade for u in LeadGraph_cascade[v] }
del LeadGraph_cascade

# convert real graph to edge lists
print("Converting real graph to edge list...")
edges['real'] = { (u,v) for v in LeadGraph_real for u in LeadGraph_real[v] }
del LeadGraph_real

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