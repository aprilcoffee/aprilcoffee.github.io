#!/usr/bin/env python3
"""Generate the static site from data/site.json and posts/*.md.

Every page gets its own folder (works/<slug>/index.html, blog/<slug>/index.html, ...)
with full SEO tags, plus sitemap.xml and robots.txt. English is at the root, German
under de/ and Traditional Chinese under zh/ (the blog posts are not translated).

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
SECTIONS = ["works", "performance", "about", "blog", "friends"]

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
       "/blog": "blog/", "/works": "works/", "/blog/categories/works": "blog/",
       "/blog/categories/technique": "blog/"}
for w in D["works"]:
    for a in w.get("aliases", []):  # hidden works have no page: send their old URLs to the list
        OLD[a.rstrip("/")] = "works/" if w.get("hidden") else "works/%s/" % w["slug"]


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
            return url("blog/%s/" % m.group(1))
        if path in OLD:
            return url(LP[CUR[0]] + OLD[path])
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


# real thumbnails recorded in site.json (works: video_thumb, performances: thumb), by video id
VIDEO_THUMBS = dict(S.get("video_thumbs", {}))  # extra ones, e.g. for videos in blog posts
for _it in D["works"] + D.get("performances", []):
    _v = video_id(_it.get("video"))
    _t = _it.get("video_thumb") or _it.get("thumb")
    if _v and _t:
        VIDEO_THUMBS.setdefault(_v[1], _t)


def embed(u, thumb="", title=""):
    v = video_id(u)
    if not v:
        return ""
    kind, vid = v
    if kind == "file":
        return '<div class="embed"><video controls preload="none" playsinline src="%s"></video></div>' % esc(asset(vid))
    src = ("https://player.vimeo.com/video/%s?dnt=1&autoplay=1" % vid if kind == "vimeo"
           else "https://www.youtube-nocookie.com/embed/%s?autoplay=1" % vid)
    thumb = thumb or VIDEO_THUMBS.get(vid)
    if not thumb:
        thumb = ("https://vumbnail.com/%s.jpg" % vid if kind == "vimeo"
                 else "https://i.ytimg.com/vi/%s/hqdefault.jpg" % vid)
    # A thumbnail that swaps itself for the player on click keeps pages light.
    return ('<button class="embed lite" type="button" data-src="%s" aria-label="Play video%s">'
            '%s<span class="play" aria-hidden="true"></span></button>') % (
        esc(src), esc(": " + title) if title else "", img(thumb, 1280, title))


def clip(c, title=""):
    """A video file kept in this repository (images/video/). Silent loops play by themselves,
    muted; anything with sound waits for the play button."""
    attrs = ('autoplay muted loop playsinline preload="auto"' if c.get("loop")
             else 'controls playsinline preload="none"')
    return '<figure class="clip"><video %s src="%s"%s aria-label="%s"></video></figure>' % (
        attrs, esc(asset(c["src"])), ' poster="%s"' % esc(asset(c["poster"])) if c.get("poster") else "", esc(title))


def cover_of(w):
    if w.get("cover"):
        return w["cover"]
    if w.get("images"):
        return w["images"][0]
    if w.get("video_thumb"):
        return w["video_thumb"]
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


# ---------- languages ----------
# English at the site root, German under de/, Traditional Chinese under zh/.
# The blog posts themselves are not translated: they live once under blog/<slug>/.
LANGS = ["en", "de", "zh"]
LP = {"en": "", "de": "de/", "zh": "zh/"}
HREFLANG = {"en": "en", "de": "de", "zh": "zh-Hant"}
LOCALE = {"en": "en_US", "de": "de_DE", "zh": "zh_TW"}
LANG_NAME = {"en": "EN", "de": "DE", "zh": "中文"}

UI = {
    "en": {
        "nav": {"works": "Works", "performance": "Performance", "about": "About", "blog": "Blog (archived)", "friends": "Friends"},
        "menu": "Menu", "language": "Language", "privacy": "Privacy",
        "selected": "Selected works", "all_works": "All works (%d) →",
        "works_lead": "Installations, performances, internet art and artistic research, %s–%s.",
        "works_desc": "Selected works by %s, %s–%s: installations, performances, internet art and artistic research on AI.",
        "Year": "Year", "Type": "Type", "Materials": "Materials", "With": "With", "Link": "Link",
        "work_desc": "%s (%s), %s by %s.", "work": "work",
        "perf_title": "Audio-Visual Performance",
        "perf_lead": "Live audio-visual sets and performance records, 2016–2024. Each video opens on %s in a new tab.",
        "perf_desc": "Audio-visual performance records of %s.", "watch": "Watch on %s ↗",
        "about": "About",
        "blog_title": "Blog Archive",
        "blog_lead": "Notes on works, and technical write-ups on Raspberry Pi, Processing and Python. The posts are written in Mandarin.",
        "blog_desc": "Blog archive of %s: notes on artworks and technical write-ups on Raspberry Pi, Processing and Python.",
        "friends_lead": "Artists and collaborators.", "friends_desc": "Friends and fellow artists of %s.",
        "Date": "Date", "Category": "Category",
        "ask": "Ask about the work", "ask_ph": "Ask a question about Liu’s work…", "ask_btn": "Ask",
        "ask_note": "Answers are written by an AI (ChatGPT) from notes on this website and can be wrong. Questions are sent to Cloudflare and OpenAI and are not stored. %s",
        "ask_more": "More in the privacy policy.",
        "ask_q": ["What is Heat as Image about?", "Which works deal with AI?", "Where does Liu teach?"],
        "ask_err": "Sorry, that didn’t work. Please try again in a moment, or write to %s.",
        "ask_busy": "Too many questions right now. Please wait a minute.",
        "ask_refusal": "I can’t answer that here. Questions about Liu’s work are welcome.",
    },
    "de": {
        "nav": {"works": "Arbeiten", "performance": "Performance", "about": "Über mich", "blog": "Blog (archiviert)", "friends": "Freunde"},
        "menu": "Menü", "language": "Sprache", "privacy": "Datenschutz",
        "selected": "Ausgewählte Arbeiten", "all_works": "Alle Arbeiten (%d) →",
        "works_lead": "Installationen, Performances, Netzkunst und künstlerische Forschung, %s–%s.",
        "works_desc": "Ausgewählte Arbeiten von %s, %s–%s: Installationen, Performances, Netzkunst und künstlerische Forschung zu KI.",
        "Year": "Jahr", "Type": "Art", "Materials": "Material", "With": "Mit", "Link": "Link",
        "work_desc": "%s (%s), %s von %s.", "work": "Arbeit",
        "perf_title": "Audiovisuelle Performance",
        "perf_lead": "Audiovisuelle Live-Sets und Performance-Dokumentationen, 2016–2024. Jedes Video öffnet sich auf %s in einem neuen Tab.",
        "perf_desc": "Audiovisuelle Performance-Dokumentationen von %s.", "watch": "Auf %s ansehen ↗",
        "about": "Über mich",
        "blog_title": "Blog-Archiv",
        "blog_lead": "Notizen zu Arbeiten und technische Anleitungen zu Raspberry Pi, Processing und Python. Die Beiträge sind auf Chinesisch (Mandarin) verfasst.",
        "blog_desc": "Blog-Archiv von %s: Notizen zu Arbeiten und technische Anleitungen zu Raspberry Pi, Processing und Python.",
        "friends_lead": "Künstler*innen und Kooperationspartner*innen.", "friends_desc": "Freund*innen und befreundete Künstler*innen von %s.",
        "Date": "Datum", "Category": "Kategorie",
        "ask": "Fragen zur Arbeit", "ask_ph": "Eine Frage zu Lius Arbeit …", "ask_btn": "Fragen",
        "ask_note": "Die Antworten schreibt eine KI (ChatGPT) auf Grundlage der Texte dieser Website; sie können Fehler enthalten. Fragen werden an Cloudflare und OpenAI übermittelt und nicht gespeichert. %s",
        "ask_more": "Mehr in der Datenschutzerklärung.",
        "ask_q": ["Worum geht es in Heat as Image?", "Welche Arbeiten beschäftigen sich mit KI?", "Wo unterrichtet Liu?"],
        "ask_err": "Das hat leider nicht geklappt. Bitte gleich noch einmal versuchen oder an %s schreiben.",
        "ask_busy": "Gerade kommen zu viele Fragen. Bitte eine Minute warten.",
        "ask_refusal": "Darauf kann ich hier nicht antworten. Fragen zu Lius Arbeit sind willkommen.",
    },
    "zh": {
        "nav": {"works": "作品", "performance": "表演", "about": "關於", "blog": "部落格（封存）", "friends": "朋友"},
        "menu": "選單", "language": "語言", "privacy": "隱私權",
        "selected": "精選作品", "all_works": "全部作品（%d）→",
        "works_lead": "裝置、表演、網路藝術與藝術研究，%s–%s。",
        "works_desc": "%s的精選作品，%s–%s：裝置、表演、網路藝術，以及關於人工智慧的藝術研究。",
        "Year": "年份", "Type": "類型", "Materials": "媒材", "With": "合作", "Link": "連結",
        "work_desc": "%s（%s），%s，%s。", "work": "作品",
        "perf_title": "影音表演",
        "perf_lead": "現場影音演出與表演紀錄，2016–2024。點擊後會在新分頁開啟 %s 影片。",
        "perf_desc": "%s的影音表演紀錄。", "watch": "在 %s 觀看 ↗",
        "about": "關於",
        "blog_title": "部落格 Blog Archive",
        "blog_lead": "作品筆記，以及 Raspberry Pi、Processing 與 Python 的技術文章。",
        "blog_desc": "%s的部落格文章彙整：作品筆記，以及 Raspberry Pi、Processing 與 Python 技術文章。",
        "friends_lead": "藝術家與合作夥伴。", "friends_desc": "%s的朋友與藝術家夥伴。",
        "Date": "日期", "Category": "分類",
        "ask": "關於作品，問問看", "ask_ph": "想知道劉庭均作品的什麼？", "ask_btn": "提問",
        "ask_note": "回答由 AI（ChatGPT）根據本網站的資料生成，可能有誤。問題會傳送至 Cloudflare 與 OpenAI，不會被保存。%s",
        "ask_more": "詳見隱私權說明。",
        "ask_q": ["《Heat as Image》在談什麼？", "哪些作品與 AI 有關？", "劉庭均在哪裡教書？"],
        "ask_err": "抱歉，暫時無法回答。請稍後再試，或寫信至 %s。",
        "ask_busy": "目前提問太多，請稍候一分鐘。",
        "ask_refusal": "這個問題我無法在這裡回答，歡迎詢問與作品相關的問題。",
    },
}
CUR = ["en"]  # language of the page being built; fix_link keeps visitors in it


def tr(obj, key, lang):
    """obj[key + '_de'] / obj[key + '_zh'] with the English field as fallback."""
    return (obj.get("%s_%s" % (key, lang)) if lang != "en" else None) or obj.get(key)


def lname(lang):
    return S.get("name_zh") if lang == "zh" and S.get("name_zh") else S["name"]


# ---------- layout ----------
def idx(n):
    return ""  # numbering removed from the design; kept as a hook


def layout(path, title, desc, body, image=None, og_type="website", lang="en", ld=None, full=False, section="",
           alts=None, content_lang=None):
    """lang: language of the interface; content_lang: of the page text (a Chinese post in the English frame);
    alts: {lang: path} of the same page in the other languages (hreflang + language switch)."""
    u = UI[lang]
    page_title = "%s — %s" % (title, S["name"]) if title else "%s %s" % (S["name"], S.get("name_zh", ""))
    canonical = abs_url(path)
    image = asset_abs(image or S.get("og_image") or "")
    nav = "".join('%s<a href="%s"%s><span>%s</span></a>' % (
        '<span class="gap" aria-hidden="true"></span>' if s == "blog" else "",  # Blog and Friends sit apart
        url(LP[lang] + s + "/"), ' class="on" aria-current="page"' if s == section else "", u["nav"][s])
        for s in SECTIONS)
    switch = "".join('<a href="%s" hreflang="%s" lang="%s"%s>%s</a>' % (
        url(alts[l] if alts else LP[l] + (section + "/" if section else "")), HREFLANG[l], HREFLANG[l],
        ' class="on" aria-current="true"' if l == lang else "", LANG_NAME[l]) for l in LANGS)
    hreflang = "".join('<link rel="alternate" hreflang="%s" href="%s">\n' % (HREFLANG[l], esc(abs_url(p)))
                       for l, p in (alts or {}).items())
    if alts:
        hreflang += '<link rel="alternate" hreflang="x-default" href="%s">\n' % esc(abs_url(alts["en"]))
    links = "".join(a(l["url"], esc(l["label"])) for l in S.get("links", []))
    ld_tag = ('<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False)) if ld else ""
    ga = ('<script async src="%s" data-ga="%s" data-banner></script>' % (url("assets/analytics.js"), esc(S["ga_id"]))
          if S.get("ga_id") else "")
    cl = content_lang or HREFLANG[lang]
    return """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="author" content="{name}">
