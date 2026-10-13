import sys, os, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows=["Karate (Real)","Scale-Free (BA)","Small-World (WS)","Random (ER)"]
cols=["ASR=100%","ASR=80%","ASR=60%","ASR=50%","Rand. ASR"]
# phase4_complete.py single-instance means (seed 42, K=512), HBnnsAGP
M=np.array([[12.86,28.38,47.18,57.01,28.24],[12.27,26.67,45.21,55.99,23.81],
            [24.71,40.01,57.56,66.76,40.15],[28.07,44.43,61.49,69.71,44.36]])
fig,ax=plt.subplots(figsize=(10,4.3))
im=ax.imshow(M,cmap="RdYlGn_r",aspect="auto",vmin=10,vmax=75)
ax.set_xticks(range(5)); ax.set_xticklabels(cols,fontsize=12); ax.set_yticks(range(4)); ax.set_yticklabels(rows,fontsize=12)
for i in range(4):
    for j in range(5):
        v=M[i,j]; ax.text(j,i,f"{v:.1f}",ha="center",va="center",fontsize=13,fontweight="bold",color="white" if v<20 or v>62 else "black")
ax.set_title("RASR under HBnnsAGP, single instances at N = 34\n(lower = more fragile)",fontsize=12)
plt.colorbar(im,ax=ax,label="RASR ×100 (lower = more fragile)")
fig.savefig(sys.argv[1],dpi=200,bbox_inches="tight",facecolor="white")
