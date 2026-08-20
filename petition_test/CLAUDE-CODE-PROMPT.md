# Claude Code prompt

## Step 0

```bash
mkdir gwangju-petition && cd gwangju-petition && git init
curl -o CLAUDE.md https://raw.githubusercontent.com/multica-ai/andrej-karpathy-skills/main/CLAUDE.md
```

Or in Claude Code:
`/plugin marketplace add multica-ai/andrej-karpathy-skills` then
`/plugin install andrej-karpathy-skills@karpathy-skills`

Start Claude Code there and paste everything below the line.

---

# Build a static petition site

Follow CLAUDE.md — **Simplicity First** and **Goal-Driven Execution** especially.
If you reach for a framework, a bundler, or a `package.json`, you have misread
the task. This page must still work in five years with nobody maintaining it.

## Context

The 16th Gwangju Biennale replaced the designation "Taiwan Pavilion" with
"NTMoFA" in its promotional materials. Taiwan's Ministry of Culture objected on
9 Aug 2026; ten Taiwanese artists issued a joint statement on 15 Aug; the Korean
coalition Artists' Solidarity Against Censorship called it political censorship
on 18 Aug. Research the current state of the story before writing any copy —
start from e-flux, Artforum, Focus Taiwan, Taipei Times, 自由藝文網.

This is an open letter others can co-sign. Tonal reference: <https://anga.live/>
— a plain black-on-white document, not a campaign landing page. No hero image,
no gradients, no animation, no logo.

## Deliverables

Four files at repo root, hostable as-is on GitHub Pages, plus one `README.md`.

- `index.html` — the letter, the embedded sign-up form, the signatory list
- `info.html` — background: a dated timeline and a list of sources
- `style.css`, `app.js`

## Hard constraints

1. **No backend, no build step, no dependencies.** No npm, no CDN, no web fonts,
   no analytics.
2. **Trilingual: English / 中文 / 한국어.** All three live in the HTML; a
   `data-lang` attribute on `<html>` plus one CSS rule set switches them. Three
   buttons, not a translation system. Korean matters here — the intended reader
   is in Gwangju.
3. **Signatures via Google Form, list read live from Google Sheets.** No
   copy-pasting names, no GitHub Action, no scheduled job.
4. **Email addresses must be unreachable from the site.** Below.

## Privacy architecture — implement exactly this

```
Form → [A] responses sheet  PRIVATE  Timestamp·Email·Name·EnglishName·Occupation
         ↓ IMPORTRANGE, columns C D E only
       [B] public mirror    a DIFFERENT spreadsheet, published to web as CSV
         ↓ fetch()
       site
```

The site must contain **no reference of any kind** to sheet [A] — not its ID, not
in a comment. The only Google URLs in the code are the published CSV of [B] and
the public form. A determined reader of the page source must find nothing they
could not already read on the page.

Known values:

- Form: `https://docs.google.com/forms/d/e/1FAIpQLSeqSDArEo8KJHKWWCMezDTg3ScAiFH3zGDRr4BVV5JX6sbQWA/viewform`
- Sheet [A] tab `表單回覆 1` (note 回覆), columns `A 時間戳記 · B 電子郵件地址 ·
  C Name in your langauge (姓名) · D English Name (英文姓名) · E Occupation (職稱)`
- Sheet [B] does not exist yet. Put the CSV URL in one `CSV_URL` constant at the
  top of `app.js` with the placeholder `PASTE_PUBLISHED_CSV_URL_HERE`, and put
  the exact clicks to create and publish [B] in `README.md`.

Defence in depth:

- `app.js` reads only fields 0,1,2 of each row and **drops any row containing
  `@`**, whatever the sheet holds.
- Render with `textContent` only — never `innerHTML`. "Occupation" is untrusted.
- CSP `<meta>`: `default-src 'none'`, `connect-src` limited to `docs.google.com`. Do not put `frame-ancestors` in a meta tag — browsers ignore
  it there and log an error.
- `<meta name="referrer" content="no-referrer">`.

## Hosting

GitHub Pages, specifically so there is nothing to attack or overload: static
files on a CDN, no server, no database, no admin. Preserve that. The only
network call the page makes is the one CSV `fetch`. If
Google is slow or unreachable the letter and the form link must still render —
never block rendering on the fetch.

## Page structure

Single column, `max-width: 40rem`, centred.

`index.html` — title + one-line standfirst; the letter as paragraphs then a
numbered list of demands (write a clearly-marked **draft**, it will be replaced);
link to `info.html`; a single black button linking to the
Google Form (a plain link, not an embedded iframe — an iframe would load Google
for every visitor) and one line saying emails are never published; `Signatories (n)` — name,
latin name in grey, occupation right-aligned, stacked on narrow screens. No footer.

`info.html` — a date-and-text timeline, the ten signatories of the 15 Aug
statement, and a list of source links. Facts and dates only, no argument.

## Success criteria — verify each before saying you are done

1. Headless-browser render of both pages against a **mock CSV**: header row
   skipped, a quoted field containing a comma parsed correctly, a row whose name
   is an email address **absent** from the output.
2. Rendered page text contains no `@`.
3. Console clean on both pages — no errors, no CSP violations.
4. `grep -ri "1Q5-P2jkna\|@gmail" .` returns nothing outside `README.md`.
5. All three languages flip every block of text and change `<html lang>`;
   the choice survives navigation between the two pages.
6. `app.js` under 200 lines, `style.css` under 100. If over, delete something.
7. `README.md` under two pages, covering: publishing sheet [B], GitHub Pages
   deployment, and a short plain-language security note for a non-technical
   maintainer — including that **fake signatures** are the one risk hosting does
   not solve.

Show me the screenshots and the mock-CSV output. Add nothing I did not ask for:
no share buttons, no animated counters, no dark mode.