<link rel="canonical" href="{c}">
{hreflang}<meta property="og:site_name" content="{name}">
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
<link rel="alternate" type="application/rss+xml" title="{name} — Blog" href="{feed}">
{ga}
<link rel="stylesheet" href="{css}">
{ld}
</head>
<body>
<aside class="side" id="side"{side_lang}>
  <div class="side-head">
    <a class="brand" href="{home}"><span class="brand-en">{name}</span><span class="brand-zh" lang="zh-Hant">{zh}</span></a>
    <button class="menu-btn" id="menuBtn" aria-label="{menu}" aria-expanded="false">{menu}</button>
  </div>
  <nav class="nav" id="nav" aria-label="Main">{nav}</nav>
  <nav class="langs" aria-label="{language}">{switch}</nav>
  <div class="side-foot">
    <div class="signal" data-effect="signal" aria-hidden="true"></div>
    <div><a href="mailto:{email}">{email}</a></div>
    <div class="links">{links}</div>
    <div>© {year} {name}</div>
    <div class="legal"><a href="{imp}" lang="de">Impressum</a><a href="{dsg}">{privacy}</a></div>
  </div>
</aside>
<main class="main{full}" id="main">
{body}
</main>
<script src="{js}" data-p5="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.4/p5.min.js" data-effects="{fx}" defer></script>
</body>
</html>
""".format(lang=cl, side_lang=' lang="%s"' % HREFLANG[lang] if cl != HREFLANG[lang] else "",
           locale=LOCALE[lang] if not content_lang else ("zh_TW" if content_lang.startswith("zh") else LOCALE[lang]),
           t=esc(page_title), d=esc(desc or tr(S, "description", lang)), name=esc(S["name"]), zh=esc(S.get("name_zh", "")),
           c=esc(canonical), hreflang=hreflang, ogt=og_type, img=esc(image), icon=url("assets/favicon.svg"),
           css=url("assets/style.css"), js=url("assets/site.js"), fx=url("assets/effects.js"), feed=url("blog/feed.xml"),
           ga=ga, ld=ld_tag, home=url(LP[lang]), imp=url("impressum/"), dsg=url("datenschutz/"), nav=nav, switch=switch,
           menu=u["menu"], language=u["language"], privacy=u["privacy"], email=esc(S["email"]), links=links,
           year=datetime.date.today().year, full=" full" if full else "", body=body)


def person(lang):
    p = {"@context": "https://schema.org", "@type": "Person", "name": S["name"],
         "alternateName": [S.get("name_zh", ""), "Liu Ting-Chun", "劉庭均"], "url": abs_url(LP[lang]),
         "email": "mailto:" + S["email"], "jobTitle": tr(S, "job_title", lang) or "Artist",
         "description": tr(S, "statement", lang) or tr(S, "description", lang),
         "knowsAbout": S.get("knows_about", []),
         "hasOccupation": [{"@type": "Occupation", "name": o} for o in S.get("occupations", [])],
         "sameAs": [l["url"] for l in S.get("links", [])]}
    p.update(S.get("person_extra", {}))
    return p


def pager(items, i, base, label, noun):
    prev = items[i - 1] if i > 0 else None
    nxt = items[i + 1] if i < len(items) - 1 else None
    one = lambda it, n, arrow: ('<a href="%s"><span class="mono">%s</span><span class="t">%s</span></a>' % (
        url(base % it["slug"]), arrow, esc(it[label])))
    return '<nav class="pager" aria-label="%s">%s%s</nav>' % (
        noun, one(prev, i, "←") if prev else "<span></span>", one(nxt, i + 2, "→") if nxt else "<span></span>")


def page_head(title, lead=""):
    return '<header class="page-head"><h1 class="page-title">%s</h1>%s</header>' % (
        esc(title), '<p class="lead">%s</p>' % esc(lead) if lead else "")


def work_card(n, w, lang):
    c = cover_of(w)
    return ('<a class="card" href="%s"><div class="thumb">%s</div><div class="cap">%s<span class="t">%s%s</span>'
            '<span class="mono">%s</span></div></a>') % (
        url(LP[lang] + "works/%s/" % w["slug"]), img(c, 900, w["title"]) if c else '<span class="ph">%s</span>' % esc(w["title"]),
        idx(n), esc(w["title"]), '<span class="zh" lang="zh-Hant">%s</span>' % esc(w["title_zh"]) if w.get("title_zh") else "",
        esc(w.get("year")))


def meta(rows):
    return '<dl class="meta">%s</dl>' % "".join("<dt>%s</dt><dd>%s</dd>" % r for r in rows if r[1])


# ---------- pages ----------
pages = {}  # path -> html
noindex = set()  # redirect stubs: kept out of the sitemap
for l in LANGS:
    TITLES.update({url(LP[l] + "works/%s/" % w["slug"]): w["title"] for w in works})
    TITLES.update({url(LP[l] + s + "/"): UI[l]["nav"][s] for s in SECTIONS})
TITLES.update({url("blog/%s/" % p["slug"]): p["title"] for p in posts})


def page(path, *args, **kw):
    pages[path] = layout(path, *args, **kw)


def each(path):
    """The same page in every language."""
    return {l: LP[l] + path for l in LANGS}


def ask_box(lang):
    """The chat box on the homepage; only rendered once site.chat_endpoint is set."""
    if not S.get("chat_endpoint"):
        return ""
    u = UI[lang]
    msgs = {k: u[k] % (S["email"],) if k == "ask_err" else u[k] for k in ("ask_err", "ask_busy", "ask_refusal")}
    return ('<section class="ask" id="ask" aria-labelledby="ask-h" data-endpoint="%s" data-msgs="%s">'
            '<h2 id="ask-h" class="ask-h">%s</h2>'
            '<div class="ask-log" aria-live="polite"></div>'
            '<form class="ask-form"><input name="q" type="text" maxlength="600" autocomplete="off" required '
            'placeholder="%s" aria-label="%s"><button type="submit">%s</button></form>'
            '<div class="ask-chips">%s</div>'
            '<p class="ask-note">%s</p>'
            '<script src="%s" defer></script></section>') % (
        esc(S["chat_endpoint"]), esc(json.dumps(msgs, ensure_ascii=False)), esc(u["ask"]),
        esc(u["ask_ph"]), esc(u["ask_ph"]), esc(u["ask_btn"]),
        "".join('<button type="button">%s</button>' % esc(q) for q in u["ask_q"]),
        esc(u["ask_note"]) % ('<a href="%s">%s</a>' % (url("datenschutz/#chat"), esc(u["ask_more"]))),
        url("assets/chat.js"))


years = sorted(w["year"][:4] for w in works if w.get("year"))
y0, y1 = (years[0], years[-1]) if years else ("", "")
platforms = sorted({"Vimeo" if "vimeo" in (p.get("video") or "") else "YouTube"
                    for p in D.get("performances", []) if not p.get("hidden")})

for L in LANGS:
    CUR[0] = L
    u, P = UI[L], LP[L]

    # home: generative field + statement, then a few recent works
    page(P, "", tr(S, "description", L),
         '<section class="home-hero"><div class="field" data-effect="field" data-words="%s" aria-hidden="true"></div>'
         '<h1 class="sr-only">%s %s</h1><p class="home-statement"><span>%s</span></p></section>'
         '%s<section class="home-selected" aria-label="%s"><div class="grid">%s</div>'
         '<a class="more" href="%s">%s</a></section>' % (
             esc(json.dumps(S.get("hidden_words", []), ensure_ascii=False)),
             esc(S["name"]), esc(S.get("name_zh", "")), esc(tr(S, "statement", L) or tr(S, "description", L)),
             ask_box(L), esc(u["selected"]),
             "".join(work_card(i + 1, w, L) for i, w in enumerate(works[:3])), url(P + "works/"), esc(u["all_works"] % len(works))),
         ld=person(L), full=True, lang=L, alts=each(""))

    page(P + "works/", u["nav"]["works"], u["works_desc"] % (lname(L), y0, y1),
         page_head(u["nav"]["works"], u["works_lead"] % (y0, y1)) +
         '<div class="grid">%s</div>' % "".join(work_card(i + 1, w, L) for i, w in enumerate(works)),
         section="works", lang=L, alts=each("works/"))

    for i, w in enumerate(works):
        rows = [(u["Year"], esc(w.get("year"))), (u["Type"], esc(tr(w, "type", L))),
                (u["Materials"], esc(tr(w, "materials", L))), (u["With"], esc(w.get("collaborators")))]
        rows += [(u["Link"], a(l["url"], esc(l.get("label") or l["url"]))) for l in w.get("links", []) if l.get("url")]
        ims = w.get("images", [])
        plates = embed(w.get("video"), w.get("video_thumb", ""), w["title"]) + "".join(clip(c, w["title"]) for c in w.get("clips", []))
        moving = w.get("video") or w.get("clips")
        # full-width lead (video, clips or the first photo), then the rest in two masonry
        # columns so photos of different proportions leave no gaps
        figs = ["<figure>%s</figure>" % img(im, 1600 if k == 0 else 1000, "%s — %d" % (w["title"], k + 1))
                for k, im in enumerate(ims)]
        if not moving and figs:
            plates += figs.pop(0).replace("<figure>", '<figure class="hero">', 1)
        if len(figs) == 1:
            plates += figs[0].replace("<figure>", '<figure class="hero">', 1)
        elif figs:
            plates += '<div class="cols">%s</div>' % "".join(figs)
        text = tr(w, "text", L)
        # a translation may be missing: then the English text is shown, marked as English
        tl = HREFLANG[L] if L == "en" or w.get("text_" + L) else "en"
        body = ('<article class="work"><aside class="work-info">%s<h1>%s</h1>%s%s<div class="prose"%s>%s</div>%s</aside>'
                '<div class="plates">%s</div>%s</article>') % (
            idx(i + 1), esc(w["title"]), '<p class="zh" lang="zh-Hant">%s</p>' % esc(w["title_zh"]) if w.get("title_zh") else "",
            meta(rows), ' lang="%s"' % tl if tl != HREFLANG[L] else "", prose(text),
            '<p class="credits">%s</p>' % esc(w["credits"]) if w.get("credits") else "",
            plates, pager(works, i, P + "works/%s/", "title", u["nav"]["works"]))
        desc = summary(text) or u["work_desc"] % (w["title"], w.get("year"), tr(w, "type", L) or u["work"], lname(L))
        ld = {"@context": "https://schema.org", "@type": "CreativeWork", "name": w["title"],
              "alternateName": w.get("title_zh") or None, "dateCreated": w.get("year", "")[:4],
              "genre": tr(w, "type", L) or None, "url": abs_url(P + "works/%s/" % w["slug"]), "inLanguage": HREFLANG[L],
              "image": asset_abs(cover_of(w)) if cover_of(w) else None, "description": desc,
              "creator": {"@type": "Person", "name": S["name"], "url": abs_url(P)}}
        page(P + "works/%s/" % w["slug"], w["title"] + (" " + w["title_zh"] if w.get("title_zh") else ""), desc, body,
             image=cover_of(w), og_type="article", ld={k: v for k, v in ld.items() if v}, section="works", lang=L,
             alts=each("works/%s/" % w["slug"]))

    # performance: each record opens on Vimeo / YouTube in a new tab (no player on this page)
    def perf_card(n, p):
        v = video_id(p.get("video"))
        where = "YouTube" if v and v[0] == "youtube" else "Vimeo"
        thumb = p.get("thumb") or cover_of({"video": p.get("video")})
        return ('<a class="perf-card" href="%s" target="_blank" rel="noopener"><div class="thumb">%s'
                '<span class="watch">%s</span></div><div class="cap">%s<h2>%s</h2><p>%s</p></div></a>') % (
            esc(p["video"]), img(thumb, 1100, p["title"]) if thumb else "", esc(u["watch"] % where), idx(n),
            esc(p["title"]), esc(tr(p, "note", L)))

    perfs = [p for p in D.get("performances", []) if not p.get("hidden") and p.get("video")]
    page(P + "performance/", u["perf_title"], u["perf_desc"] % lname(L),
         page_head(u["perf_title"], u["perf_lead"] % " / ".join(platforms)) +
         '<div class="perf">%s</div>' % "".join(perf_card(n + 1, p) for n, p in enumerate(perfs)),
         image=(perfs or [{}])[0].get("thumb"), section="performance", lang=L, alts=each("performance/"))

    cv = ""
    for sec in D["about"]["sections"]:
        rows = ""
        for it in sec["items"]:
            text = tr(it, "text", L)
            same = L != "en" and not it.get("text_" + L)  # not translated: mark the row as English
            rows += '<div class="cv-row"%s><span class="mono">%s</span><span>%s</span></div>' % (
                ' lang="en"' if same else "", esc(it.get("year")), a(it["url"], esc(text)) if it.get("url") else esc(text))
        cv += '<section class="cv-sec"><h2>%s</h2><div>%s</div></section>' % (esc(tr(sec, "title", L)), rows)
    bio = tr(D["about"], "bio", L)
    page(P + "about/", u["about"], bio,
         '<div class="about-top"><h1 class="page-title">%s</h1><div><p class="bio">%s</p>'
         '<p class="contact"><a href="mailto:%s">%s</a></p></div></div>%s' % (
             esc(u["about"]), esc(bio), esc(S["email"]), esc(S["email"]), cv),
         ld=dict(person(L), description=bio), og_type="profile", section="about", lang=L, alts=each("about/"))

    groups, order = {}, []
    for p in posts:
        y = p["date"][:4]
        if y not in groups:
            groups[y] = []
            order.append(y)
        groups[y].append('<li><a href="%s" lang="%s"><span class="t">%s</span><span class="cat mono">%s</span>'
                         '<span class="ex">%s</span></a></li>' % (
                             url("blog/%s/" % p["slug"]), p.get("lang", "zh-Hant"), esc(p["title"]), esc(p.get("category")),
                             esc(p.get("excerpt"))))
    page(P + "blog/", u["blog_title"], u["blog_desc"] % lname(L),
         page_head(u["blog_title"], u["blog_lead"]) +
         "".join('<section class="year-group"><span class="mono">%s</span><ul>%s</ul></section>' % (y, "".join(groups[y]))
                 for y in order),
         section="blog", lang=L, alts=each("blog/"))

    def friend(f):
        thumb = img(f["image"], 600, f["name"]) if f.get("image") else '<span class="ph">%s</span>' % esc(f["name"])
        if not f.get("url"):  # site no longer online: keep the name, drop the link
            return '<div class="card"><div class="thumb">%s</div><div class="cap"><span class="t">%s</span></div></div>' % (
                thumb, esc(f["name"]))
        return ('<a class="card" href="%s" target="_blank" rel="noopener"><div class="thumb">%s</div>'
                '<div class="cap"><span class="t">%s</span><span class="mono">↗</span></div></a>') % (
            esc(f["url"]), thumb, esc(f["name"]))

    page(P + "friends/", u["nav"]["friends"], u["friends_desc"] % lname(L),
         page_head(u["nav"]["friends"], u["friends_lead"]) +
         '<div class="grid friends">%s</div>' % "".join(friend(f) for f in D.get("friends", [])),
         section="friends", lang=L, alts=each("friends/"))

# blog posts: one version each (not translated), in the English frame
CUR[0] = "en"
for i, p in enumerate(posts):
    src = read_post(p["slug"])
    desc = p.get("excerpt") or summary(src)
    body = ('<article class="post"><aside class="post-info" lang="en"><h1 lang="%s">%s</h1>%s<a class="back" href="%s">← Blog Archive</a></aside>'
            '<div class="prose post-body">%s</div>%s</article>') % (
        p.get("lang", "zh-Hant"), esc(p["title"]), meta([("Date", esc(p["date"])), ("Category", esc(p.get("category")))]),
        url("blog/"), post_html(src), pager(posts, i, "blog/%s/", "title", "Posts"))
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "datePublished": p["date"],
          "inLanguage": p.get("lang", "zh-Hant"), "url": abs_url("blog/%s/" % p["slug"]),
          "image": asset_abs(p.get("cover") or S.get("og_image")), "description": desc,
          "author": {"@type": "Person", "name": S["name"], "url": abs_url()},
          "mainEntityOfPage": abs_url("blog/%s/" % p["slug"])}
    page("blog/%s/" % p["slug"], p["title"], desc, body, image=p.get("cover"), og_type="article",
         content_lang=p.get("lang", "zh-Hant"), ld=ld, section="blog")


def redirect(old, new):
    """A tiny page that forwards an old URL (e.g. writing/ -> blog/)."""
    pages[old] = ('<!doctype html><html lang="en"><meta charset="utf-8"><title>Moved</title>'
                  '<link rel="canonical" href="%s"><meta name="robots" content="noindex">'
                  '<meta http-equiv="refresh" content="0; url=%s"><a href="%s">%s</a></html>\n' % (
                      esc(abs_url(new)), esc(url(new)), esc(url(new)), esc(abs_url(new))))
    noindex.add(old)


redirect("writing/", "blog/")
for p in posts:
    redirect("writing/%s/" % p["slug"], "blog/%s/" % p["slug"])

addr = S.get("address") or []
addr_html = "<br>".join(esc(x) for x in addr) if addr else \
    '<span class="todo">[Postanschrift fehlt — in site.json → site.address eintragen]</span>'
page("impressum/", "Impressum", "Impressum / legal notice of %s." % S["name"], lang="de", body="""
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

