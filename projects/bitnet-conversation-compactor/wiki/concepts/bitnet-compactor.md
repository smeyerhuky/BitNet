---
type: "Concept"
title: "BitNet Compactor"
description: "The proxy idea: rewrite the outgoing request, forward the reply unchanged."
resource: "projects/bitnet-conversation-compactor/wiki/concepts/bitnet-compactor.md"
tags: ["concept", "compactor", "bitnet", "proxy"]
timestamp: "2026-11-21"
---

# BitNet Compactor

The compactor is an in-line proxy. It receives the client's request, rewrites the outgoing conversation to fewer tokens, and forwards it upstream. The upstream reply is returned unchanged.

What it may do: drop stale turns, summarize notes, keep only trigger tokens for the current turn, and reference large file bytes by hash or summary.

What it must not do: change the user's new message, or drop anything the upstream needs to answer correctly. Those are checked by the scoring in [n@k judging](n-at-k-judging.md).

Topology: [proxy topology](../../../architecture/proxy-topology.md).
