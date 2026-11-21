---
type: "Journal"
title: "2026-11-21 Search Live"
description: "GAN search started overnight; winner view added; the store's conversation context was stale and has been re-synced."
resource: "projects/bitnet-conversation-compactor/journal/2026-11-21-search-live.md"
tags: ["journal", "gan", "winner", "store", "context"]
timestamp: "2026-11-21"
---

# 2026-11-21 Search Live

**Did.** Started the generational search (spec v0.3) detached, with checkpoints. Built the winner view: generations as cards, with status, fitness, and changes from the closest earlier candidate. Each card's runs open in the chat inspector.

**Found.** The store's conversation context predated the adversarial conversations, so their gan runs showed no history. Rebuilt the context document (14 conversations) and synced it to context/v2, version 3. Feed synced at version 9 with 271 runs and the winner data. The browser check passes for the Winner tab and for opening a run from it.

**Changed.** Fitness formula moved into `score_runs` in `src/gan.py`, shared by the search and the winner view. Winner data in `src/winner.py`, included in the feed document.

**Next.** Watch the search; sync at checkpoints; evaluate the generations once they finish.
