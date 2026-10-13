#!/usr/bin/env python3
"""
Experiment driver for the CONNET-2026-191 revision.

Mirrors runner.py (same seeds, same RASR estimator) and calls the
submitted phase4_complete.py without modifying it.

Seeds per realization:
  graph_seed = GSEED_BASE + rep   (graph model)
  sobol_seed = 90000 + rep        (Sobol scramble)
  asr rng    = 50000 + rep        (heterogeneous ASR draw)

The parameter sweep uses GSEED_BASE = 5000 so that its graphs never
coincide with the realization study's graphs (GSEED_BASE = 1000).
"""
import argparse, csv, os, sys, time
import networkx as nx
import numpy as np
from multiprocessing import Pool
from scipy.stats.qmc import Sobol

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phase4_complete as p4  # noqa: E402

K = 512
N1, N2 = 16, 8
ALL_ASR = [("100", 1.0), ("80", 0.8), ("60", 0.6), ("50", 0.5), ("rand", None)]
FIELDS = ["model", "params", "rep", "graph_seed", "sobol_seed", "N", "M",
          "mean_degree", "density", "kmax", "hetero", "clustering",
          "strategy", "asr_label", "rasr_mean", "rasr_sd", "seconds"]


def lcc(G):
    G = nx.Graph(G)
    G.remove_edges_from(nx.selfloop_edges(G))
    return G.subgraph(max(nx.connected_components(G), key=len)).copy()


def build(model, params, seed):
    if model == "BA":
        return lcc(nx.barabasi_albert_graph(params["N"], params["m"], seed=seed))
    if model == "WS":
        return lcc(nx.watts_strogatz_graph(params["N"], params["k"], params["p"], seed=seed))
    if model == "ER":
        return lcc(nx.erdos_renyi_graph(params["N"], params["p"], seed=seed))
    raise ValueError(model)


def stats(G):
    k = [d for _, d in G.degree()]
    m = float(np.mean(k))
    return dict(N=G.number_of_nodes(), M=G.number_of_edges(),
                mean_degree=round(m, 4), density=round(nx.density(G), 4),
                kmax=max(k), hetero=round(max(k) / m, 4),
                clustering=round(nx.average_clustering(G), 4))


def seq_for(G, strat, seed):
    if strat == "HBnnsAGP":
        return p4.get_attack_sequence_hbnnagp(G, N1, N2)
    if strat == "HBA":
        return p4.get_attack_sequence_hba(G)
    if strat == "HDA":
        return p4.get_attack_sequence_hda(G)
    if strat == "RF":
        return p4.get_attack_sequence_rf(G, seed=seed)
    raise ValueError(strat)


def rasr(G, seq, pv, sseed, pool):
    if all(x >= 1.0 for x in pv):           # every attack succeeds: one outcome
        return p4.compute_ANCw(G, seq, [True] * len(seq)) * 100.0, 0.0
    pts = Sobol(d=len(seq), scramble=True, seed=sseed).random(K)
    st = (pts <= np.array(pv)).tolist()
    v = np.array(pool.map(p4._worker, [(G, seq, s) for s in st])) * 100.0
    return float(v.mean()), float(v.std(ddof=1))


def run(jobs, out, strategies, asr, pool):
    """jobs: list of (model, ptag, rep, gseed, G)."""
    new = not os.path.exists(out)
    done = set()
    if not new:
        with open(out) as fh:
            done = {(r["model"], r["params"], r["rep"], r["strategy"], r["asr_label"])
                    for r in csv.DictReader(fh)}
    fh = open(out, "a", newline="")
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    if new:
        w.writeheader()
    t0 = time.time()
    for i, (model, ptag, rep, gseed, G) in enumerate(jobs):
        st = stats(G)
        rng = np.random.default_rng(50000 + rep)
        sseed = 90000 + rep
        for strat in strategies:
            seq = seq_for(G, strat, gseed)
            for lab, val in asr:
                pv = [val] * len(seq) if val is not None else \
                    rng.uniform(0.5, 1.0, size=len(seq)).tolist()
                if (model, ptag, str(rep), strat, lab) in done:
                    continue
                t = time.time()
                m, sd = rasr(G, seq, pv, sseed, pool)
                w.writerow(dict(model=model, params=ptag, rep=rep, graph_seed=gseed,
                                sobol_seed=sseed, strategy=strat, asr_label=lab,
                                rasr_mean=round(m, 4), rasr_sd=round(sd, 4),
                                seconds=round(time.time() - t, 2), **st))
                fh.flush()
        if i % 10 == 0:
            print(f"{out}: {i+1}/{len(jobs)} {time.time()-t0:.0f}s", flush=True)
    fh.close()


def synth_jobs(conds, reps, gbase):
    for model, params in conds:
        ptag = ",".join(f"{k}={v}" for k, v in sorted(params.items()))
        for rep in range(reps):
            yield (model, ptag, rep, gbase + rep, build(model, params, gbase + rep))


def realization_conds(N=34):
    return [("BA", dict(N=N, m=2)), ("WS", dict(N=N, k=4, p=0.3)), ("ER", dict(N=N, p=0.13))]


def sweep_conds(N=34):
    out = [("BA", dict(N=N, m=m)) for m in (1, 2, 3, 5)]
    out += [("WS", dict(N=N, k=k, p=p)) for k in (4, 6, 8) for p in (0.01, 0.05, 0.1, 0.3, 0.5, 1.0)]
    out += [("ER", dict(N=N, p=p)) for p in (0.08, 0.10, 0.13, 0.16, 0.20, 0.25)]
    return out


def scale_conds(N):
    return [("BA", dict(N=N, m=2)), ("WS", dict(N=N, k=4, p=0.3)),
            ("ER", dict(N=N, p=round(4.0 / (N - 1), 5)))]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("study", choices=["realizations", "sweep", "scale", "real"])
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--N", type=int, default=34)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with Pool() as pool:
        if a.study == "realizations":
            jobs = list(synth_jobs(realization_conds(), a.reps, 1000))
            jobs.append(("karate", "", 0, 0, lcc(nx.karate_club_graph())))
            run(jobs, a.out, ["HBnnsAGP", "HBA", "HDA", "RF"], ALL_ASR, pool)
        elif a.study == "sweep":
            jobs = list(synth_jobs(sweep_conds(), a.reps, 5000))
            run(jobs, a.out, ["HBnnsAGP", "HDA"], [("100", 1.0)], pool)
        elif a.study == "scale":
            jobs = list(synth_jobs(scale_conds(a.N), a.reps, 1000))
            run(jobs, a.out, ["HBnnsAGP"], [("100", 1.0), ("60", 0.6)], pool)
        elif a.study == "real":
            import pickle
            graphs = pickle.load(open(os.path.join(os.path.dirname(a.out), "real_graphs.pkl"), "rb"))
            jobs = [(name, "", 0, 0, G) for name, G in graphs.items()]
            run(jobs, a.out, ["HBnnsAGP", "HDA"], [("100", 1.0)], pool)
