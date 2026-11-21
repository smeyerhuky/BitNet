---
type: "Spec"
title: "GAN Search v0.3: Generational Compactor Search"
description: "Committed parameters for the generational search: 6/3/3 split, population 8 with 2 elites, 6 generations, genome as a policy vector that contains both floors, six mutation operators, a fitness with a decision-failure gate, and a stop rule."
resource: "projects/bitnet-conversation-compactor/specs/gan-search-v0.3.md"
tags: ["spec", "gan", "search", "mutation", "fitness", "generations", "compactor"]
timestamp: "2026-11-21"
status: "draft"
enforcement: "prescriptive"
audience: "both"
disclosure_level: "on-demand"
scope: "project"
---

# GAN Search v0.3

Decisions made 2026-11-21, after a Sonnet review of the parameters (see the journal entry). These supersede the open items in design v0.2, section 8.

## 1. Split (12 conversations)

- **Search (6):** reverse_words, merge_intervals, slugify, flatten, roman_to_int, binary_search.
- **Selection (3):** is_palindrome, parse_duration, running_mean.
- **Test (3), touched once at the end:** chunk_list, dedupe_keep_order, count_vowels.
- **Provisional.** Before launch, check which conversations the retrieval floor fails on, across all 12. If a set has no retrieval-floor failure, swap one conversation in from another set so that each of search and selection has at least one. Record the final split here before the run.
- **Adversarial variants:** if the retrieval floor passes all 12, build two variants whose decision turn has no word overlap with the request. Put one in search and one in test.

## 2. Population and elitism

- 8 candidates per generation. The 2 best survive unchanged, and their scores are reused, not re-run.
- Generation 0 seeds the population with the three floors (keep-last-2, retrieval k=6, structural) plus 5 random genomes.

## 3. Generations tonight

- 6 generations (generation 0 plus 5 evolved).
- Estimated 564 calls and 15 to 30 minutes at the 40-requests-per-minute limit. Raise to 10 generations only if generation 1 shows a clear trend.

## 4. Repeats

- 2 repeats per candidate per search conversation, 12 calls per candidate.
- Promotion to selection: top 2 of the generation, then 3 repeats on the selection conversations.
- **Temperature 0.5, as in the baseline.** This keeps search results comparable with the sweep. Repeats therefore measure real run-to-run variance, not just endpoint noise.

## 5. Genome

A policy vector:

- `keep_last_k` (int, 0 to 8)
- `keep_first_k` (int, 0 to 4)
- `retrieval_k` (int, 0 to 12)
- `cos_threshold` (float, 0 to 1)
- `keep_set` (explicit message indices to keep)
- `tools_keep`, `files_keep`, `notes_keep` (bool)

Kept history is the union of the last k, the first k, the top retrieval_k by cosine (above the threshold), and keep_set. Both floors are special cases:

- keep-last-2: `keep_last_k=2`, everything else off.
- retrieval floor: `retrieval_k=6`, `cos_threshold=0`, everything else off.
- structural floor: history off, `tools_keep=false`.

## 6. Mutation operators

Each child gets each operator independently, and at least one operator must fire.

| Operator | Probability | Effect |
|---|---|---|
| Change `keep_last_k` by ±1 | 0.35 | |
| Change `retrieval_k` by ±1 or ±2 | 0.35 | |
| Perturb `cos_threshold` (Gaussian, σ 0.05, clipped to [0,1]) | 0.25 | |
| Toggle one of `tools_keep`, `files_keep`, `notes_keep` | 0.20 | |
| Add one message index not currently kept, chosen uniformly | 0.25 | Can add spans the floors drop. |
| Remove one index from `keep_set` | 0.15 | |
| Crossover (uniform per gene, two parents) | 0.30 | For 2 of the 6 children. |

## 7. Fitness

- `pass_rate` = mean over runs of (behavior pass AND decision pass), across search conversations and repeats.
- `tok_ratio` = mean prompt tokens divided by 3,250.
- **Decision gate:** if any search conversation fails the decision check in any repeat, fitness = −10 + pass_rate − tok_ratio. Such a candidate always ranks below any fully passing candidate.
- **Otherwise,** fitness = 10 × behavior pass rate − 5 × tok_ratio.
- **Length guard:** a candidate averaging below 150 prompt tokens counts as failing unless it passes everything. This stops empty-context degenerate solutions.
- **Cached tokens** count toward the prompt total. They're recorded separately, so the dollar view can be computed later.

## 8. Stop rule

- Stop after 6 generations, or earlier if the best elite has not improved by at least 0.1 for 2 consecutive generations, and its score is confirmed on 2 repeats.
- Improvement is measured on the mean of repeats, never a single run.
- Stop immediately on 3 consecutive endpoint or rate-limit errors, and write a checkpoint.

## 9. Records

Each candidate writes one record, with: `id`, `generation`, `parent_ids`, `operators`, the full `genome`, per-conversation and per-repeat results (behavior, decision, prompt tokens, cached tokens, latency, output hash), `fitness`, `rank`, `survived` with reason (elite, promoted, dropped), `seed`, timestamp, model ID, and the kept message indices for each conversation (for the "why was this kept" view).

## 10. Checkpointing and resume

- State goes to `runs/gan/state.json`, written atomically after each candidate. A restart resumes at the first unfinished candidate, and the same resume rule as the sweep applies.
