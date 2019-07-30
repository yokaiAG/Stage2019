"""
arg1 (string): psi emul path (ex: /home/vendeville/Stage2019/PsiResults/Psis/weibo_emul.txt)
arg2 (string): psi real path (ex: /home/vendeville/Stage2019/PsiResults/Psis/weibo_real_top10000emul.txt)
arg3 (string): psi star path (ex: /home/vendeville/Stage2019/PsiResults/Psis/weibo_oursin.txt)
arg4 (string): trace path (ex: /home/vendeville/Stage2019/Datasets/weibo_rtid.txt)
arg5 (string): adjcacency list path (ex: /home/vendeville/Stage2019/Datasets/weibo_adjList.txt)
arg6 (string): out_path (ex: /home/vendeville/Stage2019/DataAnalysis/weibo_).
        ---> outputed file: out_path + toptable.txt
arg7 (int): number of top users to consider.
"""

import sys
import util
from operator import itemgetter

psi_emul = str(sys.argv[1])
psi_real = str(sys.argv[2])
psi_star = str(sys.argv[3])
trace_path = str(sys.argv[4])
adjlist_path = str(sys.argv[5])
out_path = str(sys.argv[6])
k = int(sys.argv[7])

# load psis
Psi = {'emulator':dict(), 'real':dict(), 'star':dict()}

print("Loading psi real...")
for line in open(psi_real): # truegraph
    line = line.split()
    user, psi = int(line[0]), float(line[1])
    if psi>0:
        Psi['real'][user] = psi

print("Loading psi emul...")
for line in open(psi_emul): # emul
    line = line.split()
    user, psi = int(line[0]), float(line[1])
    if user in Psi['real']:
        Psi['emulator'][user] = psi

print("Loading psi star...")
for line in open(psi_star): # oursin
    line = line.split()
    user, psi = int(line[0]), float(line[1])
    if user in Psi['real']:
        Psi['star'][user] = psi
del user,psi

# load authors
print("Getting authors...")
Author = util.get_authors(trace_path)

# load activity
print("Getting activity...")
Lambda, Mu, total_time = util.get_activity(trace_path, False, Author, divide_by_time=True, retweeted=False)
del Mu, total_time
Lambda = {u:Lambda[u] for u in Psi['real']}

# load star graph
print("Getting follow graph (star)...")
FollowGraph = dict()
_ , FollowGraph['star'] = util.graph_from_trace(trace_path, False, Author)
del _, Author
FollowGraph['star'] = {u: {v for v in FollowGraph['star'][u] if v in Psi['real']} for u in Psi['real']}

# load real graph
print("Getting follow graph (real)...")
FollowGraph['real'] = dict()
for line in open(adjlist_path):
    line = line.split()
    lead, follow = int(line[0]), int(line[1])
    if lead in Psi['real'] and follow in Psi['real']:
        if lead in FollowGraph['real']:
            FollowGraph['real'][lead].add(follow)
        else:
            FollowGraph['real'][lead] = {follow}

# write table
print("Writing to out...")
out = open(out_path + "toptable.txt", "w")
i = 0
out.write("uid,psi_emul,psi_real,psi_star,rank_emul,rank_real,rank_star,outdeg_real,outdeg_star,lambda\n")
for user,psi_emul in sorted(Psi['emulator'].items(), key=itemgetter(1), reverse=True)[:k]:
    rank_emul = i+1
    psi_real = Psi['real'][user]
    psi_star = Psi['star'][user]
    rank_real = sorted(Psi['real'].items(), key=itemgetter(1), reverse=True).index((user,psi_real))+1
    rank_star = sorted(Psi['star'].items(), key=itemgetter(1), reverse=True).index((user,psi_star))+1
    out.write("{},{},{},{},{},{},{},{},{},{}\n".format(user, psi_emul, psi_real, psi_star, rank_emul, rank_real, rank_star, len(FollowGraph['real'][user]), len(FollowGraph['star'][user]),Lambda[user]))
    i += 1
out.close()

print("\nDone!")