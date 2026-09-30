#!/usr/bin/env python3
"""Generate the static site from data/site.json and posts/*.md.

Every page gets its own folder (works/<slug>/index.html, writing/<slug>/index.html, ...)
with full SEO tags, plus sitemap.xml and robots.txt.

    pip install markdown
    python3 liutingchun/scripts/build.py
"""
import datetime
import html
import json
import os
import re
import shutil
from urllib.parse import urlparse, urlsplit

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # liutingchun/
REPO = os.path.dirname(ROOT)
D = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))
S = D["site"]
BASE = S["base_url"].rstrip("/")
PREFIX = urlparse(BASE).path.rstrip("/") + "/"  # e.g. "/liutingchun/"
SECTIONS = ["works", "performance", "about", "writing", "friends"]

esc = lambda s: html.escape(str(s or ""), quote=True)
works = [w for w in D["works"] if not w.get("hidden")]
posts = [p for p in D.get("writing", []) if not p.get("hidden")]
post_slugs = {p["slug"] for p in posts}


# ---------- urls ----------
def url(path=""):
    return PREFIX + path


def abs_url(path=""):
    return BASE + "/" + path


def asset(u):
    return u if re.match(r"^(https?:)?//", u or "") else url((u or "").lstrip("/"))


def asset_abs(u):
    return u if re.match(r"^https?://", u or "") else abs_url((u or "").lstrip("/"))


# old liutingchun.com (Wix) paths -> new pages
OLD = {"": "", "/": "", "/cv": "about/", "/video-records": "performance/", "/friends": "friends/",
       "/blog": "writing/", "/works": "works/", "/blog/categories/works": "writing/",
       "/blog/categories/technique": "writing/"}
for w in D["works"]:
    for a in w.get("aliases", []):
        OLD[a.rstrip("/")] = "works/%s/" % w["slug"]


def fix_link(href):
    """Point old Wix links at the new pages and drop tracking parameters."""
    try:
        p = urlsplit(href)
    except ValueError:
        return href
    if p.netloc.endswith("liutingchun.com"):
        path = p.path.rstrip("/")
        m = re.match(r"^/post/([^/]+)$", path)
        if m and m.group(1) in post_slugs:
            return url("writing/%s/" % m.group(1))
        if path in OLD:
            return url(OLD[path])
    if "fbclid=" in (p.query or ""):
        q = "&".join(x for x in p.query.split("&") if not x.startswith("fbclid="))
        return p._replace(query=q).geturl()
    return href


TITLES = {}  # new page path -> title, filled in below


def a(href, text, cls=""):
    orig, href = href, fix_link(href)
    if href != orig and html.unescape(text) == orig and href in TITLES:
        text = esc(TITLES[href])  # a bare old URL as link text -> the page title
    ext = re.match(r"^https?://", href) and not href.startswith(BASE)
    return '<a href="%s"%s%s>%s</a>' % (esc(href), ' class="%s"' % cls if cls else "",
                                         ' target="_blank" rel="noopener"' if ext else "", text)


# ---------- media ----------
def img_src(u, w):
    m = re.match(r"^https://static\.wixstatic\.com/media/([^/?#]+)$", u or "")
    if not m or m.group(1).lower().endswith(".gif"):
        return asset(u)
    return "%s/v1/fit/w_%d,h_%d,q_85,enc_auto/%s" % (u, w, w, m.group(1))


def img(u, w, alt="", cls="", lazy=True):
    fb = asset(u)
    return ('<img src="%s" alt="%s" loading="%s" decoding="async"%s '
            'onerror="if(this.src!==\'%s\')this.src=\'%s\'">') % (
        esc(img_src(u, w)), esc(alt), "lazy" if lazy else "eager", ' class="%s"' % cls if cls else "", esc(fb), esc(fb))


