"""提醒服务

基于定时扫描的主动提醒系统
支持多级提醒、智能时机选择
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from loguru import logger

from ..models.schedule import ScheduleItem, Priority
from ..utils.time_utils import parse_remind_offset
from .scheduler import ScheduleManager


class ReminderService:
    """提醒服务"""
    
    def __init__(self, 
                 scheduler: ScheduleManager,
                 check_interval: int = 60,
                 send_callback: Optional[Callable] = None):
        """初始化提醒服务
        
        Args:
            scheduler: 日程管理器
            check_interval: 检查间隔（秒）
            send_callback: 发送提醒的回调函数 (user_id, message) -> None
        """
        self.scheduler = scheduler
        self.check_interval = check_interval
        self.send_callback = send_callback
        self.running = False
        self.task: Optional[asyncio.Task] = None
        
        # 已发送提醒记录（避免重复）
        self.sent_reminders: Dict[str, set] = {}  # user_id -> {schedule_id:remind_time}
        
        logger.info(f"ReminderService 初始化完成，检查间隔：{check_interval}秒")
    
    def start(self):
        """启动提醒服务"""
        if self.running:
            logger.warning("提醒服务已在运行")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_loop())
        logger.info("提醒服务已启动")
    
    def stop(self):
        """停止提醒服务"""
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None
        logger.info("提醒服务已停止")
    
    async def _run_loop(self):
        """主循环"""
        while self.running:
            try:
                await self._check_and_send_reminders()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"提醒服务异常：{e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_and_send_reminders(self):
        """检查并发送提醒"""
        now = datetime.now()
        logger.debug(f"执行提醒检查：{now}")
        
        # 获取所有用户的即将到期日程
        # 简化实现：遍历所有用户（实际应该从 Redis 获取用户列表）
        user_ids = list(self.scheduler.user_schedules.keys()) if self.scheduler.use_memory else []
        
        for user_id in user_ids:
            await self._check_user_reminders(user_id, now)
    
    async def _check_user_reminders(self, user_id: str, now: datetime):
        """检查单个用户的提醒
        
        Args:
            user_id: 用户 ID
            now: 当前时间
        """
        # 获取用户所有待处理的日程
        schedules = self.scheduler.list_schedules(user_id, status="pending")
        
        if user_id not in self.sent_reminders:
            self.sent_reminders[user_id] = set()
        
        for schedule in schedules:
            await self._check_schedule_reminder(user_id, schedule, now)
    
    async def _check_schedule_reminder(self, 
                                        user_id: str, 
                                        schedule: ScheduleItem, 
                                        now: datetime):
        """检查单个日程的提醒
        
        Args:
            user_id: 用户 ID
            schedule: 日程对象
            now: 当前时间
        """
        if not schedule.remind_times:
            return
        
        for remind_offset in schedule.remind_times:
            # 计算提醒时间
            offset = parse_remind_offset(remind_offset)
            remind_time = schedule.start_time - offset
            
            # 检查是否到达提醒时间
            reminder_key = f"{schedule.id}:{remind_offset}"
            
            if reminder_key in self.sent_reminders.get(user_id, set()):
                continue  # 已发送过
            
            # 检查时间窗口（前后 5 分钟内）
            time_diff = abs((now - remind_time).total_seconds())
            if time_diff <= 300:  # 5 分钟
                await self._send_reminder(user_id, schedule, remind_offset)
                self.sent_reminders[user_id].add(reminder_key)
    
    async def _send_reminder(self, 
                             user_id: str, 
                             schedule: ScheduleItem,
                             remind_offset: str):
        """发送提醒
        
        Args:
            user_id: 用户 ID
            schedule: 日程对象
            remind_offset: 提醒偏移
        """
        from ..utils.time_utils import format_time_display
        
        # 构建提醒消息
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        emoji = priority_emoji.get(schedule.priority, "🟡")
        
        time_str = format_time_display(schedule.start_time)
        
        message = f"""{emoji} 日程提醒

**{schedule.event_name}**

⏰ 时间：{time_str}
📍 地点：{schedule.location or "未指定"}
📝 说明：{schedule.description or "无"}

提醒时机：{remind_offset} 前
"""
        
        logger.info(f"发送提醒给用户 {user_id}: {schedule.event_name}")
        
        # 调用回调发送
        if self.send_callback:
            try:
                self.send_callback(user_id, message)
            except Exception as e:
                logger.error(f"发送提醒失败：{e}")
        else:
            logger.info(f"[提醒消息]\n{message}")
    
    def get_pending_reminders(self, user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """获取待发送的提醒列表
        
        Args:
            user_id: 用户 ID
            hours: 时间范围（小时）
        
        Returns:
            待发送提醒列表
        """
        now = datetime.now()
        end_time = now + timedelta(hours=hours)
        
        schedules = self.scheduler.list_schedules(user_id, start_date=now, end_date=end_time)
        
        reminders = []
        for schedule in schedules:
            for remind_offset in schedule.remind_times:
                offset = parse_remind_offset(remind_offset)
                remind_time = schedule.start_time - offset
                
                if remind_time > now:
                    reminders.append({
                        "schedule_id": schedule.id,
                        "event_name": schedule.event_name,
                        "remind_time": remind_time,
                        "event_time": schedule.start_time,
                        "offset": remind_offset
                    })
        
        reminders.sort(key=lambda x: x["remind_time"])
        return reminders
    
    def clear_sent_reminders(self, user_id: str):
        """清除用户的已发送提醒记录
        
        Args:
            user_id: 用户 ID
        """
        if user_id in self.sent_reminders:
            self.sent_reminders[user_id] = set()
            logger.info(f"清除用户 {user_id} 的提醒记录")
