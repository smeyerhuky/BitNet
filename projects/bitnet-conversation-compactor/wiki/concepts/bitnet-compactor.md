---
type: "Concept"
title: "BitNet Compactor"
description: "The compactor as an internal layer that chooses the minimal context for each upstream call."
resource: "projects/bitnet-conversation-compactor/wiki/concepts/bitnet-compactor.md"
tags: ["concept", "compactor", "bitnet", "compression-layer"]
timestamp: "2026-11-21"
---

# BitNet Compactor

The compactor is an internal layer inside our API. It receives the fully assembled request, chooses a minimal context C' that reproduces the baseline behavior, and makes the upstream call with C'. The upstream reply is returned unchanged.

What it may do: drop stale turns, summarize notes, keep only trigger tokens for the current turn, and reference large file bytes by hash or summary.

What it must not do: change the user's new message, or drop anything the upstream needs to answer correctly. Those are checked by the scoring in [n@k judging](n-at-k-judging.md).

Topology: [compression layer topology](../../../architecture/compression-layer-topology.md). Its window limit is covered in [design v0.2](../../specs/design-v0.2.md).
