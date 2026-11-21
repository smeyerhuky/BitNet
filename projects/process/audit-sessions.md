---
type: "Process"
title: "Audit Sessions"
description: "The hygiene audit checklist run at phase ends."
resource: "projects/process/audit-sessions.md"
tags: ["process", "audit", "hygiene", "okf"]
timestamp: "2026-11-21"
status: "finalized"
enforcement: "advisory"
audience: "both"
disclosure_level: "on-demand"
scope: "organization"
---

# Audit Sessions

An audit session checks hygiene, not progress. Run one at the end of each project phase, or after any change to the wiki structure.

Checklist:

- Run the OKF linter on every bundle. Zero errors required.
- Check every folder has an `index.md` that matches its contents.
- Check every article has a non-empty `type` and the recommended fields.
- Check the journal has an entry for the session, and no past entries were rewritten silently.
- Check no secrets are in the tree (`grep` for `nvapi-`, `sk-`, `Bearer `).
- Check the git remotes and branch against [branching and remotes](branching-and-remotes.md).

Record the result as a Review in `product/review-rounds/` if it is a project-level audit, or in the project journal otherwise. Use [the audit template](../templates/audit-session.md).
