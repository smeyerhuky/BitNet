---
type: "Concept"
title: "GAN-Style Mutation Loop"
description: "Generate, judge, keep the best, mutate; each mutation is recorded."
resource: "projects/bitnet-conversation-compactor/wiki/concepts/gan-mutation-loop.md"
tags: ["concept", "gan", "mutation", "judging"]
timestamp: "2026-11-21"
---

# GAN-Style Mutation Loop

A generator (the compactor's token policy) proposes rewrites. A judge (deterministic checks plus a blind LLM judge) scores them against the baseline. The best candidates are kept and mutated: tokens mixed in, chopped out, or re-weighted toward domain-specific trigger words.

Each mutation is recorded with its parent, its change, its scores, and its run ids, following [the record schema](../../specs/mutation-record-schema.md).

The loop stops at a score plateau or a budget limit. See [refinement](../../../pdlc/refinement.md).
