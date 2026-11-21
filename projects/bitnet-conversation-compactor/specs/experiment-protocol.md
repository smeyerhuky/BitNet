---
type: "Spec"
title: "Experiment Protocol"
description: "Baseline capture, pinned conditions, n=3 judging, keep and mutate rule."
resource: "projects/bitnet-conversation-compactor/specs/experiment-protocol.md"
tags: ["spec", "protocol", "judging", "baseline"]
timestamp: "2026-11-21"
status: "draft"
enforcement: "prescriptive"
audience: "both"
scope: "project"
---

# Experiment Protocol

Spec version 0.1, status draft.

1. Build baseline conversations with append-style n+1 turns. Keep each turn's full request and reply.
2. Pin conditions: model, temperature 0.5, top_p 1, max_tokens 1024, seed 0.
3. Run each condition 3 times (n=3). Judge A/B pairs with the blind judge and deterministic checks.
4. Keep the best candidates. Mutate the compactor's token policy. Record every mutation.
5. Decide per the rule: keep a mutation only if it reduces input tokens and its judge score is not lower than baseline beyond noise.

Concepts: [n@k judging](../wiki/concepts/n-at-k-judging.md), [GAN mutation loop](../wiki/concepts/gan-mutation-loop.md).