def video_id(u):
    u = u or ""
    m = re.search(r"vimeo\.com/(?:video/)?(\d+)", u)
    if m:
        return "vimeo", m.group(1)
    m = re.search(r"(?:youtu\.be/|v=|embed/)([\w-]{11})", u)
    if m:
        return "youtube", m.group(1)
    if re.search(r"\.(mp4|mov|webm)(\?|$)", u):
        return "file", u
    return None


def embed(u, thumb="", title=""):
    v = video_id(u)
    if not v:
        return ""
    kind, vid = v
    if kind == "file":
        return '<div class="embed"><video controls preload="none" playsinline src="%s"></video></div>' % esc(asset(vid))
    src = ("https://player.vimeo.com/video/%s?dnt=1&autoplay=1" % vid if kind == "vimeo"
           else "https://www.youtube-nocookie.com/embed/%s?autoplay=1" % vid)
    if not thumb:
        thumb = ("https://vumbnail.com/%s.jpg" % vid if kind == "vimeo"
                 else "https://i.ytimg.com/vi/%s/hqdefault.jpg" % vid)
    # A thumbnail that swaps itself for the player on click keeps pages light.
    return ('<button class="embed lite" type="button" data-src="%s" aria-label="Play video%s">'
            '%s<span class="play" aria-hidden="true"></span></button>') % (
        esc(src), esc(": " + title) if title else "", img(thumb, 1280, title))


def cover_of(w):
    if w.get("cover"):
        return w["cover"]
    if w.get("images"):
        return w["images"][0]
    v = video_id(w.get("video"))
    if v and v[0] == "vimeo":
        return "https://vumbnail.com/%s.jpg" % v[1]
    if v and v[0] == "youtube":
        return "https://i.ytimg.com/vi/%s/hqdefault.jpg" % v[1]
    return ""


# ---------- text ----------
URL_RE = re.compile(r"https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+")


def linkify(text):
    out, last = [], 0
    for m in URL_RE.finditer(text):
        u = m.group(0).rstrip(".,;:!?)")
        out.append(esc(text[last:m.start()]))
        out.append(a(u, esc(u)))
        last = m.start() + len(u)
    out.append(esc(text[last:]))
    return "".join(out)


def prose(text):
    """Work descriptions: blank line = paragraph, '# ' = heading."""
    parts = []
    for p in re.split(r"\n\s*\n", text or ""):
        p = p.strip()
        if not p:
            continue
        if p.startswith("# "):
            parts.append("<h3>%s</h3>" % esc(p[2:]))
        else:
            parts.append("<p>%s</p>" % linkify(p).replace("\n", "<br>"))
    return "".join(parts)


# a URL in running text that isn't already inside Markdown link syntax
BARE_URL_RE = re.compile(r"(?<![(<\"'\[])" + URL_RE.pattern)


def autolink(m):
    u = m.group(0)
    core = u.rstrip(".,;:!?)")
    return "<%s>%s" % (core, u[len(core):])


def post_html(src):
    """Blog posts are Markdown; bare video URLs on their own line become players."""
    lines, fenced = [], False
    for line in src.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced:
            s = line.strip()
            if URL_RE.fullmatch(s) or re.fullmatch(r"\S+\.(mp4|mov|webm)", s):
                line = ("\n" + embed(s) + "\n") if video_id(s) else "<%s>" % s
            else:
                line = BARE_URL_RE.sub(autolink, line)
        lines.append(line)
    h = markdown.markdown("\n".join(lines), extensions=["fenced_code", "nl2br", "sane_lists"])
    # images -> figures (alt text is the caption)
    h = re.sub(r'<p>\s*<img alt="([^"]*)" src="([^"]+)"\s*/?>\s*</p>',
               lambda m: "<figure>%s%s</figure>" % (
                   img(html.unescape(m.group(2)), 1600, html.unescape(m.group(1))),
                   "<figcaption>%s</figcaption>" % m.group(1) if m.group(1) else ""), h)
    h = re.sub(r'<img alt="([^"]*)" src="([^"]+)"\s*/?>',
               lambda m: img(html.unescape(m.group(2)), 1600, html.unescape(m.group(1))), h)
    # links: old site -> new pages, external -> new tab
    h = re.sub(r'<a href="([^"]+)">(.*?)</a>', lambda m: a(html.unescape(m.group(1)), m.group(2)), h)
    return h


