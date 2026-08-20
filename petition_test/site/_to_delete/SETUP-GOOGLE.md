# Google setup (do this once, by hand)

The site never talks to the spreadsheet that holds email addresses. It reads a
**second, separate spreadsheet** that contains only name / english name /
occupation. That is the whole privacy design: even if the public URL is scraped,
there is nothing there but what is already printed on the page.

```
Google Form
    ↓
[A] Responses sheet   PRIVATE   Timestamp · Email · Name · English Name · Occupation
    ↓ IMPORTRANGE (pulls columns C,D,E only)
[B] Public mirror     PUBLISHED Name · English Name · Occupation
    ↓ published CSV
website
```

---

## 1. Lock down the Form

Open the form → **Settings**:

- **Responses → "Responders can see summary charts and text responses"** → **OFF**
  (if this is on, anyone who submits can read every email address)
- **Collect email addresses** → keep as is (Verified/Responder input) — the site
  never reads that column
- Do not turn on "Response receipts" with a public link

## 2. Lock down sheet [A]

Spreadsheet `1Q5-P2jkna-QDN31XZOuuXfmBU5r3MQwFpqRo8TJODTA`

- **Share → General access → Restricted.** Never "Anyone with the link".
- **Never** use File → Share → Publish to web on this document.

Its columns are: `A 時間戳記` · `B 電子郵件地址` · `C Name in your langauge (姓名)`
· `D English Name (英文姓名)` · `E Occupation (職稱)`.

## 3. Create sheet [B] — the public mirror

1. Go to <https://sheets.new> and name it **Petition — Public List**.
2. In cell **A1** paste exactly:

```
=QUERY(IMPORTRANGE("1Q5-P2jkna-QDN31XZOuuXfmBU5r3MQwFpqRo8TJODTA","表單回應 1!A2:E"),"select Col3, Col4, Col5 where Col3 is not null or Col4 is not null",0)
```

   If the tab in sheet [A] is named something else, use that name instead of
   `表單回應 1` (look at the tab label at the bottom of sheet [A]).

3. A `#REF!` appears with a **Allow access** button — click it once.
4. **Check the result: there must be no `@` anywhere in this spreadsheet.**
   Ctrl/Cmd-F for `@`. If you see one, stop — the column mapping is wrong.

## 4. Publish sheet [B]

**File → Share → Publish to web**

- Left dropdown: select **Sheet1** — *not* "Entire Document"
- Right dropdown: **Comma-separated values (.csv)**
- **Publish** → copy the URL. It looks like:

```
https://docs.google.com/spreadsheets/d/e/2PACX-1vT..../pub?gid=0&single=true&output=csv
```

Leave sheet [B]'s normal **Share** setting on *Restricted*. Publish-to-web is a
separate channel and it exposes only cell **values** — not your formulas, and
not the ID of sheet [A].

## 5. Connect the site

Open `app.js`, replace `PASTE_PUBLISHED_CSV_URL_HERE` with that URL, commit, push.

## 6. Verify

```bash
curl -s "<your published csv url>" | grep '@' && echo "STOP — leak" || echo "clean"
grep -r "1Q5-P2jkna" . --exclude-dir=.git   # must return nothing outside this file
```

Open the site in a private window and view source — you should see only the
`2PACX-…` published URL, which leads to names and occupations only.

## Notes

- Google caches published output for **up to ~5 minutes**, so a new signature
  appears within about five minutes. That is as "live" as this method gets.
- New signatures appear **without review**. If you want to approve names first,
  add a column `Approved` in sheet [A] (column F), widen the IMPORTRANGE range to `A2:F`, and add
  `and Col6 = TRUE` to the QUERY in [B].
- To remove someone: delete their row in sheet [A]; [B] and the site follow.
