# Structural Determinants of Network Robustness Under Probabilistic Attack

A cross-topology study of network robustness when attacks are allowed to fail, built on the
RASR framework of Yang and Wang (2023). This repository holds the implementation, the
experiment scripts, the figures, and the manuscript source.

**Status:** under review at the *Journal of Complex Networks* (Oxford University Press / IMA).
Manuscript ID `CONNET-2026-191`, submitted 27 May 2026. Decision of 1 September 2026 was
revise and resubmit: Reviewer 1 minor revision, Reviewer 2 major revision. Revision due
30 October 2026.

**Authors:** B. Akshay Sriram, P. Kavya Nair, Cinu C Kiliroor
(Dept. of Computer Science and Engineering, IIIT Kottayam)

---

## What the paper claims

Most robustness measures assume every attack lands. RASR relaxes that by attaching a per-node
attack success rate (ASR) and defining robustness as an expectation over all attack outcomes,
estimated with Parallel Randomized Quasi-Monte Carlo (PRQMC) sampling. Every published RASR
result so far is anchored to one fixed network.

This work makes the structural class of the network the controlled experimental variable, holding
size, approximate density, attack strategy and ASR fixed. The headline observation is that the
fragility ordering

```
Scale-Free  <  Real-World (Karate)  <  Small-World  <  Random
```

holds at every ASR level tested from 100% down to 50%, and under heterogeneous random ASR.

Supporting numbers, all at `N = 34`:

| Quantity | Value |
|---|---|
| Lowest average RASR, HBnnsAGP | 19.47 |
| Average RASR, degree targeting (HDA) | 21.79 |
| ER over BA robustness ratio, RASR | 2.29x |
| ER over BA robustness ratio, ANC | 2.32x |
| RASR gap, ASR 100% to 50% | 41.6 to 44.2 units, topology independent |

The four networks compared, after extraction of the largest connected component:

| Network | M | mean degree | density | k_max | k_max / mean degree | clustering |
|---|---|---|---|---|---|---|
| Scale-Free (BA, m=2) | 64 | 3.76 | 0.114 | 19 | 5.05 | 0.367 |
| Karate (real) | 78 | 4.59 | 0.139 | 17 | 3.71 | 0.571 |
| Small-World (WS, k=4, p=0.3) | 68 | 4.00 | 0.121 | 6 | 1.50 | 0.241 |
| Random (ER, p=0.13) | 77 | 4.53 | 0.137 | 8 | 1.77 | 0.104 |

---

## Repository layout

```
.
├── phase2_complete.py    replication: stats, centralities, communities, topology figures
├── phase3_complete.py    extension: RF / HDA / HBA attacks, ANC, cross-topology curves
├── phase4_complete.py    RASR: BCnns, SelectionST, HBnnsAGP, ANCw, PRQMC
├── *.png                 figures used in the manuscript (top level, not in a subfolder)
├── paper_methodology_block_diagram.jpg
└── README.md
```

There is no `figures/` or `paper/` subdirectory. Earlier versions of this README described one.

---

## Requirements

```bash
pip install networkx numpy scipy matplotlib
```

Developed against Python 3.12, NetworkX 3.x, and `scipy.stats.qmc.Sobol`. A global seed of 42
is applied to every stochastic operation, so a given script reproduces its own numbers exactly.

---

## Running the experiments

```bash
python phase2_complete.py    # baseline statistics and replication figures
python phase3_complete.py    # deterministic attacks and ANC across four topologies
python phase4_complete.py    # probabilistic RASR under four strategies and five ASR settings
```

`phase4_complete.py` is the core of the paper. It builds an attack sequence per strategy, converts
`K = 512` scrambled Sobol points into binary attack-outcome vectors by comparing each coordinate
against the corresponding node's ASR, evaluates the weighted ANC for all `K` outcomes in parallel
with `multiprocessing.Pool`, and reports the mean as the RASR estimate.

**Known issue:** `phase4_complete.py` writes its figures to the absolute path
`/mnt/user-data/outputs/`, which will not exist on another machine. Change those three `savefig`
calls to a relative path before anyone else runs it.

### Algorithms implemented

- **ANC**, accumulated normalized connectivity under sequential node removal.
- **ANCw**, the weighted variant that tracks which removals actually succeeded.
- **PRQMC**, Sobol-based estimator of `RASR = E[ANCw]`, converging at `O(K^-1)` rather than the
  `O(K^-1/2)` of plain Monte Carlo.