def read_post(slug):
    p = os.path.join(ROOT, "posts", slug + ".md")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def summary(text, n=160):
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)|```.*?```", " ", text or "", flags=re.S)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"https?://\S+|[#>*_`]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[:n - 1].rstrip() + "…"


# ---------- layout ----------
NAV_LABELS = {"works": "Works", "performance": "Performance", "about": "About", "writing": "Writing", "friends": "Friends"}


def idx(n):
    return '<span class="idx">(%d)</span>' % n


def layout(path, title, desc, body, image=None, og_type="website", lang="en", ld=None, full=False, section=""):
    page_title = "%s — %s" % (title, S["name"]) if title else "%s %s" % (S["name"], S.get("name_zh", ""))
    canonical = abs_url(path)
    image = asset_abs(image or S.get("og_image") or "")
    nav = "".join('<a href="%s"%s>%s<span>%s</span></a>' % (
        url(s + "/"), ' class="on" aria-current="page"' if s == section else "", idx(i + 1), NAV_LABELS[s])
        for i, s in enumerate(SECTIONS))
    links = "".join(a(l["url"], esc(l["label"])) for l in S.get("links", []))
    ld_tag = ('<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False)) if ld else ""
    ga = ('<script async src="%s" data-ga="%s" data-banner></script>' % (url("assets/analytics.js"), esc(S["ga_id"]))
          if S.get("ga_id") else "")
    return """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="author" content="{name}">
<link rel="canonical" href="{c}">
<meta property="og:site_name" content="{name}">
<meta property="og:locale" content="{locale}">
<meta property="og:type" content="{ogt}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{c}">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{img}">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{icon}" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{name} — Writing" href="{feed}">
{ga}
<link rel="stylesheet" href="{css}">
{ld}
</head>
<body>
<aside class="side" id="side">
  <div class="side-head">
    <a class="brand" href="{home}"><span class="brand-en">{name}</span><span class="brand-zh">{zh}</span></a>
    <button class="menu-btn" id="menuBtn" aria-label="Menu" aria-expanded="false">Menu</button>
  </div>
  <nav class="nav" id="nav" aria-label="Main">{nav}</nav>
  <div class="side-foot">
    <div class="signal" data-effect="signal" aria-hidden="true"></div>
    <div><a href="mailto:{email}">{email}</a></div>
    <div class="links">{links}</div>
    <div>© {year} {name}</div>
    <div class="legal"><a href="{imp}">Impressum</a><a href="{dsg}">Datenschutz</a></div>
  </div>
</aside>
<main class="main{full}" id="main">
{body}
</main>
<script src="{js}" data-p5="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.4/p5.min.js" data-effects="{fx}" defer></script>
</body>
</html>
""".format(lang=lang, locale="zh_TW" if lang.startswith("zh") else "en_US", t=esc(page_title),
           d=esc(desc or S.get("description")), name=esc(S["name"]), zh=esc(S.get("name_zh", "")), c=esc(canonical),
           ogt=og_type, img=esc(image), icon=url("assets/favicon.svg"), css=url("assets/style.css"),
           js=url("assets/site.js"), fx=url("assets/effects.js"), feed=url("writing/feed.xml"), ga=ga, ld=ld_tag,
           home=url(), imp=url("impressum/"), dsg=url("datenschutz/"), nav=nav, email=esc(S["email"]), links=links, year=datetime.date.today().year,
           full=" full" if full else "", body=body)


PERSON = {"@context": "https://schema.org", "@type": "Person", "name": S["name"],
          "alternateName": [S.get("name_zh", ""), "Liu Ting-Chun", "劉庭均"], "url": abs_url(), "email": "mailto:" + S["email"],
          "jobTitle": S.get("job_title", "Artist"), "description": S.get("statement") or S.get("description", ""),
          "knowsAbout": S.get("knows_about", []),
          "hasOccupation": [{"@type": "Occupation", "name": o} for o in S.get("occupations", [])],
          "sameAs": [l["url"] for l in S.get("links", [])]}
PERSON.update(S.get("person_extra", {}))


def pager(items, i, base, label, noun):
    prev = items[i - 1] if i > 0 else None
    nxt = items[i + 1] if i < len(items) - 1 else None
    one = lambda it, n, arrow: ('<a href="%s"><span class="mono">%s</span><span class="t">%s</span></a>' % (
        url(base % it["slug"]), arrow % n, esc(it[label])))
    return '<nav class="pager" aria-label="%s">%s%s</nav>' % (
        noun, one(prev, i, "← (%d)") if prev else "<span></span>", one(nxt, i + 2, "(%d) →") if nxt else "<span></span>")


def page_head(title, lead=""):
    return '<header class="page-head"><h1 class="page-title">%s</h1>%s</header>' % (
        esc(title), '<p class="lead">%s</p>' % esc(lead) if lead else "")


def work_card(n, w):
    c = cover_of(w)
    return ('<a class="card" href="%s"><div class="thumb">%s</div><div class="cap">%s<span class="t">%s%s</span>'
            '<span class="mono">%s</span></div></a>') % (
        url("works/%s/" % w["slug"]), img(c, 900, w["title"]) if c else '<span class="ph">%s</span>' % esc(w["title"]),
        idx(n), esc(w["title"]), '<span class="zh">%s</span>' % esc(w["title_zh"]) if w.get("title_zh") else "",
        esc(w.get("year")))


def meta(rows):
    return '<dl class="meta">%s</dl>' % "".join("<dt>%s</dt><dd>%s</dd>" % r for r in rows if r[1])


# ---------- pages ----------
pages = {}  # path -> html
TITLES.update({url("works/%s/" % w["slug"]): w["title"] for w in works})
TITLES.update({url("writing/%s/" % p["slug"]): p["title"] for p in posts})
TITLES.update({url(s + "/"): NAV_LABELS[s] for s in SECTIONS})


def page(path, *args, **kw):
    pages[path] = layout(path, *args, **kw)


# home: generative field + statement, then a few recent works
page("", "", S.get("description"),
     '<section class="home-hero"><div class="field" data-effect="field" aria-hidden="true"></div>'
     '<h1 class="sr-only">%s %s</h1><p class="home-statement"><span>%s</span></p></section>'
     '<section class="home-selected" aria-label="Selected works"><div class="grid">%s</div>'
     '<a class="more" href="%s">All works (%d) →</a></section>' % (
         esc(S["name"]), esc(S.get("name_zh", "")), esc(S.get("statement") or S.get("description")),
         "".join(work_card(i + 1, w) for i, w in enumerate(works[:3])), url("works/"), len(works)),
     ld=PERSON, full=True)

years = sorted(w["year"][:4] for w in works if w.get("year"))
page("works/", "Works", "Selected works by %s, %s–%s: installations, performances, internet art and artistic research on AI." % (
         S["name"], years[0] if years else "", years[-1] if years else ""),
     page_head("Works", "Installations, performances, internet art and artistic research, %s–%s." % (
         years[0] if years else "", years[-1] if years else "")) +
     '<div class="grid">%s</div>' % "".join(work_card(i + 1, w) for i, w in enumerate(works)), section="works")

for i, w in enumerate(works):
    rows = [("Year", esc(w.get("year"))), ("Type", esc(w.get("type"))), ("Materials", esc(w.get("materials"))),
            ("With", esc(w.get("collaborators")))]
    rows += [("Link", a(l["url"], esc(l.get("label") or l["url"]))) for l in w.get("links", []) if l.get("url")]
    ims = w.get("images", [])
    plates = embed(w.get("video"), title=w["title"])
    plates += "".join(('<figure class="hero">%s</figure>' if k == 0 and not w.get("video") else "<figure>%s</figure>") %
                      img(u, 2000 if k == 0 else 1400, "%s — %d" % (w["title"], k + 1)) for k, u in enumerate(ims))
    rest = len(ims) - (0 if w.get("video") else 1)  # images in the two-column part of the grid
    if rest > 0 and rest % 2:
        plates = plates.replace("<figure>", '<figure class="wide">', 1)  # never leave an empty cell
    body = ('<article class="work"><aside class="work-info">%s<h1>%s</h1>%s%s<div class="prose">%s</div>%s</aside>'
            '<div class="plates">%s</div>%s</article>') % (
        idx(i + 1), esc(w["title"]), '<p class="zh">%s</p>' % esc(w["title_zh"]) if w.get("title_zh") else "",
        meta(rows), prose(w.get("text")), '<p class="credits">%s</p>' % esc(w["credits"]) if w.get("credits") else "",
        plates, pager(works, i, "works/%s/", "title", "Works"))
    desc = summary(w.get("text")) or "%s (%s), %s by %s." % (w["title"], w.get("year"), w.get("type") or "work", S["name"])
    ld = {"@context": "https://schema.org", "@type": "CreativeWork", "name": w["title"],
          "alternateName": w.get("title_zh") or None, "dateCreated": w.get("year", "")[:4],
          "genre": w.get("type") or None, "url": abs_url("works/%s/" % w["slug"]),
          "image": asset_abs(cover_of(w)) if cover_of(w) else None, "description": desc,
          "creator": {"@type": "Person", "name": S["name"], "url": abs_url()}}
    page("works/%s/" % w["slug"], w["title"] + (" " + w["title_zh"] if w.get("title_zh") else ""), desc, body,
         image=cover_of(w), og_type="article", ld={k: v for k, v in ld.items() if v}, section="works")

perf = "".join('<div>%s<div class="cap">%s<h2>%s</h2><p>%s</p></div></div>' % (
    embed(p["video"], p.get("thumb", ""), p["title"]), idx(n + 1), esc(p["title"]), esc(p.get("note")))
    for n, p in enumerate(D.get("performances", [])))
page("performance/", "Audio-Visual Performance", "Audio-visual performance records of %s." % S["name"],
     page_head("Audio-Visual Performance", "Live audio-visual sets and performance records, 2016–2024.") +
     '<div class="perf">%s</div>' % perf,
     image=(D.get("performances") or [{}])[0].get("thumb"), section="performance")

cv = ""
for n, sec in enumerate(D["about"]["sections"]):
    rows = "".join('<div class="cv-row"><span class="mono">%s</span><span>%s</span></div>' % (
        esc(it.get("year")), a(it["url"], esc(it["text"])) if it.get("url") else esc(it["text"])) for it in sec["items"])
    cv += '<section class="cv-sec"><h2>%s%s</h2><div>%s</div></section>' % (idx(n + 1), esc(sec["title"]), rows)
page("about/", "About", D["about"]["bio"],
     '<div class="about-top"><h1 class="page-title">About</h1><div><p class="bio">%s</p>'
     '<p class="contact"><a href="mailto:%s">%s</a></p></div></div>%s' % (
         esc(D["about"]["bio"]), esc(S["email"]), esc(S["email"]), cv),
     ld=dict(PERSON, description=D["about"]["bio"]), og_type="profile", section="about")

groups, order = {}, []
for p in posts:
    y = p["date"][:4]
    if y not in groups:
        groups[y] = []
        order.append(y)
    groups[y].append('<li><a href="%s"><span class="t">%s</span><span class="cat mono">%s</span>'
                     '<span class="ex">%s</span></a></li>' % (
                         url("writing/%s/" % p["slug"]), esc(p["title"]), esc(p.get("category")), esc(p.get("excerpt"))))
page("writing/", "Writing", "Writing and technical notes by %s: artworks, Raspberry Pi, Processing and Python." % S["name"],
     page_head("Writing", "Notes on works, and technical write-ups on Raspberry Pi, Processing and Python (in Mandarin).") +
     "".join('<section class="year-group"><span class="mono">%s</span><ul>%s</ul></section>' % (y, "".join(groups[y])) for y in order),
     section="writing")

for i, p in enumerate(posts):
    src = read_post(p["slug"])
    desc = p.get("excerpt") or summary(src)
    body = ('<article class="post"><aside class="post-info"><h1>%s</h1>%s<a class="back" href="%s">← Writing</a></aside>'
            '<div class="prose post-body">%s</div>%s</article>') % (
        esc(p["title"]), meta([("Date", esc(p["date"])), ("Category", esc(p.get("category")))]), url("writing/"),
        post_html(src), pager(posts, i, "writing/%s/", "title", "Posts"))
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "datePublished": p["date"],
          "inLanguage": p.get("lang", "zh-Hant"), "url": abs_url("writing/%s/" % p["slug"]),
          "image": asset_abs(p.get("cover") or S.get("og_image")), "description": desc,
          "author": {"@type": "Person", "name": S["name"], "url": abs_url()},
          "mainEntityOfPage": abs_url("writing/%s/" % p["slug"])}
    page("writing/%s/" % p["slug"], p["title"], desc, body, image=p.get("cover"), og_type="article",
         lang=p.get("lang", "zh-Hant"), ld=ld, section="writing")


