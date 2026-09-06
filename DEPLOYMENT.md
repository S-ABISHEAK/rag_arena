# Deploying RAG Arena — Render (backend) + Netlify (frontend)

Render doesn't offer managed Qdrant, and its Redis/"Key Value" add-on has
no free tier — so this uses two external free-tier services (Qdrant Cloud,
Upstash Redis) for the backend's dependencies, Render for the backend
itself, and Netlify for the frontend. Total: 4 signups, ~30–45 minutes.

## 0. Before you start

- Push the code with the recent changes (`QDRANT_URL`/`QDRANT_API_KEY`,
  `REDIS_URL`, `API_KEY` support, `Procfile`) to GitHub — Render deploys
  from the repo, not from your local disk.
- Your local Python is **3.14**, which is very new — check Render's
  supported versions (dashboard → Environment → Python Version dropdown,
  or their docs) before assuming 3.14 is available. If it isn't, set
  `PYTHON_VERSION` to the newest one Render offers (e.g. `3.12.x`) and
  test locally with that version first — the pinned versions in
  `requirements.txt` were captured on 3.14 and a couple (torch,
  sentence-transformers) may need different wheels on an older Python.

## 1. Qdrant Cloud (vector store)

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io) (free tier: 1GB cluster).
2. Create a cluster → once ready, copy its **URL** (looks like
   `https://xxxx-xxxx.aws.cloud.qdrant.io:6333`) and generate/copy an
   **API key**.
3. Keep both handy for step 4.

## 2. Upstash Redis (cache)

1. Sign up at [upstash.com](https://upstash.com) → Create Database (free tier).
2. On the database page, copy the **`rediss://` connection URL** (includes
   the password baked in) — usually under "Connect" → "redis-cli" or a
   similarly labeled field. It looks like
   `rediss://default:<password>@xxxx.upstash.io:6379`.

## 3. Backend — Render Web Service

1. Render dashboard → **New +** → **Web Service** → connect your GitHub repo.
2. **Root Directory**: leave blank (repo root — `src/`, `requirements.txt`,
   `Procfile` all live there).
3. **Runtime**: Python 3.
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
   (matches `Procfile` — set it explicitly here; don't assume Render reads
   the Procfile automatically for a Python service).
6. **Instance Type**: Free is fine to start, with two caveats:
   - It **spins down after ~15 minutes of inactivity** and cold-starts on
     the next request — expect the first request after idle to be slow
     (loading the embedding model + reconnecting).
   - No persistent disk on Free — see §5 below on what that means for you.
7. **Environment variables** (Render dashboard → Environment):

   | Key | Value |
   |---|---|
   | `GROQ_API_KEY` | your real key |
   | `QDRANT_URL` | from step 1 |
   | `QDRANT_API_KEY` | from step 1 |
   | `REDIS_URL` | from step 2 |
   | `API_KEY` | generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
   | `CORS_ORIGINS` | leave blank for now — you'll fill this in after step 4 |
   | `PYTHON_VERSION` | only if 3.14 isn't available, per §0 |

8. Deploy. Once live, note the backend's URL (`https://<your-service>.onrender.com`).
9. Sanity check: `curl https://<your-service>.onrender.com/health` — Qdrant
   and Redis should both show `connected: true`. Groq will too, if the key's valid.

## 4. Frontend — Netlify

A `frontend/netlify.toml` is already in the repo — it sets the build
command, publish directory, and the SPA rewrite rule (see below) so the
dashboard needs almost no manual config.

1. Netlify dashboard → **Add new site** → **Import an existing project** →
   connect the same GitHub repo.
2. **Base directory**: `frontend`
3. **Build command** / **Publish directory**: Netlify should auto-detect
   these from `netlify.toml` (`npm run build` / `dist`) — leave as detected.
4. **Environment variables** (Site configuration → Environment variables —
   these are build-time; a redeploy is needed after changing them):

   | Key | Value |
   |---|---|
   | `VITE_API_URL` | the backend URL from step 3.8 |
   | `VITE_API_KEY` | same value as the backend's `API_KEY` |

5. The SPA rewrite (`/* → /index.html`) is already handled by
   `netlify.toml` — this app uses React Router with real URL paths
   (`/arena`, `/dashboard`, etc.), not hash routing, so without it,
   refreshing or directly opening any route other than `/` would 404.
   No dashboard action needed here, but it's worth knowing why that file
   is there.
6. Deploy. Note the frontend's URL (`https://<your-site>.netlify.app`, or
   a custom domain if you set one).

## 5. Close the loop

1. Go back to the **backend** service's env vars → set `CORS_ORIGINS` to
   the frontend URL from step 4.6 (e.g. `https://your-app.netlify.app`) →
   save (triggers a redeploy).
2. Open the frontend URL. Dashboard/Arena should show live (empty) data,
   not errors.
3. Populate the index: either upload a PDF from the Ingest tab, or
   `curl -X POST https://<backend>.onrender.com/index/directory -H "X-API-Key: <your API_KEY>"`
   (only works if you've also pushed a PDF into `data/pdfs/` in the repo —
   otherwise use the upload route instead).

## 6. What "no persistent disk on Free" actually means for you

`data/` (document/page/graph registries, reward history, LLM cache) is
plain files — not in Qdrant or Redis. On Render's free tier, this resets
on every deploy **and** likely on every spin-down/wake cycle. Practically:
you'll re-index after most restarts, and the Arena leaderboard's history
resets with it. This is fine for a portfolio demo people click through
live; it's not fine if you want data to survive long-term. If it starts to
matter, Render's paid instance tiers support attaching a persistent disk
mounted at `data/` — say so and I'll walk through that when you're there.

## 7. Sanity checklist before sharing the link

- [ ] `GET /health` on the backend shows all three services connected
- [ ] Frontend loads and can reach the backend (no CORS errors in the browser console)
- [ ] Direct-loading `/arena` or `/dashboard` (not just `/`) works — confirms `netlify.toml`'s rewrite rule took effect
- [ ] Index has content (Ingest tab or `/index/status`) before showing anyone the Ask/Arena tabs
- [ ] A request without `X-API-Key` to a gated route (e.g. `/query/traditional`) returns 401 — confirms `API_KEY` is actually active in production, not left blank
