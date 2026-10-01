# Log

Append-only. Newest entries at the bottom. Format: `## [YYYY-MM-DD] action | subject`.

## [2026-10-01] init | wiki created
- Schema written (CLAUDE.md), folders `raw/` and `pages/` set up.

## [2026-10-01] ingest | data/site.json (works, about, performances, site)
- 18 work pages in `pages/works/` (summary, facts, key ideas, related, sources).
- Lists generated from the CV: timeline, talks-and-writing, exhibitions-and-performances, teaching-education-awards.
- Written: overview, faq, 8 topic pages, 3 people pages, 6 institution pages.

## [2026-10-01] ingest | posts/*.md (titles and excerpts only)
- blog-archive page; blog links added to related works (Imaginary Landscape, Segmentary Moonlight, Light Segment, I kept repeating…, Take Off the Clothes, Message in a Bottle).
- Open: the full post texts (Mandarin) are not yet summarised page by page.

## [2026-10-01] add | site map and links
- pages/site-map.md: every page of the website (en/de/zh) and every external link, generated from data/site.json by scripts/wiki-sitemap.py (run on every site build and before every chat deploy). The chat recommends links only from the wiki.
