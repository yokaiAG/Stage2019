import matplotlib.pyplot as plt
from operator import itemgetter

print("Reading input file...")
rt2edges = dict()
for line in open("nb_rt_vs_real_edges.txt"):
    line = line.split()
    rt, edge = int(line[0]), int(line[1])
    if rt not in rt2edges:
        if edge==0:
            rt2edges[rt] = [0,1]
        else:
            rt2edges[rt] = [1,0]
    else:
        if edge==0:
            rt2edges[rt][1] += 1
        else:
            rt2edges[rt][0] += 1

print("Sorting results for plot...")
x2plot = sorted(rt2edges.keys())
y2plot = [y[1] for y in sorted(rt2edges.items(), key=itemgetter(0))]
y2plot = [ y[0]/sum(y) for y in y2plot ]

print("Plotting...")
plt.plot(x2plot, y2plot, marker='x')
plt.xlabel("nb rt")
plt.ylabel("edge proba")
plt.savefig("rt_vs_real_edges_plot.png")
plt.show()
plt.close()

print("Done !")