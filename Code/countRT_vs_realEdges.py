# imports
import sys
import util

# args
data_path = str(sys.argv[1])
adjList_path = str(sys.argv[2])
out_path = str(sys.argv[3])

# count number of rt
Author = util.get_authors(data_path)
countRT = dict()
for line in open(data_path):
    line = line.split()
    uid, rtid = int(line[2]), int(line[-1])
    if rtid != -1 and rtid in Author:
        rtu = Author[rtid]
        if (uid, rtu) in countRT:
            countRT[(uid,rtu)] += 1
        else:
            countRT[(uid,rtu)] = 1
del Author

# real edges
countRT_vs_real = list()
real_edges = set()
for line in open(adjList_path):
    line = line.split()
    l, f = int(line[0]), int(line[1])
    if (f,l) in countRT:
        real_edges.add((f,l))
        countRT_vs_real.append((countRT[(f,l)], 1))
    else:
        countRT_vs_real.append((0,1))
for e in countRT:
    if e not in real_edges:
        countRT_vs_real.append((countRT[e], 0))

# compare
out = open(out_path + "count rt vs real edges.txt", "w")
for nbrt, real in countRT_vs_real:
    out.write(str(nbrt) + " " + str(real) + "\n")
out.close()