
# coding: utf-8

# # Online Social Platform

# ### November 2018 - Update for large Data Sets

# ### Code related to the INFOCOM submission: "Performance Analysis of Online Social Platforms"

# We analyse the influence of users in a generic online social platform. 
# 
# In such platform, there are $N$ users in total. Each user $n$ is considered as a virtual node and has a Newsfeed and a Wall. Suppose the Newsfeed of size $M$ and the Wall of size $K$. Furthermore, each user has a set of leaders, $L^{(n)}$, and he/she can be the leader of others. The Newsfeed of $n$ is refreshed instantaneously with posts published on the Walls of his Leaders. The user visits his Newsfeed and chooses among the currently available posts to re-post on his own Wall with rate $\mu^{(n)}\geq 0$ [posts/unit-time]. Additionally, he produces own posts on his Wall with rate $\lambda^{(n)}\geq 0$. These posts are marked on their production by the user-author index $(n)$.

# **Assumptions:** The choice of which post to share on one's Wall and which post to evict when a new post arrives is uniformly random, among the present posts on the Wall and the Newsfeed. Also, both post-feed processes per user are assumed Poisson.

# Consider a particular user $i$. The steady-state probability to find posts from user $i$ on the Newsfeed and Wall of user $n$ is the tuple $(p_i^{(n)},q_i^{(n)})$. With this, we form the steady state column-vectors
# 
# $Pvec(i):=(Pvec(1,i),\ldots,Pvec(N,i))=(p_i^{(1)},\ldots,p_i^{(n)})$, and
# 
# $Qvec(i):=(Qvec(1,i),\ldots,Qvec(N,i))=(q_i^{(1)},\ldots,q_i^{(n)})$.
# 
# These are the steady-state vectors for posts of origin $(i)$ on all the Newsfeeds and Walls of users. 

# ### Linear System solution

# To find the values of the steady-state vectors $Pvec(i)$ and Qvec(i), one needs to solve the following linear system:
# 
#     (1) Pvec(i) = A.Pvec(i) + b(i)
# 
#     (2) Qvec(i) = C.Pvec(i) + d(i).
# 
# In the above $A$, $C$ are $N\times N$ matrices and $b(i)$, $d(i)$ are $N\times 1$ column vectors.

# $A(j,k) = \frac{\mu^{(k)}}{\sum_{\ell\in L^{(j)}}\lambda^{(\ell)}+\mu^{(\ell)}}\mathbf{1}(k\in L^{(j)})$,
# 
# $b(j,i) = \frac{\lambda^{(i)}}{\sum_{\ell\in L^{(j)}}\lambda^{(\ell)}+\mu^{(\ell)}}\mathbf{1}(i\in L^{(j)})$,
# 
# $C(j,i) = \frac{\mu^{(j)}}{\lambda^{(j)}+\mu^{(j)}}\mathbf{1}(j==i)$,
# 
# $d(j,i) = \frac{\lambda^{(i)}}{\lambda^{(i)}+\mu^{(i)}}\mathbf{1}(j==i)$.

# ## Implementation


#EXPLANATIONS:


#pi_method_sparse_v2 is the inner routine that calculates the iteration 
# n=1... for p(n+1)=Ap(n)+bi
#AND
#solution_sparse_v2 is the big loop that calculates influence on Newsfeed and
#Wall for all the users.
#
# In[1]:


# get_ipython().run_line_magic('pylab', 'inline')
import math
import numpy as np
# import networkx as nx
import gzip
import sys
from numba import jit

if len(sys.argv) != 4:
    print("mauvais nombre d'arguments")
    sys.exit(-1)

ibegin=int(sys.argv[1])
iend=int(sys.argv[2])
datafile=str(sys.argv[3])

datashort="Wcano"
directory = "/Users/Fishbone/Desktop/NEWSFEEDfresh/PYTHON/Emulator/"
f = gzip.open(datafile)
Author = {}
for lign in f:
    lign = lign.split()
    tweetid = int(lign[0])
    userid = int(lign[2])
    Author[tweetid] = userid
f.close()


# In[9]:


