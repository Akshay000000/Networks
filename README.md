# Structural Determinants of Network Robustness Under Probabilistic Attack

Code, data and results for the paper

> B. Akshay Sriram, P. Kavya Nair and Cinu C Kiliroor,
> *Structural Determinants of Network Robustness Under Probabilistic Attack: A Cross-Topology
> Analysis Using Quasi-Monte Carlo Estimation*. Manuscript CONNET-2026-191, Journal of Complex
> Networks (under revision).
>
> Department of Computer Science and Engineering, Indian Institute of Information Technology Kottayam.

Everything needed to reproduce the numbers, tables and figures of the revised manuscript is in
this repository: the implementation, the experiment and analysis scripts, the raw network files,
and the result files that the paper reports.

---

## What the study is about

Most robustness measures assume that every attack on a node succeeds. The Robustness Attack
Success Rate (RASR) framework of Yang and Wang (2023) drops that assumption: each node has an
attack success rate (ASR), and robustness is the expected accumulated connectivity over all
possible attack outcomes, estimated with Parallel Randomized Quasi-Monte Carlo (PRQMC) sampling.
Published RASR studies analyse one fixed network at a time.

This work asks how the **structure** of a network shapes its robustness under probabilistic
attack. It estimates RASR for

- 100 independent realizations each of scale-free (Barabasi-Albert), small-world
  (Watts-Strogatz) and random (Erdos-Renyi) graphs at N = 34, under four attack strategies and
  five ASR settings;
- a 28-point parameter sweep over the generators (840 further graphs);
- 16 empirical networks from social, biological, technological and infrastructure domains
  (15 to 4,941 nodes), plus the Oregon autonomous-systems graph (10,670 nodes);
- synthetic families at N = 100, 200 and 500.

## Main findings

| Finding | Result |
|---|---|
| A strict ordering of the four network classes seen on single instances | holds in 0 of 100 realizations at full attack reliability |
| Hub-dominated networks more fragile than homogeneous ones | in 91% to 100% of realizations at every ASR level |
| RASR explained by mean degree, degree heterogeneity and clustering (1,141 synthetic graphs) | R^2 = 0.930, leave-one-out R^2 = 0.929 |
| RASR explained by the model label alone | R^2 = 0.310 (adds 0.015 once the three quantities are known) |
| Same model when attacks can fail (ASR 80%, 60%, 50%, heterogeneous) | R^2 = 0.65 to 0.85; density and heterogeneity significant at every level |
| Same three-variable model on the 16 empirical networks | R^2 = 0.693; density and heterogeneity significant, clustering not |
| Community structure (modularity) as a fourth predictor | adds almost nothing on synthetic graphs; not significant on empirical ones |
| Bridge targeting (HBnnsAGP) beats degree targeting (HDA) | in 95% of synthetic instances and all 16 empirical networks |
| Effect of lowering ASR from 100% to 50% | raises RASR by about 41 to 44 units for every structural class |

---

## Repository layout

```
.
|-- README.md
|-- code/                     scripts for the revised manuscript
|   |-- phase4_complete.py    core implementation (RASR, PRQMC, BCnns, HBnnsAGP, HDA, HBA, RF)
|   |-- driver.py             runs the experiments: realizations, sweep, scale, empirical networks
|   |-- prepare_networks.py   builds the empirical graphs from the files in data/
|   |-- analyse.py            statistics and regressions -> results/numbers.json
|   |-- analyse_lib.py        regression helpers used by modularity.py
|   |-- modularity.py         community structure (modularity Q) as a fourth predictor
|   |-- extras.py             deterministic scalability; Karate random-ASR draws
|   |-- oregon.py             Oregon autonomous-systems graph (N = 10,670)
|   |-- cost.py               run-time measurements
|   |-- figures.py            figures of the revision
|   |-- heatmap.py            single-instance RASR heatmap
|   |-- tables.py             LaTeX tables from the result files
|   |-- assemble.py           inserts the tables into the manuscript source
|   `-- verify.py             re-runs the single-instance experiment of the first submission
|-- data/                     raw network files (see "Data" below)
|-- results/                  result files behind every number in the paper
`-- original_submission/      phase2/3/4_complete.py as submitted with the first version
```

`code/phase4_complete.py` is the implementation submitted with the original paper, unchanged.
Every other script imports it, so the revision uses exactly the same RASR estimator and attack
strategies as the first submission.

---

## Requirements

```
pip install networkx numpy scipy pandas matplotlib
```

The results were produced with Python 3.13, NetworkX 3.6, NumPy 2.5, SciPy 1.18, pandas 3.0 and
matplotlib 3.11. Any recent Python 3 with NetworkX 3.x should work. Exact values for networks
loaded from NetworkX can differ in the second decimal across NetworkX versions (for example,
Les Miserables gives 9.79 with NetworkX 3.6).

## Reproducing the results

All commands run from `code/`. Everything together takes about one hour on two cores; the Oregon
run takes about seven minutes on its own.

