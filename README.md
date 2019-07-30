# Stage2019

This repository contains files used during my internship.

## Overview
- Code: contains all python codes and jupyter notebooks.
- DataAnalysis: some stats on the datasets. The name of the files and folders speak for themselves.
- PsiResults: results on the different datasets (psi model, psi emul, and comparisons between them). Also contains plots used for the journal and the internship report.

### Code
- `util.py`: contains a few useful functions that are used by a lot of other programs. That is why you will see "import util" in most of the programs. There a some more explanations in the file itself but to summarize:
  - `get_authors` returns an author dict (star) or a last publisher dict (cascade). Format: Author[twid] = uid or LAstPublisher[twid] = uid.
  - `get_activity` returns lambdas dict, mus dict, and total_time.
  - `nxgraph_from_` returns a networkx graph from a twitter trace (`nxgraph_from_trace`) or an adjacency list (`nxgraph_from_adjList`).


### PsiResults
