#!/usr/bin/env python3
"""Check every Vimeo / YouTube video used on the site through the official oEmbed APIs.

Prints, per video: status (ok / private / missing), title and thumbnail URL.
Runs in GitHub Actions (check-links.yml); needs internet access.
"""
import glob
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))

used = []  # (where, url)
for p in D.get("performances", []):
    used.append(("performance: " + p["title"], p["video"]))
for w in D["works"]:
    if w.get("video"):
        used.append(("work: " + w["slug"], w["video"]))
for f in sorted(glob.glob(os.path.join(ROOT, "posts", "*.md"))):
    for u in re.findall(r"https?://(?:www\.)?(?:vimeo\.com/\d+|youtu\.be/[\w-]+|youtube\.com/watch\?v=[\w-]+)", open(f).read()):
        used.append(("post: " + os.path.basename(f), u))

for where, u in used:
    if "vimeo" in u:
        api = "https://vimeo.com/api/oembed.json?url=" + urllib.parse.quote(u, safe="")
    else:
        api = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(u, safe="")
    try:
        req = urllib.request.Request(api, headers={"User-Agent": "Mozilla/5.0 (link check)"})
        info = json.load(urllib.request.urlopen(req, timeout=20))
        print("OK      | %-48s | %s | %s | %s" % (where, u, info.get("title"), info.get("thumbnail_url")))
    except urllib.error.HTTPError as e:
        state = {401: "PRIVATE", 403: "PRIVATE", 404: "MISSING"}.get(e.code, "HTTP %d" % e.code)
        print("%-7s | %-48s | %s" % (state, where, u))
    except Exception as e:  # network problems
        print("ERROR   | %-48s | %s | %s" % (where, u, e))