```
cd code
python prepare_networks.py ../data ../results                     # build empirical graphs
python driver.py realizations --reps 100 --out ../results/results_realizations_N34.csv
python driver.py sweep        --reps 30  --out ../results/results_sweep_N34.csv
python driver.py scale --N 100 --reps 10 --out ../results/results_scale_N100.csv
python driver.py scale --N 200 --reps 10 --out ../results/results_scale_N200.csv
python driver.py scale --N 500 --reps 10 --out ../results/results_scale_N500.csv
python driver.py real         --out ../results/results_real16.csv
python driver.py real         --out ../results/ext/results_real_ext.csv
python extras.py ../results
python oregon.py ../data/oregon1_010331.txt.gz ../results/oregon.json
python cost.py ../results/cost.json
python analyse.py ../results                                      # -> results/numbers.json
python modularity.py ../results                                   # -> results/modularity.json
mkdir ../figures
python figures.py ../results ../figures
python heatmap.py ../figures/fig_rasr_heatmap.png
python tables.py ../results ../tables
```

`driver.py real` reads the graph file `real_graphs.pkl` from the folder of its `--out` file,
which `prepare_networks.py` writes to `results/` and `results/ext/`.

### Where each result appears in the paper

| Result file | Paper |
|---|---|
| `results_realizations_N34.csv` | realization study: Tables 9 and 10, Fig. 12; structural model at every ASR level (Table 14) |
| `results_sweep_N34.csv` | parameter sweep: Table 11, Fig. 13 |
| `pooled_N34.csv` | structural model: Eq. 5.1, Tables 12 and 13, Figs 14 and 15 |
| `results_real16.csv`, `ext/results_real_ext.csv` | empirical networks: Eq. 5.2, Tables 15 and 16, Fig. 16 |
| `results_scale_N100/200/500.csv` | network size: Table 17, Fig. 17 |
| `extras.json` | deterministic scalability (Table 5, Fig. 7); Karate random-ASR draws |
| `oregon.json` | Oregon autonomous-systems graph |
| `modularity.json`, `modularity_*.csv` | community structure analysis |
| `cost.json` | run times quoted in the Limitations section |
| `numbers.json` | every summary statistic quoted in the text |

### Seeds

| Study | Graph seed | Sobol scramble seed | Heterogeneous-ASR seed |
|---|---|---|---|
| Realizations | 1000 + rep | 90000 + rep | 50000 + rep |
| Parameter sweep (ASR = 100% only) | 5000 + rep (disjoint from the realizations) | 90000 + rep | not used |
| Single instances (first submission) | 42 | 42 | 42 |

---

## Method in brief

- **ANC**: accumulated normalized connectivity, the average size of the giant component as nodes
  are removed one by one.
- **RASR**: the expected weighted ANC when each removal succeeds only with its node's ASR.
- **PRQMC**: K = 512 scrambled Sobol points turned into attack-outcome vectors, evaluated in
  parallel; the mean is the RASR estimate.
- **Attack strategies**: HBnnsAGP (adaptive removal of the node with the highest bridge
  centrality BCnns, with N1 = 16 and N2 = 8 peripheral pairs), HDA (adaptive highest degree),
  HBA (adaptive highest betweenness) and RF (random failure).
- **ASR settings**: uniform 100%, 80%, 60% and 50%, and heterogeneous ASR drawn from U[0.5, 1].

## Data

| Network | Source | Preprocessing |
|---|---|---|
| Karate, Florentine families, Davis southern women, Les Miserables | NetworkX built-ins | none |
| Sampson monastery (`data/sampson/`) | UCINET, relation SAMPLK3 | tie if either monk named the other |
| Freeman EIES (`data/eies/EIES.2`) | Freeman and Freeman (1980), time 2 | tie if either reported "met" (3) or "friend" (4); code 0 treated as missing |
| Jazz musicians (`jazz_edges.txt`) | Gleiser and Danon (2003) | as published |
| Facebook egos 698 and 414 (`facebook/`) | SNAP ego-Facebook | ego node restored and linked to all alters |
| US power grid (`Power.txt`) | Watts and Strogatz (1998) | as published |
| Dolphins, American football, C. elegans, political blogs (`.gml`) | Newman's network data | duplicate edges merged |
| Netscience (`ca-netscience.mtx`) | Network Repository | as published |
| USAir97 (`inf-USAir97.mtx`) | Network Repository (Pajek USAir97) | flight weights dropped |
| Oregon AS graph (`oregon1_010331.txt.gz`) | SNAP | as published |

Every network is converted to a simple undirected unweighted graph and reduced to its largest
connected component before analysis.

## Original submission

`original_submission/` holds the three scripts submitted with the first version of the paper:
`phase2_complete.py` (network statistics and replication figures), `phase3_complete.py`
(deterministic attacks and ANC) and `phase4_complete.py` (RASR). They are kept for reference.
`phase4_complete.py` saves its figures to `/mnt/user-data/outputs/`; change those `savefig` paths
before running it on another machine. The revision scripts in `code/` import its functions and
never call those lines.

## Acknowledgement

Built on the RASR framework of F. Yang and Y. Wang, "Analyzing the robustness of complex networks
with attack success rate", *Entropy* 25, 1508 (2023).
