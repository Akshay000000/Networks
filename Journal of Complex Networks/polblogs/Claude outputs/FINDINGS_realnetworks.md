# Empirical validation: ten real networks, five domains

Run 14 September 2026, using the six datasets supplied (dolphins, football,
C. elegans neural, USAir97, political blogs, netscience collaboration) plus the
four bundled with NetworkX (Zachary karate, Florentine families, Davis southern women,
Les Miserables). All converted to undirected, unweighted, simple graphs and
reduced to the largest connected component, matching the existing methodology.

This is the answer to Reviewer 2 major comment 2.

---

## The set

| Network | N | M | mean degree | heterogeneity | clustering | RASR @ 100% | Domain |
|---|---|---|---|---|---|---|---|
| Florentine families | 15 | 20 | 2.67 | 2.25 | 0.160 | 19.17 | historical social |
| Davis southern women | 32 | 89 | 5.56 | 2.52 | 0.000 | 19.89 | social affiliation |
| Zachary karate club | 34 | 78 | 4.59 | 3.71 | 0.571 | 12.86 | social |
| Dolphins | 62 | 159 | 5.13 | 2.34 | 0.259 | 17.61 | animal social |
| Les Miserables | 77 | 254 | 6.60 | 5.46 | 0.573 | 9.89 | co-occurrence |
| American football | 115 | 613 | 10.66 | 1.13 | 0.403 | 34.72 | sports schedule |
| Netscience collaboration | 379 | 914 | 4.82 | 7.05 | 0.741 | 2.64 | scientific collaboration |
| C. elegans neural | 297 | 2148 | 14.46 | 9.26 | 0.292 | 24.17 | biological |
| USAir97 | 332 | 2126 | 12.81 | 10.85 | 0.625 | 8.24 | transport |
| Political blogs | 1222 | 16714 | 27.36 | 12.83 | 0.320 | 18.52 | web / political |

Ten networks instead of one, spanning five domains, an order of magnitude in
degree heterogeneity (1.13 to 12.83), the full range of clustering (0.00 to
0.74) and two orders of magnitude in size.

---

## The structural model holds on real data

Fitting the same three-variable model on the empirical networks alone, with no
synthetic data involved:

```
RASR = 21.49 + 1.39*<k> - 2.60*heterogeneity - 7.44*clustering      R² = 0.788
```

All three coefficients carry the same sign as the synthetic fit. Denser is more
robust, more hub-dominated is more fragile, more clustered is more fragile.

Partial correlations, each controlling for the other two:

| Quantity | partial r | p |
|---|---|---|
| mean degree | +0.805 | 0.0049 |
| degree heterogeneity | -0.798 | 0.0056 |
| clustering | -0.325 | 0.36 |

Density and heterogeneity are both significant on ten networks. Clustering keeps
the right sign but does not reach significance, because with n = 10 and three
predictors, heterogeneity and clustering partly overlapping, the test is
underpowered. The clustering effect rests on the synthetic evidence, where
n = 1,044 gives partial r = -0.674 at p = 5e-139. State it that way in the
paper rather than claiming it is established on real data.

**The density-controlled comparison is the clearest illustration in the set.**
Four of the empirical networks happen to sit at nearly the same density, mean
degree between 4.6 and 5.6, while their clustering spans the full range:

| Network | mean degree | clustering | RASR |
|---|---|---|---|
| Davis southern women | 5.56 | 0.000 | 19.89 |
| Dolphins | 5.13 | 0.259 | 17.61 |
| Zachary karate | 4.59 | 0.571 | 12.86 |
| Netscience | 4.82 | 0.741 | 2.64 |

RASR falls monotonically from 19.89 to 2.64 as clustering rises, at essentially
constant density. Heterogeneity also rises across these four, so this is an
illustration rather than a controlled test, but it is a natural experiment in
real data and it points the same way as the model.

---

## Two cautions that belong in the paper

**The simple correlations are misleading, again.** Taken alone, heterogeneity
correlates with RASR at Spearman rho = -0.442, p = 0.200, which looks like no
effect. Controlled for density and clustering it is -0.798, p = 0.006. This is
the same trap identified in the synthetic analysis, and it appears here for the
same reason: heterogeneous real networks also tend to be denser, and the two
effects cancel in a raw correlation. Any reviewer who plots RASR against
heterogeneity without controlling for density will conclude the result is not
there.

**The fitted constants do not extrapolate.** Applying the synthetic model,
fitted on graphs with mean degree between roughly 2 and 9, to networks with
mean degree up to 27 gives absurd predictions. Political blogs is predicted at
85.8 against an actual 18.5. The relationship generalises across domains; the
coefficients are calibrated to the range they were fitted on and should be
presented that way, as a within-range description rather than a predictive
formula.

Within a sensible range the ordering does transfer. Predicting the four mid-size
networks from the synthetic model gives exactly the right fragility order,
USAir97 < dolphins < C. elegans < football, matching the measured order in all
four cases.

---

## Cost note

USAir97 at N = 332 takes about 6 seconds per evaluation. Political blogs at
N = 1222 takes 170 seconds, so it was run on a reduced grid rather than the full
five ASR settings and two strategies. The paper's claim that exhaustive BCnns
caps HBnnsAGP at N ≤ 200 remains wrong by a wide margin.

---

## Files

`results_realdata_N34.csv` (six supplied datasets),
`results_realworld_N34.csv` (four NetworkX networks),
`netdata/graphs.pkl` and the parsing code in `runner.py`.
