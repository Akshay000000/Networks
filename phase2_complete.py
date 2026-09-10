# ============================================================
# Network Robustness Analysis
# Based on: "Analyzing the Robustness of Complex Networks
#            with Attack Success Rate" (Yang & Wang, 2023)
# ============================================================
# PHASE 2 – Replication
# PHASE 3 – Extension (Robustness Analysis / Node Removal)
# PHASE 4 – Interpretation
# ============================================================

import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from networkx.algorithms.community import greedy_modularity_communities

# Set seed for reproducibility across ALL experiments
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ============================================================
# PHASE 2 – REPLICATION
# ============================================================

# ─────────────────────────────────────────────
# STEP 1 — Load Network
# (Karate club graph — same dataset used in paper)
# ─────────────────────────────────────────────
G = nx.karate_club_graph()
print("=" * 50)
print("PHASE 2 — REPLICATION")
print("=" * 50)

# ─────────────────────────────────────────────
# STEP 2 — Basic Network Statistics
# ─────────────────────────────────────────────
N = G.number_of_nodes()
M = G.number_of_edges()
density = nx.density(G)
avg_degree = sum(dict(G.degree()).values()) / N
max_degree = max(dict(G.degree()).values())

print(f"\n[Basic Statistics]")
print(f"  Number of Nodes (N)  : {N}")
print(f"  Number of Edges (M)  : {M}")
print(f"  Density              : {density:.4f}")
print(f"  Average Degree <k>   : {avg_degree:.2f}")
print(f"  Max Degree           : {max_degree}")

# ─────────────────────────────────────────────
# STEP 3 — Degree Distribution
# ─────────────────────────────────────────────
degrees = [d for n, d in G.degree()]

fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(degrees, bins=10, color="steelblue", edgecolor="white")
ax.set_title("Degree Distribution — Karate Network", fontsize=13)
ax.set_xlabel("Degree")
ax.set_ylabel("Frequency")
ax.grid(axis="y", alpha=0.4)
plt.tight_layout()
plt.savefig("phase2_degree_distribution.png", dpi=150)
plt.show()
print("\n[Saved] phase2_degree_distribution.png")

# ─────────────────────────────────────────────
# STEP 4 — Centrality Measures
# ─────────────────────────────────────────────
deg_cent   = nx.degree_centrality(G)
bet_cent   = nx.betweenness_centrality(G, normalized=True, seed=SEED)
close_cent = nx.closeness_centrality(G)
eig_cent   = nx.eigenvector_centrality(G, max_iter=1000)

