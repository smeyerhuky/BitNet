---
type: "Spec"
title: "Design v0.2: Compression Layer"
description: "Revised design: internal compression layer, cache-aware cost objective, teacher-forced inner loop, 4096-token window constraint, staged gates."
resource: "projects/bitnet-conversation-compactor/specs/design-v0.2.md"
tags: ["spec", "design", "compression-layer", "statistics", "bitnet", "gates"]
timestamp: "2026-11-21"
status: "draft"
enforcement: "prescriptive"
audience: "both"
disclosure_level: "always"
scope: "project"
---

# Design v0.2: Compression Layer

Supersedes the proxy framing in v0.1. Builds on the review in [the Opus review summary](../../product/review-rounds/index.md).

## 1. Goal and constraints

- Goal: an internal layer in our API that chooses the minimal context C' whose upstream reply R' is behaviorally equivalent to the full-context baseline R, at lower cached-input dollar cost.
- Constraint A: BitNet b1.58 2B4T has a documented maximum context of 4096 tokens. It cannot read a 20k to 100k history, so it must work in windows or on span-level decisions. Verified against the model card and Transformers docs on 2026-11-21.
- Constraint B: the upstream is a black box and is never trained.
- Constraint C: cost is dominated by cached-prefix pricing. Token count is a proxy, not the objective.

## 2. Objects

| Object | Shape | Content |
|---|---|---|
| Outcome tensor `Y` | conversation x checkpoint x candidate x run x judge | equivalence label, pairwise label with ties, unit-test flag, action-match flag |
| Fidelity tensor `F` | conversation x checkpoint x candidate | teacher-forced log-likelihood of R given C', minus the same given the full context |
| Span-keep matrix `M` | candidate x span | binary; each span tagged by type (system, tool schema, file, note, turn i) |
| Cost tensor `T` | conversation x checkpoint x candidate x {uncached, cached-read, cache-write, compressor compute} | dollars per upstream, priced per provider |
| Importance matrix `A` | (conversation x checkpoint) x span | estimated effect on `F` of keeping a span |

## 3. Metric hierarchy

1. **Primary (confirmatory):** cached-input dollar cost, at a pre-registered non-inferiority margin on equivalence. Margin is an open decision (see section 8); proposed 5 points.
2. **Inner loop (search):** teacher-forced fidelity `F` plus deterministic action equivalence (tool-call name and normalized arguments, edited paths, diff hunks). Cheap and hard to game.
3. **Confirmation:** blinded judge with randomized A/B order, a second judge family, and an A/A noise-floor study. A judge is used only if its A/A rate and inter-judge agreement (Krippendorff's alpha >= 0.6) pass.

## 4. Pipeline and gates

| Phase | Work | Gate to proceed |
|---|---|---|
| P0 | Decisions in section 8; harness and cost model; tokenizer and cache simulator; endpoint determinism probe | Decisions recorded |
| P1 | Corpus: about 40 coding conversations with unit tests and checkpoint plus dependency labels. Split 50/25/25 into search, selection, test | Labels reviewed on a sample |
| P2 | A/A study; intraclass correlation (ICC) measured; sample size finalized | A/A within noise; judge alpha >= 0.6 |
| P3 | Floors: lossless structural compression (dedupe and version tool schemas, hash file bytes with retrieval, elide tool outputs), keep-last-k, Gemma summary, LLMLingua-2-style token classifier | Pareto frontier drawn on search split |
| P4 | Span importance: random keep-masks (about 200 per checkpoint), group-testing fit of `F`, NMF on `A` at rank 4 to 8 | Factors interpretable; rule-based selector built from them |
| P5 | BitNet selector, windowed to 4096 tokens or on span scores only; distilled from P4 labels | Beats the best floor on selection split at equal fidelity |
| P6 | Evolutionary search over the candidate population with successive halving; anytime-valid e-processes for early stops | Winner chosen on selection split only |
| P7 | Single held-out test on the test split, then upstream transfer to a second provider | Pre-registered non-inferiority met on test split |

Adversarial policy-gradient training against a retrained discriminator is dropped for now. It is unlikely to be stable with fewer than about 100 conversations, and a changing judge breaks comparability across generations.

## 5. Statistics

- Equivalence: mixed-effects logistic model, `equiv ~ candidate + log(tokens) + (1|conv) + (1|conv:turn) + (1|judge) + position + (1|run)`.
- Pairwise judge outcomes: Davidson Bradley-Terry (handles ties); Plackett-Luce if a judge ranks more than two.
- Fidelity: linear model of `F` on keep-masks for span effects; NMF on `A` for archetypes.
- Early stopping: betting e-processes on paired differences (valid under optional stopping).
- Multiple candidates: Benjamini-Hochberg across non-inferiority tests; one pre-registered confirmatory comparison on the test split.
- Intervals: cluster bootstrap over whole conversations, B = 2000.

## 6. Power (paired, alpha = 0.05, power = 0.80, multiplier 7.84)

- Binary equivalence with discordance p = 0.2: n = 7.84 x 0.2 / delta^2. delta = 0.10 gives about 157 effective items; delta = 0.05 gives about 627.
- Continuous `F`, effect size dz: n = 7.84 / dz^2. dz = 0.3 gives about 87; dz = 0.5 gives about 31.
- Clustering with 10 checkpoints per conversation and ICC = 0.3: design effect 3.7. Twenty conversations give about 54 effective items. A 5-point margin needs roughly 60 to 80 conversations. The ICC is a guess and must be measured in P2.
- Add conversations before adding runs. Run variance is not the bottleneck.

## 7. Proposed kill criteria (to pre-register before P5)

- If the best floor cuts at least 30% of cached-input cost at the margin, a learned selector must cut at least 10% more on the test split, or it is dropped.
- If the P2 A/A study is not reproducible, or judge alpha is below 0.6, judge-based claims are dropped and only the deterministic and fidelity metrics count.
- If the P5 selector cannot beat the best floor on the selection split after one full pass, stop and report.

## 8. Open decisions for the owner

1. Non-inferiority margin (proposed 5 points).
2. Coding-only domain for the first phase (proposed yes).
3. Judge families available beyond Gemma.
4. Whether a windowed BitNet selector is acceptable, or a longer-context selector should be used for the rewrite role.
5. Spend cap and stop-loss for NVIDIA and upstream calls.

## 9. Logging

Every candidate writes one record per the [mutation record schema](mutation-record-schema.md), extended with: cache-aware cost fields, F, action-match flag, and the split (search, selection, test) the scores came from.