Ntweet = {}
Nrtweet = {}
LeadGraph = {}
FollowGraph = {}
FirstT = None
LastT = None
f = gzip.open(datafile)
for lign in f:
    lign = lign.split()
    tstamp = int(lign[1])
    userid = int(lign[2])
    rtid = int(lign[3])
    if FirstT == None:
        FirstT = tstamp
    if userid not in Ntweet:
        Ntweet[userid] = 0
        Nrtweet[userid] = 0
        LeadGraph[userid] = set()
        
    if rtid == -1:
        Ntweet[userid] += 1
    else: 
        Nrtweet[userid] += 1
        if rtid in Author:
            LeadGraph[userid].add(Author[rtid])
            if Author[rtid] not in FollowGraph:
                FollowGraph[Author[rtid]] = set()
            FollowGraph[Author[rtid]].add(userid)
LastT = tstamp
f.close()


# From the input we derive the posting and re-posting estimated rates (Rtweet, Rrtweet)

# In[10]:


Rtweet = {}
Rrtweet = {}
for user in Ntweet:
    Rtweet[user] = Ntweet[user]/(LastT-FirstT)
    Rrtweet[user] = Nrtweet[user]/(LastT-FirstT)

Lusers = list(Rtweet.keys())
Lusers.sort()

# Map user to a dictionary for Reference:

# In[11]:


Userlist = {}
k=0
for user in Rtweet:
    Userlist[k] = user
    k+=1


# In[13]:


#print(Userlist[10010])


# Size of the Data Sample is N

# In[12]:


N = len(Userlist)
# print(N)


# Some test calculations

# In[13]:


#print(LeadGraph[Userlist[10010]])


# In[14]:


#for k in range(10):
#    print(Userlist[k])


# In[15]:


#print(Rtweet[790])
#print(Rtweet[Userlist[1]])
#print(Userlist[1])


# In[16]:


#print(Userlist[10010])
#print(LeadGraph[Userlist[10010]])
#print(Userlist[10010] in FollowGraph[1280])


# In[17]:


#FollowGraph[205]


# In[18]:


#FollowGraph[5234901]


# ## 3. Performance evaluation

# From the Linear System solution, one realises that it is necessary to first populate the matrices $A$ and $C$, which are relevant for any solution process of the system. 
# 
# **Note** We will keep in memory Dictionaries, with Key the userid and value the list of positive matrix entries.

# ### Build matrix A in sparse format

# In[19]:


def som_sparse(Lvec,Mvec,Lead):
    Som = {} 
    for user in Lvec:
        Som[user] = 0
        for leader in Lead[user]:
            Som[user]+=Lvec[leader]+Mvec[leader]
    return Som


# In[20]:


#SomS = som_sparse(RtweetS,RrtweetS,LeadGraphS) #SomS are the sums for the grid test


# In[21]:

@jit
def fill_A_sparse(Lvec,Mvec,Lead,Som):
    A = {}
    # We consider that Lead[j] contains the set of leaders of node j.
    #
    for user in Lvec:
        A[user] = {}
        for leader in Lead[user]:
            if Som[user] == 0:
                print("-- som--", user, Lead[user])
            A[user][leader] = Mvec[leader]/Som[user]
    return A


# In[22]:


#AS = fill_A_sparse(RtweetS,RrtweetS,LeadGraphS,SomS) #AS is the A matrix for the grid test


# In[23]:


#for user in RtweetS:
#    print(user, AS[user])


# In[24]:

@jit
def fill_A_trans_sparse(Lvec,Mvec,Lead,Som):
    A_trans = {}
    # A_trans is a dictionary. The keys are the columns of matrix form A. 
    # Each key shows the non-zero elements of A for this column.
    # We consider that Lead[j] contains the set of leaders of node j.
    #
    for user in Lvec:
        A_trans[user] = {}
    for user in Lvec:
        for leader in Lead[user]:
            A_trans[leader][user] = Mvec[leader]/Som[user]
    return A_trans


# In[25]:


#A_transS = fill_A_trans_sparse(RtweetS,RrtweetS,LeadGraphS,SomS) #A_transS is the A transpose for the grid test


# In[26]:


#for user in RtweetS:
#    print(user, A_transS[user])


# ### Build matrix C in sparse format

# In[27]:

@jit
def fill_C_sparse(Lvec,Mvec):
    C = {}
    for user in Lvec:
        C[user] = 0
        if Lvec[user]+Mvec[user]>0:
            C[user] = Mvec[user]/(Lvec[user]+Mvec[user])
    return C


# In[28]:


#CS = fill_C_sparse(RtweetS,RrtweetS)
#print(CS)


# In[29]:


#for j in range(NS):
#    k = UserlistS[j]
#    print(k, CS[k])


# ### Build vectors b and d in sparse format

# We continue by including the column vectors $b_i$ and $d_i$, for a specific label $i$.

