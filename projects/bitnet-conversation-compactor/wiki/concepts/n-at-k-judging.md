---
type: "Concept"
title: "n@k Judging"
description: "Repeated runs with deterministic checks plus a blind judge."
resource: "projects/bitnet-conversation-compactor/wiki/concepts/n-at-k-judging.md"
tags: ["concept", "judging", "evaluation", "n-at-k"]
timestamp: "2026-11-21"
---

# n@k Judging

Each candidate is run n times, and k is the number of candidates compared, so every comparison has repeated trials. The first pass is 3 A/B runs.

Scoring has two parts:

1. **Deterministic checks.** Exact or structural checks where the answer is known, such as the arithmetic answer `17 * 23 = 391`.
2. **Blind LLM judge.** The judge sees A and B without knowing which is baseline and which is compacted. It scores the answers, not the compaction.

Report both scores and the disagreement rate between them. Judge prompts are versioned in the spec.
