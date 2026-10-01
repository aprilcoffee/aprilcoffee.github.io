# Chat worker — "Ask about the work"

The homepage chat box sends questions here. This Cloudflare Worker adds the knowledge
base (the LLM wiki in `../wiki/`, bundled by `../scripts/build-knowledge.py`) and the
Claude API key, asks Claude, and streams the answer back. Nothing is stored.

## Set up (once)

1. Anthropic: create an API key at console.anthropic.com and set a monthly spend limit.
2. Cloudflare: My Profile → API Tokens → Create Token → "Edit Cloudflare Workers".
3. GitHub repo → Settings → Secrets and variables → Actions: add
   `CLOUDFLARE_API_TOKEN` and `ANTHROPIC_API_KEY`.
4. Actions → "Deploy chat worker" → Run workflow. The log prints the Worker URL
   (`https://liutingchun-chat.<account>.workers.dev`).
5. Put that URL in `data/site.json` → `site.chat_endpoint`. The chat box appears on the
   homepage with the next build; leave it empty to hide it.

After that, every change to `wiki/` redeploys the Worker automatically.

## Settings (`wrangler.toml`)

- `MODEL`: which Claude model answers (`claude-opus-5-5`; cheaper: `claude-sonnet-5-5`,
  `claude-haiku-4-5`).
- `ALLOWED_ORIGINS`: pages allowed to use the Worker.
- Rate limits: 6 questions per minute per visitor, 40 per minute in total.
- Logs (Cloudflare dashboard → Workers → liutingchun-chat → Logs) show token usage per
  answer, never the questions.

## Local test

    npm install
    printf 'ANTHROPIC_API_KEY=sk-...\nALLOWED_ORIGINS=http://localhost:8000\n' > .dev.vars
    npx wrangler dev
