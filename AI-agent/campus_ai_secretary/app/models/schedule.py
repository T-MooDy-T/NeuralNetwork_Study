"""日程数据模型"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ScheduleItem(BaseModel):
    """日程实体"""
    id: str = Field(description="日程唯一标识")
    user_id: str = Field(description="用户ID")
    event_name: str = Field(description="事件名称")
    start_time: datetime = Field(description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    location: Optional[str] = Field(None, description="地点")
    source: str = Field(default="user", description="信息来源")
    priority: Priority = Field(default=Priority.MEDIUM, description="优先级")
    description: Optional[str] = Field(None, description="详细描述")
    remind_times: List[str] = Field(default_factory=lambda: ["1d", "3h"], description="提醒时间点")
    status: str = Field(default="pending", description="状态: pending/completed/cancelled")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        use_enum_values = True


class ScheduleCreate(BaseModel):
    """创建日程请求"""
    event_name: str = Field(description="事件名称")
    start_time: str = Field(description="开始时间（支持自然语言）")
    end_time: Optional[str] = Field(None, description="结束时间")
    location: Optional[str] = Field(None, description="地点")
    source: Optional[str] = Field("user", description="信息来源")
    priority: Optional[str] = Field("medium", description="优先级")
    description: Optional[str] = Field(None, description="详细描述")
    remind_times: Optional[List[str]] = Field(None, description="自定义提醒时间")


class ScheduleUpdate(BaseModel):
    """更新日程请求"""
    event_name: Optional[str] = Field(None, description="事件名称")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    location: Optional[str] = Field(None, description="地点")
    priority: Optional[str] = Field(None, description="优先级")
    description: Optional[str] = Field(None, description="详细描述")
    status: Optional[str] = Field(None, description="状态")


class ScheduleQuery(BaseModel):
    """日程查询请求"""
    user_id: str = Field(description="用户ID")
    start_date: Optional[str] = Field(None, description="查询开始日期")
    end_date: Optional[str] = Field(None, description="查询结束日期")
    priority: Optional[str] = Field(None, description="优先级筛选")
    status: Optional[str] = Field(None, description="状态筛选")


class ParseResult(BaseModel):
    """解析结果"""
    success: bool = Field(description="是否成功解析")
    event_name: Optional[str] = Field(None, description="事件名称")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    location: Optional[str] = Field(None, description="地点")
    priority: Optional[Priority] = Field(None, description="优先级")
    description: Optional[str] = Field(None, description="原始描述")
    confidence: float = Field(default=0.0, description="置信度")
    missing_fields: List[str] = Field(default_factory=list, description="缺失字段")
    raw_content: str = Field(description="原始内容")


class QARequest(BaseModel):
    """智能问答请求"""
    question: str = Field(description="用户问题")
    user_id: str = Field(description="用户ID")
    context: Optional[str] = Field(None, description="上下文信息")


class QAResponse(BaseModel):
    """智能问答响应"""
    answer: str = Field(description="回答内容")
    sources: List[dict] = Field(default_factory=list, description="知识库来源")
    confidence: float = Field(description="置信度")
    can_create_schedule: bool = Field(default=False, description="是否可创建日程")
    suggested_schedule: Optional[ScheduleCreate] = Field(None, description="建议的日程")