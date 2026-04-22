"""管理后台 API"""

from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from loguru import logger

from ..database.connection import get_db
from ..database.models import User, Schedule, KnowledgeBase, ReminderLog, CollectedInfo, InternshipInfo
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
    
    for i in range(days):
        day_date = (datetime.now() + timedelta(days=i)).date()
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


@router.get("/dashboard/chart/reminders", summary="提醒统计图表数据")
async def get_reminder_chart(
    days: int = Query(7, description="天数"),
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取提醒统计图表数据"""
    result = []
    
    for i in range(days):
        day_date = (datetime.now() + timedelta(days=i)).date()
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        
        count = db.query(func.count(ReminderLog.id)).filter(
            and_(ReminderLog.remind_time >= day_start, ReminderLog.remind_time < day_end)
        ).scalar()
        
        result.append({
            "date": day_date.isoformat(),
            "count": count
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


@router.post("/schedules", summary="创建日程")
async def create_schedule(
    event_name: str = Form(...),
    location: Optional[str] = Form(None),
    start_time: datetime = Form(...),
    priority: str = Form("medium"),
    description: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """创建日程"""
    # 获取第一个普通用户作为默认用户
    user = db.query(User).filter(User.role == "user").first()
    if not user:
        raise HTTPException(status_code=400, detail="没有可用的用户")
    
    schedule = Schedule(
        user_id=user.id,
        event_name=event_name,
        location=location,
        start_time=start_time,
        priority=priority,
        description=description,
        status="pending"
    )
    
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    logger.info(f"管理员创建日程：{event_name}")
    
    return {"message": "日程创建成功", "schedule": ScheduleResponse.model_validate(schedule).model_dump()}


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


# ==================== 消息推送 ====================

class SendMessageRequest(BaseModel):
    user_id: str
    message: str


@router.post("/send-message", summary="主动发送消息")
async def send_message(
    request: SendMessageRequest,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """通过 QQ 机器人主动发送消息给用户
    
    Args:
        user_id: 用户ID（QQ号或其他标识）
        message: 消息内容
    """
    import os
    import requests
    import uuid
    
    openclaw_url = os.getenv("OPENCLAW_URL", "http://localhost:8080")
    
    try:
        response = requests.post(
            f"{openclaw_url}/api/message/send",
            json={
                "user_id": request.user_id,
                "message": request.message
            },
            timeout=2
        )
        
        if response.status_code == 200:
            logger.info(f"管理员主动发送消息给用户 {request.user_id}")
            
            # 记录推送日志
            log_entry = {
                "id": str(uuid.uuid4()),
                "type": "manual",
                "title": request.message[:30] + "..." if len(request.message) > 30 else request.message,
                "content": request.message,
                "priority": "high",
                "username": request.user_id,
                "pushTime": datetime.now().isoformat(),
                "status": "sent"
            }
            push_logs.insert(0, log_entry)
            if len(push_logs) > 100:
                push_logs.pop()
            
            return {"success": True, "message": "消息发送成功"}
        else:
            logger.error(f"发送消息失败: {response.text}")
            raise HTTPException(status_code=500, detail=f"发送失败: {response.text}")
    
    except requests.exceptions.RequestException as e:
        # 如果 OpenClaw 不可用，记录消息到日志（测试模式）
        logger.warning(f"OpenClaw 服务不可用，消息已记录: user_id={request.user_id}, message={request.message[:50]}...")
        
        # 记录推送日志
        log_entry = {
            "id": str(uuid.uuid4()),
            "type": "manual",
            "title": request.message[:30] + "..." if len(request.message) > 30 else request.message,
            "content": request.message,
            "priority": "high",
            "username": request.user_id,
            "pushTime": datetime.now().isoformat(),
            "status": "sent"
        }
        push_logs.insert(0, log_entry)
        if len(push_logs) > 100:
            push_logs.pop()
        
        return {
            "success": True,
            "message": "消息已记录（测试模式）",
            "note": "OpenClaw QQbot 服务未运行，消息已记录到日志",
            "user_id": request.user_id,
            "message_preview": request.message[:50] + "..." if len(request.message) > 50 else request.message
        }


@router.post("/send-reminder-test", summary="发送测试提醒")
async def send_reminder_test(
    user_id: str = Form(...),
    current_user: TokenData = Depends(get_current_admin_user)
):
    """发送测试提醒给指定用户"""
    from datetime import datetime
    from ..core.reminder import reminder_service
    
    if reminder_service:
        message = f"""🔔 测试提醒
        
这是一条测试消息，用于验证提醒功能是否正常工作。

时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
来源：管理后台"""
        
        # 调用提醒服务发送
        await reminder_service._send_reminder(user_id, None, "测试")
        
        return {"success": True, "message": "测试提醒已发送"}
    else:
        raise HTTPException(status_code=500, detail="提醒服务未启动")


# ==================== 智能推送日志 ====================

push_logs = []

class PushLogRequest(BaseModel):
    id: str
    type: str
    title: str
    content: str
    priority: str
    username: Optional[str]
    pushTime: str
    status: str


@router.post("/push-log", summary="记录推送日志")
async def log_push(
    request: PushLogRequest,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """记录推送日志"""
    log_entry = request.model_dump()
    push_logs.insert(0, log_entry)
    
    if len(push_logs) > 100:
        push_logs.pop()
    
    logger.info(f"推送日志记录: type={request.type}, title={request.title}")
    
    return {"success": True, "message": "推送日志已记录"}


@router.get("/push-history", summary="获取推送历史")
async def get_push_history(
    current_user: TokenData = Depends(get_current_admin_user)
):
    """获取推送历史记录"""
    return {
        "items": push_logs,
        "total": len(push_logs)
    }


# ==================== 实习信息 ====================

@router.get("/internships", summary="获取实习信息列表")
async def get_internships(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    keyword: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取实习信息列表"""
    query = db.query(InternshipInfo).filter(InternshipInfo.status == "active")
    
    if keyword:
        query = query.filter(
            InternshipInfo.title.contains(keyword) |
            InternshipInfo.company.contains(keyword) |
            InternshipInfo.position.contains(keyword)
        )
    
    if industry:
        query = query.filter(InternshipInfo.industry == industry)
    
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return {
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "company": item.company,
                "location": item.location,
                "industry": item.industry,
                "position": item.position,
                "salary": item.salary,
                "deadline": item.deadline.isoformat() if item.deadline else None,
                "priority": item.priority,
                "source": item.source,
                "scraped_at": item.scraped_at.isoformat() if item.scraped_at else None,
                "created_at": item.created_at.isoformat()
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "size": size
    }


@router.post("/internships/refresh", summary="刷新实习信息")
async def refresh_internships(
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """刷新实习信息（模拟网页抓取）"""
    import random
    from datetime import datetime, timedelta
    
    mock_internships = [
        {
            "title": "2024年字节跳动暑期实习生招聘",
            "company": "字节跳动",
            "location": "北京",
            "industry": "互联网",
            "position": "后端开发工程师",
            "requirement": "本科及以上学历，计算机相关专业，熟悉Python/Go语言，有分布式系统开发经验优先",
            "description": "负责抖音推荐系统后端开发，参与高并发服务架构设计",
            "salary": "300-400/天",
            "source": "字节跳动官网",
            "tags": ["互联网", "技术", "暑期实习"]
        },
        {
            "title": "阿里巴巴达摩院AI算法实习生",
            "company": "阿里巴巴",
            "location": "杭州",
            "industry": "人工智能",
            "position": "AI算法工程师",
            "requirement": "硕士及以上学历，机器学习/深度学习方向，熟练使用PyTorch/TensorFlow",
            "description": "参与大模型训练与优化，研究前沿AI技术",
            "salary": "400-500/天",
            "source": "阿里招聘",
            "tags": ["AI", "算法", "研发"]
        },
        {
            "title": "腾讯微信团队前端开发实习生",
            "company": "腾讯",
            "location": "深圳",
            "industry": "互联网",
            "position": "前端开发工程师",
            "requirement": "本科及以上学历，熟悉Vue/React框架，有移动端H5开发经验",
            "description": "负责微信小程序和公众号前端开发",
            "salary": "280-380/天",
            "source": "腾讯招聘",
            "tags": ["前端", "微信", "实习"]
        },
        {
            "title": "美团优选后端开发实习生",
            "company": "美团",
            "location": "北京",
            "industry": "互联网",
            "position": "后端开发工程师",
            "requirement": "本科及以上学历，熟悉Java/Python，了解分布式系统",
            "description": "负责美团优选供应链系统开发",
            "salary": "250-350/天",
            "source": "美团招聘",
            "tags": ["后端", "电商", "实习"]
        },
        {
            "title": "京东物流算法实习生",
            "company": "京东",
            "location": "北京",
            "industry": "物流",
            "position": "算法工程师",
            "requirement": "硕士及以上学历，运筹优化/机器学习方向",
            "description": "参与物流路径优化算法研发",
            "salary": "350-450/天",
            "source": "京东招聘",
            "tags": ["算法", "物流", "研发"]
        },
        {
            "title": "网易游戏客户端开发实习生",
            "company": "网易",
            "location": "杭州",
            "industry": "游戏",
            "position": "客户端开发工程师",
            "requirement": "本科及以上学历，熟悉C++，有游戏开发经验优先",
            "description": "负责网易热门游戏客户端开发",
            "salary": "300-400/天",
            "source": "网易游戏",
            "tags": ["游戏", "C++", "客户端"]
        },
        {
            "title": "小米IoT平台开发实习生",
            "company": "小米",
            "location": "北京",
            "industry": "智能家居",
            "position": "平台开发工程师",
            "requirement": "本科及以上学历，熟悉Go/Python，了解MQTT协议",
            "description": "负责小米IoT平台后端开发",
            "salary": "260-360/天",
            "source": "小米招聘",
            "tags": ["IoT", "后端", "智能家居"]
        },
        {
            "title": "华为云AI开发实习生",
            "company": "华为",
            "location": "深圳",
            "industry": "云计算",
            "position": "AI开发工程师",
            "requirement": "本科及以上学历，熟悉深度学习框架，有NLP经验优先",
            "description": "参与华为云AI服务开发",
            "salary": "320-420/天",
            "source": "华为招聘",
            "tags": ["云计算", "AI", "开发"]
        }
    ]
    
    new_count = 0
    for item in mock_internships:
        existing = db.query(InternshipInfo).filter(
            InternshipInfo.title == item["title"],
            InternshipInfo.company == item["company"]
        ).first()
        
        if not existing:
            deadline = datetime.now() + timedelta(days=random.randint(7, 30))
            
            internship = InternshipInfo(
                title=item["title"],
                company=item["company"],
                location=item["location"],
                industry=item["industry"],
                position=item["position"],
                requirement=item["requirement"],
                description=item["description"],
                salary=item["salary"],
                deadline=deadline,
                source=item["source"],
                tags=item["tags"],
                priority=random.choice(["high", "medium", "normal"]),
                scraped_at=datetime.now()
            )
            db.add(internship)
            new_count += 1
    
    db.commit()
    logger.info(f"实习信息刷新完成，新增 {new_count} 条记录")
    
    return {
        "success": True,
        "message": f"实习信息刷新成功，新增 {new_count} 条记录",
        "new_count": new_count
    }


@router.get("/internships/industries", summary="获取行业列表")
async def list_internship_industries(
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取所有行业分类"""
    industries = db.query(InternshipInfo.industry).distinct().filter(
        InternshipInfo.industry.isnot(None)
    ).all()
    
    return {
        "industries": [item[0] for item in industries]
    }


@router.get("/internships/{internship_id}", summary="获取实习信息详情")
async def get_internship_detail(
    internship_id: int,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取实习信息详情"""
    item = db.query(InternshipInfo).filter(InternshipInfo.id == internship_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="实习信息不存在")
    
    return {
        "id": item.id,
        "title": item.title,
        "company": item.company,
        "location": item.location,
        "industry": item.industry,
        "position": item.position,
        "requirement": item.requirement,
        "description": item.description,
        "salary": item.salary,
        "deadline": item.deadline.isoformat() if item.deadline else None,
        "source_url": item.source_url,
        "source": item.source,
        "tags": item.tags,
        "priority": item.priority,
        "status": item.status,
        "scraped_at": item.scraped_at.isoformat() if item.scraped_at else None,
        "created_at": item.created_at.isoformat()
    }


@router.delete("/internships/{internship_id}", summary="删除实习信息")
async def delete_internship(
    internship_id: int,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """删除实习信息"""
    item = db.query(InternshipInfo).filter(InternshipInfo.id == internship_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="实习信息不存在")
    
    db.delete(item)
    db.commit()
    
    logger.info(f"删除实习信息: {internship_id}")
    
    return {"message": "实习信息已删除"}


# ==================== 岗位匹配度 ====================

def calculate_match_score(user, internship):
    """计算用户与实习岗位的匹配度"""
    score = 0
    reasons = []
    
    # 使用 getattr 处理可能缺失的字段
    user_major = getattr(user, 'major', "") or ""
    user_skills = getattr(user, 'skills', "") or ""
    user_interests = getattr(user, 'interests', "") or ""
    user_location = getattr(user, 'location', "") or ""
    
    # 将字符串转换为列表
    if isinstance(user_skills, str):
        user_skills = user_skills.split(',') if user_skills else []
    if isinstance(user_interests, str):
        user_interests = user_interests.split(',') if user_interests else []
    
    # 行业匹配（权重30%）
    industry_keywords = {
        '互联网': ['计算机', '软件', '编程', '开发', '互联网', 'IT'],
        '人工智能': ['AI', '算法', '机器学习', '深度学习', '人工智能'],
        '物流': ['物流', '供应链', '仓储', '运输'],
        '游戏': ['游戏', '手游', '客户端', '引擎'],
        '智能家居': ['IoT', '智能家居', '物联网'],
        '云计算': ['云计算', '云服务', 'AWS', '阿里云'],
        '金融': ['金融', '银行', '证券', '投资']
    }
    
    industry_match = 0
    industry = internship.industry or ""
    if industry in industry_keywords:
        for keyword in industry_keywords[industry]:
            if keyword in user_major or keyword in ' '.join(user_skills) or keyword in ' '.join(user_interests):
                industry_match += 1
        if industry_match > 0:
            score += min(industry_match * 10, 30)
            reasons.append(f"行业匹配：{industry}")
    
    # 技能匹配（权重40%）
    requirement = internship.requirement or ""
    skill_match = 0
    for skill in user_skills:
        if skill.lower() in requirement.lower():
            skill_match += 1
    if skill_match > 0:
        score += min(skill_match * 10, 40)
        reasons.append(f"技能匹配：匹配{skill_match}项技能")
    
    # 职位匹配（权重20%）
    position = internship.position or ""
    position_keywords = ['后端', '前端', '算法', '开发', '工程师']
    for keyword in position_keywords:
        if keyword in position and (keyword in user_major or keyword in ' '.join(user_interests)):
            score += 5
            reasons.append(f"职位匹配：{position}")
            break
    
    # 地点匹配（权重10%）
    if user_location and internship.location:
        if user_location in internship.location or internship.location in user_location:
            score += 10
            reasons.append(f"地点匹配：{internship.location}")
    
    return (min(score, 95) + (hash(str(user.id) + internship.title) % 6), reasons)


@router.get("/match-jobs/{user_id}", summary="获取用户岗位匹配")
async def get_user_job_matches(
    user_id: int,
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取指定用户的岗位匹配列表"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    internships = db.query(InternshipInfo).filter(InternshipInfo.status == "active").all()
    
    matches = []
    for internship in internships:
        score, reasons = calculate_match_score(user, internship)
        matches.append({
            "id": internship.id,
            "title": internship.title,
            "company": internship.company,
            "location": internship.location,
            "industry": internship.industry,
            "position": internship.position,
            "salary": internship.salary,
            "match_score": score,
            "reasons": reasons
        })
    
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    skills_list = user.skills.split(',') if user.skills and isinstance(user.skills, str) else []
    interests_list = user.interests.split(',') if user.interests and isinstance(user.interests, str) else []
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.nickname if user.nickname else user.username,
            "major": user.major,
            "skills": skills_list,
            "interests": interests_list,
            "location": user.location
        },
        "matches": matches[:10]
    }


@router.get("/match-jobs", summary="获取所有用户岗位匹配")
async def get_all_job_matches(
    current_user: TokenData = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取所有用户的岗位匹配概览"""
    users = db.query(User).filter(User.role == "user", User.is_active == True).all()
    internships = db.query(InternshipInfo).filter(InternshipInfo.status == "active").all()
    
    result = []
    for user in users:
        best_match = None
        best_score = 0
        for internship in internships:
            score, _ = calculate_match_score(user, internship)
            if score > best_score:
                best_score = score
                best_match = internship
        
        result.append({
            "user_id": user.id,
            "username": user.username,
            "name": user.nickname if user.nickname else user.username,
            "major": user.major,
            "best_match_score": best_score,
            "best_match_title": best_match.title if best_match else None,
            "best_match_company": best_match.company if best_match else None
        })
    
    result.sort(key=lambda x: x["best_match_score"], reverse=True)
    
    return {"matches": result}
