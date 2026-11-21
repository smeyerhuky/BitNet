---
type: "Journal"
title: "2026-11-21 GAN Decisions"
description: "Search parameters committed after the Sonnet review: split, population, generations, genome, operators, fitness, stop rule."
resource: "projects/bitnet-conversation-compactor/journal/2026-11-21-gan-decisions.md"
tags: ["journal", "gan", "decisions", "search"]
timestamp: "2026-11-21"
---

# 2026-11-21 GAN Decisions

**Did.** Had a Sonnet subagent review the loop parameters. Adopted most of its report and wrote [GAN search v0.3](../specs/gan-search-v0.3.md).

**Changed from the report.**
- Temperature stays at 0.5, to match the baseline. The report suggested 0, which would make search results incomparable with the sweep.
- The split is provisional. It has to be checked against the retrieval floor's failures across all 12 conversations before launch.

**Found.** The retrieval floor may already pass every conversation at about 350 tokens. If it does, the loop has to win on tokens below that, or on adversarial variants. This is the main risk, and the sweep will settle it.

**Next.** Finish the floor sweep, check the split, then build the search loop and run it overnight with checkpointing.
