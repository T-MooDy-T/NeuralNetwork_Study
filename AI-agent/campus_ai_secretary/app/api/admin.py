"""管理后台 API"""

from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from loguru import logger

from ..database.connection import get_db
from ..database.models import User, Schedule, KnowledgeBase, ReminderLog, CollectedInfo
from ..core.auth import get_current_admin_user, TokenData

router = APIRouter(prefix="/admin", tags=["管理后台"])


# ==================== 仪表盘统计 ====================

@router.get("/dashboard/stats", summary="仪表盘统计")
async def get_dashboard_stats(
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取仪表盘统计数据"""
    
    # 用户统计
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    
    # 日程统计
    total_schedules = db.query(func.count(Schedule.id)).scalar()
    pending_schedules = db.query(func.count(Schedule.id)).filter(Schedule.status == "pending").scalar()
    completed_schedules = db.query(func.count(Schedule.id)).filter(Schedule.status == "completed").scalar()
    
    # 今日日程
    today_start = datetime.now().replace(hour=0, minute=0, second=0)
    today_end = today_start + timedelta(days=1)
    today_schedules = db.query(func.count(Schedule.id)).filter(
        and_(Schedule.start_time >= today_start, Schedule.start_time < today_end)
    ).scalar()
    
    # 提醒统计
    total_reminders = db.query(func.count(ReminderLog.id)).scalar()
    today_reminders = db.query(func.count(ReminderLog.id)).filter(
        ReminderLog.sent_at >= today_start
    ).scalar()
    
    # 知识库统计
    total_kb = db.query(func.count(KnowledgeBase.id)).scalar()
    active_kb = db.query(func.count(KnowledgeBase.id)).filter(KnowledgeBase.is_active == True).scalar()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users
        },
        "schedules": {
            "total": total_schedules,
            "pending": pending_schedules,
            "completed": completed_schedules,
            "today": today_schedules
        },
        "reminders": {
            "total": total_reminders,
            "today": today_reminders
        },
        "knowledge_base": {
            "total": total_kb,
            "active": active_kb
        }
    }


@router.get("/dashboard/chart/users", summary="用户增长图表数据")
async def get_user_chart(
    days: int = Query(7, description="天数"),
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取用户增长图表数据"""
    result = []
    
    for i in range(days - 1, -1, -1):
        day_date = (datetime.now() - timedelta(days=i)).date()
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        
        count = db.query(func.count(User.id)).filter(
            and_(User.created_at >= day_start, User.created_at < day_end)
        ).scalar()
        
        result.append({
            "date": day_date.isoformat(),
            "count": count
        })
    
    return {"data": result, "days": days}


@router.get("/dashboard/chart/schedules", summary="日程统计图表数据")
async def get_schedule_chart(
    days: int = Query(7, description="天数"),
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取日程统计图表数据"""
    result = []
    
    for i in range(days - 1, -1, -1):
        day_date = (datetime.now() - timedelta(days=i)).date()
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        
        total = db.query(func.count(Schedule.id)).filter(
            and_(Schedule.start_time >= day_start, Schedule.start_time < day_end)
        ).scalar()
        
        completed = db.query(func.count(Schedule.id)).filter(
            and_(Schedule.start_time >= day_start, Schedule.start_time < day_end),
            Schedule.status == "completed"
        ).scalar()
        
        result.append({
            "date": day_date.isoformat(),
            "total": total,
            "completed": completed
        })
    
    return {"data": result, "days": days}


# ==================== 用户管理 ====================

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    nickname: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    schedule_count: int = 0

    class Config:
        from_attributes = True


@router.get("/users", summary="用户列表")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    role: Optional[str] = None,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User)
    
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) |
            (User.nickname.contains(keyword)) |
            (User.email.contains(keyword))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # 添加日程数量
    user_list = []
    for user in users:
        schedule_count = db.query(func.count(Schedule.id)).filter(Schedule.user_id == user.id).scalar()
        user_dict = UserResponse.model_validate(user).model_dump()
        user_dict["schedule_count"] = schedule_count
        user_list.append(user_dict)
    
    return {
        "items": user_list,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/users/{user_id}", summary="用户详情")
async def get_user(
    user_id: int,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}/toggle", summary="切换用户状态")
async def toggle_user_status(
    user_id: int,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """切换用户启用/禁用状态"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.is_active = not user.is_active
    db.commit()
    
    logger.info(f"用户状态切换：{user.username} -> {'启用' if user.is_active else '禁用'}")
    
    return {"message": f"用户已{'启用' if user.is_active else '禁用'}"}


# ==================== 日程管理 ====================

class ScheduleResponse(BaseModel):
    id: int
    user_id: int
    event_name: str
    start_time: datetime
    end_time: Optional[datetime]
    location: Optional[str]
    priority: str
    status: str
    created_at: datetime
    username: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/schedules", summary="日程列表")
async def list_schedules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取日程列表"""
    query = db.query(Schedule, User.username).join(User, isouter=True)
    
    if status:
        query = query.filter(Schedule.status == status)
    
    if priority:
        query = query.filter(Schedule.priority == priority)
    
    if start_date:
        query = query.filter(Schedule.start_time >= datetime.fromisoformat(start_date))
    
    if end_date:
        query = query.filter(Schedule.start_time <= datetime.fromisoformat(end_date))
    
    total = query.count()
    results = query.order_by(Schedule.start_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    items = []
    for schedule, username in results:
        item = ScheduleResponse.model_validate(schedule).model_dump()
        item["username"] = username
        items.append(item)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.delete("/schedules/{schedule_id}", summary="删除日程")
async def delete_schedule(
    schedule_id: int,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """删除日程"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="日程不存在")
    
    db.delete(schedule)
    db.commit()
    
    logger.info(f"管理员删除日程：{schedule_id}")
    
    return {"message": "日程已删除"}


# ==================== 知识库管理 ====================

class KnowledgeBaseResponse(BaseModel):
    id: int
    title: Optional[str]
    content: str
    source_type: str
    category: Optional[str]
    is_active: bool
    view_count: int
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/knowledge", summary="知识库列表")
async def list_knowledge(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    source_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取知识库列表"""
    query = db.query(KnowledgeBase)
    
    if category:
        query = query.filter(KnowledgeBase.category == category)
    
    if source_type:
        query = query.filter(KnowledgeBase.source_type == source_type)
    
    if is_active is not None:
        query = query.filter(KnowledgeBase.is_active == is_active)
    
    total = query.count()
    items = query.order_by(KnowledgeBase.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


class KnowledgeBaseCreate(BaseModel):
    title: Optional[str] = None
    content: str
    source_type: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None


@router.post("/knowledge", summary="添加知识库")
async def add_knowledge(
    request: Request,
    title: Optional[str] = Form(None),
    content: str = Form(None),
    source_type: str = Form("其他"),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """添加知识库文档"""
    import json
    
    try:
        body = await request.json()
        title = body.get('title') or title
        content = body.get('content') or content
        source_type = body.get('source_type') or source_type
        category = body.get('category') or category
        tags = body.get('tags') or tags
    except:
        pass
    
    if not content:
        raise HTTPException(status_code=400, detail="内容不能为空")
    
    # 根据用户名获取实际用户ID
    user = db.query(User).filter(User.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    kb = KnowledgeBase(
        title=title,
        content=content,
        source_type=source_type,
        category=category,
        tags=json.loads(tags) if isinstance(tags, str) else (tags or []),
        is_active=True,
        created_by=user.id
    )
    
    db.add(kb)
    db.commit()
    db.refresh(kb)
    
    logger.info(f"管理员添加知识库：{title or '无标题'}")
    
    return {"message": "添加成功", "id": kb.id}


@router.delete("/knowledge/{kb_id}", summary="删除知识库")
async def delete_knowledge(
    kb_id: int,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """删除知识库文档"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    db.delete(kb)
    db.commit()
    
    logger.info(f"管理员删除知识库：{kb_id}")
    
    return {"message": "知识库已删除"}


# ==================== 提醒日志 ====================

@router.get("/reminders", summary="提醒日志列表")
async def list_reminders(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取提醒日志列表"""
    query = db.query(ReminderLog, User.username).join(User, isouter=True)
    
    if status:
        query = query.filter(ReminderLog.status == status)
    
    total = query.count()
    results = query.order_by(ReminderLog.sent_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    items = []
    for log, username in results:
        item = {
            "id": log.id,
            "user_id": log.user_id,
            "username": username,
            "schedule_id": log.schedule_id,
            "event_name": log.event_name,
            "remind_time": log.remind_time,
            "offset": log.offset,
            "status": log.status,
            "sent_at": log.sent_at
        }
        items.append(item)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


# ==================== 采集信息管理 ====================

@router.get("/collected-info", summary="采集信息列表")
async def list_collected_info(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    query = db.query(CollectedInfo)
    
    if source_type:
        query = query.filter(CollectedInfo.source_type == source_type)
    
    if priority:
        query = query.filter(CollectedInfo.priority == priority)
    
    if status:
        query = query.filter(CollectedInfo.status == status)
    
    total = query.count()
    items = query.order_by(CollectedInfo.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for item in items:
        result.append({
            "id": item.id,
            "user_id": item.user_id,
            "source": item.source,
            "source_type": item.source_type,
            "sender": item.sender,
            "content": item.content,
            "url": item.url,
            "category": item.category,
            "priority": item.priority,
            "tags": item.tags,
            "status": item.status,
            "timestamp": item.timestamp,
            "created_at": item.created_at
        })
    
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.put("/collected-info/{info_id}/status", summary="更新采集信息状态")
async def update_collected_info_status(
    info_id: int,
    status: str = Form(...),
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    info = db.query(CollectedInfo).filter(CollectedInfo.id == info_id).first()
    if not info:
        raise HTTPException(status_code=404, detail="采集信息不存在")
    
    info.status = status
    db.commit()
    
    return {"message": "状态更新成功"}


@router.delete("/collected-info/{info_id}", summary="删除采集信息")
async def delete_collected_info(
    info_id: int,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    info = db.query(CollectedInfo).filter(CollectedInfo.id == info_id).first()
    if not info:
        raise HTTPException(status_code=404, detail="采集信息不存在")
    
    db.delete(info)
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/collected-info/stats", summary="采集信息统计")
async def get_collected_info_stats(
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    total = db.query(func.count(CollectedInfo.id)).scalar()
    unread = db.query(func.count(CollectedInfo.id)).filter(CollectedInfo.status == "unread").scalar()
    
    by_source = db.query(
        CollectedInfo.source_type,
        func.count(CollectedInfo.id)
    ).group_by(CollectedInfo.source_type).all()
    
    by_priority = db.query(
        CollectedInfo.priority,
        func.count(CollectedInfo.id)
    ).group_by(CollectedInfo.priority).all()
    
    return {
        "total": total,
        "unread": unread,
        "by_source": {k: v for k, v in by_source},
        "by_priority": {k: v for k, v in by_priority}
    }


# ==================== 系统设置 ====================

@router.get("/system/info", summary="系统信息")
async def get_system_info(
    current_user: TokenData = Depends(get_current_admin_user)
):
    """获取系统信息"""
    import platform
    import os
    
    return {
        "version": "1.0.0",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "debug": os.getenv("DEBUG", "false"),
        "database": "MySQL" if "mysql" in os.getenv("DATABASE_URL", "") else "SQLite"
    }
