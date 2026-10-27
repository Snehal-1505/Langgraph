from fastapi import APIRouter
from app.config import settings
from app.api.schemas.research import ConfigResponse

router = APIRouter(prefix="/config", tags=["Configuration"])


@router.get("", response_model=ConfigResponse)
def get_config():
    """Return safe frontend configuration without exposing any API keys or secrets."""
    return ConfigResponse(
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        llm_provider=settings.LLM_PROVIDER,
        search_provider=settings.SEARCH_PROVIDER,
        default_depth=settings.DEFAULT_SEARCH_DEPTH,
        max_sources_per_task=settings.MAX_SOURCES_PER_TASK
    )
