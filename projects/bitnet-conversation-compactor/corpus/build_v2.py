"""Build corpus v2: long append-style histories with the decisive rule planted in turn 2 only."""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from tasks_v2 import TASKS_V2  # noqa: E402
from src.score import run_tests  # noqa: E402
from build import SYSTEM, TOOLS, NOTES  # noqa: E402

MODULES = ["config_loader", "http_retry", "csv_export", "metrics", "lru_cache", "date_utils"]
SENTENCES = [
    "The change is small and keeps the public signature unchanged.",
    "I placed the log call before the return so the value is visible in debug output.",
    "Callers that pass an empty payload still get a dict with the step key.",
    "The module logger comes from logging.getLogger(__name__), so levels follow the package config.",
    "No new dependencies were added; this stays within the standard library.",
    "Tests for this module still pass after the edit, and coverage did not drop.",
]


def filler(k):
    mod = MODULES[k % len(MODULES)]
    fn = f"{mod}_step{k}"
    user = f"Add a debug log line inside {fn} in {mod}.py, and show me the function."
    code = (f"```python\nimport logging\nlogger = logging.getLogger(__name__)\n\n"
            f"def {fn}(payload):\n    logger.debug('{mod}: step {k} got %d keys', len(payload))\n"
            f"    return {{**payload, 'step': {k}}}\n```\n")
    prose = " ".join(SENTENCES[(k + i) % len(SENTENCES)] for i in range(4))
    return [{"role": "user", "content": user},
            {"role": "assistant", "content": f"{code}\n{prose}"}]


def history(task):
    decision = [
        {"role": "user", "content": f"Project decision for utils, please record it: {task['decision']}"},
        {"role": "assistant", "content": "Recorded. I will apply this rule to every utils function from now on."},
    ]
    filler_turns = []
    for k in range(18):
        filler_turns += filler(k)
    tail = [
        {"role": "user", "content": "Thanks. Anything blocking the release?"},
        {"role": "assistant", "content": "No blockers. Only the utils functions listed in the backlog remain."},
    ]
    return decision + filler_turns + tail


def build(task):
    return {
        "id": task["id"], "corpus": "v2", "spec_version": "0.2", "system": SYSTEM, "tools": TOOLS, "notes": NOTES,
        "config": {"temperature": 0.5, "top_p": 1, "max_tokens": 1024, "seed": 0},
        "files": {"utils.py": f"\"\"\"Helper utilities.\"\"\"\n\n# TODO: implement {task['fn']}\n"},
        "history": history(task),
        "request": f"Implement {task['fn']} in utils.py. {task['desc']} Return the full updated utils.py in one python code block.",
        "check": {"behavior_tests": task["tests"], "constraint_tests": task["ctest"], "reference": task["ref"],
                  "decision": task["decision"]},
    }


def main():
    ok = 0
    for task in TASKS_V2:
        beh, _ = run_tests(task["ref"], task["tests"])
        con, _ = run_tests(task["ref"], task["ctest"])
        status = "ok" if beh and con else "FAIL"
        ok += beh and con
        print(f"{task['id']:<18} reference behavior={beh} decision={con} {status}")
        if beh and con:
            (HERE / "conversations_v2" / f"{task['id']}.json").write_text(json.dumps(build(task), indent=2) + "\n")
    print(f"valid v2 conversations: {ok}/{len(TASKS_V2)}")


if __name__ == "__main__":
    main()