CHAT_PRIVACY = """<h2 id="chat">7. Fragen zur Arbeit (KI-Chat)</h2>
<p>Auf der Startseite können Sie Fragen zu den Arbeiten stellen. Erst wenn Sie eine Frage absenden, wird sie zusammen mit den vorherigen Fragen und Antworten dieses Gesprächs an einen Cloudflare Worker (Cloudflare, Inc., 101 Townsend St., San Francisco, CA 94107, USA) und von dort an die API von OpenAI (OpenAI Ireland Ltd., 1st Floor, The Liffey Trust Centre, 117–126 Sheriff Street Upper, Dublin 1, Irland; Konzernmutter OpenAI, L.L.C., USA) übertragen, die die Antwort erzeugt. Cloudflare verarbeitet dabei Ihre IP-Adresse, um Missbrauch zu begrenzen (höchstens einige Fragen pro Minute). Die Inhalte werden auf dieser Website nicht gespeichert und nicht für Werbung verwendet; OpenAI verwendet Daten aus der API nicht zum Training seiner Modelle und speichert sie nur kurzzeitig (in der Regel bis zu 30 Tage) zur Missbrauchserkennung. Bitte geben Sie keine personenbezogenen Daten in das Feld ein. Rechtsgrundlage ist Art. 6 Abs. 1 lit. a und f DSGVO (Ihre Anfrage; berechtigtes Interesse an einem Auskunftsangebot über die Arbeiten). Die Übermittlung in die USA erfolgt auf Grundlage der EU-Standardvertragsklauseln bzw. des EU-US Data Privacy Framework. Die Antworten werden automatisch erzeugt und können Fehler enthalten.</p>
"""

