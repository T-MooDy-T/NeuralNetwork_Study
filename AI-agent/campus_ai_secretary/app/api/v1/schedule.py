"""日程管理 API"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from loguru import logger

from ...models.schedule import ScheduleItem, ScheduleCreate, ScheduleUpdate, ScheduleQuery, Priority
from ...core.scheduler import ScheduleManager

router = APIRouter()

# 全局日程管理器（实际应该用依赖注入）
_scheduler: Optional[ScheduleManager] = None


def get_scheduler() -> ScheduleManager:
    """获取日程管理器实例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = ScheduleManager(use_memory=True)
    return _scheduler


@router.post("/create", response_model=ScheduleItem, summary="创建日程")
async def create_schedule(data: ScheduleCreate, user_id: str = "default"):
    """创建新的日程"""
    try:
        scheduler = get_scheduler()
        schedule = scheduler.create_schedule(user_id, data)
        logger.info(f"API: 创建日程 - 用户：{user_id}, 事件：{data.event_name}")
        return schedule
    except Exception as e:
        logger.exception(f"创建日程失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{schedule_id}", response_model=ScheduleItem, summary="获取日程详情")
async def get_schedule(schedule_id: str, user_id: str = "default"):
    """获取单个日程详情"""
    scheduler = get_scheduler()
    schedule = scheduler.get_schedule(user_id, schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="日程不存在")
    
    return schedule


@router.get("/list", response_model=List[ScheduleItem], summary="获取日程列表")
async def list_schedules(
    user_id: str = "default",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None
):
    """获取用户日程列表，支持过滤"""
    scheduler = get_scheduler()
    
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    priority_enum = Priority(priority) if priority else None
    
    schedules = scheduler.list_schedules(
        user_id,
        start_date=start_dt,
        end_date=end_dt,
        priority=priority_enum,
        status=status
    )
    
    return schedules


@router.put("/{schedule_id}", response_model=ScheduleItem, summary="更新日程")
async def update_schedule(schedule_id: str, data: ScheduleUpdate, user_id: str = "default"):
    """更新日程信息"""
    scheduler = get_scheduler()
    schedule = scheduler.update_schedule(user_id, schedule_id, data)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="日程不存在")
    
    logger.info(f"API: 更新日程 - 用户：{user_id}, ID: {schedule_id}")
    return schedule


@router.delete("/{schedule_id}", summary="删除日程")
async def delete_schedule(schedule_id: str, user_id: str = "default"):
    """删除日程"""
    scheduler = get_scheduler()
    success = scheduler.delete_schedule(user_id, schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="日程不存在")
    
    logger.info(f"API: 删除日程 - 用户：{user_id}, ID: {schedule_id}")
    return {"success": True, "message": "日程已删除"}


@router.get("/{schedule_id}/conflict", summary="检查日程冲突")
async def check_conflict(schedule_id: str, user_id: str = "default"):
    """检查日程是否与现有日程冲突"""
    scheduler = get_scheduler()
    schedule = scheduler.get_schedule(user_id, schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="日程不存在")
    
    conflicts = scheduler.check_conflict(
        user_id,
        schedule.start_time,
        schedule.end_time or schedule.start_time,
        exclude_id=schedule_id
    )
    
    return {
        "has_conflict": len(conflicts) > 0,
        "conflicts": conflicts
    }


@router.get("/stats", summary="获取日程统计")
async def get_stats(user_id: str = "default"):
    """获取用户日程统计信息"""
    scheduler = get_scheduler()
    stats = scheduler.get_stats(user_id)
    return stats


@router.get("/upcoming", response_model=List[ScheduleItem], summary="获取即将到来的日程")
async def get_upcoming(user_id: str = "default", hours: int = 24):
    """获取指定时间范围内的即将到来日程"""
    scheduler = get_scheduler()
    schedules = scheduler.get_upcoming_schedules(user_id, hours)
    return schedules
