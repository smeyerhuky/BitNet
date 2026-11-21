---
type: "Journal"
title: "2026-11-21 Workspace Bootstrap"
description: "Bootstrap day: tree created, endpoint verified."
resource: "projects/journal/2026-11-21-workspace-bootstrap.md"
tags: ["journal", "bootstrap", "bitnet"]
timestamp: "2026-11-21"
---

# 2026-11-21 Workspace Bootstrap

**Did.** Created the `projects/` tree with the OKF wiki structure. Scaffolded the first project. Checked the NVIDIA endpoint with the session key (HTTP 200, `17 * 23 = 391`).

**Found.** The key is in the environment as `NVIDIA_API_KEY`. The owner says it is temporary and will be rotated, so it stays out of files. The owner also said upstream must never receive pushes.

**Changed.** See the [workspace layout](../architecture/workspace-layout.md) and the [branching rules](../process/branching-and-remotes.md).

**Next.** Capture baseline conversations in the first project.
