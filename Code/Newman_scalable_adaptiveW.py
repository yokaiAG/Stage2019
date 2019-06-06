
# coding: utf-8

# # <center> Newman on custom trace and user graph </center>

# In[60]:


import sys
import util
import numpy as np
import networkx as nx
import random as random
from time import time
from operator import itemgetter
import matplotlib.pyplot as plt


# argvs
trace_path = str(sys.argv[1])
realGraph_path = str(sys.argv[2])
out_path = str(sys.argv[3])
n_samples = int(sys.argv[4])
verbose = bool(int(sys.argv[5]))

print("trace_path : ", trace_path)
print("real graph path : ", realGraph_path)
print("out path : ", out_path)
print("n samples : ", n_samples)
print("verbose : ", verbose)

# create outfile txt for printing infos
outfile = open(out_path + "newman_results.txt", "w")

# Get authors
print("Getting authors...")
Author = util.get_authors(trace_path)

# Useful function to flatten a list of lists or values from dict of dicts.
def flatten(obj):
    if type(obj) == list:
        return [l for L in obj for l in L]
    if type(obj) == dict:
        return [l for i in obj for l in obj[i].values()]

# Number of nodes n
n = len(set(Author.values()))

#### Compute E and N.
print("Computing E and N...")

# init
E = dict()

# read tweets
for line in open(trace_path):
    line = line.split()
    uid, rtid = int(line[2]), int(line[3])
    
    # if retweet of known author
    if rtid != -1 and rtid in Author:
        rtu = Author[rtid]
        if rtu != uid: # no self-edges
            if uid in E:
                if rtu in E[uid] and E[uid][rtu]<30:
                    E[uid][rtu] += 1
                else:
                    E[uid][rtu] = 1
            else:
                E[uid] = {rtu: 1}
                
# compute N
N = {u: max(flatten(E)) for u in E}


# ## 2. Iterations
print("Iterations...")

# Choose parameters.
eps = 0.001
repetitions = 100
max_iter = 100

##### Proceed NEW VERSION SPARSE.

# at each repetition we save the values of w, a and b
results = {'w':list(), 'a':list(), 'b':list()}

start = time()
for k in range(repetitions):
    
    # we may have divisions by zero
    try:
    
        # random initialization of the parameters
        w = random.uniform(0, 0.2)
        a = random.uniform(0.5, 1)
        b = random.uniform(0, 0.5)
        if verbose:
            print("init values ", w, a, b)
            print()

        # iter
        for l in range(max_iter):
            
            # print state
            sys.stdout.flush()
            sys.stdout.write("repetition {}/{} --- iteration {}/{} --- elapsed time {:.3f}\r"
                             .format(k+1, repetitions, l+1, max_iter, time()-start))

            old_w, old_a, old_b = w, a, b

            # compute Qij
            Q = dict()
            for i in E:
                ni = N[i]
                Q[i] = dict()
                for j in E[i]:
                    eij = E[i][j]
                    qij = w * a**eij * (1-a)**(ni-eij)
                    qij /= w * a**eij * (1-a)**(ni-eij) + (1-w) * b**eij * (1-b)**(ni-eij)
                    Q[i][j] = qij
            
            # update w,a,b
            w = sum(flatten(Q)) / (n*(n-1))
            numerator_a, numerator_b = 0, 0
            denominator_a, denominator_b = 0, 0
            for i in E:
                ni = N[i]
                for j in E[i]:
                    eij = E[i][j]
                    qij = Q[i][j]
                    numerator_a += qij * eij
                    numerator_b += (1-qij) * eij
                    denominator_a += qij * ni
                    denominator_b += (1-qij) * ni
            a = numerator_a / denominator_a
            b = numerator_b / denominator_b
            if verbose:
                print(w,a,b)
                print()
            
            # break if no sufficient evolution after at least one iteration
            # INCOMPLETE
            new_q = np.array(flatten(Q))
            if l>0 and np.linalg.norm(new_q - old_q) < eps:
                if verbose:
                    print(np.abs([a-old_a, b-old_b, w-old_w]))
                break
            
            # register old_q
            old_q = new_q
            
        # add results to results dict
        results['w'].append(w)
        results['a'].append(a)
        results['b'].append(b)
        
    except:
        continue


