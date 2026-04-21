"""API v1 路由"""

from fastapi import APIRouter
from .schedule import router as schedule_router
from .parse import router as parse_router
from .qa import router as qa_router

router = APIRouter(prefix="/api/v1", tags=["v1"])

router.include_router(schedule_router, prefix="/schedule")
router.include_router(parse_router, prefix="/parse")
router.include_router(qa_router, prefix="/qa")

__all__ = ["router"]
