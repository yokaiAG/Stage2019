# Stage2019

This repository contains files used during my internship. You will find an exact copy of this repository on khiva at /home/vendeville/Stage2019/. The latter also contains the datasets. They are not uploaded on github due to their  very large size. Do not remove `.gitignore` files, otherwise github might try to upload too large files such as the datasets, which will cause complications :)

## Overview
- DataAnalysis: some stats on the datasets.
- Code: contains all python codes and jupyter notebooks.
- PsiResults: results on the different datasets (psi model, psi emul, and comparisons between them). Also contains plots used for the journal and the internship report.

First I introduce the datasets, available on khiva at /home/vendeville/Stage2019/Datasets/.


## Datasets
You will find those on khiva at /home/vendeville/Stage2019/Datasets/.
- `wcano_rtid.txt` twitter trace for wcano (twid ts uid rtid). Exactly as you provided it to me at the beginning of the internship (i.e. the end of the trace has been cut because no retweets)
- `russian_rtid.txt` twitter trace for russian (twid ts uid rtid).
- `weibo_rtid.txt` trace for weibo (twid ts uid rtid).
- `weibo_adjList.txt` complete adjacency list for weibo's real graph. Each line is: leader_id follower_id.
- `weibo_filtered_adjList.txt` adjacency list for weibo's real graph except users that are not present in the trace have been excluded. This is the one to use when computing the model psis.


## DataAnalysis
The names of the folders and files pretty much speak for themselves. Generally for each dataset you will find statistics about the distribution of lambda,mu and the graph structure (for star, cascade).


## Code

### Python files (.py)
All arguments and outputs for each code are explained in details at the very beginning of the python file.
- `util.py` contains a few useful functions that are used by a lot of other programs. That is why you will see "import util" in most of the programs. Each function takes the path to an adjacency list or a twitter trace as argument, plus sometimes a boolean indicating whether we are in Cascade mode and an Author dictionary (as returned by the first function `get_authors`). There are some more explanations in the file itself but to summarize:
  - `get_authors` returns an author dict (star) or a last publisher dict (cascade) from twitter trace. Format: Author[twid] = uid or LastPublisher[twid] = uid. Such a dictionary is needed for a majority of the following functions.
  - `get_activity` returns dictionary of lambdas, dictionary of mus, and total duration of trace.
  - `nxgraph_from_` returns a networkx graph from a twitter trace (`nxgraph_from_trace`) or an adjacency list (`nxgraph_from_adjList`).
  - `graph_from_` returns a leadgraph and a followgraph as dictionaries. LeadGraph[user] = {follwoer1, follower2, ...} and analogously for FollowGraph. Can be from a twitter trace (`graph_from_trace`) or an adjacency list (`graph_fgrom_adjList`).
  - `leadgraph_from_` same but returns only the leadgraph (useful when light on RAM).
  
- `compare_psis.py` takes two psi list as arguments and outputs a txt file with (among others) kendall tau, common users proportion, mean distance considering only top2 emul users, top3, top4, ... the outputed list can be used in `Journal_plots.ipynb` to plot kendall tau and common users prop. I used this code to obtain the txt files located in `PsiResults/ComparePsis/` (more on that below).

- `compute_model_psis.py` to compute psi_model with Star or Cascade graph. Note that the number of iterations can be modified in the `pi_method_sparse_v2` function.

- `compute_model_psis_oldp_newp.py` to compute psi_model with Star or Cascade graph. Additionally saves the last two values of p in another file to compare the evolution between the last two iterations.

- `compute_psis_truegraph.py` to compute psi model with Real graph (ex: weibo). 

- `compute_psis_truegraph_32.py` to compute psi model with Real graph (ex: weibo) with float32 instead of float64. Lighter in RAM but maybe less precise? Also outputs number of iterations for each user.

- `degree_distrib.py` to plot cumulative distribution of degrees for star, cascade and real graph.

- `simple_graph_stats.py` to get some simple stats for a given graph (star, cascade or real) such as number of nodes, mean degree, etc.

- `sort_psi.py` to sort a psi list by decreasing psi.

