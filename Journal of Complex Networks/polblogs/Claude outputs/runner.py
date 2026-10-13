#!/usr/bin/env python3
"""
Experiment runner for the CONNET-2026-191 major revision.

Wraps the validated algorithms in phase4_complete.py without modifying them.
Everything it adds is plumbing: explicit per-realization seeds, tidy output,
and resume.

Design notes
------------
Two independent seeds per realization:

  graph_seed  controls the stochastic graph model (BA / WS / ER)
  sobol_seed  controls the scrambling of the Sobol sequence

Keeping them separate is what lets us report how much of the spread is
graph-to-graph structural variation and how much is quasi-Monte Carlo
estimator noise. Reviewer 2 asks precisely this.

The peripheral-pair sampler inside HBnnsAGP (SelectionST) keeps its own fixed
seed, as in the submitted code. It is treated as part of the strategy
definition rather than as a source of randomness under study.

Output is one CSV row per (model, params, realization, strategy, ASR setting).
Rerunning skips rows already present, so a run can be interrupted and resumed.
"""
import argparse
import csv
import itertools
import os
import sys
import time
from multiprocessing import Pool

import networkx as nx
import numpy as np
from scipy.stats.qmc import Sobol

REPO = os.environ.get("RASR_REPO", os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "repo")))
sys.path.insert(0, REPO)
import phase4_complete as p4  # noqa: E402  (validated algorithms)

K_SOBOL = 512
REAL = ["karate", "davis", "florentine", "lesmis"]   # bundled with NetworkX
# Empirical graphs supplied as data files, loaded from a pickle built by
# netdata/parse.py. Undirected, unweighted, simple, largest component.
NETDATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "netdata", "graphs.pkl")
_netdata_cache = None


def _netdata():
    global _netdata_cache
    if _netdata_cache is None:
        import pickle
        with open(NETDATA, "rb") as fh:
            _netdata_cache = pickle.load(fh)
    return _netdata_cache
N1, N2 = 16, 8
ASR_SETTINGS = [("100", 1.00), ("80", 0.80), ("60", 0.60),
                ("50", 0.50), ("rand", None)]
STRATEGIES = ["HBnnsAGP", "HBA", "HDA", "RF"]

FIELDS = [
    "model", "params", "rep", "graph_seed", "sobol_seed",
    "N", "M", "mean_degree", "density", "kmax", "hetero", "clustering",
    "strategy", "asr_label", "asr_value",
    "rasr_mean", "rasr_sd", "anc_det", "seconds",
]


# ----------------------------------------------------------------------
# network construction
# ----------------------------------------------------------------------
def build_graph(model, params, seed):
    """Return the largest connected component of one model realization."""
    if model == "BA":
        G = nx.barabasi_albert_graph(params["N"], params["m"], seed=seed)
    elif model == "WS":
        G = nx.watts_strogatz_graph(params["N"], params["k"], params["p"],
                                    seed=seed)
    elif model == "ER":
        G = nx.erdos_renyi_graph(params["N"], params["p"], seed=seed)
    elif model == "karate":
        G = nx.karate_club_graph()
    elif model == "davis":
        G = nx.Graph(nx.davis_southern_women_graph())
    elif model == "florentine":
        G = nx.florentine_families_graph()
    elif model == "lesmis":
        G = nx.Graph(nx.les_miserables_graph())
    elif model in _netdata():
        return _netdata()[model]          # already cleaned and reduced to LCC
    else:
        raise ValueError("unknown model: %s" % model)
    lcc = max(nx.connected_components(G), key=len)
    return G.subgraph(lcc).copy()


def graph_stats(G):
    ks = [d for _, d in G.degree()]
    mean_k = float(np.mean(ks))
    return dict(N=G.number_of_nodes(), M=G.number_of_edges(),
                mean_degree=round(mean_k, 4),
                density=round(nx.density(G), 4),
                kmax=max(ks), hetero=round(max(ks) / mean_k, 4),
                clustering=round(nx.average_clustering(G), 4))


# ----------------------------------------------------------------------
# metrics
# ----------------------------------------------------------------------
def attack_sequence(G, strategy, seed):
    if strategy == "HBnnsAGP":
        return p4.get_attack_sequence_hbnnagp(G, N1, N2)
    if strategy == "HBA":
        return p4.get_attack_sequence_hba(G)
    if strategy == "HDA":
        return p4.get_attack_sequence_hda(G)
    if strategy == "RF":
        return p4.get_attack_sequence_rf(G, seed=seed)
    raise ValueError(strategy)


def asr_vector(seq, value, rng):
    """Uniform ASR, or a fresh heterogeneous draw when value is None."""
    if value is not None:
        return [value] * len(seq)
    return rng.uniform(0.5, 1.0, size=len(seq)).tolist()


def rasr(G, seq, pv, sobol_seed, pool, K=K_SOBOL):
    """PRQMC estimate of RASR, returning both mean and spread (x100)."""
    pts = Sobol(d=len(seq), scramble=True, seed=sobol_seed).random(K)
    states = (pts <= np.array(pv)).tolist()
    vals = np.array(pool.map(p4._worker, [(G, seq, s) for s in states])) * 100.0
    return float(vals.mean()), float(vals.std(ddof=1))


def anc_deterministic(G, seq):
    """Standard ANC for a fixed removal order, every removal succeeding."""
    H = G.copy()
    base = p4.gcc_size(H)
    if base == 0:
        return 0.0
    total = 0.0
    for v in seq:
        H.remove_node(v)
        total += p4.gcc_size(H) / base
    return total / len(seq)


