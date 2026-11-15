#!/usr/bin/env python3
"""Make a Quay.io description from README.md.

Usage: quay-description.py <readme> <output>

Quay does not render Markdown tables, and relative links do not work there.
This script:
  - changes each table into a bullet list,
  - makes relative links absolute GitHub links.
"""
import re
import sys

BASE = "https://github.com/xSAVIKx/aws-emulator-docker/blob/main/"
SEPARATOR = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table_to_list(header, rows):
    out = []
    for row in rows:
        first, rest = row[0], row[1:]
        if len(header) == 2:
            out.append(f"- **{first}**: {rest[0]}")
        else:
            parts = [f"{h}: {v}" for h, v in zip(header[1:], rest) if v]
            out.append(f"- **{first}**: " + "; ".join(parts))
    return out


def convert_tables(text):
    lines, out, i, in_code = text.splitlines(), [], 0, False
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if (not in_code and line.lstrip().startswith("|") and i + 1 < len(lines)
                and SEPARATOR.match(lines[i + 1].strip())):
            header = cells(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            out.extend(table_to_list(header, rows))
            continue
        out.append(line)
        i += 1
    return "\n".join(out) + "\n"


def absolute_links(text):
    def fix(match):
        target = match.group(1)
        if re.match(r"^(https?:|mailto:|#)", target):
            return match.group(0)
        return f"]({BASE}{target.removeprefix('./')})"

    return re.sub(r"\]\(([^)\s]+)\)", fix, text)


def main():
    readme, output = sys.argv[1], sys.argv[2]
    text = open(readme, encoding="utf-8").read()
    with open(output, "w", encoding="utf-8") as f:
        f.write(absolute_links(convert_tables(text)))


if __name__ == "__main__":
    main()
