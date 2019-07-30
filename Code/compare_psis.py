
# coding: utf-8

"""
arg1 (string): psi emul path (ex: /home/vendeville/Stage2019/PsiResults/Psis/weibo_emul.txt)
arg2 (string): psi model path (ex: /home/vendeville/Stage2019/PsiResults/Psis/weibo_oursin.txt)
arg3 (string): outfile. where to write results (ex: /home/vendeville/Stage2019/PsiResults/ComparePsis/weibo_emul_oursin.txt).
arg4 (int 0 ou 1): do you want to consider only the first n users according to psi_emul? 0=no, 1=yes.
    --->arg5 (int) (only if arg4=1): number of top users to consider
"""

import sys
from time import time
import pandas as pd
import numpy as np
from operator import itemgetter
from scipy.stats import kendalltau


# Où sont les listes de psis ?
psiemul = str(sys.argv[1])
psimodel = str(sys.argv[2])
outfile = str(sys.argv[3]) # filename to write results
only_first_n_emul_users = bool(int(sys.argv[4]))
if only_first_n_emul_users:
    n_emul_users = int(sys.argv[5])



# On construit
# - `Psi` : dictionnaire des influences. Clés : users id, valeurs : [psi_emul, psi_model]
# - `emul` : les influences données par l'émulateur, par ordre décroissant
# - `model_sortby_emul` : les influences données par le modèle, triées selon l'ordre de `psi_emul`
# - `model` : les influences données par le modèle, par ordre décroissant.

# In[24]:


print("Chargement des Psis...")
Psi = dict()

start = time()

# emul
with open(psiemul) as psi_list:
    for i,line in enumerate(psi_list):
        if only_first_n_emul_users:
            if i == n_emul_users:
                break
        line = line.split()
        current_user = int(line[0])
        current_psi = float(line[1])
        if current_psi==0:
            continue
        Psi[current_user] = [current_psi, 0]

# model
with open(psimodel) as psi_list:
    for i,line in enumerate(psi_list):
        line = line.split()
        current_user = int(line[0])
        current_psi = float(line[1])
        # if current_psi==0:
        #     continue
        # if only_first_n_emul_users and current_user not in Psi:
        #     continue
        if current_user in Psi.keys():
            Psi[current_user][-1] = current_psi
        # else:
        #     Psi[current_user] = [0, current_psi]
        
            
# to arrays
emul = np.array([p[0] for p in Psi.values()])
model_sortby_emul = np.array([p[1] for p in Psi.values()])
model = - np.sort(-model_sortby_emul)

        
print("Tps ex : ", time()-start)


# I
# n[8]:

# save len emul
N = len(emul)
del line, current_user, current_psi, psi_list


# ## Dataframe pour comparaison

# On va comparer l'ordre des 2 listes : kendall tau, distance moyenne, proportion d'utilisateurs communs. On crée un dataframe pour enregistrer les résultats.

# In[34]:


print("Creation dataframe...")

df = pd.DataFrame(columns=['N', 'min_psi_emul', 'min_psi_model', 'kendall', 'mean_dist', 'common_users_prop'])
df['N'] = range(2, N+1)
df['min_psi_emul'] = emul[1:N]
df['min_psi_model'] = model[1:N]


# In[35]:


df.head()


# ## Kendall $\tau$

# On calcule maintenant les kendall tau.

# In[ ]:


print("Kendall tau...")
kendall_tau = list()

start = time()
for i in range(2, N+1):
    sys.stdout.flush()
    sys.stdout.write("step {}... elapsed time {:.3f}\r".format(i, time()-start))
    kendall_tau.append(kendalltau(emul[:i], model_sortby_emul[:i])[0])

df['kendall'] = kendall_tau

print("Tps ex : ", time()-start)


del i, kendall_tau


# ## Mean distance

# Compute ranks for emul.

# In[24]:


print("Mean distance...")

rank_emul = dict()
current_rank = 0
current_psi = 0

# pour chaque user on compare psi emul avec current psi et on update current rank si >
# ensuite on ajoute current rank à rank emul
for user, psi in sorted(Psi.items(), key=lambda x: x[1][0]):
    psi = psi[0] # car psi=[psi_emul,psi model]
    if psi > current_psi:
        current_rank += 1
    rank_emul[user] = current_rank
    current_psi = psi


# Compute ranks for model.

# In[25]:


rank_model = dict()
current_rank = 0
current_psi = 0

# pour chaque user on compare psi model avec current psi et on update current rank si >
# ensuite on ajoute current rank à rank model
for user, psi in sorted(Psi.items(), key=lambda x: x[1][1]):
    psi = psi[1] # car psi=[psi_emul,psi model]
    if psi > current_psi:
        current_rank += 1
    rank_model[user] = current_rank
    current_psi = psi


# In[26]:


del psi, current_rank, current_psi


# Compute mean distance.

# In[27]:


# first compute distance per user
dist = list()
for user, rank in sorted(rank_emul.items(), key=itemgetter(1), reverse=True)[:N]:
    dist.append(np.abs(rank - rank_model[user]))
    
# then sums of distances
mean_dist = [ dist[0] + dist[1] ]
for d in dist[2:]:
    mean_dist.append(mean_dist[-1] + d)
    
# finally divide for mean distances
for k in range(len(mean_dist)):
    mean_dist[k] /= k+2

# add to df
df['mean_dist'] = mean_dist


# In[28]:


del user, rank, d, k, dist, mean_dist


# ## Common users proportion

# In[39]:


print("Common users proportion...")

start = time()

# les liste d'utilisateurs triés par psi décroissant (emul ou model) 
# /!\ pas le même ordre
users_emul = [ user for user,psi in sorted(rank_emul.items(), key=itemgetter(1), reverse=True) ]
users_model = [ user for user,psi in sorted(rank_model.items(), key=itemgetter(1), reverse=True) ]

# les users qu'on a vu (on commence avec les 2 premiers), emul et model
seen_users_emul = set(users_emul[:2])
seen_users_model = set(users_model[:2])

# la taille de l'intersection courante et liste des proportions d'users communs
current_intersect = len(seen_users_emul.intersection(seen_users_model))
common_users_prop = [ current_intersect / len(seen_users_emul) ]


# on parcourt les users
for n in range(2, N):
    
    # le psi emul et model
    current_user_emul = users_emul[n]
    current_user_model = users_model[n]
    
    # si les 2 users sont les mêmes alors ils sont jamais vu et intersect+1 et users_seen+1
    if current_user_emul == current_user_model:
        current_intersect += 1
        
    # sinon
    else:
        
        # si le user_emul a déjà été vu dans model ou pas
        if current_user_emul in seen_users_model:
            current_intersect += 1
        
        # si le user model a déjà été vu dans emul ou pas
        if current_user_model in seen_users_emul:
            current_intersect += 1
    
    # on update les listes
    seen_users_emul.add(current_user_emul)
    seen_users_model.add(current_user_model)
    common_users_prop.append(current_intersect / len(seen_users_emul))

    
print("Tps ex : ", time()-start)

# update df and del vars
df['common_users_prop'] = common_users_prop
del n, common_users_prop, seen_users_emul, seen_users_model, current_intersect


# ## Export dataframe
print("Exporting dataframe...")
df.to_csv(outfile, sep=",", index=False)