# Deploying RAG Arena — Hugging Face Spaces (backend) + Netlify (frontend)

Render's free tier (512MB) genuinely can't run this app's dependency stack
(torch, transformers, sentence-transformers, the full langchain ecosystem)
— confirmed directly: real indexing pushed memory past 565MB and climbing,
independent of any further code optimization. Hugging Face Spaces' free
CPU tier gives ~16GB, built specifically for hosting ML apps like this one.

Qdrant Cloud + Upstash Redis are unchanged from before — those are
external services regardless of which platform hosts the backend.

## 0. Before you start

Push the current code to GitHub (or wherever your Space's remote reads
from) — this includes `Dockerfile`, `.dockerignore`, and the root
`README.md` with the Spaces YAML frontmatter, all already in the repo.

## 1. Qdrant Cloud (vector store)

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io) (free tier: 1GB cluster).
2. Create a cluster → copy its **URL** (`https://xxxx.aws.cloud.qdrant.io:6333`)
   and an **API key**.

## 2. Upstash Redis (cache)

1. Sign up at [upstash.com](https://upstash.com) → Create Database (free tier).
2. Copy the **`rediss://` connection URL** (password included) — looks like
   `rediss://default:<password>@xxxx.upstash.io:6379`.

## 3. Backend — Hugging Face Space (Docker SDK)

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2. Pick a name, set **SDK** to **Docker**, visibility your choice (public
   is fine — no secrets live in the code, only in Space secrets).
3. Once created, the Space gives you a git remote, e.g.
   `https://huggingface.co/spaces/<your-username>/<space-name>`. Push this
   repo to it:
   ```
   git remote add space https://huggingface.co/spaces/<your-username>/<space-name>
   git push space main
   ```
   (If your default branch isn't `main`, adjust accordingly. You'll be
   prompted for HF credentials — use a
   [access token](https://huggingface.co/settings/tokens) as the password.)
4. The Space auto-builds from the root `Dockerfile` on push — watch the
   "Building" logs in the Space's own UI.
5. **Secrets** (Space → Settings → Repository secrets — equivalent to
   Render's env vars):

   | Key | Value |
   |---|---|
   | `GROQ_API_KEY` | your real key |
   | `QDRANT_URL` | from step 1 |
   | `QDRANT_API_KEY` | from step 1 |
   | `REDIS_URL` | from step 2 |
   | `API_KEY` | generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
   | `CORS_ORIGINS` | leave blank for now — you'll fill this in after step 4 |

   Adding/changing a secret triggers a rebuild automatically.
6. Once live, your backend's URL is
   `https://<your-username>-<space-name>.hf.space`.
7. Sanity check: `curl https://<your-username>-<space-name>.hf.space/health`
   — Qdrant and Redis should show `connected: true`.

**Note on `MAX_OUTPUT_TOKENS`**: while verifying this, a Groq account we
tested against hit a stricter 1000-output-token-per-minute cap than
`settings.MAX_OUTPUT_TOKENS = 1024` allows for on some tiers/models. If you
see `429 ... output tokens per minute (OTPM)` errors after deploying, lower
`MAX_OUTPUT_TOKENS` in `src/config/settings.py` slightly (e.g. to `900`)
and redeploy.

## 4. Frontend — Netlify

Unchanged from before. `frontend/netlify.toml` already sets the build
command, publish directory, and the SPA rewrite rule.

1. Netlify dashboard → **Add new site** → **Import an existing project** →
   connect your GitHub repo.
2. **Base directory**: `frontend` (build command/publish dir auto-detected
   from `netlify.toml`).
3. **Environment variables** (build-time — redeploy after changing):

   | Key | Value |
   |---|---|
   | `VITE_API_URL` | the Space URL from step 3.6 |
   | `VITE_API_KEY` | same value as the backend's `API_KEY` |

4. Deploy. Note the frontend's URL (`https://<your-site>.netlify.app`).

## 5. Close the loop

1. Backend (Space secrets) → set `CORS_ORIGINS` to the frontend URL from
   step 4.4 (no trailing slash — an easy mistake, and the backend now
   strips one if you do add it, but best to just set it right).
2. Open the frontend URL — Dashboard/Arena should load without CORS errors.
3. Populate the index: upload a PDF from the Ingest tab, or
   `curl -X POST https://<space-url>/index/directory -H "X-API-Key: <your key>" -H "X-Session-Id: <any-string>"`.

## 6. Data persistence on Spaces

Same caveat as any free-tier host: `data/` (per-session document/page/graph
registries, reward history, LLM cache — see `src/config/session.py`) is
plain files on the container's disk, wiped on every rebuild (a new commit,
a secret change, or the Space restarting). Fine for a demo; if you want it
to survive rebuilds, Spaces support a paid persistent storage add-on.

## 7. Sanity checklist before sharing the link

- [ ] `GET /health` on the Space shows all three services connected
- [ ] Frontend loads and reaches the backend (no CORS errors in the browser console)
- [ ] Direct-loading `/arena` or `/dashboard` works (not just `/`) — confirms Netlify's rewrite rule
- [ ] Index has content before showing anyone the Ask/Arena tabs
- [ ] A request without `X-API-Key` to a gated route returns 401
- [ ] Two browsers (or one in a private window) see independent data — confirms session isolation is working
