# CONNET-2026-191: Revision Status Report

**Manuscript:** Structural Determinants of Network Robustness Under Probabilistic
Attack: A Cross-Topology Analysis Using Quasi-Monte Carlo Estimation

**Journal:** Journal of Complex Networks (Oxford University Press / IMA)  
**Decision:** 1 September 2026, Major Revision (Reviewer 1: minor; Reviewer 2: major)  
**Revision due:** 30 October 2026

---

## Summary

All fifteen reviewer comments now have a response.

* **Reviewer 1's five comments and Reviewer 2's five minor comments are complete
  and already written into the manuscript.** The revised source compiles under the
  journal's unmodified `comnet.cls`, runs to 23 pages, and the bibliography has
  grown from 16 to 31 entries.
* **Reviewer 2's five major comments now have the evidence they asked for.**
  This required new computation: 15,222 RASR evaluations across seven experiment
  files, covering 100 independent realizations per model, a 28-point parameter
  grid, ten real networks in five domains, and sizes up to N = 500. None of this
  is written into the manuscript yet.

One outcome needs your decision before I rewrite anything, and it is set out in
Section 3 below. In short: the repeated realization experiment that Reviewer 2
asked for does not support the four-way fragility ordering we published. It
supports a stronger and better-evidenced claim in its place.

---

## 1. Reviewer 1 (minor revision)

| # | Comment | Status | What was done |
|---|---|---|---|
| 1 | Connect the Introduction and Discussion to the broader robustness and signal-propagation literature; suggested Ji et al., Phys. Rep. 1017 (2023) and Gosak et al., Phys. Life Rev. 41 (2022) | Done, in manuscript | Ji et al. cited in the Introduction where fragmentation and targeted perturbation of network-mediated processes are discussed. Gosak et al. cited in the Discussion where topology-dependent robustness is broadened to biological and living systems. Both placed where the reviewer indicated, not merely appended. |
| 2 | State the novelty more sharply and consistently in Abstract, Introduction and Conclusion; make clear how this differs from deterministic-attack studies and single-network studies | Done, in manuscript | All three sections rewritten around one positioning: structural class is the controlled experimental variable, held against fixed size, density, attack strategy and attack success rate. The contrast with deterministic attack models and with single-network RASR studies is now stated explicitly rather than implied. |
| 3 | Justify the model and parameter choices; state whether the conclusions are expected to hold over broader ranges of density, clustering, degree heterogeneity and community structure | Done, in manuscript, and now backed by new data | A justification paragraph and a new network-statistics table were added to the Methodology. The 28-point parameter sweep run for Reviewer 2's major comment 4 answers the second half of this comment with measurements rather than expectation, so Reviewer 1 gets a quantitative answer as well. |
| 4 | Moderate the practical implications: these are structural tendencies, not universal prescriptions for real infrastructure, biological or social networks | Done, in manuscript | The design-principle passage and the Discussion were rewritten to claim tendencies observed under stated modelling assumptions. The prescriptive phrasing has been removed throughout. |
| 5 | Light editorial revision: some passages read informally, and the abbreviation-heavy phrasing is hard for readers new to the framework | Done, in manuscript | An abbreviations table was added, the key ideas (RASR, PRQMC, BCnns, ANC, HBnnsAGP) are now spelled out in words at first use and at each section opening, and the informal passages were rewritten in a neutral register. |

**Reviewer 1 is fully addressed.** Nothing on this list is outstanding.

---

## 2. Reviewer 2

### Major comments

