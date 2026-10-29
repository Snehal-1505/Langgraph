# Deploy ResearchLab AI on Render

This repository is configured for a three-service Render deployment: a React static site, a FastAPI web service, and a managed PostgreSQL database.

## Before deploying

1. Push this repository to GitHub.
2. Create a Render PostgreSQL database. Keep it in the same region as the backend.
3. Create a Render Web Service from the repository with root directory `backend`, build command `pip install -r requirements.txt`, and start command:

   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. Set backend environment variables:
   - `DATABASE_URL`: the database's **Internal Database URL**.
   - `FRONTEND_ORIGIN`: the frontend's Render host, for example `researchlab-ui.onrender.com` (the app adds `https://` if the scheme is omitted).
   - `LLM_PROVIDER`: `gemini`, `groq`, `ollama`, or `mock`.
   - Set the selected provider's model/key variables (`GEMINI_API_KEY` / `GEMINI_MODEL` or `GROQ_API_KEY` / `GROQ_MODEL`) as needed. Keep API keys in Render's backend environment, never in the frontend.
   - `SEARCH_PROVIDER`: `duckduckgo` or `tavily`. For Tavily, also set `TAVILY_API_KEY`.
   - `DEBUG`: `false`.
5. Set the backend health check path to `/health`.
6. Create a Render Static Site from the same repository with root directory `frontend`, build command `npm ci && npm run build`, and publish directory `dist`.
7. Set the static site's `VITE_API_URL` to the backend host, for example `researchlab-api.onrender.com`. The frontend accepts either a host or a full `https://` URL.
8. Deploy both services. After changing either service's environment variables, trigger the deploy so the new values take effect.
9. Verify `/health` and `/docs` on the backend, then start a research session from the frontend and check streaming progress, report generation, and both export links.

## Notes

- Use PostgreSQL for hosted data. Render's local filesystem is ephemeral by default, so the default SQLite database file is not suitable for data that must survive restarts and redeploys.
- Set `FRONTEND_ORIGIN` to the exact frontend host/URL. The backend accepts a host without a scheme and treats it as HTTPS.
- The default Ollama URL points to localhost inside the backend service. For a hosted deployment, configure Gemini/Groq or provide an Ollama server reachable from Render and set `OLLAMA_BASE_URL` accordingly.
- Research runs in an in-process asyncio task. Backend restarts interrupt active jobs; a durable worker queue is recommended before relying on long-running jobs in production.
- Render free web services spin down when idle and free Postgres databases expire after 30 days. Review Render's current plans and limits before choosing a plan for persistent use.
