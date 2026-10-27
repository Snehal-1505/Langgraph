import os
from pathlib import Path
from typing import Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application
    APP_NAME: str = "ResearchLab AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # LLM Settings
    LLM_PROVIDER: Literal["ollama", "gemini", "groq", "mock"] = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # Cloud Providers (Optional)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # Search Providers
    SEARCH_PROVIDER: Literal["duckduckgo", "tavily", "mock"] = "duckduckgo"
    TAVILY_API_KEY: Optional[str] = None

    # Database
    DATABASE_URL: str = "sqlite:///./data/research.db"

    # Workflow Constraints
    REQUEST_TIMEOUT_SECONDS: int = 20
    MAX_CONTENT_LENGTH_BYTES: int = 500000
    MAX_RESEARCH_ATTEMPTS: int = 2
    MAX_REPORT_REVISIONS: int = 2
    MAX_SOURCES_PER_TASK: int = 5
    DEFAULT_SEARCH_DEPTH: Literal["quick", "standard", "detailed"] = "standard"

    @property
    def data_dir(self) -> Path:
        base = Path(__file__).resolve().parent.parent
        data_path = base / "data"
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path

    @property
    def resolved_database_url(self) -> str:
        if self.DATABASE_URL.startswith("sqlite:///./data/"):
            db_file = self.data_dir / "research.db"
            return f"sqlite:///{db_file.as_posix()}"
        return self.DATABASE_URL


settings = Settings()