- **BCnns**, betweenness restricted to shortest paths between sampled low-degree peripheral node
  pairs, which surfaces community-to-community bridges instead of hubs.
- **SelectionST**, the peripheral pair sampler, run with `N1 = 16` and `N2 = 8`.
- **HBnnsAGP**, adaptive greedy attack that repeatedly removes the highest-BCnns node of the
  current giant component, with a degree-based fallback when all BCnns scores collapse to zero.
- **HDA** and **HBA**, adaptive highest-degree and highest-betweenness attacks, plus a
  **random failure** baseline.

Exhaustive BCnns path enumeration limits HBnnsAGP to roughly `N <= 200`. Larger networks in the
paper are handled by the deterministic ANC and HDA analysis only.

---

## Manuscript

The manuscript is written for the journal's own LaTeX class and is not in this repository by
default. The files that matter:

| File | Purpose |
|---|---|
| `conference_101719.tex` | the manuscript, working source |
| `conference_101719_marked.tex` | same content with all revision changes in blue |
| `comnet.cls` | the journal's class file, unmodified |
| the eleven `.png` figures | referenced by `\includegraphics` |

Build with `latexmk -pdf conference_101719.tex`. The marked version additionally loads `xcolor`
and defines a `\revised` macro; that is the only difference between the two sources.

Do not substitute a patched class file. An earlier version of the project used a
`comnet_patched.cls` that replaced `\usepackage{ulem}` with a no-op to work around a missing
package. The paper uses no ulem commands, so the output is identical, but production will use the
journal's own class and a local patch only hides problems until then.

---

## Revision status

Reviewer 1's five comments and Reviewer 2's five minor comments are addressed in the current
manuscript. That covers the two requested citations, a sharper novelty statement, a justification
of the model and parameter choices with a new statistics table, moderated claims throughout, an
abbreviations table, a clear separation of the deterministic and probabilistic result lines, a full
description of the heterogeneous ASR protocol, an application-settings discussion, and a broadened
literature review that took the bibliography from 16 entries to 31.

Reviewer 2's five major comments are outstanding and require new computation:

1. The ordering rests on one realisation of each stochastic model, so it is an instance-level
   result rather than a topology-class-level one.
2. Real-world validation is the Karate club alone.
3. BA, WS and ER need repeated realisations with means, variability and a rank-stability statistic.
4. Topology effects and parameterisation effects are not disentangled; sweeps over BA `m`,
   WS `k` and `p`, and ER density are needed, along with a mean-degree-matched comparison, since
   the BA graph is currently the sparsest of the four.
5. The `N = 34` to `N = 10,670` range is supported by the deterministic analysis, not by the
   probabilistic framework, and should be phrased to say so.

---

## Gaps to close before resubmission

- **Four manuscript figures have no generating script here.** `fig_topo_structures.png`,
  `fig_anc_bar_comparison.png`, `fig4_scalability.png` and `fig_rasr_heatmap.png` are committed as
  images but nothing in `phase2`, `phase3` or `phase4` produces them. The Data Availability
  statement claims all experimental scripts are available, so either the generating code should be
  committed or that statement should be narrowed.
- Several committed figures are hand-renamed copies of script outputs, for example
  `phase3_karate_robustness.png` appears as `fig1_karate_robustness.png`. Keeping the script
  output names would make the mapping obvious.
- The hardcoded output path in `phase4_complete.py`, noted above.
- There is no `LICENSE` file, although the previous README stated MIT. Add one or drop the claim.

---

## Data

The Zachary Karate Club network comes from NetworkX (`networkx.karate_club_graph()`). All other
networks are generated from their models with seed 42, so no external data files are required.

---

## Citation

The paper is under review and has no DOI yet. Until it is accepted, cite the framework it builds on:

```bibtex
@article{yang2023rasr,
  title   = {Analyzing the Robustness of Complex Networks with Attack Success Rate},
  author  = {Yang, F. and Wang, Y.},
  journal = {Entropy},
  volume  = {25},
  pages   = {1508},
  year    = {2023}
}
```

An earlier version of this README carried a BibTeX entry listing *Physica A* as the venue. That
was from an earlier submission plan and is no longer correct.

---

## Acknowledgement

Built on the RASR framework of Yang and Wang, *Entropy* 25, 1508 (2023). Experiments use NetworkX
and `scipy.stats.qmc`. The Karate Club dataset is due to Zachary (1977).