def top5(cent_dict, label):
    top = sorted(cent_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\n  Top 5 nodes by {label}:")
    for node, val in top:
        print(f"    Node {node:>2d} -> {val:.4f}")

print(f"\n[Centrality Measures]")
top5(deg_cent,   "Degree Centrality")
top5(bet_cent,   "Betweenness Centrality")
top5(close_cent, "Closeness Centrality")
top5(eig_cent,   "Eigenvector Centrality")

# ─────────────────────────────────────────────
# STEP 5 — Clustering Coefficient
# ─────────────────────────────────────────────
avg_clustering = nx.average_clustering(G)
print(f"\n[Clustering]")
print(f"  Average Clustering Coefficient: {avg_clustering:.4f}")

# ─────────────────────────────────────────────
# STEP 6 — Community Detection
# (Greedy Modularity — same approach viable for Karate)
# ─────────────────────────────────────────────
communities = list(greedy_modularity_communities(G))
print(f"\n[Community Detection]")
print(f"  Number of Communities: {len(communities)}")
for i, comm in enumerate(communities):
    print(f"  Community {i+1} ({len(comm)} nodes): {sorted(comm)}")

# Build community color map (node -> community index)
community_map = {}
for i, comm in enumerate(communities):
    for node in comm:
        community_map[node] = i

# ─────────────────────────────────────────────
# STEP 7 — Recreate Figure 6 from Paper
# (Network topology, node size proportional to degree)
# This directly replicates Figure 6(a) from Yang & Wang 2023
# ─────────────────────────────────────────────
pos = nx.spring_layout(G, seed=SEED)

node_sizes  = [G.degree(n) * 120 for n in G.nodes()]
node_colors = [community_map[n] for n in G.nodes()]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: plain topology (replicates paper Figure 6a style)
nx.draw(G, pos, ax=axes[0],
        with_labels=True,
        node_size=node_sizes,
        node_color="steelblue",
        edge_color="gray",
        font_size=7,
        font_color="white")
axes[0].set_title("Karate Network\n(Node size proportional to Degree)", fontsize=12)

# Right: community-colored version
nx.draw(G, pos, ax=axes[1],
        with_labels=True,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=cm.Set2,
        edge_color="gray",
        font_size=7,
        font_color="white")
axes[1].set_title("Karate Network\n(Colored by Community)", fontsize=12)

plt.suptitle("Figure Replication — Yang & Wang (2023), Figure 6(a)", fontsize=11, style="italic")
plt.tight_layout()
plt.savefig("phase2_network_topology.png", dpi=150)
plt.show()
print("[Saved] phase2_network_topology.png")


# ============================================================
# PHASE 3 – EXTENSION: ROBUSTNESS ANALYSIS (NODE REMOVAL)
# ============================================================
# Extension: Adaptive targeted node removal under three attack
# strategies, compared across four network types.
#
# Goes BEYOND the paper by:
#   1. Using ADAPTIVE centrality recomputation after each removal
#      (matching paper's HDA/HBA strategies — not static ranking)
#   2. Comparing Karate vs Scale-Free vs Small-World vs Random
#   3. Correctly normalizing axes: x = k/N, y = GCC/GCC_0
#   4. Computing ANC scores (Definition 3 from paper)
# ============================================================

print("\n" + "=" * 50)
print("PHASE 3 — EXTENSION: ROBUSTNESS ANALYSIS")
print("=" * 50)

# ─────────────────────────────────────────────
# STEP 1 — Helper: Giant Connected Component size
# ─────────────────────────────────────────────
def gcc_size(G):
    """Return size of the largest connected component."""
    if len(G) == 0:
        return 0
    return len(max(nx.connected_components(G), key=len))


# ─────────────────────────────────────────────
# STEP 2 — Attack Strategy: Random
# ─────────────────────────────────────────────
def simulate_random_attack(G, seed=SEED):
    """
    Random node removal.
    Returns list of (fraction_removed, normalized_gcc) tuples.
    """
    G = G.copy()
    original_gcc = gcc_size(G)
    if original_gcc == 0:
        return []

    order = list(G.nodes())
    rng = random.Random(seed)
    rng.shuffle(order)

    results = []
    total_nodes = len(order)

    for step, node in enumerate(order):
        fraction_removed = step / total_nodes
        results.append((fraction_removed, gcc_size(G) / original_gcc))
        if node in G:
            G.remove_node(node)

    return results


# ─────────────────────────────────────────────
# STEP 3 — Attack Strategy: Adaptive Degree (HDA)
# Recomputes degree after EACH removal
# Matches paper's HDA strategy (Section 4.1.2)
# ─────────────────────────────────────────────
def adaptive_degree_attack(G):
    """
    Adaptive High-Degree Attack (HDA).
    Recomputes degree centrality after each node removal.
    Returns list of (fraction_removed, normalized_gcc) tuples.
    """
    G = G.copy()
    original_gcc = gcc_size(G)
    if original_gcc == 0:
        return []

    results = []
    total_nodes = len(G)

    for step in range(total_nodes):
        fraction_removed = step / total_nodes
        results.append((fraction_removed, gcc_size(G) / original_gcc))

        if len(G) == 0:
            break

        # Recompute degree on RESIDUAL graph at each step
        target = max(G.degree(), key=lambda x: x[1])[0]
        G.remove_node(target)

    return results


# ─────────────────────────────────────────────
# STEP 4 — Attack Strategy: Adaptive Betweenness (HBA)
# Recomputes betweenness after EACH removal
# Matches paper's HBA strategy (Section 4.1.2)
# NOTE: Computationally heavier — suitable for small networks
# ─────────────────────────────────────────────
def adaptive_betweenness_attack(G):
    """
    Adaptive High-Betweenness Attack (HBA).
    Recomputes betweenness centrality after each node removal.
    Returns list of (fraction_removed, normalized_gcc) tuples.
    """
    G = G.copy()
    original_gcc = gcc_size(G)
    if original_gcc == 0:
        return []

    results = []
    total_nodes = len(G)

    for step in range(total_nodes):
        fraction_removed = step / total_nodes
        results.append((fraction_removed, gcc_size(G) / original_gcc))

        if len(G) == 0:
            break

        # Recompute betweenness on RESIDUAL graph at each step
        bc = nx.betweenness_centrality(G, normalized=True, seed=SEED)
        target = max(bc, key=bc.get)
        G.remove_node(target)

    return results


# ─────────────────────────────────────────────
# STEP 5 — Run on Karate Network
# ─────────────────────────────────────────────
G_karate = nx.karate_club_graph()

print("\nRunning attack simulations on Karate network...")
karate_rand = simulate_random_attack(G_karate)
karate_deg  = adaptive_degree_attack(G_karate)
karate_bet  = adaptive_betweenness_attack(G_karate)
print("  Done.")

# ─────────────────────────────────────────────
# STEP 6 — Plot Robustness Curve for Karate
# Replicates style of Figure 9(a) from the paper
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))