| # | Comment | Status | What was done |
|---|---|---|---|
| M1 | The main claim is broader than the evidence. The ordering rests on one BA graph, one WS graph, one ER graph and one Karate network. A single realization cannot establish a family-level ordering. | Evidence complete, not yet written in | 100 independent realizations of each of BA, WS and ER at N = 34, four attack strategies, five attack success rate settings, 6,020 evaluations. Result: the published four-way ordering holds in 0 of 100 realizations at ASR = 100%, and never above 31% at any ASR level. The two-group separation (hub-dominated below homogeneous) holds in 100% of realizations at ASR = 100% and in 91% or more everywhere else. See Section 3. |
| M2 | The real-world validation is essentially the Karate club alone, which cannot support claims about real-world networks as a category. | Evidence complete, not yet written in | Ten real networks in five domains: Florentine families, Davis southern women, Zachary karate, dolphins, Les Miserables, American football, netscience collaboration, C. elegans neural, USAir97, political blogs. Sizes 15 to 1,222 nodes, degree heterogeneity 1.13 to 12.83, clustering 0.00 to 0.74. Fitted on the empirical data alone, the structural model gives R2 = 0.788 with every coefficient carrying the same sign as the synthetic fit. |
| M3 | Stochastic models need repeated realizations with averages, variability and statistical evidence. | Evidence complete, not yet written in | Every reported quantity now carries a mean, a standard deviation and a 95% confidence interval over realizations, with Mann-Whitney U tests between families and Spearman rank correlations for the mechanism claim. Rank stability is reported as the fraction of realizations in which each ordering holds, which is the direct answer to this comment. |
| M4 | Topology effects are not disentangled from parameterization effects. BA m, WS k and p, and ER density are all fixed at one value each and directly shape the quantities being claimed. | Evidence complete, not yet written in | A 28-point parameter grid (BA m = 1 to 5; WS k = 4, 6, 8 crossed with p = 0.01 to 1.0; ER p = 0.08 to 0.25), 30 realizations each, 8,400 evaluations. The families overlap almost completely: BA spans RASR 6.62 to 32.98, ER 17.17 to 37.56, WS 21.71 to 38.54. A dense scale-free network is more robust than a sparse random one. Quantitatively, the model label alone explains R2 = 0.346 of RASR; mean degree, degree heterogeneity and clustering together explain R2 = 0.935; adding the model label on top of those three adds only +0.011. The reviewer's suspicion is correct, and we can now show exactly how correct. |
| M5 | The large-scale claim (N = 34 to N = 10,670) rests on ANC and HDA analysis rather than on the probabilistic RASR framework that is the paper's core contribution. | Evidence complete, not yet written in | The probabilistic framework itself was run at N = 100, 200 and 500. The scale-free family separates from both homogeneous families at every size and the gap widens with N, because BA degree heterogeneity grows from 3.64 at N = 34 to 13.96 at N = 500 while the other two stay flat. The claim can now be made inside the framework the paper is actually about. Separately, our own Section 6.6 statement that exhaustive BCnns limits HBnnsAGP to N <= 200 is wrong: measured cost is 3.6 s at N = 200, 21 s at N = 500 and 54 s at N = 800 on two cores. That limitation needs correcting. |

### Minor comments

| # | Comment | Status | What was done |
|---|---|---|---|
| m1 | Moderate the wording in the abstract, discussion and conclusion; phrases such as "stable, independent determinant of RASR" overstate the evidence. | Done, in manuscript | Rewritten in all three locations. Note that the major-comment work has since made a further, larger moderation necessary. See Section 3. |
| m2 | Make the distinction between RASR + HBnnsAGP results and ANC / HDA results clearer throughout. | Done, in manuscript | The Results section was restructured so the two analytical lines are presented separately rather than interleaved, and every figure and table caption is now tagged with which framework produced it. |
| m3 | Describe the random ASR scenario in more detail: how node-level values are sampled, whether they are fixed per run, and whether different heterogeneous assignments were repeated. | Done, in manuscript, and strengthened | The sampling protocol is now stated fully in the Methodology. The reviewer's implied concern turned out to be justified: the submitted paper reported a single draw, and the karate value moves from 28.24 on that draw to 31.15 with a spread of 4.53 over ten independent draws. The revision reports averages over draws. |
| m4 | Add a more concrete discussion of application settings. | Done, in manuscript | An applications passage was added covering infrastructure protection, communication-network vulnerability assessment and diffusion control, tied to which structural quantity matters in each case. |
| m5 | The reference coverage is limited and leans on classic sources; broaden to recent work on robustness, probabilistic failure models and critical-node identification. | Done, in manuscript | The bibliography went from 16 to 31 entries. The Related Work section was expanded along the three axes the reviewer named. All 15 added references were checked against OpenAlex for authors, volume, pages and DOI. |

---

## 3. The one result that needs your decision

Reviewer 2's major comment 1 asked us to repeat the experiment over many
realizations instead of one graph per model. We did, and the published four-way
ordering did not survive.

**What we claimed:** Scale-Free < Real-World < Small-World < Random, invariant
across every attack success rate setting.

**What 100 realizations show:** that exact ordering appears in 0 of 100
realizations at ASR = 100%, and in at most 31% at any setting. Two things break
it independently. Scale-Free and Karate swap: our submitted BA graph scored 12.27
against Karate's 12.86, but across realizations BA averages 16.80, and only 1% of
draws fall below Karate. Small-World and Random are not separable at all: 24.76
against 25.14, Mann-Whitney p = 0.21.

**Why the submitted result looked clean:** the seed-42 BA graph sits at the 97th
percentile of realizations for degree heterogeneity and the 0th percentile for
RASR. Of 100 draws it was the single most hub-dominated and most fragile graph we
could have picked. The seed-42 ER graph sits at the 87th percentile for
robustness. The published ordering needed both of those at once. This is exactly
the failure mode Reviewer 2 described, and it is not a coding error: all sixteen
submitted RASR means at ASR = 100% reproduce from the committed code to two
decimals.

**What survives, and it is the larger part of the paper:**

* The two-group separation of hub-dominated from homogeneous networks holds in
  100% of realizations at ASR = 100% and 91% or more at every other setting,
  p around 3e-34, and is recovered independently by the deterministic ANC line.
* HBnnsAGP outperforms degree targeting in 95% of 301 network instances by 2.39
  RASR units, against the 2.32 we published.
* The attack-success-rate gap is 40.7 to 44.2 units and topology independent,
  against the published 41.6 to 44.2.
* Hub-dominated networks show roughly double the variance of homogeneous ones.

**What replaces the ordering, and it is a better result.** Pooling all 1,044
synthetic instances at N = 34:

