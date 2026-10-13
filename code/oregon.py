import sys,os,gzip,time,json,numpy as np,networkx as nx
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import phase4_complete as p4
f,out=sys.argv[1],sys.argv[2]
G=nx.Graph()
with gzip.open(f,"rt") as fh:
    for l in fh:
        if l.startswith("#"): continue
        a,b=l.split()[:2]; G.add_edge(int(a),int(b))
G.remove_edges_from(nx.selfloop_edges(G)); G=G.subgraph(max(nx.connected_components(G),key=len)).copy()
d=[x for _,x in G.degree()]; m=float(np.mean(d))
R=dict(N=G.number_of_nodes(),M=G.number_of_edges(),mean_degree=m,hetero=max(d)/m,clustering=nx.average_clustering(G))
print(R,flush=True)
def anc(c): return float(np.mean([y for _,y in c]))
t=time.time(); seq=p4.get_attack_sequence_hda(G); R["rasr_HDA"]=p4.compute_ANCw(G,seq,[True]*len(seq))*100; R["t_hda_rasr"]=time.time()-t; print(R,flush=True)
t=time.time(); seq=p4.get_attack_sequence_hbnnagp(G,16,8); R["t_hb_seq"]=time.time()-t
R["rasr_HBnnsAGP"]=p4.compute_ANCw(G,seq,[True]*len(seq))*100; print(R,flush=True)
t=time.time(); R["anc_HDA"]=anc(p4.adaptive_degree_attack(G)); R["anc_RF"]=anc(p4.simulate_random_attack(G)); R["t_det"]=time.time()-t
R["gap"]=R["anc_RF"]-R["anc_HDA"]; print(R,flush=True)
json.dump(R,open(out,"w"),indent=1)
