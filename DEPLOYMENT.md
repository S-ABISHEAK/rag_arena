# Deploying RAG Arena (Railway / Render / Fly.io — PaaS)

This app has two independently deployable pieces: the FastAPI backend
(`src/`) and the Vite/React frontend (`frontend/`). It also depends on
Qdrant and Redis, which the included `docker-compose.yml` only runs
**locally** — a PaaS deploy needs managed equivalents (see below).

## 1. Qdrant + Redis (managed, not docker-compose)

Most PaaS free/hobby tiers give the app container an **ephemeral
filesystem** — anything written to disk (including a self-hosted Qdrant or
Redis inside the same container) is wiped on every restart or redeploy.
Use managed services instead:

- **Qdrant Cloud** (qdrant.tech) has a free tier — gives you a host + API key.
- **Redis**: Railway/Render both offer a one-click managed Redis add-on;
  Upstash's free tier also works over the same `redis://` protocol.

Either way, this project's `QDRANT_HOST`/`QDRANT_PORT` and
`REDIS_HOST`/`REDIS_PORT` env vars point at whatever host you're given —
no code changes needed, both were already (or are now) fully
env-configurable.

> Qdrant Cloud typically requires TLS + an API key, which this project's
> `QdrantStore` doesn't currently pass — if you go that route, say so and
> I'll wire up `QDRANT_API_KEY`/HTTPS support before you deploy.

## 2. The app's own data directory

`data/` (document/page/graph registries, the reward-tracker history, the
LLM response cache) is plain files on local disk — **not** in Qdrant or
Redis. On an ephemeral filesystem this resets on every redeploy: you'd
need to re-run `/index/directory` (or re-upload PDFs) and the Arena
leaderboard would lose its history each time.

- If your platform offers a **persistent volume/disk** (Render disks,
  Fly.io volumes, Railway volumes), mount it at `data/` and this is a
  non-issue.
- Otherwise, treat re-indexing after each deploy as expected, and know the
  reward history resets too.

## 3. Environment variables to set on the platform

Copy from `.env.example` — set these in your platform's dashboard, never
commit real values:

| Var | Notes |
|---|---|
| `GROQ_API_KEY` | required |
| `QDRANT_HOST` / `QDRANT_PORT` | your managed Qdrant instance |
| `REDIS_HOST` / `REDIS_PORT` | your managed Redis instance |
| `CORS_ORIGINS` | your deployed **frontend's** URL(s), comma-separated |
| `API_KEY` | generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"` — gates the costly/mutating routes |
| `MAX_UPLOAD_SIZE_MB` | optional, defaults to 25 |

## 4. Backend start command

Already provided in `Procfile`:
```
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```
`--host 0.0.0.0` is required — the default `127.0.0.1` only accepts
connections from inside the same container, which breaks on every PaaS.
`$PORT` is injected by Railway/Render/Heroku-style platforms; if yours
doesn't, hardcode the port it expects instead.

## 5. Frontend

Build as a static site (`npm run build` → `frontend/dist/`) and deploy it
to whatever static hosting your platform offers (or a separate
Vercel/Netlify/Cloudflare Pages project — nothing here requires it to be
on the same platform as the backend). Set at build time:

- `VITE_API_URL` — your deployed backend's public URL
- `VITE_API_KEY` — the same value as the backend's `API_KEY`, if set

Both are baked into the built JS bundle (Vite behavior for any
`VITE_`-prefixed var) — this is normal and expected, not a leak of a real
secret, but it does mean `API_KEY` is only a bot/abuse deterrent, not a
true secret, once shipped to a browser.

## 6. First deploy checklist

1. Managed Qdrant + Redis provisioned, host/port env vars set.
2. `GROQ_API_KEY`, `API_KEY`, `CORS_ORIGINS` set on the backend.
3. Backend deployed, `GET /health` returns all three services connected.
4. Frontend built with `VITE_API_URL` + `VITE_API_KEY` pointing at that
   backend, deployed.
5. `POST /index/directory` (with the `X-API-Key` header) or upload a PDF
   from the Ingest tab to populate the index before demoing.
