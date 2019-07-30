# Stage2019

This repository contains files used during my internship.

## Overview
- Code: contains all python codes and jupyter notebooks.
- DataAnalysis: some stats on the datasets. The name of the files and folders speak for themselves.
- PsiResults: results on the different datasets (psi model, psi emul, and comparisons between them). Also contains plots used for the journal and the internship report.

### Code
- `util.py`: contains a few useful functions that are used by a lot of other programs. That is why you will see "import util" in most of the programs. Each function takes the path to an adjacency list or a twitter trace as argument, plus sometimes a boolean indicating if we are in Cascade mode and an Author dictionary (as return by the first function `get_authors`). There are some more explanations in the file itself but to summarize:
  - `get_authors` returns an author dict (star) or a last publisher dict (cascade). Format: Author[twid] = uid or LastPublisher[twid] = uid. Such a dictionary is needed for a majority of the following functions.
  - `get_activity` returns lambdas dict, mus dict, and total_time.
  - `nxgraph_from_` returns a networkx graph from a twitter trace (`nxgraph_from_trace`) or an adjacency list (`nxgraph_from_adjList`).
  - `graph_from_` returns a leadgraph and a followgraph as dictionaries. LeadGraph[user] = {follwoer1, follower2, ...} and analogously for FollowGraph. Can be from a twitter trace (`graph_from_trace`) or an adjacency list (`graph_fgrom_adjList`).
  - `leadgraph_from_` same but returns only the leadgraph (useful when light on RAM).
 
- labla

### PsiResults
