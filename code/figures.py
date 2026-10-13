#!/usr/bin/env python3
"""Figures for the CONNET-2026-191 revision, built from the result CSVs and numbers.json."""
import json, os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R, OUTDIR = sys.argv[1], sys.argv[2]
N = json.load(open(os.path.join(R, "numbers.json")))
X = json.load(open(os.path.join(R, "extras.json")))
COL = {"BA": "#2a78d6", "WS": "#eb6834", "ER": "#1baf7a", "Karate": "#eda100", "real": "#555555"}
MK = {"BA": "o", "WS": "s", "ER": "^", "Karate": "D"}
NAME = {"BA": "Scale-free (BA)", "WS": "Small-world (WS)", "ER": "Random (ER)", "Karate": "Karate"}
INK, MUTED, GRID = "#222222", "#666666", "#e3e3e0"
plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "legend.frameon": False, "savefig.dpi": 300})


def save(fig, name):
    fig.savefig(os.path.join(OUTDIR, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


# ---------------------------------------------------------------- rank stability
rz = N["realizations"]
labs = ["100", "80", "60", "50", "rand"]
xt = ["100%", "80%", "60%", "50%", "Random\n[0.5, 1]"]
fig, ax = plt.subplots(figsize=(6.2, 3.0))
x = np.arange(len(labs)); w = 0.36
four = [rz[a]["four_way_pct"] for a in labs]; two = [rz[a]["two_group_pct"] for a in labs]
b1 = ax.bar(x - w / 2 - 0.01, four, w, color="#9a9a96", label="Four-class ordering (BA < Karate < WS < ER)")
b2 = ax.bar(x + w / 2 + 0.01, two, w, color=COL["BA"], label="Two-group separation ({BA, Karate} < {WS, ER})")
for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 1.5, f"{r.get_height():.0f}",
                ha="center", va="bottom", fontsize=8, color=INK)
ax.set_xticks(x); ax.set_xticklabels(xt); ax.set_ylim(0, 112)
ax.set_ylabel("Realizations in which\nordering holds (%)"); ax.set_xlabel("Attack success rate")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=1, fontsize=8)
ax.grid(axis="x", visible=False)
save(fig, "fig_rank_stability.png")

# ---------------------------------------------------------------- parameter sweep
sw = N["sweep"]
fig, ax = plt.subplots(figsize=(6.2, 3.2))
rows = []
for key, v in sw.items():
    m, p = key.split("|")
    rows.append((m, p, v["rasr"], v["sd"], v["k"]))
for m, yoff in (("BA", 2), ("WS", 1), ("ER", 0)):
    pts = [r for r in rows if r[0] == m]
    ks = np.array([r[4] for r in pts]); rs = np.array([r[2] for r in pts]); sds = np.array([r[3] for r in pts])
    ax.errorbar(ks, rs, yerr=sds, fmt=MK[m], ms=6, color=COL[m], ecolor=COL[m], elinewidth=1,
                capsize=0, mec="white", mew=0.8, label=NAME[m], lw=0)
ax.set_xlabel(r"Mean degree $\langle k\rangle$ (realized)")
ax.set_ylabel(r"RASR$\times$100 at ASR = 100%")
ax.legend(loc="lower right", fontsize=8)
save(fig, "fig_parameter_sweep.png")

# ---------------------------------------------------------------- R2 ladder
L = N["pooled"]["ladder"]
names = ["Model label\nonly", r"$\langle k\rangle$ only", r"$\langle k\rangle$ +" "\nheterogeneity",
         r"$\langle k\rangle$ + het." "\n+ clustering", "Structure\n+ model label"]
vals = [L["label"], L["k"], L["k_het"], L["k_het_C"], L["k_het_C_label"]]
cols = ["#9a9a96", "#9ec5f4", "#5598e7", COL["BA"], "#9ec5f4"]
fig, ax = plt.subplots(figsize=(6.2, 2.9))
bars = ax.bar(range(5), vals, 0.62, color=cols)
for r, v in zip(bars, vals):
    ax.text(r.get_x() + r.get_width() / 2, v + 0.015, f"{v:.3f}", ha="center", fontsize=8, color=INK)
ax.set_xticks(range(5)); ax.set_xticklabels(names, fontsize=8); ax.set_ylim(0, 1.05)
ax.set_ylabel(r"$R^2$ for RASR at ASR = 100%"); ax.grid(axis="x", visible=False)
save(fig, "fig_r2_bars.png")

# ---------------------------------------------------------------- LOO validation + coefficients
pool = pd.read_csv(os.path.join(R, "pooled_N34.csv"))
P = N["pooled"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.55))
for m in ["ER", "WS", "BA", "Karate"]:
    s = pool[pool.model == m]
    a1.scatter(s.rasr_mean, s.loo_pred, s=9 if m != "Karate" else 30, marker=MK[m], color=COL[m],
               alpha=0.65 if m != "Karate" else 1, lw=0, label=NAME[m])
