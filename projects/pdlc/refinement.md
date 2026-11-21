---
type: "Process"
title: "Refinement"
description: "The baseline, score, mutate, review loop."
resource: "projects/pdlc/refinement.md"
tags: ["pdlc", "refinement", "gan", "judging"]
timestamp: "2026-11-21"
status: "draft"
enforcement: "advisory"
audience: "both"
disclosure_level: "on-demand"
scope: "project"
---

# Refinement

Refinement is the loop from a baseline to a better artifact:

1. **Baseline.** Run uncompacted conversations, record everything (see [experiment protocol](../bitnet-conversation-compactor/specs/experiment-protocol.md)).
2. **Score.** Judge each response with deterministic checks and a blind LLM judge.
3. **Mutate.** Keep the top-scored candidates and mutate the compactor's token policy.
4. **Review.** Record a review round with what changed and what to try next.
5. **Repeat** until the score stops improving or the budget ends.

Each step writes to the journal and the runs folder. A mutation that is kept or dropped is recorded with its reason.
