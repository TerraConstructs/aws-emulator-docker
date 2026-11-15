#!/usr/bin/env python3
"""Build site/llms-full.txt: the full project docs in one Markdown file.

Usage: build-llms-full.py <repo> <output-file>

The file contains:
  - the README of this repository,
  - the README of the examples,
  - the README of the GitHub Action, from its latest release,
  - the FAQ of the site (from the FAQPage JSON-LD in site/index.html),
  - the notes of the latest image release.

Relative links become absolute GitHub links. Set GH_TOKEN for a higher
API rate limit.
"""
import json
import os
import re
import sys
import urllib.request

API = "https://api.github.com"
ACTION_REPO = "xSAVIKx/run-aws-emulator"
SITE = "https://xsavikx.github.io/aws-emulator-docker/"


def get(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url)
    req.add_header("Accept", accept)
    token = os.environ.get("GH_TOKEN")
    if token and url.startswith(API):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def absolute_links(text, base):
    """Make relative Markdown link targets absolute. Keep in-page anchors."""

    def fix(match):
        target = match.group(1)
        if re.match(r"^(https?:|mailto:|#)", target):
            return match.group(0)
        return f"]({base}{target.removeprefix('./')})"

    return re.sub(r"\]\(([^)\s]+)\)", fix, text)


def demote(text):
    """Move each Markdown heading one level down, outside code blocks."""
    out, in_code = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if not in_code and re.match(r"^#{1,5} ", line):
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def faq(index_html):
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', index_html, re.S):
        data = json.loads(block)
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        for node in nodes:
            if node.get("@type") == "FAQPage":
                return "\n\n".join(
                    f"### {q['name']}\n\n{q['acceptedAnswer']['text']}" for q in node["mainEntity"]
                )
    raise SystemExit("No FAQPage JSON-LD in site/index.html")


def main():
    repo, output = sys.argv[1], sys.argv[2]
    blob = f"https://github.com/{repo}/blob/main/"

    readme = open("README.md", encoding="utf-8").read()
    examples = open("examples/README.md", encoding="utf-8").read()
    index_html = open("site/index.html", encoding="utf-8").read()

    action_tag = json.loads(get(f"{API}/repos/{ACTION_REPO}/releases/latest"))["tag_name"]
    action_readme = get(
        f"{API}/repos/{ACTION_REPO}/contents/README.md?ref={action_tag}",
        accept="application/vnd.github.raw",
    )
    release = json.loads(get(f"{API}/repos/{repo}/releases/latest"))

    parts = [
        "# AWS Emulator Docker Image: full documentation",
        "",
        "> The full docs of the unofficial AWS Emulator container image and the Run AWS Emulator "
        f"GitHub Action, in one file. The short version is {SITE}llms.txt. "
        "Not affiliated with Amazon Web Services.",
        "",
        demote(absolute_links(readme, blob)),
        "",
        f"Source: {blob}README.md",
        "",
        demote(absolute_links(examples, blob + "examples/")),
        "",
        f"Source: {blob}examples/README.md",
        "",
        demote(absolute_links(action_readme, f"https://github.com/{ACTION_REPO}/blob/{action_tag}/")),
        "",
        f"Source: https://github.com/{ACTION_REPO}/blob/{action_tag}/README.md (GitHub Action, release {action_tag})",
        "",
        "## FAQ",
        "",
        faq(index_html),
        "",
        f"## Latest image release: {release['name']}",
        "",
        demote(release["body"]),
        "",
    ]
    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"Wrote {output}: action {action_tag}, release {release['tag_name']}")


if __name__ == "__main__":
    main()
