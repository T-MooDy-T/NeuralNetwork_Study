"""数据库模型定义"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from .connection import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True)
    nickname = Column(String(50))
    avatar = Column(String(255))
    role = Column(String(20), default="user")  # admin, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime)
    
    # 岗位匹配相关字段
    major = Column(String(100))  # 专业
    skills = Column(String(500))  # 技能，逗号分隔
    interests = Column(String(500))  # 兴趣爱好，逗号分隔
    location = Column(String(100))  # 地点/城市
    
    # 关联
    schedules = relationship("Schedule", back_populates="user")
    reminder_logs = relationship("ReminderLog", back_populates="user")


class Schedule(Base):
    """日程表"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    event_name = Column(String(200), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    location = Column(String(200))
    source = Column(String(100), default="user")
    priority = Column(String(20), default="medium")  # high, medium, low
    description = Column(Text)
    remind_times = Column(JSON)  # ["1d", "3h"]
    status = Column(String(20), default="pending")  # pending, completed, cancelled
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    user = relationship("User", back_populates="schedules")


class KnowledgeBase(Base):
    """知识库表"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text, nullable=False)
    source_type = Column(String(50))  # 教务通知、校园设施、社团公告
    source_url = Column(String(500))
    category = Column(String(50))
    tags = Column(JSON)  # ["图书馆", "开放时间"]
    priority = Column(String(20), default="medium")
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    is_active = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(Integer, ForeignKey("users.id"))


class ReminderLog(Base):
    """提醒日志表"""
    __tablename__ = "reminder_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    remind_time = Column(DateTime, nullable=False)
    event_time = Column(DateTime)
    event_name = Column(String(200))
    offset = Column(String(20))  # 1d, 3h
    status = Column(String(20), default="sent")  # sent, failed, skipped
    message = Column(Text)
    sent_at = Column(DateTime, default=datetime.now)
    
    # 关联
    user = relationship("User", back_populates="reminder_logs")


class CollectedInfo(Base):
    """采集信息表"""
    __tablename__ = "collected_info"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    source = Column(String(100), index=True)  # 来源名称
    source_type = Column(String(50), index=True)  # qq_group, wechat_chat, wechat_official
    sender = Column(String(100))  # 发送者
    content = Column(Text)  # 内容
    url = Column(String(500))  # 链接
    category = Column(String(50))  # 分类
    priority = Column(String(20), default="normal")  # high, medium, normal
    tags = Column(JSON)  # 标签列表
    status = Column(String(20), default="unread")  # unread, read, processed
    raw_data = Column(JSON)  # 原始数据
    timestamp = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联
    user = relationship("User")


class InternshipInfo(Base):
    """实习信息表"""
    __tablename__ = "internship_info"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    company = Column(String(100))
    location = Column(String(100))
    industry = Column(String(100))
    position = Column(String(100))
    requirement = Column(Text)
    description = Column(Text)
    salary = Column(String(50))
    deadline = Column(DateTime)
    source_url = Column(String(500))
    source = Column(String(100))  # 来源网站
    tags = Column(JSON)  # ["互联网", "技术", "全职"]
    priority = Column(String(20), default="normal")  # high, medium, normal
    status = Column(String(20), default="active")  # active, expired
    scraped_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)


class SystemStats(Base):
    """系统统计表"""
    __tablename__ = "system_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    stat_date = Column(Date, index=True)
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    total_schedules = Column(Integer, default=0)
    completed_schedules = Column(Integer, default=0)
    total_reminders = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
