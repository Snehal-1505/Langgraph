import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database.session import Base, engine
from app.api.routes import api_v1_router, health_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema is created
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized. Server ready on provider: {settings.LLM_PROVIDER}")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agent Research System powered by LangGraph, local Ollama, and parallel researchers.",
    lifespan=lifespan
)

# CORS configuration
frontend_origin = settings.FRONTEND_ORIGIN.rstrip("/")
if frontend_origin and not frontend_origin.startswith(("http://", "https://")):
    frontend_origin = f"https://{frontend_origin}"

origins = [
    frontend_origin,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(health_router)
app.include_router(api_v1_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred. Please consult backend logs."}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
