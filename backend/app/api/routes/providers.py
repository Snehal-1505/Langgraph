from fastapi import APIRouter
from app.config import settings
from app.api.schemas.research import ProviderStatusResponse
from app.tools.llm_provider import check_ollama_status

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("", response_model=ProviderStatusResponse)
def get_provider_status():
    """Returns availability and operational status of local and cloud providers."""
    # Check Ollama
    ollama_info = check_ollama_status(settings.OLLAMA_BASE_URL)
    
    # Check search provider status
    search_status = "ready"
    if settings.SEARCH_PROVIDER == "tavily" and not settings.TAVILY_API_KEY:
        search_status = "fallback_to_duckduckgo"

    configured_model = settings.OLLAMA_MODEL
    if settings.LLM_PROVIDER == "gemini":
        configured_model = settings.GEMINI_MODEL
    elif settings.LLM_PROVIDER == "groq":
        configured_model = settings.GROQ_MODEL
    elif settings.LLM_PROVIDER == "mock":
        configured_model = "deterministic-mock"

    return ProviderStatusResponse(
        llm_provider=settings.LLM_PROVIDER,
        configured_model=configured_model,
        ollama_status=ollama_info["status"],
        ollama_base_url=settings.OLLAMA_BASE_URL,
        gemini_configured=bool(settings.GEMINI_API_KEY),
        groq_configured=bool(settings.GROQ_API_KEY),
        search_provider=settings.SEARCH_PROVIDER,
        tavily_configured=bool(settings.TAVILY_API_KEY),
        active_search_status=search_status
    )
