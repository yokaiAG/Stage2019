
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

# INIT
print("init...")
dataset = str(sys.argv[1])
adjList_path = str(sys.argv[2])
cascade = bool(int(sys.argv[3]))
save_news_wall = bool(int(sys.argv[4]))
ibegin = int(sys.argv[5])
iend = int(sys.argv[6])

print("Cascade : ", cascade)

# to compute psi only for the nb_best most influent users from emul
best_from_emul = bool(int(sys.argv[7]))
if best_from_emul:
    best_start = int(sys.argv[8])
    best_end = int(sys.argv[9])
    emul_path = str(sys.argv[10])
    # save id of best users from emul
    best_users_emul = set()
    for i,line in enumerate(open(emul_path)):
        if i < best_start:
            continue
        else:
            best_users_emul.add(int(line.split()[0]))
            if i >= best_end:
                break
    
# final arg: out path
out_path = str(sys.argv[11])

# Author dict creation if not RTU
if cascade:
    print("LastPublisher dict creation...")
else:
    print("Author dict creation...")
Author = util.get_authors(data_path)


# GET LAMBDAS MUS AND GRAPH
print("Getting lambdas and mus...")
Rtweet, Rrtweet, total_time = util.get_activity(data_path, cascade, Author, divide_by_time=True, retweeted=False)
print("Getting leaders and followers...")
LeadGraph, FollowGraph = util.graph_from_adjList(adjList_path)

# get common users between trace and real graph
# we remove users with 0 activity or 0 edges
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

# eliminate users that are not common between graph and twitter trace
Rtweet = { u: Rtweet[u] for u in common_users }
Rrtweet = { u: Rrtweet[u] for u in common_users }
LeadGraph = { u: LeadGraph[u].intersection(common_users) for u in common_users }
FollowGraph = { u: FollowGraph[u].intersection(common_users) for u in common_users }
del common_users

# list of users
Lusers = list(Rtweet.keys())
Lusers.sort()
N = len(Lusers)

# ## 3. Performance evaluation
# From the Linear System solution, one realises that it is necessary to first populate the matrices $A$ and $C$, which are relevant for any solution process of the system. 
# **Note** We will keep in memory Dictionaries, with Key the userid and value the list of positive matrix entries.


# ### Build matrix A in sparse format
def som_sparse(Lvec,Mvec,Lead):
    Som = dict()
    for user in Lvec:
        Som[user] = 0
        for leader in Lead[user]:
            Som[user]+=Lvec[leader]+Mvec[leader]
    return Som


# fill A function
@jit
def fill_A_sparse(Lvec,Mvec,Lead,Som):
    A = dict()
    # We consider that Lead[j] contains the set of leaders of node j.
    #
    for user in Lvec:
        A[user] = dict()
        for leader in Lead[user]:
            if Som[user] == 0:
                print("-- som--", user, Lead[user])
            A[user][leader] = Mvec[leader]/Som[user]
    return A


@jit
def fill_A_trans_sparse(Lvec,Mvec,Lead,Som):
    A_trans = dict()
    # A_trans is a dictionary. The keys are the columns of matrix form A. 
    # Each key shows the non-zero elements of A for this column.
    # We consider that Lead[j] contains the set of leaders of node j.
    #
    for user in Lvec:
        A_trans[user] = dict()
    for user in Lvec:
        for leader in Lead[user]:
            A_trans[leader][user] = Mvec[leader]/Som[user]
    return A_trans



# ### Build matrix C in sparse format
@jit
def fill_C_sparse(Lvec,Mvec):
    C = dict()
    for user in Lvec:
        C[user] = 0
        if Lvec[user]+Mvec[user]>0:
            C[user] = Mvec[user]/(Lvec[user]+Mvec[user])
    return C



# ### Build vectors b and d in sparse format
# We continue by including the column vectors $b_i$ and $d_i$, for a specific label $i$.
@jit
def fill_bi_sparse_v2(useri,Lvec,Som,Follow):
    b = dict()
    if useri not in Follow:
        b[useri] = 0
        return b
    for user in Follow[useri]:
        b[user] = Lvec[useri]/Som[user]
    return b


@jit
def fill_di_sparse_v2(useri,Lvec,Mvec):
    d = Lvec[useri]/(Lvec[useri]+Mvec[useri])
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
def pi_method_sparse_v2(N,useri,A,A_trans,Lvec,Lead,Follow,Som,it = 1000, eps = .001):
    # V2: This method resolves the fixed-point exploiting vector sparsity further.
    #
    bi = fill_bi_sparse_v2(useri,Lvec,Som,Follow)
    #
    # Initialisation (the result should be independent of initialisation vector)
    #
    p_new = bi
    p_old = dict()
    #
    normdiff = 2*eps
    #
    t = 0
    while (t<it) & (normdiff>eps):
        normdiff = 0
        p_old = p_new.copy()
        p_new = dict()
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




# The following function is the general iteration to derive the solution on the Walls, Newsfeeds and the metric of Influence \Psi, for all users i=1...N
@jit
def solution_sparse_v2(N,A,A_trans,C,Lvec,Mvec,Lead,Follow,Som,begin,end,fp,fq,fpsi,it = 1000, eps = .001):
    # The fixed point solution is slow because the fixed point needs to be 
    # calculated for each label i separately.
    #
    # Newsfeed & Wall
    pNews = dict()
    qWall = dict()
    # Influence metric
    Psi = dict()
    l=0  #just a counter (could be used for parallelization)
    for i in range(begin,end):
        user = Lusers[i]
        if best_from_emul:
            if user not in best_users_emul:
                continue
        sys.stdout.flush()
        sys.stdout.write("Computing p,q,PSi for user {} / {}...\r".format(l, end-begin))
        pNews[user] = pi_method_sparse_v2(N,user,A,A_trans,Lvec,Lead,Follow,Som)
        #
        di = fill_di_sparse_v2(user,Lvec,Mvec)
        qWall[user]=dict()
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
    #
    return (pNews,qWall,Psi)



# Calculation of the general input: dictionary Som and the three dictionaries A, A-trans, C for the matrices.
print("Computing A and C matrices...")
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
    qWall=dict()
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


# COMPUTE VALUES
print("Computing p, q and psi...")
if iend==-1:
    iend = N

fp = open(out_path + "pNews_%d_%d.txt" %(ibegin,iend), 'w')
fq = open(out_path + "qWall_%d_%d.txt" %(ibegin,iend), 'w')
fpsi = open(out_path + "Psi_model_%d_%d.txt" %(ibegin,iend), 'w')

(pNews_v2,qWall_v2,Psi_v2) = solution_sparse_v2(N,A,A_trans,C,Rtweet,Rrtweet,LeadGraph,FollowGraph,Som,ibegin,iend,fp,fq,fpsi)

fpsi.close()
fq.close()
fp.close()

print("\nSuccess !")