def friend(f):
    thumb = img(f["image"], 600, f["name"]) if f.get("image") else '<span class="ph">%s</span>' % esc(f["name"])
    if not f.get("url"):  # site no longer online: keep the name, drop the link
        return '<div class="card"><div class="thumb">%s</div><div class="cap"><span class="t">%s</span></div></div>' % (
            thumb, esc(f["name"]))
    return ('<a class="card" href="%s" target="_blank" rel="noopener"><div class="thumb">%s</div>'
            '<div class="cap"><span class="t">%s</span><span class="mono">↗</span></div></a>') % (
        esc(f["url"]), thumb, esc(f["name"]))


page("friends/", "Friends", "Friends and fellow artists of %s." % S["name"],
     page_head("Friends", "Artists and collaborators.") +
     '<div class="grid friends">%s</div>' % "".join(friend(f) for f in D.get("friends", [])), section="friends")


addr = S.get("address") or []
addr_html = "<br>".join(esc(x) for x in addr) if addr else \
    '<span class="todo">[Postanschrift fehlt — in site.json → site.address eintragen]</span>'
page("impressum/", "Impressum", "Impressum / legal notice of %s." % S["name"], """
<div class="legal-page">
<h1 class="page-title">Impressum</h1>
<h2>Angaben gemäß § 5 DDG</h2>
<p>{name}<br>{addr}</p>
<h2>Kontakt</h2>
<p>E-Mail: <a href="mailto:{email}">{email}</a></p>
<h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2>
<p>{name}<br>{addr}</p>
<h2>Haftung für Links</h2>
<p>Diese Website enthält Links zu externen Websites Dritter, auf deren Inhalte ich keinen Einfluss habe. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter verantwortlich. Bei Bekanntwerden von Rechtsverletzungen werden derartige Links umgehend entfernt.</p>
<h2>Urheberrecht</h2>
<p>Texte, Bilder und Videos auf dieser Website unterliegen dem Urheberrecht von {name} bzw. der genannten Fotograf*innen und Kooperationspartner*innen. Eine Verwendung ist nur nach vorheriger Zustimmung erlaubt.</p>
<p class="en">Legal notice for this personal artist website. Contact: {email}.</p>
</div>""".format(name=esc(S["name"]), addr=addr_html, email=esc(S["email"])))

