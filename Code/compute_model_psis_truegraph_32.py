
# coding: utf-8

"""
Syntax : ~/anaconda3/bin/python3 clem-numba_allusers.py dataset cascade ibegin iend
with : dataset to choose between wcano, weibo_rtu, weibo_rtid, russian_rtu, russian_rtid, tdn10, tdn11
    cascade = 0 or 1
    iend = -1 if all users wanted
"""

# ## Implementation
#EXPLANATIONS:
#pi_method_sparse_v2 is the inner routine that calculates the iteration 
# n=1... for p(n+1)=Ap(n)+bi
#AND
#solution_sparse_v2 is the big loop that calculates influence on Newsfeed and
#Wall for all the users.


# IMPORTS 
import util
import math
import numpy as np
import sys
from numba import jit
from time import time

# for debugging
debug = open("debugging_weibo.txt", "w")


# INIT
debug.write("\n"); debug.write("init...")
data_path = str(sys.argv[1])
adjList_path = str(sys.argv[2])
cascade = bool(int(sys.argv[3]))
save_news_wall = bool(int(sys.argv[4]))
ibegin = int(sys.argv[5])
iend = int(sys.argv[6])
out_path = str(sys.argv[7])

debug.write("\n"); debug.write("Cascade : {}".format(cascade))

# to compute psi only for the nb_best most influent users from emul
best_from_emul = bool(int(sys.argv[8]))
if best_from_emul:
    best_start = int(sys.argv[9])
    best_end = int(sys.argv[10])
    emul_path = str(sys.argv[11])
    # save id of best users from emul
    best_users_emul = set()
    for i,line in enumerate(open(emul_path)):
        if i < best_start:
            continue
        else:
            best_users_emul.add(int(line.split()[0]))
            if i >= best_end:
                break

# Author dict creation if not RTU
if cascade:
    debug.write("\n"); debug.write("LastPublisher dict creation...")
else:
    debug.write("\n"); debug.write("Author dict creation...")
Author = util.get_authors(data_path)


# GET LAMBDAS MUS 
debug.write("\n"); debug.write("Getting lambdas and mus...")
start = time()
Rtweet, Rrtweet, total_time = util.get_activity(data_path, cascade, Author, divide_by_time=True, retweeted=False)
debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))

# get leaders followers
debug.write("\n"); debug.write("Getting leaders and followers...")
start = time()
LeadGraph, FollowGraph = util.graph_from_adjList(adjList_path)
debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))

# get common users between trace and real graph
# we remove users with 0 activity or 0 edges
debug.write("\n"); debug.write("Searching for common users...")
start = time()
common_users_old = set(Rtweet.keys()).intersection(set(LeadGraph.keys()))
common_users = set()
for u in common_users_old:
    if Rtweet[u]==0 and Rrtweet[u]==0:
        continue
    elif LeadGraph[u]==set() and FollowGraph[u]==set():
        continue
    else:
        common_users.add(u)
del common_users_old
debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))

# eliminate users that are not common between graph and twitter trace
debug.write("\n"); debug.write("Filtering common users...")
start = time()
Rtweet = { u: Rtweet[u] for u in common_users }
Rrtweet = { u: Rrtweet[u] for u in common_users }
LeadGraph = { u: LeadGraph[u].intersection(common_users) for u in common_users }
FollowGraph = { u: FollowGraph[u].intersection(common_users) for u in common_users }
del common_users
debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))

# list of users
Lusers = list(Rtweet.keys())
Lusers.sort()
N = len(Lusers)

# ## 3. Performance evaluation
# From the Linear System solution, one realises that it is necessary to first populate the matrices $A$ and $C$, which are relevant for any solution process of the system. 
# **Note** We will keep in memory Dictionaries, with Key the userid and value the list of positive matrix entries.


# ### Build matrix A in sparse format
def som_sparse(Lvec,Mvec,Lead):
    Som = {} 
    for user in Lvec:
        Som[user] = 0
        for leader in Lead[user]:
            Som[user] += np.float32(Lvec[leader]+Mvec[leader])
        Som[user] = np.float32(Som[user])
    return Som


# fill A function
@jit
def fill_A_sparse(Lvec,Mvec,Lead,Som):
    A = {}
    # We consider that Lead[j] contains the set of leaders of node j.
    #
    for user in Lvec:
        A[user] = {}
        for leader in Lead[user]:
            A[user][leader] = np.float32(Mvec[leader]/Som[user])
    return A


@jit
def fill_A_trans_sparse(Lvec,Mvec,Lead,Som):
    A_trans = {}
    # This is the A transpose that we will use also later.
    # A_trans is a dictionary. The keys are the columns of matrix form A. 
    # Each key shows the non-zero elements of A for this column.
    # We consider that Lead[j] contains the set of leaders of node j.
    #
    for user in Lvec:
        A_trans[user] = {}
    for user in Lvec:
        for leader in Lead[user]:
            A_trans[leader][user] = np.float32(Mvec[leader]/Som[user])
    return A_trans



