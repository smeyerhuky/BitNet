# Source

Compactor harness, stdlib only. Phase 0 modules.

* [budget.py](budget.py) - token budget ledger: 2M phase cap, halt at 80%, 50k per-run limit
* [upstream.py](upstream.py) - NVIDIA chat-completions client; reads the key from the environment only
* [cost.py](cost.py) - cache-aware cost model and prefix-cache simulator
* [records.py](records.py) - append-only JSONL run records with required-field checks
* [__init__.py](__init__.py) - package marker