page("datenschutz/", "Datenschutz", "Privacy policy (Datenschutzerklärung) of %s." % S["name"], """
<div class="legal-page">
<h1 class="page-title">Datenschutz&shy;erklärung</h1>
<h2>1. Verantwortlicher</h2>
<p>{name}<br>{addr}<br>E-Mail: <a href="mailto:{email}">{email}</a></p>
<h2>2. Hosting</h2>
<p>Diese Website wird bei GitHub Pages (GitHub Inc., 88 Colin P. Kelly Jr. St., San Francisco, CA 94107, USA) gehostet. Beim Aufruf verarbeitet GitHub technisch notwendige Daten wie IP-Adresse, Zeitpunkt und aufgerufene Seite in Server-Logfiles, um die Website auszuliefern und abzusichern. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an einer sicheren und funktionsfähigen Website). Die Übermittlung in die USA erfolgt auf Grundlage des EU-US Data Privacy Framework.</p>
<h2>3. Google Analytics</h2>
<p>Nur wenn Sie im Hinweis auf „OK“ klicken, wird Google Analytics 4 (Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland) geladen. Google Analytics setzt dann Cookies und erfasst pseudonymisierte Nutzungsdaten (z.&nbsp;B. aufgerufene Seiten, Verweildauer, ungefährer Standort, Gerät), um die Nutzung dieser Website statistisch auszuwerten. IP-Adressen werden von Google Analytics 4 nicht gespeichert. Werbefunktionen sind deaktiviert. Rechtsgrundlage ist Ihre Einwilligung (Art. 6 Abs. 1 lit. a DSGVO, § 25 Abs. 1 TDDDG). Ohne Einwilligung wird Google Analytics nicht geladen. Eine Übermittlung in die USA ist möglich; Google ist unter dem EU-US Data Privacy Framework zertifiziert.</p>
<p>Sie können Ihre Einwilligung jederzeit widerrufen: <button type="button" data-consent-reset>Einstellung zurücksetzen / Reset choice</button></p>
<h2>4. Eingebettete Videos (Vimeo, YouTube)</h2>
<p>Videos werden erst geladen, wenn Sie auf das Vorschaubild klicken. Erst dann werden Daten (u.&nbsp;a. IP-Adresse) an Vimeo (Vimeo.com Inc., New York, USA) bzw. YouTube (Google Ireland Limited) übertragen; YouTube wird im erweiterten Datenschutzmodus (youtube-nocookie.com) eingebunden. Vorschaubilder einiger Vimeo-Videos werden über vumbnail.com geladen.</p>
<h2>5. Externe Bilder</h2>
<p>Einzelne ältere Bilder werden noch vom Server der früheren Website (static.wixstatic.com, Wix.com Ltd.) geladen. Dabei wird Ihre IP-Adresse an Wix übertragen. Diese Bilder werden nach und nach auf diese Website verlagert.</p>
<h2>6. Schriften und Skripte</h2>
<p>Es werden keine Google Fonts von Google-Servern geladen. Die Bibliothek p5.js für die grafischen Animationen wird von cdnjs (Cloudflare, Inc.) geladen; dabei wird Ihre IP-Adresse an Cloudflare übertragen (Art. 6 Abs. 1 lit. f DSGVO).</p>
<h2>7. Ihre Rechte</h2>
<p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit, Widerspruch sowie auf Widerruf erteilter Einwilligungen. Außerdem können Sie sich bei einer Datenschutz-Aufsichtsbehörde beschweren.</p>
<p class="en">In short: analytics only runs after you click OK; videos only load when you press play; nothing else tracks you.</p>
</div>""".format(name=esc(S["name"]), addr=addr_html, email=esc(S["email"])))