# Print results.

# plot the results
print("Plotting histograms of results...")
plt.rcParams["figure.figsize"] = [10,2]
fig, ax = plt.subplots(1, 3, sharey=True)
for i,(key,values) in enumerate(results.items()):
    values = sorted(values)
    ax[i].hist(values, label=key, facecolor='yellow', edgecolor='red')
    ax[i].set_xlabel(key)  
plt.savefig(out_path + "results_hist.pdf")
plt.close()

# print results
print("Getting top values...")
for key,val in results.items():
    outfile.write("top 5 values for {} and proportion\n".format(key))
    val = [round(v,3) for v in val]
    valcount = list()
    for v in set(val):
        valcount.append((v, val.count(v)/len(val)))
    valcount = sorted(valcount, key=itemgetter(1), reverse=True)
    for x in valcount[:5]:
        outfile.write(x[0], x[1], '\n')
    outfile.write('\n')
    
outfile.write("top 5 values for (w,a,b) and proportion\n")
val = list()
for i in range(len(results['w'])):
    val.append((round(results['w'][i],3), round(results['a'][i],3), round(results['b'][i],3)))
valcount = list()
for v in set(val):
    valcount.append((v, val.count(v)/len(val)))
valcount = sorted(valcount, key=itemgetter(1), reverse=True)
for x in valcount[:5]:
    outfile.write(x[0], x[1], '\n')
outfile.write('\n')


# Set w,a,b to the most observed values and compute Q accordingly.
w, a, b = max([(v, val.count(v)/len(val)) for v in set(val)], key=itemgetter(1))[0]

# compute Q
Q = dict()
for i in E:
    ni = N[i]
    Q[i] = dict()
    for j in E[i]:
        eij = E[i][j]
        qij = w * a**eij * (1-a)**(ni-eij)
        qij /= w * a**eij * (1-a)**(ni-eij) + (1-w) * b**eij * (1-b)**(ni-eij)
        Q[i][j] = qij
        
# plot
outfile.write("w, a, b = ", w,a,b,'\n')
plt.hist(flatten(Q), facecolor='yellow', edgecolor='red')
plt.xlabel("Q distrib")
plt.savefig(out_path + "Q_distrib.pdf")
plt.close()


# ## 3. Result analysis

# ### 3.1 Plots

# Plot E/N vs Q.
plt.rcParams["figure.figsize"] = [6,4]
x2plot = flatten(E)
y2plot = flatten(Q)
plt.scatter(x2plot, y2plot, color='blue', marker='x', alpha=.5)
plt.xlabel("E [edge]")
plt.ylabel("Q [edge]")
plt.savefig(out_path + "EvsQ.pdf")
plt.close()


# Get real graph.
print("Getting real graph...")

G = nx.DiGraph()
G.add_nodes_from(set(Author.values()))
for line in open(realGraph_path):
    line = line.split()
    user = int(line[0])
    for leader in line[1:]:
        leader = int(leader)
        G.add_edge(leader, user)


# Compare expected degrees.
print("Comparing expected degrees...")
expected_deg = 2*sum(flatten(Q)) / n
var = 4*sum([q*(1-q) for q in flatten(Q)]) / n**2
std = np.sqrt(var)
outfile.write("Expected degree observed : {:.3f} with variance {:.3f} and std_dev {:.3f}\n".format(expected_deg, var, std))
outfile.write("Expected degree estimated from real graph : {:.3f}\n".format(np.mean(G.degree())))


# ## 4. Compare real graph, oursin, cascade and Newman

# Get oursin graph.
print("Getting oursin and cascade graph...")
G_oursin = util.nxgraph_from_trace(trace_path, False, Author)
G_cascade = util.nxgraph_from_trace(trace_path, True, Author)


