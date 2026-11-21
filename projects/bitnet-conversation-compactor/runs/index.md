# Runs

Raw run records, state and the stored documents behind the run-watch page.

* [records.jsonl](records.jsonl) - one JSON record per run, per the mutation record schema
* [budget.json](budget.json) - local ledger: spend against the 100M cap
* [sweep_state.json](sweep_state.json) - resumable sweep state (done and failed runs)
* [sweep.log](sweep.log) - sweep progress lines
* [publish_state.json](publish_state.json) - last applied feed fingerprint and store version
* [feed_doc.json](feed_doc.json) - the feed document written to the store (runs with replies, budget)
* [context_doc.json](context_doc.json) - the v2 conversation context written to the store
* [embed_cache.json](embed_cache.json) - cached embedding vectors for the retrieval floor
* [api_telemetry.jsonl](api_telemetry.jsonl) - per-call telemetry from the middleware
* [baseline/](baseline/), [keep_last_k/](keep_last_k/), [structural/](structural/) - v1 run outputs
* [v2-baseline/](v2-baseline/), [v2-keep_last_k/](v2-keep_last_k/), [v2-structural/](v2-structural/), [v2-retrieval/](v2-retrieval/) - v2 run outputs
* [probe/](probe/) - end-to-end pipeline probe outputs
