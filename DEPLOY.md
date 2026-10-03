# Deploying EduGenie

The app needs only one secret: `GEMINI_API_KEY`. Set it as an **environment variable in your host's dashboard**
(never commit `.env`). Without it the site still loads but serves canned "Demo mode" content.

After deploying, open `/health` — it should show `"mode": "gemini"`.

## Option A — Render (easiest)
1. Push this folder to a GitHub repo.
2. Render → New → Blueprint → pick the repo (it reads `render.yaml`).
3. Paste your `GEMINI_API_KEY` when prompted → Deploy.

## Option B — Railway / Heroku-style hosts
Uses the `Procfile`. Add `GEMINI_API_KEY` under Variables and deploy the repo.

## Option C — Any Docker host (Fly.io, Cloud Run, VPS)
```bash
docker build -t edugenie .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key edugenie
```
The container listens on `$PORT` (default 8000).

## Optional settings (environment variables)
| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_MODEL` | `gemini-3.5-flash` | Change if Google retires/renames the model |
| `RATE_LIMIT_PER_MINUTE` | `30` | Per-visitor limit; protects your quota (0 = off) |
| `MAX_INPUT_CHARS` | `12000` | Max input length |
| `REQUEST_TIMEOUT_SECONDS` | `60` | Gemini call timeout |

## Notes
- The rate limiter is in-memory, so run a single instance/worker (the default) for accurate limits.
- Free tiers may sleep when idle; the first request after a pause can be slow.
- The optional local T5 model (`EXPLANATION_PROVIDER=local`) needs several GB of RAM/disk — not recommended on free hosts.