page("datenschutz/", "Datenschutz", "Privacy policy (Datenschutzerklärung) of %s." % S["name"], lang="de", body="""
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
{chat}<h2>{n}. Ihre Rechte</h2>
<p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit, Widerspruch sowie auf Widerruf erteilter Einwilligungen. Außerdem können Sie sich bei einer Datenschutz-Aufsichtsbehörde beschweren.</p>
<p class="en">In short: analytics only runs after you click OK; videos only load when you press play;{chat_en} nothing else tracks you.</p>
</div>""".format(name=esc(S["name"]), addr=addr_html, email=esc(S["email"]), n=8 if S.get("chat_endpoint") else 7,
               chat_en=" questions in the “Ask” box go to Cloudflare and OpenAI and are not stored;" if S.get("chat_endpoint") else "",
               chat=CHAT_PRIVACY if S.get("chat_endpoint") else ""))


# ---------- write ----------
def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)


for s in SECTIONS + ["impressum", "datenschutz", "writing"] + [LP[l].strip("/") for l in LANGS if LP[l]]:  # start clean so removed works/posts disappear
    shutil.rmtree(os.path.join(ROOT, s), ignore_errors=True)
for path, text in pages.items():
    write(path + "index.html", text)

# RSS feed for the blog
feed_items = "".join(
    "<item><title>%s</title><link>%s</link><guid>%s</guid><pubDate>%s</pubDate><description>%s</description></item>" % (
        esc(p["title"]), abs_url("blog/%s/" % p["slug"]), abs_url("blog/%s/" % p["slug"]),
        datetime.datetime.strptime(p["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000"), esc(p.get("excerpt")))
    for p in posts)
feed = ('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>%s — Blog</title>'
        "<link>%s</link><description>%s</description>%s</channel></rss>\n" % (esc(S["name"]), abs_url("blog/"), esc(S.get("description")), feed_items))
write("blog/feed.xml", feed)
write("writing/feed.xml", feed)  # old feed address, for existing subscribers

# llms.txt: a plain-language summary for AI assistants (llmstxt.org), linked from robots.txt
llms = ["# %s (%s)" % (S["name"], S.get("name_zh", "")), "",
        "> " + (S.get("statement") or S.get("description", "")), "",
        "Areas: " + ", ".join(S.get("knows_about", [])), "",
        "## Main pages", "",
        "- [Works](%s): installations, performances, internet art and artistic research" % abs_url("works/"),
        "- [About / CV](%s): biography, teaching, exhibitions, talks, publications" % abs_url("about/"),
        "- [Blog Archive](%s): texts and technical notes (in Mandarin)" % abs_url("blog/"),
        "- [Audio-Visual Performance](%s)" % abs_url("performance/"), "",
        "The site is also available in German (%s) and Traditional Chinese (%s)." % (abs_url("de/"), abs_url("zh/")), "",
        "## Works", ""]
llms += ["- [%s](%s) (%s): %s" % (w["title"], abs_url("works/%s/" % w["slug"]), w.get("year"), w.get("type"))
         for w in works]
llms += ["", "## Contact", "", "- Email: " + S["email"]] + ["- %s: %s" % (l["label"], l["url"]) for l in S.get("links", [])]
llms_txt = "\n".join(llms) + "\n"
write("llms.txt", llms_txt)

# sitemap.xml and robots.txt only count at the domain root, so when the site lives
# in a subfolder they go to the repo root; the sitemap then also lists the other
# project sites on the domain (site.sitemap_extra).
dates = {"blog/%s/" % p["slug"]: p["date"] for p in posts}
locs = ["  <url><loc>%s</loc>%s</url>\n" % (esc(abs_url(p)), "<lastmod>%s</lastmod>" % dates[p] if p in dates else "")
        for p in pages if p not in noindex]
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
    old = dict(OLD, **{"/post/" + s: "blog/%s/" % s for s in post_slugs})
    for o, new in old.items():
        if o.strip("/") and o.strip("/") + "/" != new:
            write(o.strip("/") + "/index.html", '<!doctype html><meta charset="utf-8"><title>Moved</title>'
                  '<link rel="canonical" href="%s"><meta name="robots" content="noindex">'
                  '<meta http-equiv="refresh" content="0; url=%s"><a href="%s">%s</a>\n' % ((esc(abs_url(new)),) * 4))

print("built %d pages -> %s" % (len(pages), BASE))
