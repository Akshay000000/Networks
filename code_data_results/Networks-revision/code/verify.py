import sys, time, numpy as np
sys.path.insert(0, sys.argv[1])
import phase4_complete as p4
from multiprocessing import Pool
from scipy.stats.qmc import Sobol
nets = p4.get_networks()
def rasr_ms(G, seq, pv, pool, K=512, seed=42):
    pts = Sobol(d=len(seq), scramble=True, seed=seed).random(K)
    st = (pts <= np.array(pv)).tolist()
    v = np.array(pool.map(p4._worker, [(G, seq, s) for s in st]))*100
    return v.mean(), v.std(ddof=1), v.std(ddof=0)
t=time.time()
with Pool() as pool:
    for n,G in nets.items():
        seqs={"HBnnsAGP":p4.get_attack_sequence_hbnnagp(G,16,8),"HBA":p4.get_attack_sequence_hba(G),"HDA":p4.get_attack_sequence_hda(G),"RF":p4.get_attack_sequence_rf(G)}
        for s,seq in seqs.items():
            row=[]
            for lab,a in [("100",1.0),("80",.8),("60",.6),("50",.5),("rand",None)]:
                pv=p4.make_random_asr_vector(seq) if a is None else p4.make_asr_vector(seq,a)
                m,sd1,sd0=rasr_ms(G,seq,pv,pool)
                row.append(f"{lab}:{m:.2f}±{sd1:.2f}/{sd0:.2f}")
            print(f"{n[:12]:12s} {s:9s}", " ".join(row), flush=True)
print("secs",time.time()-t)
