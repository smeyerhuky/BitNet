---
type: "Journal"
title: "2026-11-21 Floor Sweep Results"
description: "Corpus v2 floors: retrieval passes all 36 runs at 373 prompt tokens; keep-last-2 and structural lose the planted decision in every run."
resource: "projects/bitnet-conversation-compactor/journal/2026-11-21-floor-sweep-results.md"
tags: ["journal", "results", "floors", "retrieval", "planted-decision", "corpus-v2"]
timestamp: "2026-11-21"
---

# 2026-11-21 Floor Sweep Results

**Did.** Ran three floors on corpus v2 (12 conversations, 3 runs each, 36 per condition) and synced them to the run-watch store (feed version 7, 252 runs).

**Found.**

| Condition | Behavior | Decision | Mean prompt tokens |
|---|---|---|---|
| Baseline (full context) | 36/36 | 36/36 | 3,247 |
| Retrieval floor (k=6) | 36/36 | 36/36 | 373 |
| Keep last 2 messages | 23/36 | 0/36 | 308 |
| Structural (no history, no tools) | 21/36 | 0/36 | 187 |

- Dropping history loses the planted decision in every run. The decision check is therefore a working probe of dependency.
- Retrieval keeps the decision. It uses about 11.5% of the baseline's prompt tokens with no drop in pass rate.
- Retrieval is a strong floor. The GAN search has to beat about 373 tokens at equal pass rate, or win on robustness, to show anything beyond it.

**Caveat.** Corpus v2 uses one planted rule per conversation, with templated filler. The retrieval result may not hold where the dependency is less lexically obvious. That's the reason for the adversarial variants in the search spec.

**Next.** Build the search loop per GAN search v0.3, using retrieval as the seed and the floor to beat.
