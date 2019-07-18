# coding: utf-8

# IMPORTS 
import util
import math
import numpy as np
import sys
from numba import jit

# INIT
out_path = str(sys.argv[1])
best_from_emul = bool(int(sys.argv[2]))
best_start = int(sys.argv[3])
best_end = int(sys.argv[4])
emul_path = str(sys.argv[5])

# save id of best users from emul
best_users_emul = set()
for i,line in enumerate(open(emul_path)):
    if i < best_start:
        continue
    else:
        best_users_emul.add(int(line.split()[0]))
        if i >= best_end:
            break

# get lambdas mus from txt file
print("Getting lambdas...")
Rtweet = dict()
for line in open("weibo_input/lambdas.txt"):
    line = line.split()
    Rtweet[int(line[0])] = float(line[1])
print("Getting mus...")
Rrtweet = dict()
for line in open("weibo_input/mus.txt"):
    line = line.split()
    Rrtweet[int(line[0])] = float(line[1])

# get leaders from txt file
print("Getting leaders...")
LeadGraph = dict()
for line in open("weibo_input/follow2lead.txt"):
    follow, lead = int(line.split()[0]), int(line.split()[1])
    if follow in LeadGraph:
        LeadGraph[follow].add(lead)
    else:
        LeadGraph[follow] = {lead}
for u in Rtweet:
    if u not in LeadGraph:
        LeadGraph[u] = set()

# get followers from txt file
print("Getting followers...")
FollowGraph = dict()
for line in open("weibo_input/follow2lead.txt"):
    follow, lead = int(line.split()[0]), int(line.split()[1])
    if lead in FollowGraph:
        FollowGraph[lead].add(follow)
    else:
        FollowGraph[lead] = {follow}
for u in Rtweet:
    if u not in FollowGraph:
        FollowGraph[u] = set()

# list of users
Lusers = list(Rtweet.keys())
Lusers.sort()
N = len(Lusers)

# ## 3. Performance evaluation
# From the Linear System solution, one realises that it is necessary to first populate the matrices $A$ and $C$, which are relevant for any solution process of the system. 
# **Note** We will keep in memory Dictionaries, with Key the userid and value the list of positive matrix entries.


# Som
def som_sparse(Lvec,Mvec,Lead):
    Som = {} 
    for user in Lvec:
        Som[user] = 0
        for leader in Lead[user]:
            Som[user] += np.float32(Lvec[leader]+Mvec[leader])
        Som[user] = np.float32(Som[user])
    return Som

# ### Build vectors b and d in sparse format
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
    print("ok 2.1")
    bi = fill_bi_sparse_v2(useri,Lvec,Som,Follow)
    print("ok 2.2")
    #
    # Initialisation (the result should be independent of initialisation vector)
    #
    p_new = bi
    print("ok 2.3")
    p_old = {}
    print("ok 2.4")
    #
    normdiff = np.float32(2*eps)
    print("ok 2.5")
    #
    t = int(0)
    print("ok 2.6")
    while (t<it) & (normdiff>eps):
        print("ok 2.6.1")
        normdiff = np.float32(0)
        print("ok 2.6.2")
        p_old = p_new.copy()
        print("ok 2.6.3")
        p_new = {}
        print("ok 2.6.4")
        # We search the lines of A which contain non-zero entries coinciding with the non-zero
        # entries of p_old.
        mlines = set()
        print("ok 2.6.5")
        for key in p_old:
            print("ok 2.6.5.1")
            for tutu in A_trans[key]:
                print("ok 2.6.5.1.1")
                mlines.add(tutu)
                print("ok 2.6.5.1.2")
            #mlines = mlines.union(set(A_trans[key].keys()))
        #print("p_old",p_old)
        print("ok 2.6.6")
        for tutu in bi:
            print("ok 2.6.6.1")
            mlines.add(tutu)
        #mlines = mlines.union(set(bi.keys()))
        #print("mlines",mlines)
        print("ok 2.6.7")
        for user in mlines:
            print("ok 2.6.7.1")
            p_new[user] = np.float32(0)
            print("ok 2.6.7.2")
            for leader in Lead[user]:
                print("ok 2.6.7.2.1")
                if leader in p_old:
                    print("ok 2.6.7.2.2")
                    p_new[user] += np.float32(A[user][leader]*p_old[leader])
                    print("ok 2.6.7.2.3")
                print("ok 2.6.7.2.4")
            if user in bi.keys():
                print("ok 2.6.7.2.5")
                p_new[user]+=np.float32(bi[user])
                print("ok 2.6.7.2.6")
            # Norm 1 criterion:
            #normdiff += abs(p_old[user]-p_new[user])
            # Norm INF criterion:
            print("ok 2.6.7.3")
            if user in p_old.keys():
                print("ok 2.6.4")
                if abs(p_old[user]-p_new[user])>normdiff:
                    print("ok 2.6.7.5")
                    normdiff = np.float32(abs(p_old[user]-p_new[user]))
                    print("ok 2.6.7.6")
            else:
                print("ok 2.6.7.7")
                if abs(0-p_new[user])>normdiff:
                    print("ok 2.6.7.8")
                    normdiff = np.float32(abs(0-p_new[user]))
                    print("ok 2.6.7.9")
        t += 1
        print("ok 2.6.7.10")
        #Tracer()()
        #print("p_new",p_new)
    iter_infos.write("user {}: nb iter {}\n".format(useri,t))
    iter_infos.flush()
    #
    # print("t=",t,"\n")
    # print("diff_last=",normdiff,"\n")
    return p_new




