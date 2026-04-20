from loguru import logger
from typing import List, Dict
import time

class WeChatCollector:
    def __init__(self, corpid: str = None, corpsecret: str = None):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.chats = []
        logger.info("WeChat collector initialized")
    
    def add_chat(self, chat_id: str, chat_name: str, chat_type: str = 'group'):
        self.chats.append({
            'id': chat_id,
            'name': chat_name,
            'type': chat_type,
            'last_fetch_time': 0
        })
        logger.info(f"Added monitored chat: {chat_name}")
    
    def fetch_messages(self, chat_id: str = None) -> List[Dict]:
        messages = []
        
        target_chats = self.chats if not chat_id else \
            [c for c in self.chats if c['id'] == chat_id]
        
        for chat in target_chats:
            try:
                msgs = self._fetch_from_api(chat['id'], chat['last_fetch_time'])
                messages.extend(msgs)
                chat['last_fetch_time'] = int(time.time())
            except Exception as e:
                logger.error(f"Failed to fetch messages from chat {chat['name']}: {e}")
        
        return messages
    
    def _fetch_from_api(self, chat_id: str, since_time: int) -> List[Dict]:
        return [
            {
                'chat_id': chat_id,
                'chat_name': next(c['name'] for c in self.chats if c['id'] == chat_id),
                'sender': '班长李明',
                'content': '本周六晚上6点班级聚餐，地点在学校西门火锅店，每人AA',
                'timestamp': int(time.time()),
                'type': 'event'
            },
            {
                'chat_id': chat_id,
                'chat_name': next(c['name'] for c in self.chats if c['id'] == chat_id),
                'sender': '团支书',
                'content': '下周三下午2点在团委办公室开团支部会议，请各位团支委参加',
                'timestamp': int(time.time()) - 7200,
                'type': 'meeting'
            }
        ]