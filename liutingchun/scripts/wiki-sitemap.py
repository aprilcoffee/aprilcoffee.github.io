#!/usr/bin/env python3
"""Write wiki/pages/site-map.md from data/site.json: every page of the website (in each
language) and every external link the site points to. The homepage chat recommends links
only from the knowledge base, so this page is what it can send visitors to.

Run by scripts/build.py and scripts/build-knowledge.py; safe to run by hand."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))
S = D["site"]
BASE = S["base_url"].rstrip("/") + "/"
# Sun and Heat as Image live on the GitHub Pages domain whichever domain the site uses.
PROJECTS = "https://aprilcoffee.github.io/"
LANGS = [("en", ""), ("de", "de/"), ("zh", "zh/")]


def each(path):
    return " · ".join("[%s](%s%s%s)" % (l, BASE, p, path) for l, p in LANGS)


works = [w for w in D["works"] if not w.get("hidden")]
perfs = [p for p in D.get("performances", []) if not p.get("hidden") and p.get("video")]
posts = [p for p in D.get("writing", []) if not p.get("hidden")]
friends = [f for f in D.get("friends", []) if f.get("url")]

out = ["""---
title: "Site map and links"
type: list
tags: [navigation, links]
sources:
  - ../../data/site.json
  - %s
updated: generated
---
# Site map and links

Every page of the website and every external link it points to, generated from the site data.
Each page exists in English, German (de) and Traditional Chinese (zh); blog posts exist once,
in Mandarin. Recommend the version in the visitor's language.

## Main sections

- **Home** (statement, selected works, "ask about the work"): %s
- **Works** (all works, %d): %s
- **Performance** (audio-visual performance videos): %s
- **About** (biography and CV: teaching, education, awards, talks, publications, exhibitions): %s
- **Blog archive** (notes on works, technical write-ups; in Mandarin): %sblog/
- **Friends** (artists and collaborators): %s
- **Impressum** (legal notice): %simpressum/
- **Privacy policy** (Datenschutz): %sdatenschutz/
""" % (BASE, each(""), len(works), each("works/"), each("performance/"), each("about/"),
       BASE, each("friends/"), BASE, BASE)]

out.append("## Works\n")
for w in works:
    line = "- **%s**%s (%s): %s" % (w["title"], " %s" % w["title_zh"] if w.get("title_zh") else "",
                                    w.get("year", ""), each("works/%s/" % w["slug"]))
    for l in w.get("links", []):
        if l.get("url"):
            line += " — %s: %s" % (l.get("label") or "link", l["url"])
    out.append(line)

out.append("\n## Performance videos\n")
for p in perfs:
    out.append("- **%s**: %s" % (p["title"], p["video"]))

out.append("\n## Blog posts (Mandarin)\n")
for p in posts:
    out.append("- **%s** (%s): %sblog/%s/" % (p["title"], p.get("date", "")[:10], BASE, p["slug"]))

out.append("\n## Other projects on the same domain\n")
out.append("- **Sun** (internet art, open on a phone): %ssun/" % PROJECTS)
out.append("- **Heat as Image** (artistic research website): %sheat_as_image/" % PROJECTS)

out.append("\n## Elsewhere\n")
for l in S.get("links", []):
    out.append("- **%s**: %s" % (l["label"], l["url"]))
out.append("- **Email**: mailto:%s" % S["email"])

out.append("\n## Friends' websites\n")
for f in friends:
    out.append("- **%s**: %s" % (f["name"], f["url"]))

out.append("\n## Sources\n\n- ../../data/site.json\n- %s\n" % BASE)

path = os.path.join(ROOT, "wiki", "pages", "site-map.md")
text = "\n".join(out)
old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
if text != old:  # untouched files keep watchers (wrangler dev) from rebuilding in a loop
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
