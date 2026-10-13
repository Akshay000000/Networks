#!/usr/bin/env python3
"""
Build the empirical-network pickles used by driver.py ("real" study).

Usage: python prepare_networks.py <data_dir> <out_dir>

<data_dir> must contain:
  sampson/sampson.##d          UCINET binary, 10 relations x 18 x 18 float32
  eies/EIES.2                  32 x 32 acquaintance matrix, time 2, codes 1..4
  jazz_edges.txt               edge list parsed from Jazz-Musicians-Network.wl
  facebook/698.edges, 414.edges  SNAP ego-Facebook
  Power.txt                    US power grid, GML
  dolphins.gml football.gml celegansneural.gml polblogs.gml ca-netscience.mtx
  inf-USAir97.mtx              USAir97, Matrix Market (UF Sparse Matrix Collection, Pajek/USAir97)

Writes <out_dir>/real_graphs.pkl (the 10 networks of results_real16.csv: four
NetworkX networks plus the six added ones) and <out_dir>/ext/real_graphs.pkl
(the six benchmark files).
"""
import os, pickle, re, sys
import networkx as nx
import numpy as np

D, OUT = sys.argv[1], sys.argv[2]


def lcc(G):
    G = nx.Graph(G.to_undirected()) if G.is_directed() else nx.Graph(G)
    G.remove_edges_from(nx.selfloop_edges(G))
    return G.subgraph(max(nx.connected_components(G), key=len)).copy()


def gml(path):
    """Read GML that may contain duplicate edges (C. elegans, political blogs)."""
    t = open(path).read()
    t = re.sub(r"(\n\s*directed\s+\d)", r"\1\n  multigraph 1", t, count=1)
    return nx.parse_gml(t, label="id")


g = {}
g["florentine"] = lcc(nx.florentine_families_graph())
g["davis"] = lcc(nx.davis_southern_women_graph())
g["karate"] = lcc(nx.karate_club_graph())
g["lesmis"] = lcc(nx.les_miserables_graph())

# Sampson: relation 3 = SAMPLK3 (liking, third wave); tie if either names the other
a = np.fromfile(os.path.join(D, "sampson", "sampson.##d"), dtype="<f4").reshape(10, 18, 18)[2]
G = nx.Graph(); G.add_nodes_from(range(18))
G.add_edges_from((i, j) for i in range(18) for j in range(18) if i != j and (a[i, j] > 0 or a[j, i] > 0))
g["sampson"] = lcc(G)

# EIES (32 researchers, time 2): tie if either reports "met" (3) or "friend" (4)
M = np.loadtxt(os.path.join(D, "eies", "EIES.2"))
G = nx.Graph(); G.add_nodes_from(range(32))
G.add_edges_from((i, j) for i in range(32) for j in range(32) if i != j and (M[i, j] >= 3 or M[j, i] >= 3))
g["eies"] = lcc(G)

g["jazz"] = lcc(nx.read_edgelist(os.path.join(D, "jazz_edges.txt"), nodetype=int))

# Facebook ego networks: ego-alter edges are implicit in SNAP files, so restore them
for e in (698, 414):
    G = nx.read_edgelist(os.path.join(D, "facebook", f"{e}.edges"), nodetype=int)
    for n in list(G.nodes()):
        G.add_edge(e, n)
    g[f"fb{e}"] = lcc(G)

g["powergrid"] = lcc(nx.read_gml(os.path.join(D, "Power.txt"), label="id"))

ext = {}
ext["dolphins"] = lcc(gml(os.path.join(D, "dolphins.gml")))
ext["football"] = lcc(gml(os.path.join(D, "football.gml")))
ext["celegans"] = lcc(gml(os.path.join(D, "celegansneural.gml")))
G = nx.Graph()
G.add_edges_from(tuple(map(int, l.split()[:2])) for l in open(os.path.join(D, "ca-netscience.mtx"))
                 if l.strip() and not l.startswith("%"))
ext["netscience"] = lcc(G)
ext["polblogs"] = lcc(gml(os.path.join(D, "polblogs.gml")))
import scipy.io
G = nx.from_scipy_sparse_array(scipy.io.mmread(os.path.join(D, "inf-USAir97.mtx")))
for u, v in G.edges():
    G[u][v].clear()                       # drop flight weights: unweighted graph
ext["usair"] = lcc(G)

os.makedirs(os.path.join(OUT, "ext"), exist_ok=True)
pickle.dump(g, open(os.path.join(OUT, "real_graphs.pkl"), "wb"))
pickle.dump(ext, open(os.path.join(OUT, "ext", "real_graphs.pkl"), "wb"))
for k, G in {**g, **ext}.items():
    d = [x for _, x in G.degree()]
    print(f"{k:11s} N={G.number_of_nodes():5d} M={G.number_of_edges():6d} "
          f"<k>={np.mean(d):.2f} het={max(d)/np.mean(d):.2f} C={nx.average_clustering(G):.3f}")