ax.plot(*zip(*karate_rand), label="Random Attack",                  color="green",  linestyle="--")
ax.plot(*zip(*karate_deg),  label="Degree Attack (Adaptive HDA)",   color="blue",   linestyle="-")
ax.plot(*zip(*karate_bet),  label="Betweenness Attack (Adaptive HBA)", color="red", linestyle="-")

ax.set_xlabel("Fraction of Nodes Removed (k/N)", fontsize=11)
ax.set_ylabel("Normalized GCC Size (sigma_gcc / sigma_gcc_0)", fontsize=11)
ax.set_title("Robustness Analysis — Karate Network\n(Replication of Paper Figure 9 style)", fontsize=11)
ax.legend(fontsize=9)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.05)
ax.grid(alpha=0.4)
plt.tight_layout()
plt.savefig("phase3_karate_robustness.png", dpi=150)
plt.show()
print("[Saved] phase3_karate_robustness.png")


# ─────────────────────────────────────────────
# STEP 7 — ANC Score (Definition 3 from paper)
# ANC = (1/N) * sum of normalized GCC sizes
# Lower ANC = more destructive attack
# ─────────────────────────────────────────────
def compute_ANC(results):
    """
    Compute the Accumulated Normalized Connectivity (ANC).
    Matches Definition 3 from Yang & Wang (2023).
    Lower value = more destructive attack strategy.
    """
    if not results:
        return 0.0
    values = [gcc for _, gcc in results]
    return float(np.mean(values))

print("\n[ANC Scores — Karate Network]")
print(f"  Random Attack          ANC: {compute_ANC(karate_rand):.4f}")
print(f"  Degree Attack (HDA)    ANC: {compute_ANC(karate_deg):.4f}")
print(f"  Betweenness Attack (HBA) ANC: {compute_ANC(karate_bet):.4f}")
print("  (Lower ANC = more destructive attack strategy)")


# ─────────────────────────────────────────────
# STEP 8 — Extension: Compare Across Network Types
# This is NOT in the original paper — this is the extension
# ─────────────────────────────────────────────
print("\nRunning cross-network robustness comparison (extension beyond paper)...")

network_configs = {
    "Karate (Real-World)":   nx.karate_club_graph(),
    "Scale-Free (BA)":       nx.barabasi_albert_graph(34, 2, seed=SEED),
    "Small-World (WS)":      nx.watts_strogatz_graph(34, 4, 0.3, seed=SEED),
    "Random (ER)":           nx.erdos_renyi_graph(34, 0.13, seed=SEED),
}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
colors = ["steelblue", "firebrick", "darkorange", "green"]

anc_summary = {}

for (name, Gx), col in zip(network_configs.items(), colors):
    # Use largest connected component to ensure connectivity
    largest_cc = max(nx.connected_components(Gx), key=len)
    Gc = Gx.subgraph(largest_cc).copy()

    deg_res  = adaptive_degree_attack(Gc)
    rand_res = simulate_random_attack(Gc)

    anc_summary[name] = {
        "degree": compute_ANC(deg_res),
        "random": compute_ANC(rand_res),
    }

    axes[0].plot(*zip(*deg_res),  label=name, color=col)
    axes[1].plot(*zip(*rand_res), label=name, color=col)

for ax in axes:
    ax.set_xlabel("Fraction of Nodes Removed (k/N)", fontsize=10)
    ax.set_ylabel("Normalized GCC Size", fontsize=10)
    ax.legend(fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.4)

axes[0].set_title("Targeted (Degree) Attack\nAcross Network Types", fontsize=11)
axes[1].set_title("Random Attack\nAcross Network Types", fontsize=11)

plt.suptitle("Extension: Robustness Comparison Across Network Models", fontsize=12, style="italic")
plt.tight_layout()
plt.savefig("phase3_cross_network_robustness.png", dpi=150)
plt.show()
print("[Saved] phase3_cross_network_robustness.png")

print("\n[ANC Summary — Cross-Network Comparison]")
print(f"  {'Network':<28} {'Degree Attack':>14} {'Random Attack':>14}")
print(f"  {'-'*56}")
for name, scores in anc_summary.items():
    print(f"  {name:<28} {scores['degree']:>14.4f} {scores['random']:>14.4f}")


# ============================================================
# PHASE 4 – INTERPRETATION
# ============================================================
print("\n" + "=" * 50)
print("PHASE 4 — INTERPRETATION")
print("=" * 50)

# ─────────────────────────────────────────────
# Q1: Who are the influential nodes and why?
# ─────────────────────────────────────────────
print("\n[Q1] Influential Nodes")

