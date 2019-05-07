import sys
import util
import numpy as np
from operator import itemgetter

# args
dataset = str(sys.argv[1])
psi_path = str(sys.argv[2])
cascade = bool(int(sys.argv[3]))
print("Cascade : {}".format(cascade))

# load data
print("Loading data...")
data_path, RTU, truegraph = util.load_data(dataset)
print("Getting author dict...")
Author = util.get_authors(data_path)
print("Getting user graph...")
LeadGraph, FollowGraph = util.get_graph(data_path, RTU, cascade, truegraph, Author)

# get outdegrees and psis
print("Getting outdegrees...")
outdeg = { u:len(FollowGraph[u]) for u in FollowGraph }
print("Getting psis...")
psi = dict()
for line in open(psi_path):
    line = line.split()
    psi[int(line[0])] = float(line[1])

# correlation
print("Same users outdeg and psi ? (just to make sure) {}".format(outdeg.keys() == psi.keys()))
print("Computing correlation...")
outdeg = sorted(outdeg.items(), key=itemgetter(0))
outdeg = np.array([x[1] for x in outdeg])
psi = sorted(psi.items(), key=itemgetter(0))
psi = np.array([x[1] for x in psi])
print("Correlation coeff : {}".format(np.corrcoef(outdeg, psi)))