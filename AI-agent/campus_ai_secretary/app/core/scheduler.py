"""日程管理器

负责日程的 CRUD 操作、冲突检测、查询等
"""

import os
import uuid
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis 未安装，日程管理将使用内存模式")

from ..models.schedule import ScheduleItem, ScheduleCreate, ScheduleUpdate, Priority
from ..utils.time_utils import parse_time


class ScheduleManager:
    """日程管理器"""
    
    def __init__(self, use_memory: bool = True):
        """初始化日程管理器
        
        Args:
            use_memory: 是否使用内存模式（本地测试）
        """
        self.use_memory = use_memory
        self.memory_store: Dict[str, ScheduleItem] = {}
        self.user_schedules: Dict[str, List[str]] = {}  # user_id -> [schedule_ids]
        
        if REDIS_AVAILABLE and not use_memory:
            self._init_redis()
        else:
            logger.info("ScheduleManager 使用内存模式")
            self.redis = None
    
    def _init_redis(self):
        """初始化 Redis 连接"""
        try:
            self.redis = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True
            )
            self.redis.ping()
            logger.info("Redis 连接成功")
        except Exception as e:
            logger.warning(f"Redis 连接失败，切换到内存模式：{e}")
            self.redis = None
            self.use_memory = True
    
    def create_schedule(self, user_id: str, data: ScheduleCreate) -> ScheduleItem:
        """创建日程
        
        Args:
            user_id: 用户 ID
            data: 创建请求数据
        
        Returns:
            创建的日程对象
        """
        schedule_id = str(uuid.uuid4())
        
        # 解析时间
        start_time = parse_time(data.start_time)
        if not start_time:
            start_time = datetime.now() + timedelta(days=1)
        
        end_time = None
        if data.end_time:
            end_time = parse_time(data.end_time)
        
        # 解析优先级
        priority = Priority(data.priority) if data.priority else Priority.MEDIUM
        
        # 创建日程对象
        schedule = ScheduleItem(
            id=schedule_id,
            user_id=user_id,
            event_name=data.event_name,
            start_time=start_time,
            end_time=end_time,
            location=data.location,
            source=data.source or "user",
            priority=priority,
            description=data.description,
            remind_times=data.remind_times or ["1d", "3h"],
            status="pending"
        )
        
        # 存储
        if self.redis:
            key = f"schedule:{user_id}:{schedule_id}"
            self.redis.set(key, schedule.model_dump_json())
            
            # 更新用户日程列表
            user_key = f"user:{user_id}:schedules"
            self.redis.sadd(user_key, schedule_id)
        else:
            self.memory_store[schedule_id] = schedule
            if user_id not in self.user_schedules:
                self.user_schedules[user_id] = []
            self.user_schedules[user_id].append(schedule_id)
        
        logger.info(f"创建日程：{schedule_id[:8]}... 用户：{user_id} 事件：{data.event_name}")
        return schedule
    
    def get_schedule(self, user_id: str, schedule_id: str) -> Optional[ScheduleItem]:
        """获取单个日程
        
        Args:
            user_id: 用户 ID
            schedule_id: 日程 ID
        
        Returns:
            日程对象，不存在返回 None
        """
        if self.redis:
            key = f"schedule:{user_id}:{schedule_id}"
            data = self.redis.get(key)
            if data:
                return ScheduleItem.model_validate_json(data)
            return None
        else:
            schedule = self.memory_store.get(schedule_id)
            if schedule and schedule.user_id == user_id:
                return schedule
            return None
    
    def list_schedules(self, 
                       user_id: str,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       priority: Optional[Priority] = None,
                       status: Optional[str] = None) -> List[ScheduleItem]:
        """获取用户日程列表
        
        Args:
            user_id: 用户 ID
            start_date: 开始日期过滤
            end_date: 结束日期过滤
            priority: 优先级过滤
            status: 状态过滤
        
        Returns:
            日程列表
        """
        if self.redis:
            user_key = f"user:{user_id}:schedules"
            schedule_ids = self.redis.smembers(user_key)
            
            schedules = []
            for schedule_id in schedule_ids:
                schedule = self.get_schedule(user_id, schedule_id)
                if schedule:
                    # 过滤
                    if start_date and schedule.start_time < start_date:
                        continue
                    if end_date and schedule.start_time > end_date:
                        continue
                    if priority and schedule.priority != priority.value:
                        continue
                    if status and schedule.status != status:
                        continue
                    schedules.append(schedule)
        else:
            user_schedule_ids = self.user_schedules.get(user_id, [])
            schedules = []
            for schedule_id in user_schedule_ids:
                schedule = self.memory_store.get(schedule_id)
                if schedule:
                    # 过滤
                    if start_date and schedule.start_time < start_date:
                        continue
                    if end_date and schedule.start_time > end_date:
                        continue
                    if priority and schedule.priority != priority:
                        continue
                    if status and schedule.status != status:
                        continue
                    schedules.append(schedule)
        
        # 按时间排序
        schedules.sort(key=lambda x: x.start_time)
        return schedules
    
    def update_schedule(self, 
                        user_id: str, 
                        schedule_id: str, 
                        updates: ScheduleUpdate) -> Optional[ScheduleItem]:
        """更新日程
        
        Args:
            user_id: 用户 ID
            schedule_id: 日程 ID
            updates: 更新数据
        
        Returns:
            更新后的日程，失败返回 None
        """
        schedule = self.get_schedule(user_id, schedule_id)
        if not schedule:
            return None
        
        # 应用更新
        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "start_time" and value:
                value = parse_time(value)
            elif key == "end_time" and value:
                value = parse_time(value)
            elif key == "priority" and value:
                value = Priority(value)
            
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        schedule.updated_at = datetime.now()
        
        # 保存
        if self.redis:
            key = f"schedule:{user_id}:{schedule_id}"
            self.redis.set(key, schedule.model_dump_json())
        else:
            self.memory_store[schedule_id] = schedule
        
        logger.info(f"更新日程：{schedule_id[:8]}...")
        return schedule
    
    def delete_schedule(self, user_id: str, schedule_id: str) -> bool:
        """删除日程
        
        Args:
            user_id: 用户 ID
            schedule_id: 日程 ID
        
        Returns:
            是否删除成功
        """
        if self.redis:
            key = f"schedule:{user_id}:{schedule_id}"
            result = self.redis.delete(key)
            
            if result:
                user_key = f"user:{user_id}:schedules"
                self.redis.srem(user_key, schedule_id)
            return bool(result)
        else:
            if schedule_id in self.memory_store:
                del self.memory_store[schedule_id]
                if user_id in self.user_schedules:
                    self.user_schedules[user_id].remove(schedule_id)
                return True
            return False
    
    def check_conflict(self, 
                       user_id: str, 
                       start_time: datetime, 
                       end_time: datetime,
                       exclude_id: Optional[str] = None) -> List[ScheduleItem]:
        """检查日程冲突
        
        Args:
            user_id: 用户 ID
            start_time: 开始时间
            end_time: 结束时间
            exclude_id: 排除的日程 ID（更新时使用）
        
        Returns:
            冲突的日程列表
        """
        schedules = self.list_schedules(user_id)
        conflicts = []
        
        for schedule in schedules:
            if exclude_id and schedule.id == exclude_id:
                continue
            
            # 检查时间重叠
            if schedule.start_time < end_time and schedule.start_time > start_time:
                conflicts.append(schedule)
            elif schedule.start_time <= start_time and schedule.end_time and schedule.end_time > start_time:
                conflicts.append(schedule)
        
        return conflicts
    
    def get_upcoming_schedules(self, 
                                user_id: str, 
                                hours: int = 24) -> List[ScheduleItem]:
        """获取即将到来的日程
        
        Args:
            user_id: 用户 ID
            hours: 时间范围（小时）
        
        Returns:
            日程列表
        """
        now = datetime.now()
        end_time = now + timedelta(hours=hours)
        
        schedules = self.list_schedules(user_id, start_date=now, end_date=end_time)
        return schedules
    
    def get_stats(self, user_id: str) -> Dict[str, Any]:
        """获取用户日程统计
        
        Args:
            user_id: 用户 ID
        
        Returns:
            统计信息
        """
        all_schedules = self.list_schedules(user_id)
        
        return {
            "total": len(all_schedules),
            "pending": len([s for s in all_schedules if s.status == "pending"]),
            "completed": len([s for s in all_schedules if s.status == "completed"]),
            "high_priority": len([s for s in all_schedules if s.priority == Priority.HIGH]),
            "this_week": len([s for s in all_schedules 
                             if s.start_time >= datetime.now() 
                             and s.start_time <= datetime.now() + timedelta(days=7)])
        }
