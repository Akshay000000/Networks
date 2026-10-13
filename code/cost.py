import sys,os,time,json,numpy as np,networkx as nx
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import phase4_complete as p4
from multiprocessing import Pool
from scipy.stats.qmc import Sobol
out={}
with Pool() as pool:
    for N in (34,100,200,500,1000):
        G=nx.barabasi_albert_graph(N,2,seed=1000)
        t=time.time(); seq=p4.get_attack_sequence_hbnnagp(G,16,8); ts=time.time()-t
        t=time.time(); p4.compute_ANCw(G,seq,[True]*N); t1=time.time()-t
        t=time.time(); st=(Sobol(d=N,scramble=True,seed=90000).random(512)<=0.6).tolist(); pool.map(p4._worker,[(G,seq,s) for s in st]); tk=time.time()-t
        out[N]=dict(seq=ts,anc_100=t1,prqmc_60=tk); print(N,out[N],flush=True)
json.dump(out,open(sys.argv[1],"w"),indent=1)
