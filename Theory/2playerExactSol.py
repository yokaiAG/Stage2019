
# coding: utf-8

# In[1]:

import sys
import numpy as np
from sympy import *
import networkx as nx


# Choose $N, K$ and $M$. We compute $S$ = nb of states (=cardinal of state-space) and `users`=iterator over set of users.

# In[19]:


N = 2 # nb users
users = range(N)
K = int(sys.argv[1])
M = int(sys.argv[2])
S = (K+1)**2 * (M+1)**2


# Create $\lambda$s and $\mu$s.

# In[20]:


lambd = { 0:Symbol('La'), 1:Symbol('Lb')}
mu = { 0:Symbol('Ma'), 1:Symbol('Mb')}


# We define the transition rate from a state `start` to a state `end`.

# In[21]:


def transition_rate(start, end):

    # get init values of walls and newsfeeds
    w0, n0, w1, n1 = start[0], start[1], start[2], start[3]
    
    # movement
    z = list(np.array(end) - np.array(start))
    
    # case w0 +1
    if z == [1,0,0,0]:
        return (lambd[0] + mu[0]*n0/M) * (1-w0/K) * n1/M
    # case n1 +1
    elif z == [0,0,0,1]:
        return (lambd[0] + mu[0]*n0/M)  * w0/K * (1-n1/M)
    # case w0 +1 & n1 +1
    elif z == [1,0,0,1]:
        return (lambd[0] + mu[0]*n0/M) * (1-w0/K) * (1-n1/M)
    
    # case w0 -1
    elif z == [-1,0,0,0]:
        return mu[0] * (1-n0/M) * w0/K * (1-n1/M)
    # case n1 -1
    elif z == [0,0,0,-1]:
        return mu[0] * (1-n0/M) * (1-w0/K) * n1/M
    # case w0 -1 & n1 -1
    elif z == [-1,0,0,-1]:
        return mu[0] * (1-n0/M) * w0/K * n1/M
    
    # case w1 +1
    elif z == [0,0,1,0]:
        return mu[1] * n1/M * (1-w1/K) * n0/M
    # case n0 +1
    elif z == [0,1,0,0]:
        return mu[1] * n1/M * w1/K * (1-n0/M)
    # case w1 +1 & n0 +1
    elif z == [0,1,1,0]:
        return mu[1] * n1/M * (1-w1/K) * (1-n0/M)
        
    # case w1 -1
    elif z == [0,0,-1,0]:
        return (lambd[1] + mu[1]*(1-n1/M)) * w1/K * (1-n0/M)
    # case n0 -1
    elif z == [0,-1,0,0]:
        return (lambd[1] + mu[1]*(1-n1/M)) * (1-w1/K) * n0/M
    # case w1 -1
    elif z == [0,-1,-1,0]:
        return (lambd[1] + mu[1]*(1-n1/M)) * w1/K * n0/M
        
    # otherwise rate=0
    else:
        return 0


# Create $Q$ (rate matrix). Make a copy as $Q_{theo}$ to keep original expressions.

# In[22]:


Q = list()
for k1 in range(K+1):
    for k2 in range(M+1):
        for m2 in range(K+1):
            for m1 in range(M+1):
                Q.append(list())
                for k1_ in range(K+1):
                    for k2_ in range(M+1):
                        for m2_ in range(K+1):
                            for m1_ in range(M+1):
                                Q[-1].append(Symbol('q_%d%d%d%d^%d%d%d%d'%(k1, m1, k2, m2, k1_, m1_, k2_, m2_)))
Q = Matrix(Q)
Q_theo = Matrix(Q)


# Fill $Q$ matrix with transition rates.

# In[23]:


# iterate over Q matrix
for i in range(S):
    for j in range(S):
    
        # x=start, y=end
        x = [ int(xi) for xi in Q[i,j].name[2:6] ]
        y = [ int(yi) for yi in Q[i,j].name[-4:] ]

        # compute transition rate
        expr = transition_rate(x, y)
    
        # put new value in Q
        Q[i,j] = simplify(expr)
        
# now add diagonal values
for i in range(S):
    Q[i,i] = simplify(-sum(Q[i,:]))


# In[24]:



# Create $U$ (vector of stationary probability).

# In[25]:


U = list()    
for k1 in range(K+1):
    for k2 in range(M+1):
        for m2 in range(K+1):
            for m1 in range(M+1):
                U.append(Symbol('Pi_%d%d%d%d'%(k1, m1, k2, m2)))
# U = Matrix([U])

print(U)
# In[26]:


U


# Define $Q_{aug}$ as $Q^T$ with row $(1, ...,1)$ added at the end, and $b=(0,...,0,1)^T$ so that we can resolve $Q_{aug}U^T=b$ (equivalent $UQ_{aug}=b$) instead of $\left\{UQ=0, Ue=1\right\}$. 

# **Important :** $Q$ is overranked so we delete $Q_{aug}$'s first line and the first line of $b$.

# In[27]:


Q_aug = Q.T[1:,:]
Q_aug = Q_aug.row_insert(S-1, Matrix([[1]*S]))
b = Matrix([0]*S + [1])
b = b[1:,:]


# Solve $Q_{aug}U^T=b$.

# In[ ]:


sol = linsolve((Q_aug, b), U)


# In[ ]:

out = open("2playersol_K{}M{}.txt".format(K,M), "w")
for S in sol:
    for i,s in enumerate(list(sol)[0]):
        # print(U[i], s)
        out.write("{} : {}\n".format(U[i], simplify(s)))
    out.write("\n\n\n")
out.close()

sys.exit()

# ## Graphe

# In[110]:


G = nx.DiGraph()


# In[111]:


for i in range(Q_theo.shape[0]):
    for j in range(Q_theo.shape[1]):
        if Q[i,j] != 0:
            u = Q_theo[i,j].name[2:6]
            v = Q_theo[i,j].name[-4:]
            weight = Q[i,j]
            G.add_edge(u, v, weight=weight)


# In[115]:


for scc in nx.strongly_connected_components(G):
    print(scc)


# In[68]:


edge_labels = { e: G.edges[e]['weight'] for e in G.edges }
pos = nx.shell_layout(G)
nx.draw_networkx_nodes(G, pos)
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
nx.draw_networkx_labels(G, pos)


# In[20]:


nx.is_strongly_connected(G)