# ### Build matrix C in sparse format
@jit
def fill_C_sparse(Lvec,Mvec):
    C = {}
    for user in Lvec:
        C[user] = 0
        if Lvec[user]+Mvec[user]>0:
            C[user] = np.float32(Mvec[user]/(Lvec[user]+Mvec[user]))
    return C



# ### Build vectors b and d in sparse format
# We continue by including the column vectors $b_i$ and $d_i$, for a specific label $i$.
@jit
def fill_bi_sparse_v2(useri,Lvec,Som,Follow):
    b = {}
    if useri not in Follow:
        b[useri] = 0
        return b
    for user in Follow[useri]:
        b[user] = np.float32(Lvec[useri]/Som[user])
    return b


@jit
def fill_di_sparse_v2(useri,Lvec,Mvec):
    d = np.float32(Lvec[useri]/(Lvec[useri]+Mvec[useri]))
    return d


# ## Solution
# After defining all matrices $A$, $C$ and vectors $b_i$, $d_i$ per label $i$ we can write down the main routine to find the fixed point.
# ** The method is based on the fixed point convergence**
# $p_i(t+1) = A.p_i(t) + b_i$, for $t\rightarrow\infty$.
# This should converge to $p_i$. Once it is found, the Wall steady-state can be calculated
# $q_i = C.p_i + d_i$.
# We first solve the fixed point for a specific label $i$.
# **Implementation Note:** We have decided to consider a sparse realisation. We choose for each user the initialisation p0 = bi, which is sparse and has a few positive entries. We identify in the matrix A, those lines who have at least one positive entry on the columns that coincide with the non-zero elements of bi. We further add as extra lines those that have positive entry in bi (due to addition) and have not been considered. In this way we reduce the number of lines and columns to be dealt with per iteration. The new vector p1 will probably have more positive entries than the previous one. 
# Hence V2 improves on the speed due to extra sparsity on bi_sparse_v2, and on the column/line multiplication.


@jit
def pi_method_sparse_v2(N,useri,A,A_trans,Lvec,Lead,Follow,Som,iter_infos, it = 1000, eps = .001):
    # v2: This method resolves the fixed-point exploiting vector sparsity.
    #
    debug.write("\n"); debug.write("fill bi sparse...")
    start = time()
    bi = fill_bi_sparse_v2(useri,Lvec,Som,Follow)
    debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))
    #
    # Initialisation (the result should be independent of initialisation vector)
    #
    p_new = bi
    p_old = {}
    #
    normdiff = np.float32(2*eps)
    #
    t = int(0)
    while (t<it) & (normdiff>eps):
        debug.write("\n"); debug.write("iteration #{}...".format(t+1))
        normdiff = np.float32(0)
        p_old = p_new.copy()
        p_new = {}
        # We search the lines of A which contain non-zero entries coinciding with the non-zero
        # entries of p_old.
        debug.write("\n"); debug.write("mlines...")
        start = time()
        mlines = set()
        for key in p_old:
            for tutu in A_trans[key]:
                mlines.add(tutu)
        debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))
            #mlines = mlines.union(set(A_trans[key].keys()))
        #debug.write("\n"); debug.write("p_old",p_old)
        debug.write("\n"); debug.write("tutu...")
        start = time()
        for tutu in bi:
            mlines.add(tutu)
        debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))
        #mlines = mlines.union(set(bi.keys()))
        #debug.write("\n"); debug.write("mlines",mlines)
        for user in mlines:
            p_new[user] = np.float32(0)
            debug.write("\n"); debug.write("for leader in Lead[user]...")
            start = time()
            for leader in Lead[user]:
                if leader in p_old:
                    p_new[user] += np.float32(A[user][leader]*p_old[leader])
            if user in bi.keys():
                p_new[user]+=np.float32(bi[user])
            debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))
            # Norm 1 criterion:
            #normdiff += abs(p_old[user]-p_new[user])
            # Norm INF criterion:
            debug.write("\n"); debug.write("if user in p_old keys...")
            start = time()
            if user in p_old.keys():
                if abs(p_old[user]-p_new[user])>normdiff:
                    normdiff = np.float32(abs(p_old[user]-p_new[user]))
            else:
                if abs(0-p_new[user])>normdiff:
                    normdiff = np.float32(abs(0-p_new[user]))
            debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))
        t += 1
        #Tracer()()
        #debug.write("\n"); debug.write("p_new",p_new)
    iter_infos.write("user {}: nb iter {}\n".format(useri,t))
    iter_infos.flush()
    #
    # debug.write("\n"); debug.write("t=",t,"\n")
    # debug.write("\n"); debug.write("diff_last=",normdiff,"\n")
    return p_new