```
RASR = 18.40 + 3.44*(mean degree) - 3.14*(degree heterogeneity) - 12.70*(clustering)
R2 = 0.935
```

Partial correlations, each controlling for the other two: mean degree +0.936,
degree heterogeneity -0.817 (p = 3e-251), clustering -0.674 (p = 5e-139).
Variance inflation factors near 1.4, so the three effects are separable rather
than an artifact of collinearity. The same model fitted on the ten real networks
alone gives R2 = 0.788 with all three signs matching.

So the paper moves from "the topology label predicts fragility in this fixed
ordering" to "three measurable structural quantities predict fragility, and the
topology label is very nearly redundant once you know them". That is a continuous
mechanism supported by 1,044 synthetic instances and 10 real networks, in place of
a discrete ordering supported by four graphs. It is a narrower headline and a much
stronger paper, and it is precisely what Reviewer 2 asked for.

**My view on how this reads to the reviewer.** Reviewer 2 predicted this outcome
in writing. Reporting that the prediction was correct, with the experiment that
established it, is the strongest possible response to a major revision. The
alternative, defending the ordering, would fail at the first repeat experiment the
reviewer runs. I would rather we report it than they discover it.

**This is the decision I need guidance on before I rewrite anything**,
because it changes the abstract, contribution 2, Section 5.4.4, Table 9,
Section 6.1 and the conclusion.

---

## 4. Work completed, by the numbers

| Study | Purpose | Evaluations |
|---|---|---|
| Realizations, N = 34 | Reviewer 2 major 1 and 3 | 6,020 |
| Parameter sweep, 28 settings | Reviewer 2 major 4 | 8,400 |
| Real networks, NetworkX set | Reviewer 2 major 2 | 400 |
| Real networks, external data | Reviewer 2 major 2 | 252 |
| Scale study, N = 100, 200, 500 | Reviewer 2 major 5 | 150 |
| **Total** | | **15,222** |

Everything is reproducible. The experiment driver wraps the submitted
`phase4_complete.py` without modifying a line of it, and records two independent
seeds per realization (one for the graph model, one for the Sobol scramble) so the
graph-to-graph variation and the estimator noise can be reported separately. Every
number quoted above comes out of two analysis scripts run over the committed CSVs.

---

## 5. What remains before we can resubmit

Seven items, none of which can start until the decision in Section 3 is made.

1. Rewrite the central claim in six locations: abstract, contribution 2,
   Section 5.4.4, Table 9, Section 6.1, conclusion.
2. Add the new results as tables: realization spread, parameter grid, ten real
   networks, scale study.
3. Build the new figures, each with alt text. The editor's letter makes alt text a
   requirement for every figure, including the existing ones.
4. Recompute the Table 7 standard deviations. The means reproduce exactly, but the
   spread column does not reproduce at the stated seed and K, nor at six other
   scramble seeds, nor across K from 128 to 1024. That column did not come from the
   committed code and has to be regenerated either way, since it is being replaced
   by realization-level statistics.
5. Fix two factual errors: the "80 experiments" count in the Methodology, and the
   Section 6.6 claim that BCnns caps HBnnsAGP at N <= 200.
6. Write the point-by-point response letter, all fifteen entries.
7. Update the Data Availability statement and push the runner, the analysis
   scripts and the result files to the repository. Four manuscript figures
   currently have no generating script committed, which the present statement
   overclaims.

Estimated effort once the decision is made: the manuscript rewrite and the new
tables and figures are about a week of work, the response letter two days.
Against a 30 October deadline this is comfortable.

---

## 6. Optional additions, if we want to go further

These would strengthen the paper and each one answers a comment already on the
table, but none of them is required to respond:

1. **Degree-correlated attack success rates.** Every attack currently succeeds
   with the same probability regardless of which node it hits. Testing profiles
   where hubs are better defended would show whether the fragility result survives
   realistic defence. Our own Limitations section already promises this as future
   work.
2. **Five more real networks chosen for high clustering and low heterogeneity.**
   Clustering is the one term in the structural model that is not yet significant
   on real data (partial r = -0.325, p = 0.36 at n = 10). This is a power problem,
   not an absence, and five more networks should resolve it.
3. **A measured cost curve out to N = 1000**, which turns the Section 6.6
   correction from a retraction into a contribution.
4. **Leave-one-out validation of the structural model**, which costs no compute and
   pre-empts the obvious objection that we fitted three parameters to ten points.
5. **A Zenodo DOI for the code and data**, referenced from the Data Availability
   statement. Reviewer 2's underlying concern is reproducibility, and a versioned
   archive answers it in one line.

I would not add new attack strategies, new robustness metrics or comparisons
against other frameworks. None of that is responsive to anything either reviewer
wrote, and each one opens a new surface for a third round.

---

## 7. Guidance needed on

1. Agreement, or not, on replacing the four-way ordering with the structural model
   described in Section 3.
2. A view on how far down the Section 6 list you want to go before we resubmit.
3. Confirmation that I should draft the response letter for your review once
   point 1 is settled.
