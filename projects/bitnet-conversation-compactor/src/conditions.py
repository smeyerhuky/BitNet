"""Build the message list for a condition from a corpus conversation.

baseline: full composition, append-style history, as a normal client would send it.
"""
import json


def load_conversation(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _system_text(conv):
    tools = "\n".join(json.dumps(t) for t in conv["tools"])
    notes = "\n".join(f"- {n}" for n in conv["notes"])
    return f"{conv['system']}\n\nNotes:\n{notes}\n\nTools:\n{tools}"


def _file_text(conv):
    return "\n\n".join(f"File {name}:\n```python\n{body}```" for name, body in conv["files"].items())


def baseline(conv):
    msgs = [{"role": "system", "content": _system_text(conv)}]
    msgs += conv["history"]
    msgs.append({"role": "user", "content": f"{conv['request']}\n\n{_file_text(conv)}"})
    return msgs


def keep_last_k(conv, k=2):
    """P3 floor: keep only the last k history messages; system, notes and tools unchanged."""
    msgs = [{"role": "system", "content": _system_text(conv)}]
    msgs += conv["history"][-k:]
    msgs.append({"role": "user", "content": f"{conv['request']}\n\n{_file_text(conv)}"})
    return msgs


def structural(conv):
    """P3 floor, structural: drop tool schemas (this request uses none) and the history turns.
    Notes and file bytes are kept."""
    notes = "\n".join(f"- {n}" for n in conv["notes"])
    msgs = [{"role": "system", "content": f"{conv['system']}\n\nNotes:\n{notes}"}]
    msgs.append({"role": "user", "content": f"{conv['request']}\n\n{_file_text(conv)}"})
    return msgs
