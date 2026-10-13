#!/usr/bin/env python3
"""Write LaTeX table bodies for the revision from numbers.json / extras.json / CSVs."""
import json, os, sys
import pandas as pd

R, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
N = json.load(open(os.path.join(R, "numbers.json")))
X = json.load(open(os.path.join(R, "extras.json")))


def w(name, s):
    open(os.path.join(OUT, name + ".tex"), "w").write(s)


def f2(x): return f"{x:.2f}"


def pfmt(p):
    if p == 0:
        return "$<10^{-300}$"
    if p < 0.01:
        m, e = f"{p:.1e}".split("e")
        return f"${m}\\times10^{{{int(e)}}}$"
    if p < 1e-4:
        m, e = f"{p:.0e}".split("e")
        return f"${m}\\times10^{{{int(e)}}}$"
    return f"{p:.3f}" if p < 0.01 else f"{p:.2f}"


# --- single-instance SDs (phase4, seed 42, K=512), from verification run
si = {"Karate (Real)": [("28.38", "13.70"), ("47.18", "17.92"), ("57.01", "17.72"), ("28.24", "13.23")],
      "Scale-Free (BA)": [("26.67", "14.33"), ("45.21", "19.16"), ("55.99", "19.27"), ("23.81", "11.98")],
      "Small-World (WS)": [("40.01", "8.60"), ("57.56", "10.93"), ("66.76", "10.54"), ("40.15", "8.32")],
      "Random (ER)": [("44.43", "8.48"), ("61.49", "9.42"), ("69.71", "8.63"), ("44.36", "7.68")]}
w("tab_rasr_full", "\n".join(
    f"{k}\n  & " + "\n  & ".join(f"${m} \\pm {s}$" for m, s in v) + " \\\\" for k, v in si.items()))

# --- deterministic scalability (10 realizations, mean degree about 4)
d = X["det_scal"]
rows = []
for n in sorted(d, key=int):
    first = True
    for m, lab in (("BA", "Scale-Free (BA)"), ("WS", "Small-World (WS)"), ("ER", "Random (ER)")):
        v = d[n][m]
        lead = f"\\multirow{{3}}{{*}}{{{int(n):,}}}".replace(",", "{,}") if first else ""
        rows.append(f"{lead}  & {lab} & {v['k']:.2f} & ${v['hda']:.4f} \\pm {v['hda_sd']:.4f}$ & ${v['gap']:.4f} \\pm {v['gap_sd']:.4f}$ \\\\")
        first = False
    rows.append("\\hline")
w("tab_scalability", "\n".join(rows[:-1]))

# --- realization study
rz = N["realizations"]
labs = [("100", "100\\%"), ("80", "80\\%"), ("60", "60\\%"), ("50", "50\\%"), ("rand", "Rand.")]
rows = []
for a, la in labs:
    r = rz[a]
    rows.append(f"{la} & {r['BA']['mean']:.2f} [{r['BA']['lo']:.2f}, {r['BA']['hi']:.2f}] & "
                f"{r['WS']['mean']:.2f} [{r['WS']['lo']:.2f}, {r['WS']['hi']:.2f}] & "
                f"{r['ER']['mean']:.2f} [{r['ER']['lo']:.2f}, {r['ER']['hi']:.2f}] & {r['Karate']:.2f} \\\\")
w("tab_realization_means", "\n".join(rows))
rows = []
for a, la in labs:
    r = rz[a]
    rows.append(f"{la} & {r['four_way_pct']:.0f} & {r['two_group_pct']:.0f} & {r['BA_below_karate_pct']:.0f} & "
                f"{r['WS_below_ER_pct']:.0f} & {pfmt(r['MW_BA_WS_p'])} & {pfmt(r['MW_BA_ER_p'])} & {pfmt(r['MW_WS_ER_p'])} \\\\")
w("tab_rank_stability", "\n".join(rows))

# --- parameter sweep
sw = N["sweep"]
order = [("BA", ["m=1", "m=2", "m=3", "m=5"]), ("ER", ["p=0.08", "p=0.1", "p=0.13", "p=0.16", "p=0.2", "p=0.25"])]
rows = []
for m, ps in order:
    for p in ps:
        v = sw[f"{m}|N=34,{p}"]
        lab = {"BA": "Scale-Free (BA)", "ER": "Random (ER)"}[m]
        rows.append(f"{lab} & ${p.replace('p=', 'p=').replace('m=', 'm=')}$ & {v['k']:.2f} & {v['het']:.2f} & {v['C']:.3f} & ${v['rasr']:.2f} \\pm {v['sd']:.2f}$ \\\\")
    rows.append("\\hline")
