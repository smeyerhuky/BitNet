# Source

Harness code, standard library only (plus `numpy`-free paths; no model dependencies yet).

* [budget.py](budget.py) - local token ledger: 100M cap, halt at 80%, 50k per-run limit
* [upstream.py](upstream.py) - NVIDIA chat and embedding clients: throttle to 40 requests per minute, telemetry, budget charges
* [conditions.py](conditions.py) - message builders for baseline, keep-last-2 and structural floors
* [retrieval.py](retrieval.py) - retrieval floor: embedding cosine over history, cached in runs/embed_cache.json
* [score.py](score.py) - deterministic scoring: runs the reply's last code block against behavior and decision tests in a subprocess
* [cost.py](cost.py) - cache-aware cost model and prefix-cache simulator
* [records.py](records.py) - append-only run records with required-field checks
* [telemetry.py](telemetry.py) - middleware: logs every call's shape, headers, status and usage to runs/api_telemetry.jsonl
* [telemetry_report.py](telemetry_report.py) - summarizes fingerprint and header changes over time
* [run_condition.py](run_condition.py) - original single-condition runner (not resumable; kept for the v1 record)
* [sweep.py](sweep.py) - resumable sweep over corpus v2: state in runs/sweep_state.json, retries, budget guard
* [feed.py](feed.py) - builds the run-watch feed document (runs with replies, budget) and the context document
* [publisher.py](publisher.py) - detects new results and reports SYNC_DUE; ack records what was applied
* [publish_nested.py](publish_nested.py) - applies the feed through a print-mode Claude call; blocked on write permission (see CLAUDE.md)
