---
title: RAG Arena
emoji: 🏟️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# RAG Arena

FastAPI backend comparing four RAG retrieval strategies (Traditional,
Hybrid, PageIndex, Graph) with an LLM auto-router and a contextual-bandit
leaderboard. Deployed here as a Hugging Face Space (Docker SDK) — see
`DEPLOYMENT.md` in the repo for the full setup, including the separate
Netlify-hosted frontend this API serves.
