#!/usr/bin/env python3
"""Health check for the LLM wiki in liutingchun/wiki/ (see wiki/CLAUDE.md).

    python3 liutingchun/scripts/wiki-lint.py            # report problems
    python3 liutingchun/scripts/wiki-lint.py --index    # also rewrite wiki/index.md

Checks: front matter (title, type, sources, updated), a "## Sources" section, broken relative
links, pages missing from index.md, and works on the website that have no wiki page.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = os.path.join(ROOT, "wiki")
ORDER = ["overview", "faq", "timeline", "work", "topic", "person", "institution", "list"]
HEAD = {"overview": "Start here", "faq": "Start here", "timeline": "Start here", "work": "Works",
        "topic": "Topics", "person": "People", "institution": "Institutions", "list": "Lists"}


def front(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    meta = {}
    for line in m.group(1).splitlines():
        k = re.match(r"(\w+):\s*(.*)", line)
        if k:
            meta[k.group(1)] = k.group(2).strip().strip('"')
    return meta, text[m.end():]


def summary(body):
    for para in body.split("\n\n"):
        p = para.strip()
        if p and not p.startswith("#"):
            p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p.replace("\n", " "))
            return p if len(p) < 170 else p[:167].rsplit(" ", 1)[0] + "…"
    return ""


pages = sorted(glob.glob(os.path.join(WIKI, "pages", "**", "*.md"), recursive=True))
problems, entries = [], []
for p in pages:
    rel = os.path.relpath(p, WIKI)
    text = open(p, encoding="utf-8").read()
    meta, body = front(text)
    if meta is None:
        problems.append("%s: no front matter" % rel)
        continue
    for k in ("title", "type", "sources", "updated"):
        if k not in meta:
            problems.append("%s: front matter misses '%s'" % (rel, k))
    if "\n## Sources" not in body:
        problems.append("%s: no '## Sources' section" % rel)
    for target in re.findall(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", body):
        if not target.startswith("http") and not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(p), target))):
            problems.append("%s: broken link -> %s" % (rel, target))
    t = meta.get("type", "list")
    if os.path.basename(p) == "timeline.md":
        t = "timeline"
    entries.append((ORDER.index(t) if t in ORDER else 99, rel, meta.get("title", rel), summary(body), t))

# works on the website without a page
site = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))
for w in site["works"]:
    if not w.get("hidden") and not os.path.exists(os.path.join(WIKI, "pages", "works", w["slug"] + ".md")):
        problems.append("missing work page: pages/works/%s.md" % w["slug"])

if "--index" in sys.argv:
    out = ["# Index", "", "Catalogue of the wiki. Read this first, then open the pages you need.", ""]
    last = None
    for _, rel, title, summ, t in sorted(entries):
        if HEAD.get(t) != last:
            last = HEAD.get(t, "Other")
            out += ["", "## " + last, ""]
        out.append("- [%s](%s) — %s" % (title, rel, summ))
    open(os.path.join(WIKI, "index.md"), "w", encoding="utf-8").write("\n".join(out).replace("\n\n\n", "\n\n") + "\n")
    print("index.md rewritten (%d pages)" % len(entries))

index = open(os.path.join(WIKI, "index.md"), encoding="utf-8").read() if os.path.exists(os.path.join(WIKI, "index.md")) else ""
for _, rel, *_ in entries:
    if "(%s)" % rel not in index:
        problems.append("not in index.md: %s" % rel)

print("%d pages, %d problems" % (len(entries), len(problems)))
for x in problems:
    print("  - " + x)
sys.exit(1 if problems else 0)