# ----------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------
def done_keys(path):
    if not os.path.exists(path):
        return set()
    with open(path, newline="") as fh:
        return {(r["model"], r["params"], r["rep"], r["strategy"],
                 r["asr_label"]) for r in csv.DictReader(fh)}


def run(conditions, reps, out, strategies=STRATEGIES, asr=ASR_SETTINGS,
        single_rep_real=True):
    seen = done_keys(out)
    new = not os.path.exists(out)
    fh = open(out, "a", newline="")
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    if new:
        w.writeheader()

    total = len(conditions) * reps * len(strategies) * len(asr)
    n = 0
    started = time.time()
    with Pool(max(1, os.cpu_count())) as pool:
        for model, params in conditions:
            ptag = ",".join("%s=%s" % (k, v) for k, v in sorted(params.items()))
            n_reps = 1 if (model in REAL and single_rep_real) else reps
            for rep in range(n_reps):
                gseed = 1000 + rep
                sseed = 90000 + rep
                G = build_graph(model, params, gseed)
                st = graph_stats(G)
                rng = np.random.default_rng(50000 + rep)
                for strat in strategies:
                    seq = attack_sequence(G, strat, seed=gseed)
                    anc = anc_deterministic(G, seq)
                    for label, value in asr:
                        n += 1
                        key = (model, ptag, str(rep), strat, label)
                        if key in seen:
                            continue
                        t0 = time.time()
                        pv = asr_vector(seq, value, rng)
                        m, sd = rasr(G, seq, pv, sseed, pool)
                        row = dict(model=model, params=ptag, rep=rep,
                                   graph_seed=gseed, sobol_seed=sseed,
                                   strategy=strat, asr_label=label,
                                   asr_value="" if value is None else value,
                                   rasr_mean=round(m, 4), rasr_sd=round(sd, 4),
                                   anc_det=round(anc, 6),
                                   seconds=round(time.time() - t0, 2), **st)
                        w.writerow(row)
                        fh.flush()
                if rep % 10 == 0 or rep == n_reps - 1:
                    el = time.time() - started
                    print("[%s %s] rep %d/%d  %d/%d rows  %.0fs elapsed"
                          % (model, ptag, rep + 1, n_reps, n, total, el),
                          flush=True)
    fh.close()


def realization_conditions(N=34):
    """The four topologies of the submitted paper, at their published params."""
    return [
        ("BA", dict(N=N, m=2)),
        ("WS", dict(N=N, k=4, p=0.3)),
        ("ER", dict(N=N, p=0.13)),
        ("karate", dict()),
    ]


def sweep_conditions(N=34):
    """Parameter sensitivity grid for Reviewer 2 major comment 4."""
    out = []
    for m in (1, 2, 3, 5):
        out.append(("BA", dict(N=N, m=m)))
    for k, p in itertools.product((4, 6, 8), (0.01, 0.05, 0.1, 0.3, 0.5, 1.0)):
        out.append(("WS", dict(N=N, k=k, p=p)))
    for p in (0.08, 0.10, 0.13, 0.16, 0.20, 0.25):
        out.append(("ER", dict(N=N, p=p)))
    return out


def realworld_conditions():
    """Reviewer 2 major comment 2: more than one real-world network.

    These four are the empirical social networks shipped with NetworkX, so no
    external data download is required to reproduce them. The graph is fixed,
    so repeats vary only the Sobol scramble and the heterogeneous ASR draw.
    """
    return [(m, dict()) for m in REAL]


def realdata_conditions():
    """Reviewer 2 major comment 2, with empirical data files.

    Five networks spanning four domains and an order of magnitude of degree
    heterogeneity, which is what makes them a real test of the structural
    model rather than more of the same.
    """
    return [(m, dict()) for m in
            ["dolphins", "football", "celegans", "usair", "polblogs"]]


def scale_conditions(N):
    """Reviewer 2 major comment 5: does the probabilistic result hold at size?

    Mean degree is held near 4 at every N so that density does not drift with
    scale and confound the comparison.
    """
    return [("BA", dict(N=N, m=2)),
            ("WS", dict(N=N, k=4, p=0.3)),
            ("ER", dict(N=N, p=round(4.0 / (N - 1), 5)))]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("study", choices=["realizations", "sweep",
                                     "realworld", "scale", "realdata"])
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--N", type=int, default=34)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    conds = {"realizations": lambda: realization_conditions(a.N),
             "sweep": lambda: sweep_conditions(a.N),
             "realworld": realworld_conditions,
             "realdata": realdata_conditions,
             "scale": lambda: scale_conditions(a.N)}[a.study]()
    strat = STRATEGIES if a.study == "realizations" else ["HBnnsAGP", "HDA"]
    asr = ASR_SETTINGS
    if a.study == "realdata":
        strat = ["HBnnsAGP", "HDA"]
    if a.study == "scale":                      # keep the large-N grid affordable
        strat = ["HBnnsAGP"]
        asr = [("100", 1.00), ("60", 0.60)]
    out = a.out or os.path.join(os.path.dirname(__file__),
                                "results_%s_N%d.csv" % (a.study, a.N))
    print("study=%s conditions=%d reps=%d -> %s"
          % (a.study, len(conds), a.reps, out), flush=True)
    run(conds, a.reps, out, strategies=strat, asr=asr,
        single_rep_real=False)
    print("done", flush=True)