- `top_influencers_table.py` table for top influencers (contains psi, outdeg, lambda, rank, etc.)


### Jupyter notebooks (.ipynb)
- `Journal_plots.ipynb` code for 
  1. plotting kendall tau and common users proportion. Uses a file such as created by `compare_psis.py`.
  2. plotting psi scatter plot and cumulative distribution. Uses lists of psis.
  3. plotting lambda,mu cumulative distribution
  4. computing correlations between out-degree and psi, lambda and psi, etc.
  5. computing stats table for top influencers (same as `top_influencers_table.py`)
  
- `Newman_scalable_adaptiveN.ipynb` newman algorithm with evolving N and fixed w.

- `Newman_scalable_adaptiveW.ipynb` newman algorithm with evolving w and fixed N.

- `Simulator_official_NEW.ipynb` for simulating the model. It is the same notebook which is on Anastasios's page for the project (https://github.com/yokaiAG/social-platform-model).


## PsiResults

### PsiResults/Psis/
Here you will find list of psis for wcano, russian, weibo with star, cascade, and real graph (only weibo). The lists are ordered by decreasing psi. Except stated otherwise, the convergence criterion is ||p_old - p_new|| < 10^(-3) where ||.|| denotes infinity norm. EAch file is a .txt where each line is: uid psi.
- `wcano_emul.txt` psis emul for wcano.
- `wcano_oursin.txt` psis model for wcano with oursin graph. AMong users with psi_emul < 10^(-7), 77000 have been forced to do at least 5 iterations when computing p (i stopped at 77000 because it was too long and took a lot of RAM on the server). For other users it is the usual convergence criterion explained above.
- `russian_cascade.txt` psis model cascade for russian with cascade graph.
- `russian_oursin_full0.txt` psis model for russian with oursin graph. We made 0 iterations for users with psi_emul <10^(-6). For other users it is the usual convergence criterion.
- `russian_oursin_full15.txt` psis model for russian with oursin graph. We forced 15 iterations for users with psi_emul <10^(-6). For other users it is the usual convergence criterion.
- `weibo_emul.txt` psis emul for weibo.
- `weibo_oursin.txt` psis model for weibo with oursin graph.
- `weibo_real_top10000emul.txt` psi model for weibo with real graph. Only top 10 000 users according to `weibo_emul.txt`.
- `weibo_cascade_top10000emul.txt` psi model for weibo with cascade graph. Only top 10 000 users according to `weibo_emul.txt`.
Note that there is no file for Cascade in wcano because the computation was very very slow. Thus you will find no other results nor plots for wcano with cascade graph.

### PsiResults/ComparePsis/
Contains comparison between psi emul and model lists obtained via `Code/compare_psis.py`. Each line is
> N,min_psi_emul,min_psi_model,kendall,mean_dist,common_users_prop

where N is the number of top users we are considering, min_psi_emul is the minimum value of psi_emul among those, min_psi_model the minimum value of psi_model among those, kendall is the value of kendall_tau for those, mean_dist is the mean distance for each of those users between psi_emul and psi_model (absolute value) and common_users_prop is the proportion of common users between psi_emul and psi_model.

Here for each file I precise which lists of psis are compared (the lists of psis are from PsiResults/Psis/).
- `wcano_emul_oursin.txt` ---> comparing `wcano_emul.txt` with `wcano_oursin.txt`.
- `russian_emul_oursin.txt` ---> comparing `russian_emul.txt` with `russian_oursin.txt`.
- `russian_emul_cascade.txt` ---> comparing `russian_emul.txt` with `russian_cascade.txt`.
- WEIBO TO DO

### PsiResults/Plots/
Here are the plots obtained with `Code/Journal_plots.ipynb` ie kendall tau, common users prop, psi scatter plot, etc. Except for the psi scatter plot, the results for the different user graphs (star, cascade, real) are plotted on the same figure). We also have small txt files with values of correlations between out-degree and psis, lambda and psis, etc. The names are rather explicit. Example: `russian_psi_cumul_distrib.pdf` is the plot for cumulative distribution of psis in russian. It will contain cumulative distribution for emulator as well as model with star and cascade graph.
