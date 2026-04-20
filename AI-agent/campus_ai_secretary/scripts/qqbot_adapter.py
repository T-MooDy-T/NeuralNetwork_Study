#!/usr/bin/env python3
"""QQbot 适配器

将校园 AI 秘书服务与 OpenClaw QQbot 插件集成
通过 HTTP API 与主服务通信

使用方法:
1. 确保主服务已启动 (python -m app.main)
2. 在 OpenClaw 配置中启用此适配器
3. QQ 消息将自动转发到 AI 秘书处理
"""

import os
import json
import asyncio
import httpx
from typing import Optional, Dict, Any
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# 服务配置
CAMPUS_AI_SERVICE_URL = os.getenv("CAMPUS_AI_SERVICE_URL", "http://localhost:8000")
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "qqbot_default")


class CampusAIBotAdapter:
    """校园 AI 秘书 QQbot 适配器"""
    
    def __init__(self, service_url: str = CAMPUS_AI_SERVICE_URL):
        self.service_url = service_url
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"CampusAIBotAdapter 初始化完成，服务地址：{service_url}")
    
    async def handle_message(self, user_id: str, content: str, 
                             message_type: str = "text") -> Dict[str, Any]:
        """处理 QQ 消息
        
        Args:
            user_id: 用户 ID (QQ 号)
            content: 消息内容
            message_type: 消息类型 (text/image/forward)
        
        Returns:
            响应数据
        """
        logger.info(f"收到 QQ 消息 - 用户：{user_id}, 内容：{content[:30]}...")
        
        try:
            # 1. 尝试解析为日程
            parse_result = await self._parse_content(user_id, content, message_type)
            
            # 2. 判断用户意图
            intent = self._detect_intent(content, parse_result)
            
            # 3. 根据意图处理
            if intent == "schedule_create":
                response = await self._handle_schedule_create(user_id, parse_result)
            elif intent == "schedule_query":
                response = await self._handle_schedule_query(user_id, content)
            elif intent == "question":
                response = await self._handle_question(user_id, content)
            else:
                response = await self._handle_general(user_id, content, parse_result)
            
            return response
            
        except Exception as e:
            logger.exception(f"处理消息失败：{e}")
            return {
                "success": False,
                "message": "抱歉，处理您的消息时出现了问题，请稍后重试~"
            }
    
    async def _parse_content(self, user_id: str, content: str, 
                             message_type: str) -> Optional[Dict]:
        """解析消息内容"""
        try:
            if message_type == "text":
                resp = await self.client.post(
                    f"{self.service_url}/api/v1/parse/text",
                    params={"user_id": user_id},
                    json={"content": content}
                )
                return resp.json()
            elif message_type == "forward":
                resp = await self.client.post(
                    f"{self.service_url}/api/v1/parse/forwarded",
                    params={"user_id": user_id},
                    json={"content": content, "source": "QQ 群"}
                )
                return resp.json()
        except Exception as e:
            logger.warning(f"解析失败：{e}")
        return None
    
    def _detect_intent(self, content: str, parse_result: Optional[Dict]) -> str:
        """检测用户意图
        
        Returns:
            "schedule_create" | "schedule_query" | "question" | "general"
        """
        content_lower = content.lower()
        
        # 查询意图
        query_keywords = ["查询", "查看", "列表", "有哪些", "什么时候", "日程"]
        if any(kw in content_lower for kw in query_keywords):
            return "schedule_query"
        
        # 问答意图
        question_patterns = ["什么是", "怎么", "如何", "哪里", "多少", "吗", "?", "？"]
        if any(p in content for p in question_patterns):
            return "question"
        
        # 创建日程意图（解析成功且包含时间）
        if parse_result and parse_result.get("success") and parse_result.get("start_time"):
            return "schedule_create"
        
        return "general"
    
    async def _handle_schedule_create(self, user_id: str, 
                                       parse_result: Dict) -> Dict[str, Any]:
        """处理创建日程"""
        try:
            # 构建创建请求
            create_data = {
                "event_name": parse_result.get("event_name", "待命名事件"),
                "start_time": parse_result.get("start_time"),
                "location": parse_result.get("location"),
                "priority": parse_result.get("priority", "medium"),
                "description": parse_result.get("description")
            }
            
            if parse_result.get("end_time"):
                create_data["end_time"] = parse_result["end_time"]
            
            # 调用创建 API
            resp = await self.client.post(
                f"{self.service_url}/api/v1/schedule/create",
                params={"user_id": user_id},
                json=create_data
            )
            
            if resp.status_code == 200:
                schedule = resp.json()
                return {
                    "success": True,
                    "message": f"✅ 日程已创建!\n\n"
                              f"📅 {schedule['event_name']}\n"
                              f"⏰ {schedule['start_time']}\n"
                              f"📍 {schedule.get('location', '未指定')}\n"
                              f"🔔 我会在合适的时间提醒你~",
                    "schedule_id": schedule["id"]
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ 创建失败：{resp.text}"
                }
                
        except Exception as e:
            logger.exception(f"创建日程失败：{e}")
            return {
                "success": False,
                "message": "❌ 创建日程时出错，请稍后重试"
            }
    
    async def _handle_schedule_query(self, user_id: str, content: str) -> Dict[str, Any]:
        """处理日程查询"""
        try:
            resp = await self.client.get(
                f"{self.service_url}/api/v1/schedule/list",
                params={"user_id": user_id}
            )
            
            if resp.status_code == 200:
                schedules = resp.json()
                
                if not schedules:
                    return {
                        "success": True,
                        "message": "📭 你还没有任何日程哦~\n\n发送日程信息给我，我来帮你记录!"
                    }
                
                # 格式化日程列表
                message = f"📅 你共有 {len(schedules)} 个日程:\n\n"
                for i, s in enumerate(schedules[:5], 1):  # 最多显示 5 个
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    emoji = priority_emoji.get(s.get("priority", "medium"), "🟡")
                    message += f"{i}. {emoji} {s['event_name']}\n"
                    message += f"   ⏰ {s['start_time']}\n"
                    if s.get('location'):
                        message += f"   📍 {s['location']}\n"
                    message += "\n"
                
                if len(schedules) > 5:
                    message += f"... 还有 {len(schedules) - 5} 个日程"
                
                return {
                    "success": True,
                    "message": message
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ 查询失败：{resp.text}"
                }
                
        except Exception as e:
            logger.exception(f"查询日程失败：{e}")
            return {
                "success": False,
                "message": "❌ 查询日程时出错，请稍后重试"
            }
    
    async def _handle_question(self, user_id: str, content: str) -> Dict[str, Any]:
        """处理智能问答"""
        try:
            resp = await self.client.post(
                f"{self.service_url}/api/v1/qa/ask",
                params={"user_id": user_id, "question": content}
            )
            
            if resp.status_code == 200:
                result = resp.json()
                return {
                    "success": True,
                    "message": result["answer"],
                    "confidence": result["confidence"]
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ 回答失败：{resp.text}"
                }
                
        except Exception as e:
            logger.exception(f"问答失败：{e}")
            return {
                "success": False,
                "message": "❌ 回答你的问题时出错了，请稍后重试"
            }
    
    async def _handle_general(self, user_id: str, content: str, 
                               parse_result: Optional[Dict]) -> Dict[str, Any]:
        """处理一般消息"""
        if parse_result and parse_result.get("missing_fields"):
            # 解析不完整，引导用户补充
            missing = parse_result["missing_fields"]
            message = "🤔 我需要更多信息才能创建日程~\n\n"
            
            if "event_name" in missing:
                message += "• 这是什么事件？\n"
            if "start_time" in missing:
                message += "• 什么时候开始？\n"
            
            message += "\n请补充一下信息吧!"
            
            return {
                "success": True,
                "message": message
            }
        
        # 默认回复
        return {
            "success": True,
            "message": "👋 你好！我是校园 AI 秘书~\n\n"
                      "我可以帮你:\n"
                      "• 📅 记录日程和提醒\n"
                      "• 📚 回答校园相关问题\n"
                      "• 🔔 主动提醒重要事项\n\n"
                      "试试发送：'明天下午 3 点开会'\n"
                      "或者问：'图书馆开放时间'"
        }
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 全局适配器实例
_adapter: Optional[CampusAIBotAdapter] = None


def get_adapter() -> CampusAIBotAdapter:
    """获取适配器实例"""
    global _adapter
    if _adapter is None:
        _adapter = CampusAIBotAdapter()
    return _adapter


# ============================================
# OpenClaw QQbot 插件集成入口
# ============================================

async def on_qq_message(user_id: str, content: str, 
                        message_type: str = "text") -> str:
    """
    OpenClaw QQbot 插件调用的消息处理入口
    
    Args:
        user_id: 用户 ID
        content: 消息内容
        message_type: 消息类型
    
    Returns:
        回复消息文本
    """
    adapter = get_adapter()
    result = await adapter.handle_message(user_id, content, message_type)
    return result.get("message", "")


if __name__ == "__main__":
    # 测试运行
    async def test():
        adapter = get_adapter()
        
        # 测试消息
        test_messages = [
            ("user123", "明天下午 3 点在教学楼 A302 开班会"),
            ("user123", "查询我的日程"),
            ("user123", "图书馆开放时间"),
        ]
        
        for user_id, content in test_messages:
            print(f"\n用户：{user_id}")
            print(f"消息：{content}")
            result = await adapter.handle_message(user_id, content)
            print(f"回复：{result['message']}")
        
        await adapter.close()
    
    asyncio.run(test())
