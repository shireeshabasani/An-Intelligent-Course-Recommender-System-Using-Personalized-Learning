# Course Recommender - Full ML Project (MVP)

This repository is an enhanced full-stack Course Recommender MVP with ML features.

Features included:
- User registration & login (simple)
- Text & semantic search (semantic requires sentence-transformers)
- Simple personalization (tag-based + similarity)
- Learning path generator that builds a schedule from user's available hours
- Event tracking (user actions)
- Aggregator script to seed courses and compute embeddings (optional)
- React frontend (Vite) with search and recommendations
- Docker Compose for running backend + MongoDB

Quick start (dev):
1. Install Docker & Docker Compose
2. `docker compose up --build`
3. Seed DB: `./run_seed.sh`
4. Frontend dev: `cd frontend && npm install && npm run dev`

Notes:
- The backend supports semantic search if `sentence-transformers` is installed in the backend container.
- For production, replace simple auth with JWT and hashed passwords, secure secrets, and use a managed vector DB if needed.
