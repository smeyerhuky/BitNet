"""Publisher: detects new sweep results and prepares the store documents.

The artifact store accepts writes only through the session's ArtifactData tool, so this process
cannot push to it. It does the rest: rebuilds the feed and context documents when the results change,
and reports SYNC_DUE, so the session can apply them right away.

Usage:
  python3 src/publisher.py check   # rebuild if changed; prints SYNC_DUE <runs> or SAME
  python3 src/publisher.py ack     # record that the current documents were applied to the store
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import feed  # noqa: E402

STATE = ROOT / "runs" / "publish_state.json"


def fingerprint():
    h = hashlib.sha256()
    for p in [feed.RECORDS, feed.BUDGET]:
        if p.exists():
            h.update(p.read_bytes())
    for p in sorted((ROOT / "runs").glob("*/*.json")):
        h.update(p.name.encode())
    return h.hexdigest()


def main(cmd):
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    if cmd == "check":
        fp = fingerprint()
        if fp == state.get("applied") and state.get("pending") is None:
            print("SAME")
            return
        n, size = feed.build_doc()
        feed.build_context()
        state["pending"] = fp
        STATE.write_text(json.dumps(state, indent=1))
        if fp == state.get("applied"):
            print("SAME")
        else:
            print(f"SYNC_DUE runs={n} feed_bytes={size}")
    elif cmd == "ack":
        if state.get("pending"):
            state["applied"] = state.pop("pending")
            STATE.write_text(json.dumps(state, indent=1))
        print("acked")
    else:
        sys.exit("usage: publisher.py check | ack")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "check")
