import sys
import util
import numpy as np 

dataset = str(sys.argv[1])
psi_path = str(sys.argv[2])
cascade = bool(int(sys.argv[3]))

# load data
data_path, RTU, truegraph = util.load_data(dataset)
Author = util.get_authors(data_path)
LeadGraph, FollowGraph = util.get_graph(data_path, RTU, cascade, truegraph, Author)

# get outdegrees and psis
outdeg = { u:len(FollowGraph[u]) for u in FollowGraph }
psi = dict()
for line in open(psi_path):
    line = line.split()
    psi[int(line[0])] = float(line[1])

# correlation
print(outdeg.keys() == psi.keys())