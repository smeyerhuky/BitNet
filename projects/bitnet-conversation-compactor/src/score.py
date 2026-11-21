"""Deterministic scoring for coding replies: extract the last python block, run behavior and constraint tests in a subprocess."""
import re
import subprocess
import sys
import tempfile
import os

BLOCK = re.compile(r"```(?:python)?\s*\n(.*?)```", re.S)


def extract_code(reply):
    blocks = BLOCK.findall(reply)
    return blocks[-1] if blocks else None


def run_tests(code, tests, timeout=10):
    """Return (passed: bool, detail: str). Executes model code: callers must treat it as untrusted."""
    if code is None:
        return False, "no code block"
    src = code + "\n\n" + tests
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "t.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        try:
            p = subprocess.run([sys.executable, "-I", path], capture_output=True, text=True, timeout=timeout, cwd=d)
        except subprocess.TimeoutExpired:
            return False, "timeout"
    return p.returncode == 0, (p.stderr.strip().splitlines() or [""])[-1][:200]


def score_reply(reply, task):
    code = extract_code(reply)
    ok_beh, why_beh = run_tests(code, task["tests"])
    ok_con, why_con = run_tests(code, task["ctest"])
    return {"behavior_pass": ok_beh, "constraint_pass": ok_con, "detail": why_beh or why_con}
