# Open Letter — Gwangju Biennale

Static site. Four files, no build, no backend, no dependencies.
`index.html` (letter + form + list) · `info.html` (background) · `style.css` · `app.js`

---

## 1. Connect the signatory list

The site must never touch the sheet that holds email addresses. So:

```
Form → [A] responses sheet   PRIVATE   Timestamp·Email·Name·EnglishName·Occupation
         ↓ IMPORTRANGE, columns C D E only
       [B] public mirror     PUBLISHED Name·EnglishName·Occupation
         ↓ published CSV
       website
```

**Form settings:** Responses → *"Responders can see summary charts and text responses"* → **OFF**.

**Sheet [A]** (`1Q5-P2jkna-…`): Share → **Restricted**. Never publish it.

**Sheet [B]:** open <https://sheets.new>, paste into **A1**:

```
=QUERY(IMPORTRANGE("1Q5-P2jkna-QDN31XZOuuXfmBU5r3MQwFpqRo8TJODTA","A2:E"),"select Col3, Col4, Col5 where Col3 is not null or Col4 is not null",0)
```

Click **Allow access**. Then Ctrl-F for `@` — there must be none. If there is, the
columns are wrong; stop.

No tab name is given, so IMPORTRANGE reads the **first sheet** of [A]. That is
deliberate: naming the tab is what breaks this formula (a Chinese-language form
creates `表單回覆 1`, not `表單回應 1`). If [A] ever gains a second tab, put the
real name back in: `"'表單回覆 1'!A2:E"`.

Errors you may see in A1:
`找不到試算表` — the ID or the range is wrong ·
`您必須將這兩份試算表建立連結` — click Allow access ·
`#REF!` — [B] has content below A1 blocking the result; clear the sheet.

**Connect it.** Two ways. The site is currently wired the first way.

*Link mode (in use now).* [B] is shared "anyone with the link can view", and
`CSV_URL` in `app.js` reads it directly:
`https://docs.google.com/spreadsheets/d/<B-id>/gviz/tq?tqx=out:csv`
Works immediately. One cost: anyone who opens [B] in a browser sees the
IMPORTRANGE formula, which contains the ID of [A]. [A] is Restricted so they
still cannot read it — but it is an identifier you did not have to hand out.

*Publish mode (tighter).* File → Share → **Publish to web** → left dropdown
**工作表1** (*not* 整份文件) → right dropdown **CSV** → 發布. Copy the URL
(`.../d/e/2PACX-…/pub?gid=0&single=true&output=csv`). Then Share → General
access → **Restricted**. Publishing keeps working; it serves cell *values* only,
so the formula and [A]'s ID become invisible to everyone.

Either way, the URL goes in `CSV_URL` at the top of `app.js`.

New signatures appear within about 5 minutes (Google caches published output).
To remove someone, delete their row in [A]. To approve names before they show,
add an `Approved` column F in [A], widen the range to `A2:F`, and add
`and Col6 = TRUE` to the QUERY.

## 2. Deploy

Push the four files to a repo root → **Settings → Pages → Deploy from a branch →
`main` / `(root)`**. Leave **Enforce HTTPS** on. Done.

## 3. Security, briefly

GitHub Pages serves static files from a CDN. No server, no database, no login —
nothing to overload or break into, and a traffic flood is absorbed by GitHub. The
bandwidth allowance is ~100 GB/month against a ~20 KB page; you will not reach it.

| Risk | Handled by |
|---|---|
| Emails found | They are in a spreadsheet the site never references. The published sheet has no email column. |
| Published URL scraped | It contains only what the page already shows. |
| HTML typed into "Occupation" | Rendered with `textContent`, never `innerHTML`. |
| Injected tracker or script | CSP allows scripts from this repo only, network calls to `docs.google.com` only. |
| Compromised dependency | There are none. No npm, no CDN, no web fonts. |
| Google slow or down | The letter still renders; only the list shows a short notice. |

Not handled by hosting: **fake signatures**. Delete the row, or set the form to
one response per Google account, or use the `Approved` column above.
Turn on 2FA for the GitHub and Google accounts — those are the only two keys.

The form is a plain link, so Google only sees people who click through to sign.

## 4. Editing

The letter is in `index.html` — `<div class="en">`, `<div class="zh">`,
`<div class="ko">`. **The current text is a draft; replace it.** The timeline and
sources are in `info.html`. Language switching is CSS only.
