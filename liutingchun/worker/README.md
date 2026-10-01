# Chat worker — "Ask about the work"

The homepage chat box sends questions here. This Cloudflare Worker adds the knowledge
base (the LLM wiki in `../wiki/`, bundled by `../scripts/build-knowledge.py`) and the
OpenAI API key, asks a ChatGPT model, and streams the answer back. Nothing is stored.

## Set up (once)

1. OpenAI: create an API key at platform.openai.com/api-keys and set a monthly budget
   (Settings → Limits).
2. Cloudflare: My Profile → API Tokens → Create Token → "Edit Cloudflare Workers".
3. GitHub repo → Settings → Secrets and variables → Actions: add
   `CLOUDFLARE_API_TOKEN` and `OPENAI_API_KEY`.
4. Actions → "Deploy chat worker" → Run workflow. The log prints the Worker URL
   (`https://liutingchun-chat.<account>.workers.dev`).
5. Put that URL in `data/site.json` → `site.chat_endpoint`. The chat box appears on the
   homepage with the next build; leave it empty to hide it.

After that, every change to `wiki/` redeploys the Worker automatically.

## Settings (`wrangler.toml`)

- `MODEL`: which OpenAI model answers (`gpt-5.4-mini`; larger: `gpt-5.5`).
- `REASONING_EFFORT`: `none` (required with the `suggest_links` tool on gpt-5.4 models in the
  chat completions API); remove it for models without reasoning.
- `ALLOWED_ORIGINS`: pages allowed to use the Worker.
- Rate limits: 5 questions per minute per visitor, 20 per minute in total.
- Context: only the new question and the exchange before it are sent; answers are short.
- Links: the model may call the `suggest_links` tool; only URLs that appear in the wiki
  (see `wiki/pages/site-map.md`, generated from `data/site.json`) reach the visitor.

## Bot check (optional, recommended)

Cloudflare → Turnstile → Add widget (hostname `aprilcoffee.github.io`, later also
`liutingchun.com`; mode "Invisible"). Put the **site key** in `data/site.json` →
`site.turnstile_sitekey`, and the **secret key** in the GitHub secret `TURNSTILE_SECRET`,
then run "Deploy chat worker". Requests without a valid check are refused.
- Logs (Cloudflare dashboard → Workers → liutingchun-chat → Logs) show token usage per
  answer, never the questions.

## Local test

    npm install
    printf 'OPENAI_API_KEY=sk-...\nALLOWED_ORIGINS=http://localhost:8000\n' > .dev.vars
    npx wrangler dev
