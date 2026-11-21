"""Live-feed preparer for the run-watch artifact (one db document `feed/latest`).

The page reads an artifact database; this process cannot write to it directly.
So this module prepares pending documents as a batch file. The session then
applies that batch with ArtifactData, and `ack` marks the ids as synced.

Usage:
  python3 src/feed.py build   # writes runs/feed_doc.json (the whole document)
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORDS = ROOT / "runs" / "records.jsonl"
BUDGET = ROOT / "runs" / "budget.json"
FEED_DOC = ROOT / "runs" / "feed_doc.json"


def _load_synced():
    return set(json.loads(SYNCED.read_text())) if SYNCED.exists() else set()


def _doc_for(rec):
    return {
        "run_id": rec["run_id"], "ts": rec.get("timestamp"), "condition": rec.get("condition"),
        "conversation": rec.get("conversation"), "behavior_pass": rec.get("behavior_pass"),
        "constraint_pass": rec.get("constraint_pass"), "input_tokens": rec.get("input_tokens"),
        "output_tokens": rec.get("output_tokens"), "cached_tokens": rec.get("cached_tokens", 0),
        "model": rec.get("model"),
    }


REPLY_CAP = 3000  # characters kept per reply; the flag records any cut


def _reply_for(rec):
    path = ROOT / "runs" / rec["condition"] / f"{rec['run_id']}.json"
    if not path.exists():
        return {"reply": None, "reply_truncated": False}
    reply = json.loads(path.read_text()).get("reply") or ""
    return {"reply": reply[:REPLY_CAP], "reply_truncated": len(reply) > REPLY_CAP}


def build_doc():
    """One document for the page: every unique run (last record per run id wins) with its reply,
    plus the budget. Written in full on each sync, so the page reads one document."""
    latest = {}
    if RECORDS.exists():
        for line in RECORDS.read_text().splitlines():
            rec = json.loads(line)
            if "conversation" in rec:
                latest[rec["run_id"]] = rec
    runs = [dict(_doc_for(rec), **_reply_for(rec)) for rec in latest.values()]
    runs.sort(key=lambda r: (r["ts"] or "", r["run_id"]), reverse=True)
    budget = json.loads(BUDGET.read_text()) if BUDGET.exists() else {}
    from src import winner  # noqa: E402
    doc = {"winner": winner.build(), "runs": runs, "spent_tokens": budget.get("spent_tokens", 0),
           "cap_tokens": budget.get("cap_tokens", 0), "run_count": len(runs)}
    FEED_DOC.write_text(json.dumps(doc, separators=(",", ":")))
    return len(runs), FEED_DOC.stat().st_size


CONTEXT_DOC = ROOT / "runs" / "context_doc.json"


def build_context():
    """Conversation context for the chat view: system text, notes, history and request, per v2 conversation.
    Stored as one document, keyed by conversation id."""
    convs = {}
    for path in sorted((ROOT / "corpus" / "conversations_v2").glob("*.json")):
        c = json.loads(path.read_text())
        convs[c["id"]] = {"system": c["system"], "notes": c["notes"], "history": c["history"],
                          "request": c["request"], "files": c["files"],
                          "tools": [{"name": x["name"], "description": x.get("description", "")} for x in c.get("tools", [])]}
    CONTEXT_DOC.write_text(json.dumps({"conversations": convs}, separators=(",", ":")))
    return len(convs), CONTEXT_DOC.stat().st_size


if __name__ == "__main__":
    if sys.argv[1:] == ["build"]:
        n, size = build_doc()
        print(f"feed document: {n} runs, {size} bytes -> {FEED_DOC}")
        k, csize = build_context()
        print(f"context document: {k} conversations, {csize} bytes -> {CONTEXT_DOC}")
    else:
        sys.exit("usage: feed.py build")
