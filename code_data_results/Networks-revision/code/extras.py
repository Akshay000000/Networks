import sys, os, json, numpy as np, networkx as nx
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phase4_complete as p4
from scipy.stats.qmc import Sobol
R=sys.argv[1]; out={}
def lcc(G): return G.subgraph(max(nx.connected_components(G),key=len)).copy()
def anc(c): return float(np.mean([y for _,y in c]))
# deterministic scalability, 10 realizations, mean degree ~4 for every family
det={}
for N in (34,100,500,1000):
    det[N]={}
    for m in ("BA","WS","ER"):
        h=[];g=[];k=[]
        for rep in range(10):
            s=1000+rep
            G={"BA":lambda:nx.barabasi_albert_graph(N,2,seed=s),"WS":lambda:nx.watts_strogatz_graph(N,4,0.3,seed=s),
               "ER":lambda:nx.erdos_renyi_graph(N,4.0/(N-1),seed=s)}[m]()
            G=lcc(G); hd=anc(p4.adaptive_degree_attack(G)); rf=anc(p4.simulate_random_attack(G,seed=s))
            h.append(hd); g.append(rf-hd); k.append(2*G.number_of_edges()/G.number_of_nodes())
        det[N][m]=dict(hda=np.mean(h),hda_sd=np.std(h,ddof=1),gap=np.mean(g),gap_sd=np.std(g,ddof=1),k=np.mean(k))
    print(N,{m:(round(v['hda'],4),round(v['gap'],4),round(v['k'],2)) for m,v in det[N].items()},flush=True)
out["det_scal"]=det
# karate heterogeneous ASR over 10 independent draws (runner seeds), HBnnsAGP
G=lcc(nx.karate_club_graph()); seq=p4.get_attack_sequence_hbnnagp(G,16,8); vals=[]
for rep in range(10):
    pv=np.random.default_rng(50000+rep).uniform(0.5,1.0,size=len(seq))
    st=(Sobol(d=len(seq),scramble=True,seed=90000+rep).random(512)<=pv).tolist()
    vals.append(np.mean([p4.compute_ANCw(G,seq,s) for s in st])*100)
out["karate_rand10"]=dict(mean=float(np.mean(vals)),sd=float(np.std(vals,ddof=1)),vals=[float(v) for v in vals])
print(out["karate_rand10"])
json.dump(out,open(os.path.join(R,"extras.json"),"w"),indent=1,default=float)
