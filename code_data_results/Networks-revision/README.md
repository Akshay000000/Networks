# CONNET-2026-191 revision: code, data and results

Everything here reproduces the numbers, tables and figures of the revised manuscript.
`code/phase4_complete.py` is the implementation submitted with the original paper,
unchanged. All other scripts call it.

## Steps
```
cd code
python prepare_networks.py ../data ../results          # builds the empirical graph pickles
python driver.py real          --out ../results/results_real16.csv
python driver.py realizations  --reps 100 --out ../results/results_realizations_N34.csv
python driver.py sweep         --reps 30  --out ../results/results_sweep_N34.csv
python driver.py scale --N 100 --reps 10 --out ../results/results_scale_N100.csv
python driver.py scale --N 200 --reps 10 --out ../results/results_scale_N200.csv
python driver.py scale --N 500 --reps 10 --out ../results/results_scale_N500.csv
python driver.py real          --out ../results/ext/results_real_ext.csv   # uses results/ext/real_graphs.pkl
python extras.py ../results                 # deterministic scalability, Karate random-ASR draws
python cost.py ../results/cost.json         # timing
python analyse.py ../results                # writes results/numbers.json
python modularity.py ../results             # community structure (modularity Q) as a fourth predictor
python figures.py ../results <figure_dir>
python heatmap.py <figure_dir>/fig_rasr_heatmap.png
python tables.py ../results <table_dir>
python verify.py .                          # single-instance check against the submitted tables
```

## Seeds
Realization study: graph seed 1000+rep, Sobol scramble seed 90000+rep, heterogeneous-ASR
seed 50000+rep. Parameter sweep: graph seed 5000+rep (disjoint from the realization study).
Single instances: seed 42, as in the original submission.

## Notes
- All 16 empirical networks and the Oregon graph are rebuilt from the raw files in `data/`.
- Run time on two cores: about one hour for everything.

## Community structure
`modularity.py` rebuilds every graph of the pooled regression from its seed, checks its
structural statistics against `pooled_N34.csv`, computes the modularity of the greedy
(Clauset-Newman-Moore) and Louvain (seed 0) partitions, and refits the synthetic and empirical
regressions with Q added. Output: `modularity.json`, `modularity_per_graph.csv`,
`modularity_empirical.csv`. It needs the graph pickles from `prepare_networks.py`. Run `analyse.py` first;
`tables.py` reads `modularity.json` for the Q column of the empirical-network table.

## Oregon autonomous-systems graph (N = 10,670)
```
python oregon.py ../data/oregon1_010331.txt.gz ../results/oregon.json
```
SNAP dataset oregon1_010331 (Leskovec, Kleinberg and Faloutsos 2005). Reported separately
from the regression because k_max/<k> = 560.6. Takes about 7 minutes on two cores.
