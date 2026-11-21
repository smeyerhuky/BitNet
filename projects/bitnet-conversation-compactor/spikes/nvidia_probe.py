"""Spike: one chat completion against the NVIDIA-hosted Gemma endpoint.

Reads the key from NVIDIA_API_KEY. Never put the key in this file.
"""
import json
import os
import sys
import urllib.request

URL = "https://integrate.api.nvidia.com/v1/chat/completions"
key = os.environ.get("NVIDIA_API_KEY")
if not key:
    sys.exit("NVIDIA_API_KEY is not set")

payload = {
    "model": "google/gemma-4-31b-it",
    "max_tokens": 1024,
    "stream": False,
    "temperature": 0.5,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "seed": 0,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 17 * 23?"},
    ],
}
req = urllib.request.Request(
    URL,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
             "Accept": "application/json"},
)
with urllib.request.urlopen(req, timeout=60) as resp:
    body = json.load(resp)
print(body["choices"][0]["message"]["content"])
print(json.dumps(body.get("usage")))
