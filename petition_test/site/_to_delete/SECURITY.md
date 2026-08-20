# Security notes (plain language)

You are not running a server. That is the whole security posture, and it is a
strong one — most of what goes wrong with petition sites cannot happen here.

## Why GitHub Pages is hard to knock over

GitHub Pages serves your three files from a global CDN (Fastly). Every visitor
gets a cached copy from an edge node near them. There is no database, no login,
no server-side code, no admin panel — so there is nothing to overload, nothing
to inject into, and nothing to break into except the repository itself.

A flood of traffic hits GitHub's CDN, not you. You do not have to do anything.

Two things worth knowing:

- GitHub Pages has a **soft limit of ~100 GB of bandwidth per month**. This page
  is roughly 15 KB, so that is millions of views. If a genuine flood ever passed
  it, GitHub emails you and may throttle — it does not bill you.
- **Do not put the site behind anything.** No analytics, no comment widget, no
  form embed, no third-party script. Every one of those adds a service that can
  fail, be attacked, or track your signatories.

Turn on **Settings → Pages → Enforce HTTPS** (it is on by default).

## The actual attack surface, and what handles each

| Risk | Handled by |
|---|---|
| Someone finds signatories' email addresses | Emails live in a spreadsheet the site has no reference to. The published sheet the site reads physically does not contain an email column. |
| Someone scrapes the published sheet URL directly | They get exactly what the page already displays: names and occupations. |
| Someone types HTML or a script into the "Occupation" field | `app.js` renders with `textContent`, never `innerHTML`. Their tags appear as literal text. |
| A script gets injected into the page some other way | `Content-Security-Policy` allows scripts only from your own repo and network calls only to `docs.google.com`. An injected tracker or beacon simply fails to load. |
| A dependency gets compromised | There are no dependencies. No npm, no CDN, no web fonts. |
| Google is slow or rate-limits during a traffic spike | The letter renders from static HTML regardless; only the list shows "Could not load". Nothing else breaks. |
| Traffic flood | Absorbed by GitHub's CDN. |

## What is *not* automatically handled

**Fake or abusive signatures.** This is the real risk with any open petition, and
no amount of hosting security touches it. Options, cheapest first:

1. Delete the row in the responses sheet. The public list follows within ~5 min.
2. In the Form: **Settings → Responses → Limit to 1 response** (requires
   signing in with a Google account — raises the cost of mass submission a lot).
3. Add an `Approved` column and only publish approved rows — see the note at the
   end of `SETUP-GOOGLE.md`. Slower, but nothing appears until you say so.

**Your accounts.** The repository and the Google account are now the only two
things that matter. Turn on two-factor authentication on both. If more than one
person can push, turn on branch protection so the live site cannot be changed by
a single compromised laptop.

**A custom domain**, if you add one, becomes a thing that can expire or be
hijacked. `username.github.io` cannot.

## Before you go live — a five-minute check

```bash
# 1. no trace of the private spreadsheet anywhere in the repo
grep -ri "1Q5-P2jkna" . --exclude-dir=.git --exclude=SETUP-GOOGLE.md

# 2. the published CSV really has no addresses in it
curl -s "<your published csv url>" | grep '@'

# 3. both must print nothing
```

Then open the live site in a private window, View Source, and read all three
files top to bottom. They are short on purpose: you should be able to satisfy
yourself, personally, that nothing in them phones anywhere unexpected. That is
worth more than trusting this document.
