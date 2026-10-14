#!/usr/bin/env python3
"""
Analysis for the CONNET-2026-191 revision. Reads the result CSVs written by
driver.py and prints every number used in the revised manuscript, and saves
them to numbers.json.
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

R = sys.argv[1]                       # results directory
OUT = {}


def ci95(x):
    x = np.asarray(x, float)
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean() - h, x.mean() + h


def ols(X, y, names):
    """OLS with intercept; returns dict with coef, se, t, p, ci, partial r, R2, LOO R2, VIF."""
    X = np.column_stack([np.ones(len(y)), X])
    n, p = X.shape
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    res = y - X @ b
    sst = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (res @ res) / sst
    s2 = res @ res / (n - p)
    se = np.sqrt(np.diag(s2 * XtXi))
    t = b / se
    pv = 2 * stats.t.sf(np.abs(t), n - p)
    tq = stats.t.ppf(0.975, n - p)
    H = X @ XtXi @ X.T
    loo_res = res / (1 - np.diag(H))
    r2_loo = 1 - (loo_res @ loo_res) / sst
    vif = []
    for j in range(1, p):
        others = [k for k in range(1, p) if k != j]
        Xo = np.column_stack([np.ones(n), X[:, others]])
        bo = np.linalg.lstsq(Xo, X[:, j], rcond=None)[0]
        rr = X[:, j] - Xo @ bo
        r2j = 1 - (rr @ rr) / ((X[:, j] - X[:, j].mean()) ** 2).sum()
        vif.append(1 / (1 - r2j))
    out = dict(n=int(n), R2=r2, R2_loo=r2_loo, intercept=b[0])
    for j, nm in enumerate(names, start=1):
        out[nm] = dict(coef=b[j], se=se[j], t=t[j], p=pv[j],
                       ci=(b[j] - tq * se[j], b[j] + tq * se[j]),
                       partial_r=t[j] / np.sqrt(t[j] ** 2 + n - p), vif=vif[j - 1])
    out["pred"] = X @ b
    out["loo_pred"] = y - loo_res
    return out


def r2_of(X, y):
    X = np.column_stack([np.ones(len(y)), X])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    res = y - X @ b
    return 1 - res @ res / ((y - y.mean()) ** 2).sum()


def show(title, d):
    print(f"\n== {title}")
    print(json.dumps(d, indent=1, default=lambda o: float(o) if np.isscalar(o) else str(o)))


# ----------------------------------------------------------------------
# realization study
# ----------------------------------------------------------------------
rz = pd.read_csv(os.path.join(R, "results_realizations_N34.csv"))
rz["model"] = rz["model"].replace({"karate": "Karate"})
hb = rz[rz.strategy == "HBnnsAGP"]
ASR = ["100", "80", "60", "50", "rand"]
piv = {a: hb[hb.asr_label == a].pivot_table(index="rep", columns="model", values="rasr_mean")
       for a in ASR}
kar = {a: float(hb[(hb.model == "Karate") & (hb.asr_label == a)].rasr_mean.iloc[0]) for a in ASR}

real_tab = {}
for a in ASR:
    p = piv[a]
    row = {}
    for m in ["BA", "WS", "ER"]:
        x = p[m].dropna().values
        lo, hi = ci95(x)
        row[m] = dict(mean=x.mean(), sd=x.std(ddof=1), lo=lo, hi=hi, n=len(x))
    row["Karate"] = kar[a]
    four = ((p.BA < kar[a]) & (kar[a] < p.WS) & (p.WS < p.ER)).mean() * 100
    two = ((p.BA < p.WS) & (p.BA < p.ER) & (kar[a] < p.WS) & (kar[a] < p.ER)).mean() * 100
    row["four_way_pct"] = four
    row["two_group_pct"] = two
    row["BA_below_karate_pct"] = (p.BA < kar[a]).mean() * 100
    row["WS_below_ER_pct"] = (p.WS < p.ER).mean() * 100
    row["MW_BA_WS_p"] = stats.mannwhitneyu(p.BA, p.WS).pvalue
    row["MW_BA_ER_p"] = stats.mannwhitneyu(p.BA, p.ER).pvalue
    row["MW_WS_ER_p"] = stats.mannwhitneyu(p.WS, p.ER).pvalue
    real_tab[a] = row
OUT["realizations"] = real_tab
show("realizations", real_tab)

# ASR gap 100 -> 50, per realization
gap = {m: (piv["50"][m] - piv["100"][m]) for m in ["BA", "WS", "ER"]}
OUT["asr_gap"] = {m: dict(mean=g.mean(), sd=g.std(ddof=1)) for m, g in gap.items()}
OUT["asr_gap"]["Karate"] = kar["50"] - kar["100"]
show("asr_gap", OUT["asr_gap"])

# within-instance outcome spread (sd over Sobol outcomes), mean over realizations
spread = {}
for a in ["80", "60", "50"]:
    sub = hb[hb.asr_label == a]
    spread[a] = {m: sub[sub.model == m].rasr_sd.mean() for m in ["BA", "WS", "ER", "Karate"]}
OUT["outcome_sd"] = spread
show("outcome_sd", spread)

# HBnnsAGP vs HDA across all instances at 100%
s100 = rz[rz.asr_label == "100"].pivot_table(index=["model", "rep"], columns="strategy",
                                            values="rasr_mean")
adv = s100["HDA"] - s100["HBnnsAGP"]
OUT["hb_vs_hda"] = dict(n=int(len(adv)), frac_better=float((adv > 0).mean() * 100),
                         frac_tie=float((adv == 0).mean() * 100),
                         mean_margin=float(adv.mean()), sd_margin=float(adv.std(ddof=1)))
avg100 = s100.groupby(level=0).mean()
OUT["strategy_means_100"] = avg100.to_dict()
show("hb_vs_hda", OUT["hb_vs_hda"])
show("strategy means at 100 by model", OUT["strategy_means_100"])

# seed-42 single instances: percentiles within realizations
seed42 = {"BA": (12.27, 5.05), "WS": (24.71, 1.50), "ER": (28.07, 1.77)}
st100 = hb[hb.asr_label == "100"]
pct = {}
for m, (r, h) in seed42.items():
    x = st100[st100.model == m]
    pct[m] = dict(rasr_pctile=stats.percentileofscore(x.rasr_mean, r, kind="weak"),
                  hetero_pctile=stats.percentileofscore(x.hetero, h, kind="weak"))
OUT["seed42_percentiles"] = pct
show("seed42 percentiles", pct)

# heterogeneity -> fragility across instances at 100%
synth = st100[st100.model.isin(["BA", "WS", "ER"])]
rho = stats.spearmanr(synth.hetero, synth.rasr_mean)
OUT["spearman_hetero_rasr"] = dict(rho=rho.statistic, p=rho.pvalue, n=len(synth))
show("spearman", OUT["spearman_hetero_rasr"])

# ----------------------------------------------------------------------
# parameter sweep
# ----------------------------------------------------------------------
sw = pd.read_csv(os.path.join(R, "results_sweep_N34.csv"), dtype={"asr_label": str})
swh = sw[sw.strategy == "HBnnsAGP"]
g = swh.groupby(["model", "params"]).agg(rasr=("rasr_mean", "mean"), sd=("rasr_mean", "std"),
                                         k=("mean_degree", "mean"), het=("hetero", "mean"),
                                         C=("clustering", "mean"), n=("rasr_mean", "size"))
OUT["sweep"] = {f"{a}|{b}": r for (a, b), r in g.to_dict("index").items()}
rng = g.groupby(level=0).rasr.agg(["min", "max"])
OUT["sweep_ranges"] = rng.to_dict("index")
show("sweep", OUT["sweep"])
show("sweep ranges", OUT["sweep_ranges"])

# ----------------------------------------------------------------------
# pooled structural regression at N = 34
# ----------------------------------------------------------------------
pool = pd.concat([
    st100[["model", "rep", "mean_degree", "hetero", "clustering", "rasr_mean"]].assign(src="realization"),
    swh[["model", "params", "rep", "mean_degree", "hetero", "clustering", "rasr_mean"]].assign(src="sweep"),
], ignore_index=True)
y = pool.rasr_mean.values
Xs = pool[["mean_degree", "hetero", "clustering"]].values
lab = pd.get_dummies(pool.model, drop_first=True).values.astype(float)
fit = ols(Xs, y, ["k", "het", "C"])
ladder = {
    "label": r2_of(lab, y),
    "k": r2_of(Xs[:, :1], y),
    "k_het": r2_of(Xs[:, :2], y),
    "k_het_C": fit["R2"],
    "k_het_C_label": r2_of(np.column_stack([Xs, lab]), y),
}
OUT["pooled"] = {k: v for k, v in fit.items() if k not in ("pred", "loo_pred")}
OUT["pooled"]["ladder"] = ladder
OUT["pooled"]["n_by_src"] = pool.src.value_counts().to_dict()
show("pooled regression", OUT["pooled"])
pool.assign(pred=fit["pred"], loo_pred=fit["loo_pred"]).to_csv(os.path.join(R, "pooled_N34.csv"), index=False)

# ----------------------------------------------------------------------
# real networks (16)
# ----------------------------------------------------------------------
r1 = pd.read_csv(os.path.join(R, "results_real16.csv"))
r2p = os.path.join(R, "ext", "results_real_ext.csv")
parts = [r1]
if os.path.exists(r2p):
    parts.append(pd.read_csv(r2p))
rw = pd.concat(parts, ignore_index=True)
rwh = rw[rw.strategy == "HBnnsAGP"].copy()
rwh = rwh.drop_duplicates("model", keep="first")
fr = ols(rwh[["mean_degree", "hetero", "clustering"]].values, rwh.rasr_mean.values, ["k", "het", "C"])
OUT["real"] = {k: v for k, v in fr.items() if k not in ("pred", "loo_pred")}
OUT["real_table"] = rwh[["model", "N", "M", "mean_degree", "hetero", "clustering", "rasr_mean"]].to_dict("records")
syn_pred = fit["intercept"] + fit["k"]["coef"] * rwh.mean_degree + fit["het"]["coef"] * rwh.hetero + fit["C"]["coef"] * rwh.clustering
OUT["real_synthpred"] = dict(zip(rwh.model, syn_pred))
OUT["real_rwpred"] = dict(zip(rwh.model, fr["pred"]))
inrange = rwh.mean_degree <= pool.mean_degree.max()
rs = stats.spearmanr(syn_pred[inrange], rwh.rasr_mean[inrange])
OUT["real_synth_transfer"] = dict(n_inrange=int(inrange.sum()), rho=rs.statistic, p=rs.pvalue,
                                  kmax_pool=float(pool.mean_degree.max()))
hd = rw[rw.strategy == "HDA"].set_index("model").rasr_mean
hbv = rwh.set_index("model").rasr_mean
common = hd.index.intersection(hbv.index)
OUT["real_hb_vs_hda"] = dict(n=len(common), better=int((hd[common] > hbv[common]).sum()))
show("real networks", {k: OUT[k] for k in ("real", "real_table", "real_synthpred", "real_rwpred", "real_synth_transfer", "real_hb_vs_hda")})
# 10-network refit (without the 6 added) for the letter
ten = rwh[~rwh.model.isin(["sampson", "eies", "jazz", "fb698", "fb414", "powergrid"])]
f10 = ols(ten[["mean_degree", "hetero", "clustering"]].values, ten.rasr_mean.values, ["k", "het", "C"])
OUT["real10"] = {k: v for k, v in f10.items() if k not in ("pred", "loo_pred")}
show("real 10", OUT["real10"])

# ----------------------------------------------------------------------
# scale study
# ----------------------------------------------------------------------
sc = {}
sc[34] = {m: dict(rasr100=piv["100"][m].mean(), sd100=piv["100"][m].std(ddof=1),
                  rasr60=piv["60"][m].mean(), sd60=piv["60"][m].std(ddof=1),
                  het=st100[st100.model == m].hetero.mean(), n=int(piv["100"][m].count()))
          for m in ["BA", "WS", "ER"]}
for N in (100, 200, 500):
    f = os.path.join(R, f"results_scale_N{N}.csv")
    if not os.path.exists(f):
        continue
    d = pd.read_csv(f, dtype={"asr_label": str})
    sc[N] = {}
    for m in ["BA", "WS", "ER"]:
        a = d[(d.model == m) & (d.asr_label == "100")]
        b = d[(d.model == m) & (d.asr_label == "60")]
        sc[N][m] = dict(rasr100=a.rasr_mean.mean(), sd100=a.rasr_mean.std(ddof=1),
                        rasr60=b.rasr_mean.mean(), sd60=b.rasr_mean.std(ddof=1),
                        het=a.hetero.mean(), k=a.mean_degree.mean(), n=len(a))
    ba = d[(d.model == "BA") & (d.asr_label == "100")].rasr_mean
    others = d[(d.model != "BA") & (d.asr_label == "100")].rasr_mean
    sc[N]["MW_BA_vs_rest_p"] = stats.mannwhitneyu(ba, others).pvalue
    sc[N]["BA_below_all_pct"] = float(np.mean([x < others.min() for x in ba]) * 100)
OUT["scale"] = sc
show("scale", sc)

# ----------------------------------------------------------------------
# structural model when attacks can fail: refit on the realization graphs
# (300 realizations + Karate) at every ASR setting, and on the scale-study
# graphs (N = 100, 200, 500) at ASR = 100% and 60%
# ----------------------------------------------------------------------
def strip(f):
    return {k: v for k, v in f.items() if k not in ("pred", "loo_pred")}


asr_models = {}
for a in ["100", "80", "60", "50", "rand"]:
    x = hb[hb.asr_label == a]
    asr_models[a] = strip(ols(x[["mean_degree", "hetero", "clustering"]].values, x.rasr_mean.values, ["k", "het", "C"]))
OUT["asr_models"] = asr_models
show("structural model by ASR (realization graphs)", asr_models)
sm = {}
parts = [pd.read_csv(os.path.join(R, f"results_scale_N{N}.csv"), dtype={"asr_label": str})
         for N in (100, 200, 500) if os.path.exists(os.path.join(R, f"results_scale_N{N}.csv"))]
if parts:
    dsc = pd.concat(parts, ignore_index=True)
    dsc = dsc[dsc.strategy == "HBnnsAGP"]
    for a in ["100", "60"]:
        x = dsc[dsc.asr_label == a]
        sm[a] = strip(ols(x[["mean_degree", "hetero", "clustering"]].values, x.rasr_mean.values, ["k", "het", "C"]))
OUT["scale_model"] = sm
show("structural model, scale-study graphs", sm)

json.dump(OUT, open(os.path.join(R, "numbers.json"), "w"), indent=1,
          default=lambda o: float(o) if np.isscalar(o) else (o.tolist() if hasattr(o, "tolist") else str(o)))
print("\nsaved numbers.json")