# In[30]:

@jit
def fill_bi_sparse_v2(useri,Lvec,Som,Follow):
    b = {}
    if useri not in Follow:
        b[useri] = 0
        return b
    for user in Follow[useri]:
        b[user] = Lvec[useri]/Som[user]
    return b


# In[31]:


#biS_v2 = fill_bi_sparse_v2(UserlistS[0],RtweetS,SomS,FollowGraphS) #biS_v2 is the bi entries of grid (v2 refers to the accelerated method)
#print(biS_v2)


# In[32]:
@jit
def fill_di_sparse_v2(useri,Lvec,Mvec):
    d = Lvec[useri]/(Lvec[useri]+Mvec[useri])
    return d


# In[33]:


#diS_v2 = fill_di_sparse_v2(UserlistS[0],RtweetS,RrtweetS) #diS_v2 is the di entries of grid (v2 refers to the accelerated method)
#print(UserlistS[0], diS_v2)


# ## Solution

# After defining all matrices $A$, $C$ and vectors $b_i$, $d_i$ per label $i$ we can write down the main routine to find the fixed point.

# ** The method is based on the fixed point convergence**
# 
# $p_i(t+1) = A.p_i(t) + b_i$, for $t\rightarrow\infty$.
# 
# This should converge to $p_i$. Once it is found, the Wall steady-state can be calculated
# 
# $q_i = C.p_i + d_i$.
# 
# We first solve the fixed point for a specific label $i$.

# **Implementation Note:** We have decided to consider a sparse realisation. We choose for each user the initialisation p0 = bi, which is sparse and has a few positive entries. We identify in the matrix A, those lines who have at least one positive entry on the columns that coincide with the non-zero elements of bi. We further add as extra lines those that have positive entry in bi (due to addition) and have not been considered. In this way we reduce the number of lines and columns to be dealt with per iteration. The new vector p1 will probably have more positive entries than the previous one. 

# Hence V2 improves on the speed due to extra sparsity on bi_sparse_v2, and on the column/line multiplication.

# In[34]:

@jit
def pi_method_sparse_v2(N,useri,A,A_trans,Lvec,Lead,Follow,Som,it = 1000, eps = .001):
    # V2: This method resolves the fixed-point exploiting vector sparsity further.
    #
    bi = fill_bi_sparse_v2(useri,Lvec,Som,Follow)
    #
    # Initialisation (the result should be independent of initialisation vector)
    #
    p_new = bi
    p_old = {}
    #
    normdiff = 2*eps
    #
    t = 0
    while (t<it) & (normdiff>eps):
        normdiff = 0
        p_old = p_new.copy()
        p_new = {}
        # We search the lines of A which contain non-zero entries coinciding with the non-zero
        # entries of p_old.
        mlines = set()
        for key in p_old:
            for tutu in A_trans[key]:
                mlines.add(tutu)
            #mlines = mlines.union(set(A_trans[key].keys()))
        #print("p_old",p_old)
        for tutu in bi:
            mlines.add(tutu)
        #mlines = mlines.union(set(bi.keys()))
        #print("mlines",mlines)
        for user in mlines:
            p_new[user] = 0
            for leader in Lead[user]:
                if leader in p_old:
                    p_new[user] += A[user][leader]*p_old[leader]
            if user in bi:
                p_new[user]+=bi[user]
            # Norm 1 criterion:
            #normdiff += abs(p_old[user]-p_new[user])
            # Norm INF criterion:
            if user in p_old:
                if abs(p_old[user]-p_new[user])>normdiff:
                    normdiff = abs(p_old[user]-p_new[user])
            else:
                if abs(0-p_new[user])>normdiff:
                    normdiff = abs(0-p_new[user])
        t += 1
        #Tracer()()
        #print("p_new",p_new)
    #
    # print("t=",t,"\n")
    # print("diff_last=",normdiff,"\n")
    return p_new



# In[35]:


#pi_end_v2 = pi_method_sparse_v2(NS,UserlistS[0],AS,A_transS,RtweetS,LeadGraphS,FollowGraphS,SomS)
#print(pi_end_v2)


# In[36]:


#sum2 = 0
#for user in RtweetS:
#    sum2 += pi_end_v2[user]
#print(sum2)


# The following function is the general iteration to derive the solution on the Walls, Newsfeeds and the metric of Influence \Psi, for all users i=1...N

# In[37]:

