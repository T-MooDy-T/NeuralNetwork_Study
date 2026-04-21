"""API v1 路由"""

from fastapi import APIRouter
from .schedule import router as schedule_router
from .parse import router as parse_router
from .qa import router as qa_router
from .smart_push import router as smart_push_router
from .student_profile import router as student_profile_router

router = APIRouter(prefix="/api/v1", tags=["v1"])

router.include_router(schedule_router, prefix="/schedule")
router.include_router(parse_router, prefix="/parse")
router.include_router(qa_router, prefix="/qa")
router.include_router(smart_push_router, prefix="/smart-push")
router.include_router(student_profile_router, prefix="/student")

__all__ = ["router"]