# ---------- write ----------
def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)


for s in SECTIONS + ["impressum", "datenschutz"]:  # start clean so removed works/posts disappear
    shutil.rmtree(os.path.join(ROOT, s), ignore_errors=True)
for path, text in pages.items():
    write(path + "index.html", text)

# RSS feed for the blog
feed_items = "".join(
    "<item><title>%s</title><link>%s</link><guid>%s</guid><pubDate>%s</pubDate><description>%s</description></item>" % (
        esc(p["title"]), abs_url("writing/%s/" % p["slug"]), abs_url("writing/%s/" % p["slug"]),
        datetime.datetime.strptime(p["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000"), esc(p.get("excerpt")))
    for p in posts)
write("writing/feed.xml", '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>%s — Writing</title>'
      "<link>%s</link><description>%s</description>%s</channel></rss>\n" % (esc(S["name"]), abs_url("writing/"), esc(S.get("description")), feed_items))

# llms.txt: a plain-language summary for AI assistants (llmstxt.org), linked from robots.txt
llms = ["# %s (%s)" % (S["name"], S.get("name_zh", "")), "",
        "> " + (S.get("statement") or S.get("description", "")), "",
        "Areas: " + ", ".join(S.get("knows_about", [])), "",
        "## Main pages", "",
        "- [Works](%s): installations, performances, internet art and artistic research" % abs_url("works/"),
        "- [About / CV](%s): biography, teaching, exhibitions, talks, publications" % abs_url("about/"),
        "- [Writing](%s): texts and technical notes" % abs_url("writing/"),
        "- [Audio-Visual Performance](%s)" % abs_url("performance/"), "",
        "## Works", ""]
llms += ["- [%s](%s) (%s): %s" % (w["title"], abs_url("works/%s/" % w["slug"]), w.get("year"), w.get("type"))
         for w in works]
llms += ["", "## Contact", "", "- Email: " + S["email"]] + ["- %s: %s" % (l["label"], l["url"]) for l in S.get("links", [])]
llms_txt = "\n".join(llms) + "\n"
write("llms.txt", llms_txt)

# sitemap.xml and robots.txt only count at the domain root, so when the site lives
# in a subfolder they go to the repo root; the sitemap then also lists the other
# project sites on the domain (site.sitemap_extra).
dates = {"writing/%s/" % p["slug"]: p["date"] for p in posts}
locs = ["  <url><loc>%s</loc>%s</url>\n" % (esc(abs_url(p)), "<lastmod>%s</lastmod>" % dates[p] if p in dates else "") for p in pages]
locs += ["  <url><loc>%s</loc></url>\n" % esc(u) for u in S.get("sitemap_extra", [])]
top = REPO if PREFIX != "/" else ROOT
origin = "{0.scheme}://{0.netloc}/".format(urlparse(BASE))
open(os.path.join(top, "sitemap.xml"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % "".join(locs))
open(os.path.join(top, "llms.txt"), "w", encoding="utf-8").write(llms_txt)
open(os.path.join(top, "robots.txt"), "w").write(
    "User-agent: *\nAllow: /\nDisallow: %sadmin/\nDisallow: %spreview.html\n\nSitemap: %ssitemap.xml\n"
    "# Summary for AI assistants: %sllms.txt\n" % (PREFIX, PREFIX, origin, origin))

# When the site lives at the domain root, keep old Wix URLs working.
if PREFIX == "/":
    old = dict(OLD, **{"/post/" + s: "writing/%s/" % s for s in post_slugs})
    for o, new in old.items():
        if o.strip("/") and o.strip("/") + "/" != new:
            write(o.strip("/") + "/index.html", '<!doctype html><meta charset="utf-8"><title>Moved</title>'
                  '<link rel="canonical" href="%s"><meta name="robots" content="noindex">'
                  '<meta http-equiv="refresh" content="0; url=%s"><a href="%s">%s</a>\n' % ((esc(abs_url(new)),) * 4))

print("built %d pages -> %s" % (len(pages), BASE))
