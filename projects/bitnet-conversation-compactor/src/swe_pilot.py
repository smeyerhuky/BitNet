"""SWE-bench Verified pilot, step 1: generate one candidate diff per task (baseline, full context).

Context given to the model: the problem statement, plus the content of each file the official fix touches,
at the task's base commit ("oracle file" setting from the SWE-bench paper). The model returns a unified diff.
Output: runs/swe/predictions.jsonl in the swebench predictions format.
"""
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import budget as B, upstream  # noqa: E402

REPO_DIR = pathlib.Path("/tmp/django_src")
IDS = json.loads((ROOT / "corpus" / "swe" / "pilot_ids.json").read_text())
PRED = ROOT / "runs" / "swe" / "predictions.jsonl"
RUNS = ROOT / "runs" / "swe" / "generation.jsonl"
SYSTEM = ("You fix bugs in the Django source code. Reply with only one unified diff in a ```diff block, "
          "with paths relative to the repository root, that applies cleanly to the files shown.")


def retry(fn, tries=4):
    """Run fn, retrying network-type failures with backoff. The pilot resumes from saved diffs, so a crash loses little."""
    import time
    for attempt in range(tries):
        try:
            return fn()
        except (TimeoutError, OSError, urllib.error.URLError, ConnectionError) as e:
            if attempt == tries - 1:
                raise
            print(f"retry {attempt + 1}: {e}", flush=True)
            time.sleep(min(60, 10 * 2 ** attempt))


def fetch_row(iid):
    url = ("https://datasets-server.huggingface.co/search?dataset=princeton-nlp%2FSWE-bench_Verified"
           f"&config=default&split=test&query={iid}&offset=0&length=1")
    return retry(lambda: json.load(urllib.request.urlopen(url, timeout=120))["rows"][0]["row"])


def touched_files(patch):
    return sorted(set(re.findall(r"^diff --git a/(\S+) b/", patch, re.M)))


def file_at(commit, path):
    return subprocess.run(["git", "-C", str(REPO_DIR), "show", f"{commit}:{path}"],
                          capture_output=True, text=True, check=True).stdout


def extract_diff(reply):
    """Return the last diff in the reply: a fenced ```diff block, or raw text starting at a diff header."""
    blocks = re.findall(r"```(?:diff|patch)?[ \t]*\n(.*?)```", reply, re.S)
    candidates = blocks[::-1] + [reply]
    for body in candidates:
        m = re.search(r"^(diff --git |--- a/)", body, re.M)
        if m:
            return body[m.start():].strip() + "\n"
    return ""


def main(limit=None):
    budget = B.Budget(ROOT / "runs" / "budget.json")
    done = set()
    if PRED.exists():
        done = {json.loads(l)["instance_id"] for l in PRED.read_text().splitlines()}
    todo = [i for i in IDS["instance_ids"] if i not in done][: limit or None]
    for iid in todo:
        row = fetch_row(iid)
        files = touched_files(row["patch"])
        base = row["base_commit"]
        blocks = []
        for f in files:
            blocks.append(f"File {f}:\n```python\n{file_at(base, f)}```")
        user = (f"Problem statement:\n{row['problem_statement']}\n\n"
                f"Files (at the base commit):\n\n" + "\n\n".join(blocks) +
                "\n\nReturn the unified diff that fixes the problem.")
        res = retry(lambda: upstream.call([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                            budget, seed=0, temperature=0.5, max_tokens=2048))
        diff = extract_diff(res["reply"])
        with PRED.open("a") as f:
            f.write(json.dumps({"instance_id": iid, "model_name_or_path": "gemma-4-31b-it-baseline",
                                "model_patch": diff}) + "\n")
        with RUNS.open("a") as f:
            f.write(json.dumps({"instance_id": iid, "reply": res["reply"][:4000], "files": files, "prompt_tokens": res["usage"].get("prompt_tokens"),
                                "completion_tokens": res["usage"].get("completion_tokens"),
                                "diff_chars": len(diff)}) + "\n")
        print(iid, "files", len(files), "prompt", res["usage"].get("prompt_tokens"), "diff chars", len(diff), flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