@jit
def solution_sparse_v2(N,A,A_trans,C,Lvec,Mvec,Lead,Follow,Som,begin, end,fp,fq,fpsi,it = 1000, eps = .001):
    # The fixed point solution is slow because the fixed point needs to be 
    # calculated for each label i separately.
    #
    # Newsfeed & Wall
    pNews = {}
    qWall = {}
    # Influence metric
    Psi = {}
    l=0  #just a counter (could be used for parallelization)
    for i in range(begin, end+1):
        user = Lusers[i]
        # print(l)
        pNews[user] = pi_method_sparse_v2(N,user,A,A_trans,Lvec,Lead,Follow,Som)
        #
        di = fill_di_sparse_v2(user,Lvec,Mvec)
        qWall[user]={}
        Psi[user] =0
        for userj in pNews[user]:
            qWall[user][userj] = C[userj]*pNews[user][userj]
            if userj==user:
                qWall[user][userj]+=di
            Psi[user] += qWall[user][userj]
        if user not in pNews[user]:
            qWall[user][user] = di
            Psi[user] += qWall[user][user]
        Psi[user] = (Psi[user]-qWall[user][user])/(N-1)
        l+=1
        #if command can be used to break the routine at l==1000 or some other number.
        #if l == 1000:
        #    return (pNews,qWall,Psi)
        fp.write("%d "%user)
        for news in pNews[user]:
            fp.write("%d %g "%(news,pNews[user][news]))
        fp.write("\n")
        fq.write("%d "%user)
        for wall in qWall[user]:
            fq.write("%d %g "%(wall,qWall[user][wall]))
        fq.write("\n")
        fpsi.write("%d %g\n"%(user,Psi[user]))
        fp.flush()
        fq.flush()
        fpsi.flush()
    #
    return (pNews,qWall,Psi)





# Calculation of the general input: dictionary Som and the three dictionaries A, A-trans, C for the matrices.


Som = som_sparse(Rtweet,Rrtweet,LeadGraph)
A = fill_A_sparse(Rtweet,Rrtweet,LeadGraph,Som)
A_trans = fill_A_trans_sparse(Rtweet,Rrtweet,LeadGraph,Som)
C = fill_C_sparse(Rtweet,Rrtweet)



# This routine just calculates the influence of a specific user on the Wall and Newsfeed of others as well as its Influence metric \Psi[user].


@jit
def user_influence_v2(user,N,A,A_trans,C,Lvec,Mvec,Lead,Follow,Som,it = 100, eps = .001):
    #
    pNews = pi_method_sparse_v2(N,user,A,A_trans,Lvec,Lead,Follow,Som,it,eps)
    #
    di = fill_di_sparse_v2(user,Lvec,Mvec)
    qWall={}
    PsiU =0
    for userj in pNews:
        qWall[userj] = C[userj]*pNews[userj]
        if userj==user:
            qWall[userj]+=di
        PsiU += qWall[userj]
    if user not in pNews:
        qWall[user] = di
        PsiU += qWall[user]
    PsiU = (PsiU-qWall[user])/(N-1)

    return (qWall,PsiU)


# Importing time to calculate the time of each run.

# In[44]:


import time




fp = open("%s.pNews.%d.%d"%(datashort,ibegin,iend), 'w')
fq = open("%s.qWall.%d.%d"%(datashort,ibegin,iend), 'w')
fpsi = open("%s.Psi.%d.%d"%(datashort,ibegin,iend), 'w')

(pNews_v2,qWall_v2,Psi_v2) = solution_sparse_v2(N,A,A_trans,C,Rtweet,Rrtweet,LeadGraph,FollowGraph,Som,ibegin,iend,fp,fq,fpsi)

fpsi.close()
fq.close()
fp.close()

# In[ ]:


#endT_big = time.time()
#elapsed_time = endT_big-startT_big
#print(elapsed_time,'\n')


# Print the results to output files.

# In[75]:


#fresQ=open("/Users/Fishbone/Desktop/NEWSFEEDfresh/PYTHON/Analysis/RESULTwall.txt","w")
#print(qWall_v2,"\n",file=fresQ)
#fresQ.close()

#
#fresN=open("/Users/Fishbone/Desktop/NEWSFEEDfresh/PYTHON/Analysis/RESULTnews.txt","w")
#print(pNews_v2,"\n",file=fresN)
#fresN.close()

#fresP=open("/Users/Fishbone/Desktop/NEWSFEEDfresh/PYTHON/Analysis/RESULTpsi.txt","w")
#print(Psi_v2,"\n",file=fresP)
#fresP.close()


