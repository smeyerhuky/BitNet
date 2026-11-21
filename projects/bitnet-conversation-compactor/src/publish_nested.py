"""Nested publisher: applies the feed document to the artifact store through a print-mode Claude call.

Flow: publisher.py check (is a sync due?) -> one `claude -p` call that runs ArtifactData set on
feed/latest, pinned to the last applied version -> confirm the new version -> publisher.py ack.

The call uses a short system prompt, JSON output, no session persistence, and no stdin. Project
permissions for ArtifactData come from .claude/settings.local.json (git-ignored).

Usage:
  python3 src/publish_nested.py            # sync if due; prints PUBLISHED <version> or SAME or FAILED <reason>
  python3 src/publish_nested.py --probe    # same as above, but also reports the cost of the call
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import publisher  # noqa: E402

URL = "https://claude.ai/artifact/NQFW6ohN5bPMDc3xSMJbvY"
FEED = ROOT / "runs" / "feed_doc.json"
STATE = ROOT / "runs" / "publish_state.json"
AUTO_SETTINGS = pathlib.Path.home() / ".claude" / "auto-settings.json"  # allow rule for ArtifactData
SYSTEM = "You are a publisher. Run the one tool call requested, then reply with only the number."


def store_version():
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    return st.get("store_version", 7), st


def set_store_version(v):
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    st["store_version"] = v
    STATE.write_text(json.dumps(st, indent=1))


def call_claude(version):
    prompt = (f"Call ArtifactData once: action set, url {URL}, collection feed, doc_id latest, "
              f"file_path {FEED}, if_version {version}. Reply with only the new version number from the result.")
    proc = subprocess.run(
        ["claude", "-p", prompt, "--model", "claude-haiku-5-5", "--system-prompt", SYSTEM,
         "--output-format", "json", "--no-session-persistence", "--settings", str(AUTO_SETTINGS)],
        cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=240)
    text = proc.stdout
    i = text.find("{")
    if i < 0:
        return None, f"no JSON from claude (exit {proc.returncode}): {proc.stderr[:200]}"
    return json.loads(text[i:]), None


def main(probe=False):
    fp = publisher.fingerprint()
    cur, st = store_version()
    if fp == st.get("applied") and not probe:
        print("SAME")
        return
    n, size = publisher.feed.build_doc()
    publisher.feed.build_context()
    st["pending"] = fp
    STATE.write_text(json.dumps(st, indent=1))

    result, err = call_claude(cur)
    if err:
        print("FAILED", err)
        sys.exit(1)
    if result.get("permission_denials"):
        print("FAILED permission denied:", result["permission_denials"][0].get("tool_name"))
        sys.exit(1)
    m = re.search(r"\d+", str(result.get("result", "")))
    new = int(m.group()) if m else None
    if new != cur + 1:
        print(f"FAILED expected version {cur + 1}, got {result.get('result')!r}")
        sys.exit(1)
    set_store_version(new)
    publisher.main("ack")
    line = f"PUBLISHED version {new}, runs {n}"
    if probe:
        line += f", cost ${result.get('total_cost_usd', 0):.5f}"
    print(line)


if __name__ == "__main__":
    main(probe="--probe" in sys.argv)