for k in (4, 6, 8):
    for p in ("0.01", "0.05", "0.1", "0.3", "0.5", "1.0"):
        v = sw[f"WS|N=34,k={k},p={p}"]
        rows.append(f"Small-World (WS) & $k={k},\\,p={p}$ & {v['k']:.2f} & {v['het']:.2f} & {v['C']:.3f} & ${v['rasr']:.2f} \\pm {v['sd']:.2f}$ \\\\")
w("tab_sweep", "\n".join(rows))

# --- pooled regression
P = N["pooled"]
rows = []
for t, lab in (("k", "Mean degree $\\langle k\\rangle$"), ("het", "Degree heterogeneity $k_{\\max}/\\langle k\\rangle$"),
               ("C", "Average clustering $C$")):
    c = P[t]
    rows.append(f"{lab} & {c['coef']:+.2f} & [{c['ci'][0]:+.2f}, {c['ci'][1]:+.2f}] & {c['partial_r']:+.3f} & {pfmt(c['p'])} & {c['vif']:.2f} \\\\")
w("tab_regression", "\n".join(rows))
L = P["ladder"]
w("tab_ladder", "\n".join([
    f"Model label only (BA, WS, ER, Karate) & {L['label']:.3f} \\\\",
    f"$\\langle k\\rangle$ only & {L['k']:.3f} \\\\",
    f"$\\langle k\\rangle$ + heterogeneity & {L['k_het']:.3f} \\\\",
    f"$\\langle k\\rangle$ + heterogeneity + clustering & {L['k_het_C']:.3f} \\\\",
    f"Structural quantities + model label & {L['k_het_C_label']:.3f} \\\\"]))

# --- real networks
rt = pd.DataFrame(N["real_table"])
info = {"florentine": ("Florentine families", "historical social", "b37"), "davis": ("Davis southern women", "affiliation", "b38"),
        "karate": ("Zachary karate club", "social", "b11"), "lesmis": ("Les Mis\\'erables", "co-occurrence", "b39"),
        "sampson": ("Sampson monastery", "social", "b32"), "eies": ("Freeman EIES", "communication", "b33"),
        "dolphins": ("Dolphins", "animal social", "b40"), "football": ("American football", "sports schedule", "b41"),
        "netscience": ("Netscience", "collaboration", "b42"), "jazz": ("Jazz musicians", "collaboration", "b34"),
        "fb698": ("Facebook ego 698", "online social", "b35"), "fb414": ("Facebook ego 414", "online social", "b35"),
        "celegans": ("\\textit{C. elegans} neural", "biological", "b10"), "usair": ("USAir97", "transport", "b43"),
        "polblogs": ("Political blogs", "web", "b44"), "powergrid": ("US power grid", "infrastructure", "b10")}
rt = rt.sort_values("N")
MQ = json.load(open(os.path.join(R, "modularity.json")))["empirical_Q"]
rows = []
for _, r in rt.iterrows():
    nm, dom, cite = info[r.model]
    rows.append(f"{nm}~\\cite{{{cite}}} & {dom} & {int(r.N):,} & {int(r.M):,} & {r.mean_degree:.2f} & {r.hetero:.2f} & {r.clustering:.3f} & {MQ[r.model]:.2f} & {r.rasr_mean:.2f} \\\\".replace(",", "{,}").replace("{,}~", ",~"))
w("tab_realworld", "\n".join(rows))
Q = N["real"]
rows = []
for t, lab in (("k", "$\\langle k\\rangle$"), ("het", "$k_{\\max}/\\langle k\\rangle$"), ("C", "$C$")):
    c = Q[t]
    rows.append(f"{lab} & {c['coef']:+.2f} & [{c['ci'][0]:+.2f}, {c['ci'][1]:+.2f}] & {c['partial_r']:+.3f} & {pfmt(c['p'])} \\\\")
w("tab_real_regression", "\n".join(rows))

# --- scale study
sc = N["scale"]
rows = []
for n in sorted(sc, key=int):
    v = sc[n]
    reps = v["BA"]["n"]
    rows.append(f"{int(n)} & {reps} & ${v['BA']['rasr100']:.2f} \\pm {v['BA']['sd100']:.2f}$ & ${v['WS']['rasr100']:.2f} \\pm {v['WS']['sd100']:.2f}$ & "
                f"${v['ER']['rasr100']:.2f} \\pm {v['ER']['sd100']:.2f}$ & ${v['BA']['rasr60']:.2f}$ / ${v['WS']['rasr60']:.2f}$ / ${v['ER']['rasr60']:.2f}$ & {v['BA']['het']:.2f} \\\\")
w("tab_scale", "\n".join(rows))
print("tables written:", sorted(os.listdir(OUT)))