# Compare nb edges among all graphs.
print("Comparing nb of edges between graphs...")
outfile.write("Mean nb edges in Newman graph : ", 0.5*expected_deg*n, '\n')
outfile.write("Nb edges in oursin graph : ", G_oursin.number_of_edges(), '\n')
outfile.write("Nb edges in cascade graph : ", G_cascade.number_of_edges(), '\n')
outfile.write("Real nb edges : ", G.number_of_edges(), '\n')


# Compare proportion of common edges.
print("Comparing proportion of common edges between graphs...")

sample_in_real = list()
real_in_sample = list()
sample_in_oursin = list()
oursin_in_sample = list()
sample_in_cascade = list()
cascade_in_sample = list()

# edges lists
oursin_edges = set(G_oursin.edges)
cascade_edges = set(G_cascade.edges)
real_edges = set(G.edges)

for k in range(n_samples):
    
    # sample graph
    G_sample = nx.DiGraph()
    G_sample.add_nodes_from(set(Author.values()))
    for i in range(n):
        for j in range(n):
            if i in Q:
                if j in Q[i] and random.random() < Q[i][j]:
                    G_sample.add_edge(j,i)
    sample_edges = set(G_sample.edges)
            
    # compare edges in sample with real graph
    nb_common_edges = len(sample_edges.intersection(real_edges))
    sample_in_real = nb_common_edges / len(sample_edges)
    real_in_sample = nb_common_edges / len(real_edges)
    
    # compare edges in sample with oursin graph
    nb_common_edges = len(sample_edges.intersection(oursin_edges))
    sample_in_oursin = nb_common_edges / len(sample_edges)
    oursin_in_sample = nb_common_edges / len(oursin_edges)
    
    # compare edges in sample with cascade graph
    nb_common_edges = len(sample_edges.intersection(cascade_edges))
    sample_in_cascade = nb_common_edges / len(sample_edges)
    cascade_in_sample = nb_common_edges / len(cascade_edges)
    
# compare oursin and cascade with real
oursin_in_real = len(oursin_edges.intersection(real_edges)) / len(oursin_edges)
real_in_oursin = len(oursin_edges.intersection(real_edges)) / len(real_edges)
cascade_in_real = len(cascade_edges.intersection(real_edges)) / len(cascade_edges)
real_in_cascade = len(cascade_edges.intersection(real_edges)) / len(real_edges)
oursin_in_cascade = len(oursin_edges.intersection(cascade_edges)) / len(oursin_edges)
cascade_in_oursin = len(oursin_edges.intersection(cascade_edges)) / len(cascade_edges)

# print results
outfile.write("Mean prop of sample edges that are in real graph : ", np.mean(sample_in_real), '\n')
outfile.write("Mean prop of real edges that are in sample graph : ", np.mean(real_in_sample), '\n')
outfile.write('\n')
outfile.write("Mean prop of sample edges that are in oursin graph : ", np.mean(sample_in_oursin), '\n')
outfile.write("Mean prop of oursin edges that are in sample graph : ", np.mean(oursin_in_sample), '\n')
outfile.write('\n')
outfile.write("Mean prop of sample edges that are in cascade graph : ", np.mean(sample_in_cascade), '\n')
outfile.write("Mean prop of cascade edges that are in sample graph : ", np.mean(cascade_in_sample), '\n')
outfile.write('\n')
outfile.write("Prop of oursin edges that are in real graph : ", oursin_in_real, '\n')
outfile.write("Prop of real edges that are in oursin graph : ", real_in_oursin, '\n')
outfile.write('\n')
outfile.write("Prop of cascade edges that are in real graph : ", cascade_in_real, '\n')
outfile.write("Prop of real edges that are in cascade graph : ", real_in_cascade, '\n')
outfile.write('\n')
outfile.write("Prop of oursin edges that are in cascade graph : ", oursin_in_cascade, '\n')
outfile.write("Prop of cascade edges that are in oursin graph : ", cascade_in_oursin, '\n')

# close outfile
print("Done !")
outfile.close()