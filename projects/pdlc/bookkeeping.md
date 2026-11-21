---
type: "Process"
title: "Bookkeeping"
description: "What is recorded, where, and in what form."
resource: "projects/pdlc/bookkeeping.md"
tags: ["pdlc", "bookkeeping", "journal", "specs"]
timestamp: "2026-11-21"
status: "finalized"
enforcement: "prescriptive"
audience: "both"
disclosure_level: "on-demand"
scope: "organization"
---

# Bookkeeping

Every project records four things, in these places:

| What | Where | Form |
|---|---|---|
| Decisions and plans | `specs/` | Spec articles (see [experiment spec template](../templates/experiment-spec.md)) |
| What happened, daily | `journal/` | One file per day, append-only ([journal template](../templates/journal-entry.md)) |
| Raw data | `runs/` | Machine-readable (JSON/JSONL), one record per run, tagged with the spec version |
| Findings | `wiki/results/` | Results articles that cite the run files they depend on |

A change in direction is a journal entry plus a spec revision. Never edit a spec silently.
