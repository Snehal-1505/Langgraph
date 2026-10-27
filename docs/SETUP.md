# ResearchLab AI - Local Setup & Developer Guide

This guide provides step-by-step instructions to configure, run, and test **ResearchLab AI** on Windows using PowerShell.

---

## 1. Prerequisites

Ensure you have the following installed on your Windows system:

1. **Python 3.11+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Check in PowerShell:
     ```powershell
     python --version
     ```
2. **Node.js (v18+ or v20+) and npm**
   - Download from [nodejs.org](https://nodejs.org/)
   - Check in PowerShell:
     ```powershell
     node -v
     npm -v
     ```
3. **Ollama (Default Free Local AI)**
   - Download from [ollama.com](https://ollama.com/download/windows)
   - Install and pull the recommended lightweight instruction model:
     ```powershell
     ollama pull llama3.2
     ```
   - Ensure Ollama is running in the background:
     ```powershell
     ollama serve
     ```

---

## 2. Workspace Setup

Clone or open the repository directory:

```powershell
cd c:\Users\SNEHAL\Downloads\Langgraph
```

Copy the environment example file:

```powershell
Copy-Item .env.example .env
```

---

## 3. Backend Setup & Startup

### Step A: Create and Activate Virtual Environment
Open a new Windows PowerShell terminal:

```powershell
cd c:\Users\SNEHAL\Downloads\Langgraph\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> **Note for Windows Execution Policy:** If you encounter `running scripts is disabled on this system`, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Step B: Install Backend Dependencies
```powershell
pip install -r requirements.txt
```

### Step C: Run Database Migrations (Alembic)
```powershell
alembic upgrade head
```

### Step D: Start FastAPI Backend Server
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Verify backend health by opening your browser to:
- Health check: `http://127.0.0.1:8000/health`
- Interactive Swagger docs: `http://127.0.0.1:8000/docs`

---

## 4. Frontend Setup & Startup

Open a **second** Windows PowerShell terminal:

```powershell
cd c:\Users\SNEHAL\Downloads\Langgraph\frontend
npm install
npm run dev
```

The Vite dev server will start at:
- **Application UI:** `http://localhost:5173`

---

## 5. Running Automated Tests

### Run Backend Unit & Integration Tests (pytest)
In your backend terminal with the venv active:

```powershell
cd c:\Users\SNEHAL\Downloads\Langgraph\backend
.\venv\Scripts\pytest -v
```

All 23 unit and end-to-end workflow tests will run using deterministic mock fixtures without incurring any API costs.

### Run Frontend Component Tests (Vitest)
In your frontend terminal:

```powershell
cd c:\Users\SNEHAL\Downloads\Langgraph\frontend
npm test
```

### Build Frontend for Production
```powershell
npm run build
```

---

## 6. Optional Free-Tier Cloud Configuration

If you do not wish to run local Ollama, you can configure optional free cloud providers by editing `.env`:

```env
# Switch LLM Provider to Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_google_ai_studio_key_here
GEMINI_MODEL=gemini-1.5-flash

# OR Switch LLM Provider to Groq
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Optional Tavily Search
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_tavily_api_key_here
```

---

## 7. Troubleshooting Common Errors

### 1. `Cannot connect to Ollama at http://localhost:11434`
- Make sure Ollama desktop app is running in the Windows system tray, or run `ollama serve` in a terminal.
- If Ollama is offline, the backend automatically logs a warning and falls back to deterministic mode for safety.

### 2. `Port 8000 is already in use`
- Find and terminate the process:
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
  ```

### 3. DuckDuckGo Rate Limits / Blocks
- The system includes automatic error isolation. If DuckDuckGo blocks a query or times out, the Researcher logs the limitation and proceeds without crashing the entire workflow.