# The following function is the general iteration to derive the solution on the Walls, Newsfeeds and the metric of Influence \Psi, for all users i=1...N
@jit
def solution_sparse_v2(N,A,A_trans,C,Lvec,Mvec,Lead,Follow,Som,begin,end,fp,fq,fpsi,iter_infos,it = 1000, eps = .001):
    # The fixed point solution is slow because the fixed point needs to be 
    # calculated for each label i separately.
    #
    # Newsfeed & Wall
    pNews = dict()
    qWall = dict()
    # Influence metric
    Psi = dict()
    l = 0 # counter
    for i in range(begin,end):
        user = Lusers[i]
        if best_from_emul:
            if user not in best_users_emul:
                continue
        sys.stdout.flush()
        sys.stdout.write("Computing p,q,Psi for user {} / {}...\r".format(l+1, end-begin))
        debug.write("\n"); debug.write("pi method sparse...")
        start = time()
        pNews[user] = pi_method_sparse_v2(N,user,A,A_trans,Lvec,Lead,Follow,Som,iter_infos)
        debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))
        #
        debug.write("\n"); debug.write("fill di sparse...")
        start = time()
        di = fill_di_sparse_v2(user,Lvec,Mvec)
        debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))
        qWall[user]=dict()
        Psi[user] = np.float32(0)
        debug.write("\n"); debug.write("for userj in pNews[user]...")
        start = time()
        for userj in pNews[user]:
            qWall[user][userj] = np.float32(C[userj]*pNews[user][userj])
            if userj==user:
                qWall[user][userj]+=np.float32(di)
            Psi[user] += np.float32(qWall[user][userj])
        debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))
        debug.write("\n"); debug.write("if user not in pNews[user]...")
        start = time()
        if user not in pNews[user]:
            qWall[user][user] = np.float32(di)
            Psi[user] += np.float32(qWall[user][user])
        Psi[user] = np.float32((Psi[user]-qWall[user][user])/(N-1))
        debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))
        #if command can be used to break the routine at l==1000 or some other number.
        #if l == 1000:
        #    return (pNews,qWall,Psi)
        debug.write("\n"); debug.write("save news wall...")
        start = time()
        if save_news_wall:
            fp.write("%d "%user)
            for news in pNews[user]:
                fp.write("%d %g "%(news,pNews[user][news]))
            fp.write("\n")
            fq.write("%d "%user)
            for wall in qWall[user]:
                fq.write("%d %g "%(wall,qWall[user][wall]))
            fq.write("\n")
            fp.flush()
            fq.flush()
        fpsi.write("%d %g\n"%(user,Psi[user]))
        fpsi.flush()
        l += 1 # up counter
        debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))
    #
    return (pNews,qWall,Psi)


# Calculation of the general input: dictionary Som and the three dictionaries A, A-trans, C for the matrices.
debug.write("\n"); debug.write("Computing Som...")
start = time()
Som = som_sparse(Rtweet,Rrtweet,LeadGraph)
debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))

debug.write("\n"); debug.write("Computing A...")
start = time()
A = fill_A_sparse(Rtweet,Rrtweet,LeadGraph,Som)
debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))

debug.write("\n"); debug.write("Computing A_trans...")
start = time()
A_trans = fill_A_trans_sparse(Rtweet,Rrtweet,LeadGraph,Som)
debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))

debug.write("\n"); debug.write("Computing C...")
start = time()
C = fill_C_sparse(Rtweet,Rrtweet)
debug.write("\n"); debug.write("Done in {:.3f}s.".format(time()-start))

# This routine just calculates the influence of a specific user on the Wall and Newsfeed of others as well as its Influence metric \Psi[user].
@jit
def user_influence_v2(user,N,A,A_trans,C,Lvec,Mvec,Lead,Follow,Som,it = 100, eps = .001):
    #
    pNews = pi_method_sparse_v2(N,user,A,A_trans,Lvec,Lead,Follow,Som,it,eps)
    #
    di = fill_di_sparse_v2(user,Lvec,Mvec)
    qWall=dict()
    PsiU = np.float32(0)
    for userj in pNews:
        qWall[userj] = np.float32(C[userj]*pNews[userj])
        if userj==user:
            qWall[userj]+= np.float32(di)
        PsiU += np.float32(qWall[userj])
    if user not in pNews:
        qWall[user] = np.float32(di)
        PsiU += np.float32(qWall[user])
    PsiU = np.float32((PsiU-qWall[user])/(N-1))

    return (qWall,PsiU)


# COMPUTE VALUES
debug.write("\n"); debug.write("Computing p, q and psi...")
if iend==-1:
    iend = N

fp = open(out_path + "pNews_%d_%d.txt" %(ibegin,iend), 'w')
fq = open(out_path + "qWall_%d_%d.txt" %(ibegin,iend), 'w')
fpsi = open(out_path + "Psi_model_%d_%d.txt" %(ibegin,iend), 'w')
iter_infos = open(out_path + "iter_infos.txt", 'w')

(pNews_v2,qWall_v2,Psi_v2) = solution_sparse_v2(N,A,A_trans,C,Rtweet,Rrtweet,LeadGraph,FollowGraph,Som,ibegin,iend,fp,fq,fpsi,iter_infos)

fpsi.close()
fq.close()
fp.close()
iter_infos.close()

debug.write("\n"); debug.write("\nSuccess !")