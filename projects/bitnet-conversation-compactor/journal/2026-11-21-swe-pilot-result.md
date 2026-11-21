---
type: "Journal"
title: "2026-11-21 SWE-bench Pilot Result"
description: "19 Django tasks from SWE-bench Verified, oracle-file setting, single run: 11 resolved, 3 unresolved, 5 patches that did not apply. Harness validated with the gold patch (2 of 2)."
resource: "projects/bitnet-conversation-compactor/journal/2026-11-21-swe-pilot-result.md"
tags: ["journal", "swe-bench", "pilot", "result", "harness-validation"]
timestamp: "2026-11-21"
---

# 2026-11-21 SWE-bench Pilot Result

**Result.** Gemma-4-31B, one sample per task, oracle-file setting (problem statement plus the files the official fix touches, at the base commit). Official 2.1.8 harness, local images, Docker.

- Resolved: 11 of 19 (django-15741, 15851, 16139, 16145, 16255, 16429, 16569, 16801, 16899, 17029, 17087).
- Unresolved (tests ran, target tests failed): 3.
- Patch did not apply: 5 (15930, 16100, 16116, 16333, 16595).

**Why earlier results were discarded.** The dataset search endpoint returned one row for every query, so every early prompt used the wrong problem and files. Fixed by paging the 500 rows and matching on instance id. Earlier predictions are in runs/swe/invalid_v1.

**Harness check.** Gold patches on two tasks resolved 2 of 2, so the harness scores correct patches as correct.

**Caveats.** Single run per task. Oracle-file context is easier than an agent that searches the repository. The result is not comparable with leaderboard numbers. Baseline only: no compaction arm has run on this benchmark yet.

**Next.** Decide whether to run a compaction arm on these 19 tasks, and whether to extend the set.
