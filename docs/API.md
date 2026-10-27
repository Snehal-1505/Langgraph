# ResearchLab AI - API Reference

The FastAPI backend provides a versioned REST API at `/api/v1` along with Server-Sent Events (SSE) for live streaming.

Interactive OpenAPI documentation is accessible at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 1. System Health & Configuration

### `GET /health`
Returns application health and operational provider modes.

**Response:**
```json
{
  "status": "healthy",
  "app_name": "ResearchLab AI",
  "version": "1.0.0",
  "llm_provider": "ollama",
  "search_provider": "duckduckgo"
}
```

---

### `GET /api/v1/config`
Returns frontend-safe configuration options without exposing secrets.

**Response:**
```json
{
  "app_name": "ResearchLab AI",
  "app_version": "1.0.0",
  "llm_provider": "ollama",
  "search_provider": "duckduckgo",
  "default_depth": "standard",
  "max_sources_per_task": 5
}
```

---

### `GET /api/v1/providers`
Returns provider connection statuses.

**Response:**
```json
{
  "llm_provider": "ollama",
  "configured_model": "llama3.2",
  "ollama_status": "ready",
  "ollama_base_url": "http://localhost:11434",
  "gemini_configured": false,
  "groq_configured": false,
  "search_provider": "duckduckgo",
  "tavily_configured": false,
  "active_search_status": "ready"
}
```

---

## 2. Research Workflow Endpoints

### `POST /api/v1/research`
Initiates an autonomous research session. Returns immediately with the created session metadata while the multi-agent workflow executes in the background.

**Request Body:**
```json
{
  "topic": "Analyze the impact of generative AI on software development",
  "scope": "Enterprise velocity and security audits",
  "depth": "standard",
  "max_sources": 4
}
```

**Response (201 Created):**
```json
{
  "id": "e4587c14-2c09-43c2-bf72-1b6c085b46e1",
  "topic": "Analyze the impact of generative AI on software development",
  "scope": "Enterprise velocity and security audits",
  "depth": "standard",
  "max_sources": 4,
  "status": "pending",
  "current_stage": "initialization",
  "created_at": "2026-10-26T12:00:00Z",
  "updated_at": "2026-10-26T12:00:00Z",
  "completed_at": null,
  "error_summary": null
}
```

---

### `GET /api/v1/research/{research_id}/events`
Server-Sent Events (SSE) stream delivering real-time workflow notifications.

**Event Protocol:**
- Event Name: `workflow_event`
- Data Payload: JSON string
```json
{
  "session_id": "e4587c14-2c09-43c2-bf72-1b6c085b46e1",
  "stage": "planning",
  "event_type": "completed",
  "message": "Planner generated 3 targeted research tasks.",
  "data": {
    "plan_tasks": [
      "Current Developments, Facts & Trends",
      "Benefits, Opportunities & Productivity",
      "Risks, Limitations & Challenges"
    ]
  },
  "timestamp": "2026-10-26T12:00:05Z"
}
```

---

### `GET /api/v1/research/{research_id}/report`
Retrieves the finalized 14-section research report.

**Response:**
```json
{
  "id": "report-uuid",
  "session_id": "e4587c14-2c09-43c2-bf72-1b6c085b46e1",
  "version": 1,
  "title": "Comprehensive Research Report: Generative AI in Software Development",
  "markdown_content": "# Comprehensive Research Report...",
  "executive_summary": "High-level synthesis...",
  "review_status": "passed",
  "created_at": "2026-10-26T12:01:30Z"
}
```

---

### `GET /api/v1/research/{research_id}/sources`
Retrieves all collected web sources with extracted evidence snippets.

---

### `GET /api/v1/research/{research_id}/export/markdown`
Downloads the report as a clean `.md` document.

---

### `GET /api/v1/research/{research_id}/export/pdf`
Streams a formatted PDF document generated dynamically via ReportLab.

---

### `POST /api/v1/research/{research_id}/cancel`
Requests cancellation of a running background research job.

---

### `DELETE /api/v1/research/{research_id}`
Deletes the session, its reports, source records, and associated checkpoints.
