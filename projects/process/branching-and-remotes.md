---
type: "Process"
title: "Branching and Remotes"
description: "Git remote and branch rules; pushing upstream is forbidden."
resource: "projects/process/branching-and-remotes.md"
tags: ["process", "git", "remotes", "policy"]
timestamp: "2026-11-21"
status: "finalized"
enforcement: "prescriptive"
audience: "both"
disclosure_level: "always"
scope: "organization"
---

# Branching and Remotes

Rules for git in this repo:

1. Work on the designated branch only: `claude/bitnet-conversation-compactor-nqbsed`.
2. Push only to `origin`, which is the fork (`smeyerhuky/BitNet`).
3. **Never push to the upstream repository this was forked from.** If an `upstream` remote exists, it is read-only for us. Do not add push URLs to it and do not use it as a push target.
4. If the fork must be detached from upstream entirely, that is a separate, explicit decision by the owner. Do it by removing the remote, not by pushing.
5. Use `git push -u origin <branch>` and retry network errors with backoff. Never force-push a shared branch.
