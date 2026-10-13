"""OLS helpers copied verbatim from analyse.py."""
import numpy as np
from scipy import stats


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
