# imports
import sys
import util
import matplotlib.pyplot as plt

# args
data_path = str(sys.argv[1])
adjList_path = str(sys.argv[2])
out_path = str(sys.argv[3])

# count number of rt
Author = util.get_authors(data_path)
countRT = dict()
for line in open(data_path):
    line = line.split()
    uid, rtid = line[2], line[-1]
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
    l, f = line[0], line[1]
    if (l,f) in countRT:
        real_edges.add((l,f))
        countRT_vs_real.append((countRT[(l,f)], 1))
    else:
        countRT_vs_real.append((0,1))
for e in countRT:
    if e not in real_edges:
        countRT_vs_real.append((countRT[(l,f)], 0))

# compare
plt.scatter([x[0] for x in countRT_vs_real], [x[0] for x in countRT_vs_real])
plt.savefig(out_path + "count rt vs real edges")
plt.show()
plt.close()