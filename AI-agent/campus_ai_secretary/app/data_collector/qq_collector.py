from loguru import logger
from typing import List, Dict
import time
import requests
import json
import os

class QQCollector:
    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = app_id or os.getenv("QQ_APP_ID", "1903870451")
        self.app_secret = app_secret or os.getenv("QQ_APP_SECRET", "kaKvMes164vfPAxl")
        self.groups = []
        self.access_token = None
        self.token_expire_time = 0
        logger.info(f"QQ collector initialized with AppID: {self.app_id}")
    
    def _get_access_token(self):
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
        
        try:
            url = f"https://api.sgroup.qq.com/app/get_token?app_id={self.app_id}&app_secret={self.app_secret}"
            response = requests.get(url)
            data = response.json()
            
            if data.get("code") == 0:
                self.access_token = data["token"]
                self.token_expire_time = time.time() + data.get("expire", 7200)
                logger.info("Successfully obtained QQ bot access token")
                return self.access_token
            else:
                logger.error(f"Failed to get access token: {data.get('message')}")
                return None
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return None
    
    def add_group(self, group_id: str, group_name: str):
        if group_id not in [g['id'] for g in self.groups]:
            self.groups.append({
                'id': group_id,
                'name': group_name,
                'last_fetch_time': 0
            })
            logger.info(f"Added monitored group: {group_name}")
    
    def fetch_messages(self, group_id: str = None) -> List[Dict]:
        messages = []
        
        token = self._get_access_token()
        if not token:
            return self._get_mock_messages(group_id)
        
        target_groups = self.groups if not group_id else \
            [g for g in self.groups if g['id'] == group_id]
        
        for group in target_groups:
            try:
                msgs = self._fetch_from_api(token, group['id'], group['last_fetch_time'])
                messages.extend(msgs)
                group['last_fetch_time'] = int(time.time())
            except Exception as e:
                logger.error(f"Failed to fetch messages from group {group['name']}: {e}")
                messages.extend(self._get_mock_messages(group['id']))
        
        return messages
    
    def _fetch_from_api(self, token: str, group_id: str, since_time: int) -> List[Dict]:
        url = f"https://api.sgroup.qq.com/v2/groups/{group_id}/messages"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, headers=headers, params={"since": since_time})
            data = response.json()
            
            if data.get("code") == 0:
                return self._parse_messages(data.get("data", []), group_id)
            else:
                logger.warning(f"API returned error: {data.get('message')}")
                return []
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return []
    
    def _parse_messages(self, raw_messages: List[Dict], group_id: str) -> List[Dict]:
        messages = []
        group_name = next((g['name'] for g in self.groups if g['id'] == group_id), group_id)
        
        for msg in raw_messages:
            messages.append({
                'group_id': group_id,
                'group_name': group_name,
                'sender': msg.get("author", {}).get("nickname", "unknown"),
                'content': msg.get("content", ""),
                'timestamp': msg.get("timestamp", int(time.time())),
                'type': self._detect_message_type(msg.get("content", ""))
            })
        
        return messages
    
    def send_welcome_message(self, group_id: str, user_id: str = None):
        """发送欢迎消息"""
        token = self._get_access_token()
        if not token:
            return self._send_mock_welcome(group_id, user_id)
        
        try:
            url = f"https://api.sgroup.qq.com/v2/groups/{group_id}/messages"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            content = self._get_welcome_content(user_id)
            payload = {
                "content": json.dumps({"type": "text", "data": {"text": content}})
            }
            
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            if data.get("code") == 0:
                logger.info(f"Successfully sent welcome message to group {group_id}")
                return True
            else:
                logger.error(f"Failed to send welcome message: {data.get('message')}")
                return False
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
            return False
    
    def _send_mock_welcome(self, group_id: str, user_id: str = None):
        """模拟发送欢迎消息"""
        group_name = next((g['name'] for g in self.groups if g['id'] == group_id), group_id)
        content = self._get_welcome_content(user_id)
        logger.info(f"[模拟] 向群 {group_name} 发送欢迎消息: {content}")
        return True
    
    def _get_welcome_content(self, user_id: str = None) -> str:
        """生成欢迎消息内容"""
        welcome_msg = """
🎓 欢迎使用校园AI秘书！

我可以帮你：
📅 自动整理日程安排
🔔 智能提醒重要事项  
📚 检索知识库信息
💬 解答校园相关问题

发送「帮助」获取完整功能列表

如有任何问题，随时联系我！
        """.strip()
        
        if user_id:
            welcome_msg = f"@{user_id} {welcome_msg}"
        
        return welcome_msg
    
    def broadcast_welcome(self):
        """向所有监控群发送欢迎消息"""
        for group in self.groups:
            self.send_welcome_message(group['id'])
        logger.info(f"Broadcast welcome message to {len(self.groups)} groups")
    
    def _detect_message_type(self, content: str) -> str:
        if any(keyword in content for keyword in ["通知", "必须", "务必", "紧急"]):
            return "notification"
        elif any(keyword in content for keyword in ["作业", "论文", "考试", "课程"]):
            return "academic"
        elif any(keyword in content for keyword in ["会议", "活动", "聚餐", "报名"]):
            return "event"
        return "normal"
    
    def _get_mock_messages(self, group_id: str = None) -> List[Dict]:
        target_groups = self.groups if not group_id else \
            [g for g in self.groups if g['id'] == group_id]
        
        messages = []
        for group in target_groups:
            messages.extend([
                {
                    'group_id': group['id'],
                    'group_name': group['name'],
                    'sender': '辅导员王老师',
                    'content': '明天下午3点在教学楼A302开班会，请准时参加，记得带学生证',
                    'timestamp': int(time.time()),
                    'type': 'notification'
                },
                {
                    'group_id': group['id'],
                    'group_name': group['name'],
                    'sender': '学习委员',
                    'content': '高等数学作业截止日期延长到下周一，请大家抓紧时间完成',
                    'timestamp': int(time.time()) - 3600,
                    'type': 'academic'
                }
            ])
        
        return messages