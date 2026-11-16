#!/usr/bin/env python3
"""Check the versions in the docs snippets against the latest GitHub releases.

Usage: check-doc-versions.py <file>...

It finds:
  - action references, for example "actions/checkout@v7",
  - the cosign container image, for example "cosign/cosign:v3.1.4".

A major tag (v7) is current when it is the major version of the latest
release. A full version (v3.1.4) is current when it is the latest release.
The script prints a GitHub error annotation for each old version and exits
with status 1. Set GH_TOKEN for a higher API rate limit.
"""
import json
import os
import re
import sys
import urllib.request

ACTION = re.compile(r"\b([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@(v\d+(?:\.\d+)*)\b")
IMAGES = {re.compile(r"\bcosign/cosign:(v\d+(?:\.\d+)*)\b"): "sigstore/cosign"}

_latest = {}


def latest(repo):
    if repo not in _latest:
        req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/latest")
        req.add_header("Accept", "application/vnd.github+json")
        token = os.environ.get("GH_TOKEN")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=30) as resp:
            _latest[repo] = json.load(resp)["tag_name"]
    return _latest[repo]


def is_current(used, newest):
    used_parts = used.lstrip("v").split(".")
    newest_parts = newest.lstrip("v").split(".")
    return used_parts == newest_parts[: len(used_parts)]


def main(files):
    problems = checked = 0
    for path in files:
        for number, line in enumerate(open(path, encoding="utf-8"), start=1):
            found = [(m.group(1), m.group(2)) for m in ACTION.finditer(line)]
            for pattern, repo in IMAGES.items():
                found += [(repo, m.group(1)) for m in pattern.finditer(line)]
            for repo, used in found:
                checked += 1
                newest = latest(repo)
                if not is_current(used, newest):
                    problems += 1
                    print(f"::error file={path},line={number}::{repo} {used} is old. The latest release is {newest}.")
    print(f"Checked {checked} references in {len(files)} files. Old: {problems}.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
