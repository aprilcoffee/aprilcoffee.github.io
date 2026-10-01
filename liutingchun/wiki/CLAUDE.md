# LLM Wiki — Ting-Chun Liu

This folder is a knowledge base about the artist Ting-Chun Liu (劉庭均), built on the
"LLM Wiki" pattern (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):
instead of searching raw material on every question, a language model writes and keeps up
a set of interlinked Markdown pages. Later, the chat box on the website answers visitors'
questions from these pages.

This file is the **schema**: read it before touching anything in `wiki/`.

## Layers

| Layer | Where | Who changes it |
|---|---|---|
| Raw sources | `../data/site.json`, `../posts/*.md`, `raw/` (anything the artist drops in) | the artist; the LLM only reads |
| Wiki | `pages/`, `index.md`, `log.md` | the LLM |
| Schema | this file | the artist and the LLM together |

## Ground rules

1. **Only public, sourced facts.** Every statement must be traceable to a raw source or a
   public page. If something is not in the sources, write "unknown" — never guess dates,
   venues, awards, collaborators or quotes.
2. **Cite.** Each page ends with `## Sources`; each source is a repo path or a public URL.
3. **Nothing private.** No home address, phone number, private email threads, health,
   family or finances, even if a raw source contains them. Contact = the public email
   tingchun.liu.tw@gmail.com only. Material in `raw/private/` is never used.
4. **The artist's own wording wins.** When the site text and a later source disagree, keep
   both, flag it under `## Open questions`, and add a line to `log.md`.
5. **English** is the wiki language; keep original titles (German, Chinese) next to the
   English ones. The chat answers in the visitor's language.
6. **Pronouns:** the artist's own bio uses "he". Prefer the name ("Liu") in running text.

## Page format

```markdown
---
title: <page title>
type: overview | work | topic | person | institution | list | faq
tags: [short, lowercase, tags]
sources:
  - <repo path or URL>
updated: YYYY-MM-DD
---
# <title>

<one-paragraph summary a visitor could read on its own>

... body ...

## Related
- [Other page](relative/path.md)

## Sources
- <same list, human-readable>
```

- Links are plain relative Markdown links (they work on GitHub, in Obsidian and in the
  chat's citations). One page per work, topic, person and institution.
- File names: lowercase, hyphenated, ASCII (work pages use the website slug).

## Workflows

**Ingest** (new material in `raw/` or a change in `site.json`):
1. Read the new source.
2. Update or create every affected page (work, topics, people, institutions, timeline).
3. Update `index.md` (one line per page) and append to `log.md`:
   `## [YYYY-MM-DD] ingest | <source>` plus a bullet list of pages touched.

**Query** (a visitor's question, or the artist's):
1. Read `index.md` first, then the relevant pages.
2. Answer only from the wiki, link the pages used, say so when the wiki has no answer.
3. A good new answer can be filed back as a page (or into `faq.md`).

**Lint** (from time to time, and before each release of the chat):
1. `python3 liutingchun/scripts/wiki-lint.py` — broken links, pages missing from the
   index, missing front matter or sources.
2. Read for contradictions, stale claims ("upcoming" events now past), works on the
   website without a page, and gaps worth asking the artist about (`## Open questions`).