# The following function is the general iteration to derive the solution on the Walls, Newsfeeds and the metric of Influence \Psi, for all users i=1...N
@jit
def solution_sparse_v2(N,A,A_trans,C,Lvec,Mvec,Lead,Follow,Som,fpsi,iter_infos,it = 1000, eps = .001):
    # The fixed point solution is slow because the fixed point needs to be 
    # calculated for each label i separately.
    #
    # Newsfeed & Wall
    pNews = dict()
    qWall = dict()
    # Influence metric
    Psi = dict()
    l = 0 # counter
    for i in range(N):
        user = Lusers[i]
        if user not in best_users_emul:
            continue
        print("ok2")
        sys.stdout.flush()
        sys.stdout.write("Computing p,q,Psi for user {} / {}...\r".format(l+1, best_end - best_start))
        pNews[user] = pi_method_sparse_v2(N,user,A,A_trans,Lvec,Lead,Follow,Som,iter_infos)
        print("ok3")
        #
        di = fill_di_sparse_v2(user,Lvec,Mvec)
        print("ok4")
        qWall[user]=dict()
        print("ok5")
        Psi[user] = np.float32(0)
        print("ok6")
        for userj in pNews[user]:
            qWall[user][userj] = np.float32(C[userj]*pNews[user][userj])
            print("ok7")
            if userj==user:
                print("ok8")
                qWall[user][userj]+=np.float32(di)
                print("ok9")
            Psi[user] += np.float32(qWall[user][userj])
            print("ok9")
        if user not in pNews[user]:
            print("ok10")
            qWall[user][user] = np.float32(di)
            print("ok11")
            Psi[user] += np.float32(qWall[user][user])
            print("ok12")
        Psi[user] = np.float32((Psi[user]-qWall[user][user])/(N-1))
        print("ok13")
        #if command can be used to break the routine at l==1000 or some other number.
        #if l == 1000:
        #    return (pNews,qWall,Psi)
        fpsi.write("%d %g\n"%(user,Psi[user]))
        fpsi.flush()
        print("ok14")
        l += 1 # up counter
        print("ok15")
    #
    return (pNews,qWall,Psi)


# Calculation of the general input: dictionary Som and the three dictionaries A, A-trans, C for the matrices.
print("Getting Som...")
Som = dict()
for line in open("weibo_input/Som.txt"):
    line = line.split()
    Som[int(line[0])] = float(line[1])
print("Getting A...")
A = dict()
for line in open("weibo_input/A.txt"):
    line = line.split()
    A[int(line[0])] = dict()
    A[int(line[0])][int(line[1])] = float(line[2])
print("Getting A_trans...")
A_trans = dict()
for line in open("weibo_input/A_trans.txt"):
    line = line.split()
    A_trans[int(line[0])] = dict()
    A_trans[int(line[0])][int(line[1])] = float(line[2])
print("Getting C...")
C = dict()
for line in open("weibo_input/C.txt"):
    line = line.split()
    C[int(line[0])] = float(line[1])


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
print("Computing p, q and psi...")
fpsi = open(out_path + "Psi_model.txt", 'w')
iter_infos = open(out_path + "iter_infos.txt", 'w')

(pNews_v2,qWall_v2,Psi_v2) = solution_sparse_v2(N,A,A_trans,C,Rtweet,Rrtweet,LeadGraph,FollowGraph,Som,fpsi,iter_infos)

fpsi.close()
iter_infos.close()

print("\nSuccess !")