lim = [min(pool.rasr_mean.min(), pool.loo_pred.min()) - 1, max(pool.rasr_mean.max(), pool.loo_pred.max()) + 1]
a1.plot(lim, lim, color=MUTED, lw=1, ls="--"); a1.set_xlim(lim); a1.set_ylim(lim)
a1.set_xlabel("Observed RASR"); a1.set_ylabel("Leave-one-out prediction")
a1.legend(fontsize=7, loc="upper left", markerscale=1.5)
terms = [("k", r"$\langle k\rangle$"), ("het", r"$k_{\max}/\langle k\rangle$"), ("C", "Clustering $C$")]
for i, (t, lab) in enumerate(terms):
    c = P[t]; lo, hi = c["ci"]
    a2.plot([lo, hi], [i, i], color=COL["BA"], lw=2)
    a2.plot(c["coef"], i, "o", color=COL["BA"], ms=6, mec="white")
    a2.text(c["coef"], i + 0.22, f"{c['coef']:.2f}", ha="center", fontsize=8, color=INK)
a2.axvline(0, color=MUTED, lw=1, ls="--")
a2.set_yticks(range(3)); a2.set_yticklabels([t[1] for t in terms]); a2.set_ylim(-0.6, 2.7)
a2.set_xlabel("Coefficient (95% CI)"); a2.grid(axis="y", visible=False)
save(fig, "fig_loo_validation.png")

# ---------------------------------------------------------------- real-world validation
rt = pd.DataFrame(N["real_table"])
pred = N["real_rwpred"]
LBL = {"florentine": "Florentine", "davis": "Davis", "karate": "Karate", "lesmis": "Les Mis.",
       "sampson": "Sampson", "eies": "EIES", "jazz": "Jazz", "fb698": "FB-698", "fb414": "FB-414",
       "powergrid": "Power grid", "usair": "USAir97", "dolphins": "Dolphins", "football": "Football",
       "celegans": "C. elegans", "netscience": "Netscience", "polblogs": "Pol. blogs"}
added = {"sampson", "eies", "jazz", "fb698", "fb414", "powergrid"}
fig, ax = plt.subplots(figsize=(5.2, 4.2))
for _, r in rt.iterrows():
    new = r.model in added
    ax.scatter(r.rasr_mean, pred[r.model], s=34, marker="s" if new else "o",
               color=COL["WS"] if new else COL["BA"], edgecolor="white", lw=0.8, zorder=3)
    off = {"eies": (4, 5), "sampson": (-10, -12), "karate": (-34, 4), "fb698": (5, -9), "lesmis": (4, -9),
           "netscience": (-8, -12), "usair": (4, -9), "florentine": (4, -3), "dolphins": (-44, 3)}.get(r.model, (4, 3))
    ax.annotate(LBL.get(r.model, r.model), (r.rasr_mean, pred[r.model]), xytext=off,
                textcoords="offset points", fontsize=7, color=INK)
lim = [0, max(rt.rasr_mean.max(), max(pred.values())) + 3]
ax.plot(lim, lim, color=MUTED, lw=1, ls="--"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel(r"Observed RASR$\times$100 (HBnnsAGP, ASR = 100%)")
ax.set_ylabel("Fitted value, three-variable model")
ax.scatter([], [], marker="o", color=COL["BA"], label="Ten networks of the first revision")
ax.scatter([], [], marker="s", color=COL["WS"], label="Six networks added")
ax.legend(fontsize=7, loc="upper left")
save(fig, "fig_realworld_validation.png")

# ---------------------------------------------------------------- scale study (RASR)
sc = N["scale"]
Ns = sorted(int(k) for k in sc)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.9))
for m in ["BA", "WS", "ER"]:
    y = [sc[str(n)][m]["rasr100"] for n in Ns]; e = [sc[str(n)][m]["sd100"] for n in Ns]
    a1.errorbar(Ns, y, yerr=e, marker=MK[m], color=COL[m], lw=2, ms=6, mec="white", capsize=0, label=NAME[m])
    h = [sc[str(n)][m]["het"] for n in Ns]
    a2.plot(Ns, h, marker=MK[m], color=COL[m], lw=2, ms=6, mec="white", label=NAME[m])
for a in (a1, a2):
    a.set_xscale("log"); a.set_xticks(Ns); a.set_xticklabels([str(n) for n in Ns]); a.set_xlabel("Network size $N$")
    a.minorticks_off()
a1.set_ylabel(r"RASR$\times$100 at ASR = 100%"); a2.set_ylabel(r"$k_{\max}/\langle k\rangle$")
a1.legend(fontsize=7, loc="best")
save(fig, "fig_scale_rasr.png")

# ---------------------------------------------------------------- deterministic scalability (replaces fig4)
d = X["det_scal"]; Ns2 = sorted(int(k) for k in d)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.9))
for m in ["BA", "WS", "ER"]:
    a1.errorbar(Ns2, [d[str(n)][m]["hda"] for n in Ns2], yerr=[d[str(n)][m]["hda_sd"] for n in Ns2],
                marker=MK[m], color=COL[m], lw=2, ms=6, mec="white", capsize=0, label=NAME[m])
    a2.errorbar(Ns2, [d[str(n)][m]["gap"] for n in Ns2], yerr=[d[str(n)][m]["gap_sd"] for n in Ns2],
                marker=MK[m], color=COL[m], lw=2, ms=6, mec="white", capsize=0, label=NAME[m])
for a in (a1, a2):
    a.set_xscale("log"); a.set_xticks(Ns2); a.set_xticklabels([str(n) for n in Ns2]); a.set_xlabel("Network size $N$")
    a.minorticks_off()
a1.set_ylabel("ANC under HDA"); a2.set_ylabel(r"$\Delta_{\mathrm{gap}}$ = ANC$_{\mathrm{RF}}$ $-$ ANC$_{\mathrm{HDA}}$")
a1.legend(fontsize=7)
save(fig, "fig4_scalability.png")
