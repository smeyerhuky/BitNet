"""Build one conversation per task and validate reference solutions against both test sets."""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from tasks import TASKS  # noqa: E402
from src.score import run_tests  # noqa: E402

SYSTEM = ("You are a careful Python coding assistant working in the utils project. "
          "Follow the file's constraints. Reply with the complete updated module in one python code block.")
TOOLS = [
    {"name": "read_file", "description": "Read a project file", "parameters": {"path": "string"}},
    {"name": "write_file", "description": "Write a project file", "parameters": {"path": "string", "content": "string"}},
    {"name": "run_tests", "description": "Run the test suite", "parameters": {}},
]
NOTES = ["Project: utils, a small pure-Python helper library.",
         "Style: type hints optional; docstrings short.",
         "CI runs on Python 3.11 and 3.13.",
         "Owner prefers standard library only."]


def history_for(task_id):
    return [
        {"role": "user", "content": "Please add a one-line docstring to the module header of utils.py."},
        {"role": "assistant", "content": "Added: \"\"\"Helper utilities.\"\"\" at the top of utils.py."},
        {"role": "user", "content": "Thanks. Is there anything else pending in utils.py?"},
        {"role": "assistant", "content": "Only the function you asked about next. The file has one constraint comment per function."},
    ]


def build(task):
    stub = f"\"\"\"Helper utilities.\"\"\"\n\n{task['constraint']}\n# TODO: implement {task['fn']}\n"
    conv = {
        "id": task["id"], "spec_version": "0.2", "system": SYSTEM, "tools": TOOLS, "notes": NOTES,
        "config": {"temperature": 0.5, "top_p": 1, "max_tokens": 1024, "seed": 0},
        "files": {"utils.py": stub},
        "history": history_for(task["id"]),
        "request": f"Implement {task['fn']} in utils.py. {task['desc']} Return the full updated utils.py in one python code block.",
        "check": {"behavior_tests": task["tests"], "constraint_tests": task["ctest"], "reference": task["ref"]},
    }
    return conv


def main():
    ok = 0
    for task in TASKS:
        beh, _ = run_tests(task["ref"], task["tests"])
        con, _ = run_tests(task["ref"], task["ctest"])
        status = "ok" if beh and con else "FAIL"
        ok += beh and con
        print(f"{task['id']:<18} reference behavior={beh} constraint={con} {status}")
        if beh and con:
            (HERE / "conversations" / f"{task['id']}.json").write_text(json.dumps(build(task), indent=2) + "\n")
    print(f"valid conversations: {ok}/{len(TASKS)}")


if __name__ == "__main__":
    main()
