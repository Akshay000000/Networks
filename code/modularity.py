#!/usr/bin/env python3
"""
Community structure as a fourth structural quantity (Reviewer 1, comment 3).

Rebuilds every graph of the pooled synthetic regression (same generators and
seeds as driver.py) and loads the 16 empirical networks, computes the
modularity Q of the greedy-modularity partition (Clauset-Newman-Moore, the
same partition used for the Karate figure), checks that the rebuilt graphs
match the stored structural statistics, and refits the regressions with Q
added. Writes <res>/modularity.json and <res>/modularity_per_graph.csv.

Usage: python modularity.py <res_dir>
"""
import json, os, pickle, sys
import networkx as nx
import numpy as np
import pandas as pd
from networkx.algorithms.community import greedy_modularity_communities, modularity, louvain_communities

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from driver import build, stats as gstats, lcc  # noqa: E402
from analyse_lib import ols, r2_of  # noqa: E402

R = sys.argv[1]


def Q(G):
    return modularity(G, greedy_modularity_communities(G))


def Q_louvain(G, seed=0):
    return modularity(G, louvain_communities(G, seed=seed))


def parse(ptag):
    d = {}
    for kv in ptag.split(","):
        k, v = kv.split("=")
        d[k] = int(v) if k in ("N", "m", "k") else float(v)
    return d


pool = pd.read_csv(os.path.join(R, "pooled_N34.csv"))
real_conds = {"BA": dict(N=34, m=2), "WS": dict(N=34, k=4, p=0.3), "ER": dict(N=34, p=0.13)}
rows, mism = [], 0
for _, r in pool.iterrows():
    if r.model == "Karate":
        G = lcc(nx.karate_club_graph())
    elif r.src == "realization":
        G = build(r.model, real_conds[r.model], 1000 + int(r.rep))
    else:
        G = build(r.model, parse(r.params), 5000 + int(r.rep))
    s = gstats(G)
    if (abs(s["mean_degree"] - r.mean_degree) > 1e-3 or abs(s["hetero"] - r.hetero) > 1e-3
            or abs(s["clustering"] - r.clustering) > 1e-3):
        mism += 1
    rows.append(dict(Q=Q(G), Q_louvain=Q_louvain(G)))
pool = pd.concat([pool.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
print("synthetic graphs:", len(pool), "stat mismatches:", mism)

rw = pd.concat([pd.read_csv(os.path.join(R, "results_real16.csv")),
                pd.read_csv(os.path.join(R, "ext", "results_real_ext.csv"))], ignore_index=True)
rw = rw[rw.strategy == "HBnnsAGP"].drop_duplicates("model", keep="first").reset_index(drop=True)
graphs = {**pickle.load(open(os.path.join(R, "real_graphs.pkl"), "rb")),
          **pickle.load(open(os.path.join(R, "ext", "real_graphs.pkl"), "rb"))}
rq, rmism = [], 0
for _, r in rw.iterrows():
    G = graphs[r.model]
    s = gstats(G)
    if abs(s["mean_degree"] - r.mean_degree) > 1e-3 or abs(s["clustering"] - r.clustering) > 1e-3:
        rmism += 1
    rq.append(dict(Q=Q(G), Q_louvain=Q_louvain(G)))
rw = pd.concat([rw, pd.DataFrame(rq)], axis=1)
print("empirical networks:", len(rw), "stat mismatches:", rmism)


def strip(f):
    return {k: v for k, v in f.items() if k not in ("pred", "loo_pred")}


def block(df, qcol):
    y = df.rasr_mean.values
    X3 = df[["mean_degree", "hetero", "clustering"]].values
    X4 = np.column_stack([X3, df[qcol].values])
    f3 = ols(X3, y, ["k", "het", "C"])
    f4 = ols(X4, y, ["k", "het", "C", "Q"])
    res3 = y - f3["pred"]
    return dict(base=strip(f3), withQ=strip(f4),
                dR2=f4["R2"] - f3["R2"], dR2_loo=f4["R2_loo"] - f3["R2_loo"],
                Q_alone_R2=r2_of(df[[qcol]].values, y),
                corr_Q_residual=float(np.corrcoef(df[qcol].values, res3)[0, 1]),
                corr_Q=dict(k=float(np.corrcoef(df[qcol], df.mean_degree)[0, 1]),
                            het=float(np.corrcoef(df[qcol], df.hetero)[0, 1]),
                            C=float(np.corrcoef(df[qcol], df.clustering)[0, 1])),
                Q_range=(float(df[qcol].min()), float(df[qcol].max())))


out = dict(synthetic=block(pool, "Q"), synthetic_louvain=block(pool, "Q_louvain"),
           empirical=block(rw, "Q"), empirical_louvain=block(rw, "Q_louvain"),
           checks=dict(synthetic_n=len(pool), synthetic_mismatch=mism, empirical_n=len(rw), empirical_mismatch=rmism),
           empirical_Q={m: float(q) for m, q in zip(rw.model, rw.Q)},
           synthetic_Q_by_family=pool.groupby("model").Q.agg(["mean", "min", "max"]).to_dict("index"))
json.dump(out, open(os.path.join(R, "modularity.json"), "w"), indent=1, default=float)
pool.to_csv(os.path.join(R, "modularity_per_graph.csv"), index=False)
rw[["model", "N", "mean_degree", "hetero", "clustering", "Q", "Q_louvain", "rasr_mean"]].to_csv(
    os.path.join(R, "modularity_empirical.csv"), index=False)

for k in ("synthetic", "synthetic_louvain", "empirical", "empirical_louvain"):
    b = out[k]; q = b["withQ"]["Q"]
    print(f"\n{k}: R2 {b['base']['R2']:.4f} -> {b['withQ']['R2']:.4f} (dR2 {b['dR2']:+.4f}); "
          f"LOO {b['base']['R2_loo']:.4f} -> {b['withQ']['R2_loo']:.4f}")
    print(f"  Q coef {q['coef']:+.2f} CI [{q['ci'][0]:+.2f},{q['ci'][1]:+.2f}] p={q['p']:.3g} "
          f"partial r {q['partial_r']:+.3f} VIF {q['vif']:.2f}; Q alone R2 {b['Q_alone_R2']:.3f}; "
          f"corr(Q,resid) {b['corr_Q_residual']:+.3f}; corr {b['corr_Q']}; range {b['Q_range']}")
    for t in ("k", "het", "C"):
        c = b["withQ"][t]
        print(f"   {t}: {c['coef']:+.2f} p={c['p']:.3g} VIF {c['vif']:.2f}")
print(out["synthetic_Q_by_family"])
print(out["empirical_Q"])
