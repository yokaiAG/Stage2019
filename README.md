# Stage2019

This repository contains files used during my internship.

## Overview
- Code: contains all python codes and jupyter notebooks.
- DataAnalysis: some stats on the datasets. The name of the files and folders speak for themselves.
- PsiResults: results on the different datasets (psi model, psi emul, and comparisons between them). Also contains plots used for the journal and the internship report.

## Code
All arguments and outputs for each code are explained in details at the very beginning of the python file.
- `util.py`: contains a few useful functions that are used by a lot of other programs. That is why you will see "import util" in most of the programs. Each function takes the path to an adjacency list or a twitter trace as argument, plus sometimes a boolean indicating if we are in Cascade mode and an Author dictionary (as return by the first function `get_authors`). There are some more explanations in the file itself but to summarize:
  - `get_authors`: returns an author dict (star) or a last publisher dict (cascade) from twitter trace. Format: Author[twid] = uid or LastPublisher[twid] = uid. Such a dictionary is needed for a majority of the following functions.
  - `get_activity`: returns dictionary of lambdas, dictionary of mus, and total duration of trace.
  - `nxgraph_from_`: returns a networkx graph from a twitter trace (`nxgraph_from_trace`) or an adjacency list (`nxgraph_from_adjList`).
  - `graph_from_`: returns a leadgraph and a followgraph as dictionaries. LeadGraph[user] = {follwoer1, follower2, ...} and analogously for FollowGraph. Can be from a twitter trace (`graph_from_trace`) or an adjacency list (`graph_fgrom_adjList`).
  - `leadgraph_from_`: same but returns only the leadgraph (useful when light on RAM).
  
- `compare_psis.py`: takes two psi list as arguments and outputs a txt file with (among others) kendall tau, common users proportion, mean distance considering only top2 emul users, top3, top4, ... the outputed list can be used in `Journal_plots.ipynb` to plot kendall tau and common users prop.

- `compute_model_psis.py`: to compute psi_model with Star or Cascade graph. Note that the number of iterations can be modified in the `pi_method_sparse_v2` function.

- `compute_model_psis_oldp_newp.py`: to compute psi_model with Star or Cascade graph. Additionally saves the last two values of p in another file to compare the evolution between the last two iterations.

- `compute_psis_truegraph.py`: to compute psi model with Real graph (ex: weibo). 

- `compute_psis_truegraph_32.py`: to compute psi model with Real graph (ex: weibo) with float32 instead of float64. Lighter in RAM but maybe less precise? Also outputs number of iterations for each user.

- `degree_distrib.py`: to plot cumulative distribution of degrees for star, cascade and real graph.

- `simple_graph_stats.py`: to get some simple stats for a given graph (star, cascade or real) such as number of nodes, mean degree, etc.

- `sort_psi.py`: to sort a psi list by decreasing psi.

- `top_influencers_table.py`: table for top influencers (contains psi, outdeg, lambda, rank, etc.)

Jupyter notebooks:
- `Journal_plots.ipynb`: code for 
  1. plotting kendall tau and common users proportion. Uses a file such as created by `compare_psis.py`.
  2. plotting psi scatter plot and cumulative distribution. Uses lists of psis.
  3. plotting lambda,mu cumulative distribution
  4. computing correlations between out-degree and psi, lambda and psi, etc.
  5. computing stats table for top influencers (same as `top_influencers_table.py`)
  
- `Newman_scalable_adaptiveN.ipynb`: newman algorithm with evolving N and fixed w.

- `Newman_scalable_adaptiveW.ipynb`: newman algorithm with evolving w and fixed N.

- `Simulator_official_NEW.ipynb`: for simulating the model. It is the same notebook which is on Anastasios's page for the project (https://github.com/yokaiAG/social-platform-model).

## PsiResults
