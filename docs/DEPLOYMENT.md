# ResearchLab AI - Production Deployment Guide

This guide covers deployment strategies for **ResearchLab AI**, including containerization, production database setup, model hosting, and environment security.

---

## 1. Architecture Deployment Overview

```
                      [ User Traffic ]
                             │
                             ▼
                    [ Reverse Proxy / CDN ]
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    [ Static Frontend ]           [ FastAPI Backend ]
       (Vercel / Nginx)              (Docker / Gunicorn)
                                            │
                             ┌──────────────┼──────────────┐
                             ▼              ▼              ▼
                       [ PostgreSQL ]   [ Ollama/Cloud ] [ Web Search ]
                         (Persistent)       (LLM API)      (DuckDuckGo)
```

---

## 2. Docker Compose Deployment (Recommended for Self-Hosting)

The project includes a complete `docker-compose.yml` that builds both backend and frontend.

### Step 1: Configure Environment Variables
Ensure `.env` contains production values:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2
SEARCH_PROVIDER=duckduckgo
DATABASE_URL=sqlite:///./data/research.db
FRONTEND_ORIGIN=http://your-domain.com
```

### Step 2: Build and Launch Containers
```bash
docker-compose up --build -d
```

### Step 3: Verify Container Health
```bash
docker-compose ps
docker-compose logs -f backend
```

---

## 3. Production Database: Upgrading to PostgreSQL

While SQLite is the default local database, SQLite concurrency has limits under high write volumes. For multi-user production deployments, configure PostgreSQL:

1. Install `asyncpg` or `psycopg2-binary`:
   ```bash
   pip install psycopg2-binary
   ```
2. Update `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@db-host:5432/researchlab
   ```
3. Run Alembic migrations against the PostgreSQL instance:
   ```bash
   alembic upgrade head
   ```

> [!WARNING]
> Never deploy to serverless containers with an ephemeral SQLite database file without mounting a persistent volume. Ephemeral containers will lose all research history and checkpoints when recycled.

---

## 4. Production AI Model Strategy

A local Ollama instance on your developer PC is not automatically accessible to a cloud server. When deploying to production:

### Option A: Dedicated GPU VPS with Ollama
Host Ollama on a secure Linux VPS equipped with an NVIDIA GPU (e.g., RunPod, Lambda Labs, Hetzner, AWS EC2 G5).
- Restrict Ollama's port `11434` to your backend's internal private VPC network or secure with an API gateway.

### Option B: Free-Tier / Production Cloud APIs
Configure your cloud backend with Google Gemini or Groq:
- `LLM_PROVIDER=gemini` with `GEMINI_API_KEY`
- `LLM_PROVIDER=groq` with `GROQ_API_KEY`

---

## 5. Security Checklist for Production

- [x] **SSRF Protection:** Ensure internal link-local (169.254.169.254) and VPC subnets remain blocked in `source_validator.py`.
- [x] **CORS:** Set `FRONTEND_ORIGIN` strictly to your production domain (e.g. `https://researchlab.yourdomain.com`).
- [x] **Secrets Management:** Store `GEMINI_API_KEY`, `GROQ_API_KEY`, and `TAVILY_API_KEY` in environment secret managers (e.g., AWS Secrets Manager, GitHub Actions Secrets). Never commit `.env`.
- [x] **Rate Limiting:** Place Cloudflare or Nginx in front of the API to throttle abuse.
