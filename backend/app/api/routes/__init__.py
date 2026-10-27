from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.config import router as config_router
from app.api.routes.providers import router as providers_router
from app.api.routes.research import router as research_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(config_router)
api_v1_router.include_router(providers_router)
api_v1_router.include_router(research_router)

__all__ = ["api_v1_router", "health_router"]
