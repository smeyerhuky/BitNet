# Spikes

Throwaway experiments.

* [nvidia-probe-result.md](nvidia-probe-result.md) - result of the endpoint probe; the script is nvidia_probe.py
* [determinism-probe.md](determinism-probe.md) - same request 10 times at seed 0; one distinct reply; cached tokens appear from call 9
* [nvidia_probe.py](nvidia_probe.py) - one chat completion, key from environment
* [determinism_probe.py](determinism_probe.py) - repeated-request determinism check, charges the budget ledger
* [browser_check_modal.js](browser_check_modal.js) - headless Chromium check: loads run-watch with a stub store, expands a group, clicks a run, and confirms the inspector opens