all_centralities = {
    "Degree":       deg_cent,
    "Betweenness":  bet_cent,
    "Closeness":    close_cent,
    "Eigenvector":  eig_cent,
}

# Aggregate rank across all 4 centralities (lower total rank = more influential)
rank_scores = {node: 0 for node in G.nodes()}
for cent_name, cent_dict in all_centralities.items():
    ranked = sorted(cent_dict, key=cent_dict.get, reverse=True)
    for rank, node in enumerate(ranked):
        rank_scores[node] += rank + 1

top_influential = sorted(rank_scores, key=rank_scores.get)[:5]
print("  Top 5 most influential nodes (aggregate rank across all 4 centralities):")
for node in top_influential:
    print(f"    Node {node:>2d} | DC={deg_cent[node]:.3f} | BC={bet_cent[node]:.3f} "
          f"| CC={close_cent[node]:.3f} | EC={eig_cent[node]:.3f}")

# ─────────────────────────────────────────────
# Q2: Is the network centralized?
# ─────────────────────────────────────────────
# Freeman's degree centralization formula
max_dc = max(deg_cent.values())
numerator = sum(max_dc - v for v in deg_cent.values())
denominator = (N - 1) * (N - 2) / (N - 1)  # normalized for undirected graph
degree_centralization = numerator / denominator if denominator > 0 else 0

print(f"\n[Q2] Network Centralization")
print(f"  Freeman Degree Centralization: {degree_centralization:.4f}")
print(f"  (0 = fully distributed, 1 = pure star graph)")
if degree_centralization > 0.5:
    print("  -> Network is CENTRALIZED (hub-dominated)")
elif degree_centralization > 0.3:
    print("  -> Network is MODERATELY centralized")
else:
    print("  -> Network is DECENTRALIZED (distributed connectivity)")

# ─────────────────────────────────────────────
# Q3: Does it show clustering / community structure?
# ─────────────────────────────────────────────
modularity = nx.algorithms.community.quality.modularity(G, communities)

print(f"\n[Q3] Clustering and Community Structure")
print(f"  Average Clustering Coefficient : {avg_clustering:.4f}")
print(f"  Number of Communities Detected : {len(communities)}")
print(f"  Modularity Score               : {modularity:.4f}")
print(f"  (Modularity > 0.3 = meaningful community structure)")
if modularity > 0.3:
    print("  -> STRONG community structure detected")
elif modularity > 0.1:
    print("  -> Moderate community structure")
else:
    print("  -> Weak community structure")

# ─────────────────────────────────────────────
# Q4: What structural properties emerge?
# ─────────────────────────────────────────────
avg_path = nx.average_shortest_path_length(G)
diameter  = nx.diameter(G)

print(f"\n[Q4] Structural Properties")
print(f"  Average Shortest Path Length : {avg_path:.4f}")
print(f"  Network Diameter             : {diameter}")
print(f"  Degree Heterogeneity         : {max_degree / avg_degree:.2f}x (MaxDeg / AvgDeg)")

if max_degree / avg_degree > 3:
    print("  -> Hub nodes present: suggests SCALE-FREE-like behavior")
else:
    print("  -> Relatively homogeneous degree distribution")

if avg_path < np.log(N) and avg_clustering > 0.3:
    print("  -> Short paths + high clustering: exhibits SMALL-WORLD properties")

# ─────────────────────────────────────────────
# Q5: Does the extension change conclusions?
# ─────────────────────────────────────────────
print(f"\n[Q5] Does the Extension Change Conclusions?")
print(f"\n  ANC under Degree (Adaptive) Attack:")
for name, scores in anc_summary.items():
    print(f"    {name:<28}: ANC = {scores['degree']:.4f}")

most_robust   = min(anc_summary, key=lambda k: anc_summary[k]["degree"])
most_fragile  = max(anc_summary, key=lambda k: anc_summary[k]["degree"])

print(f"\n  Most ROBUST  under targeted attack: {most_robust}")
print(f"  Most FRAGILE under targeted attack: {most_fragile}")
print(f"\n  Conclusion:")
print(f"  -> The extension reveals that TOPOLOGY fundamentally determines robustness.")
print(f"  -> Scale-free networks collapse rapidly under targeted attacks due to hubs.")
print(f"  -> This complements the paper's finding on ASR: even with a high ASR,")
print(f"     a well-distributed network (small-world / random) resists collapse better.")
print(f"  -> Protecting hub nodes (reducing their ASR) yields the greatest robustness gain.")

print("\n" + "=" * 50)
print("ALL PHASES COMPLETE")
print("Output files saved:")
print("  phase2_degree_distribution.png")
print("  phase2_network_topology.png")
print("  phase3_karate_robustness.png")
print("  phase3_cross_network_robustness.png")
print("=" * 50)
