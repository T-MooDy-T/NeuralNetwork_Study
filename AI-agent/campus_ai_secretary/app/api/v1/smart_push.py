"""智能推送增强 API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from ...database.connection import get_db
from ...database.models import Schedule, KnowledgeBase, CollectedInfo, ReminderLog
from ...core.llm import QwenLLM

router = APIRouter(tags=["智能推送"])


@router.post("/generate-content", summary="生成智能推送内容")
async def generate_push_content(
    data: Dict[str, Any]
):
    """利用LLM生成智能推送内容
    
    Args:
        data: 包含type和原始数据的字典
            - type: schedule/knowledge/collected/reminder
            - item: 原始数据项
    
    Returns:
        生成的智能推送内容
    """
    try:
        llm = QwenLLM()
        item_type = data.get("type")
        item = data.get("item")
        
        if item_type == "schedule":
            return await _generate_schedule_content(llm, item)
        elif item_type == "knowledge":
            return await _generate_knowledge_content(llm, item)
        elif item_type == "collected":
            return await _generate_collected_content(llm, item)
        elif item_type == "reminder":
            return await _generate_reminder_content(llm, item)
        else:
            raise HTTPException(status_code=400, detail="未知的内容类型")
    
    except Exception as e:
        logger.error(f"生成推送内容失败: {e}")
        return {"success": False, "message": str(e)}


async def _generate_schedule_content(llm: QwenLLM, schedule: Dict):
    """生成日程智能提醒内容"""
    system_prompt = """你是一个校园日程助手，擅长用友好自然的语言提醒用户日程安排。
    
    请根据提供的日程信息，生成一条温馨、简洁的提醒消息：
    - 突出时间和地点
    - 添加适当的emoji表情
    - 语气亲切友好
    - 如果有备注信息，自然地融入提醒中
    """
    
    user_prompt = f"""日程信息：
    事件名称：{schedule.get('event_name', '')}
    开始时间：{schedule.get('start_time', '')}
    结束时间：{schedule.get('end_time', '')}
    地点：{schedule.get('location', '')}
    备注：{schedule.get('description', '')}
    
    请生成一条温馨的提醒消息。"""
    
    response = llm.chat([{"role": "user", "content": user_prompt}], system_prompt, temperature=0.8)
    
    return {
        "success": True,
        "type": "schedule",
        "original_title": schedule.get("event_name"),
        "generated_content": response,
        "priority": schedule.get("priority", "medium")
    }


async def _generate_knowledge_content(llm: QwenLLM, knowledge: Dict):
    """生成知识库推荐内容"""
    system_prompt = """你是一个知识推荐助手，擅长发现和推荐有价值的知识内容。
    
    请根据提供的知识库内容，生成一条吸引人的推荐消息：
    - 突出内容亮点
    - 使用适当的emoji表情
    - 激发用户兴趣
    - 保持简洁
    """
    
    content_preview = knowledge.get("content", "")[:200] if knowledge.get("content") else ""
    
    user_prompt = f"""知识库内容：
    标题：{knowledge.get('title', '未命名')}
    内容摘要：{content_preview}
    分类：{knowledge.get('category', '')}
    
    请生成一条吸引人的知识推荐消息。"""
    
    response = llm.chat([{"role": "user", "content": user_prompt}], system_prompt, temperature=0.9)
    
    return {
        "success": True,
        "type": "knowledge",
        "original_title": knowledge.get("title"),
        "generated_content": response,
        "priority": "medium"
    }


async def _generate_collected_content(llm: QwenLLM, collected: Dict):
    """生成采集信息智能摘要"""
    system_prompt = """你是一个信息处理助手，擅长提炼关键信息。
    
    请根据提供的采集信息，生成一条简洁的推送消息：
    - 提取核心要点
    - 标明信息来源
    - 使用适当的emoji表情
    - 根据内容重要性添加感叹词
    """
    
    user_prompt = f"""采集信息：
    来源：{collected.get('source', '')}
    发送者：{collected.get('sender', '')}
    内容：{collected.get('content', '')}
    分类：{collected.get('category', '')}
    优先级：{collected.get('priority', 'normal')}
    
    请生成一条简洁的推送消息。"""
    
    response = llm.chat([{"role": "user", "content": user_prompt}], system_prompt, temperature=0.7)
    
    return {
        "success": True,
        "type": "collected",
        "original_title": collected.get("category"),
        "generated_content": response,
        "priority": collected.get("priority", "normal")
    }


async def _generate_reminder_content(llm: QwenLLM, reminder: Dict):
    """生成提醒通知内容"""
    system_prompt = """你是一个贴心的提醒助手，擅长用温暖的语言提醒用户。
    
    请根据提供的提醒信息，生成一条温馨的提醒消息：
    - 使用温馨的语气
    - 添加适当的emoji表情
    - 突出关键信息
    """
    
    user_prompt = f"""提醒信息：
    事件名称：{reminder.get('event_name', '')}
    提醒时间：{reminder.get('remind_time', '')}
    提前时间：{reminder.get('offset', '')}
    
    请生成一条温馨的提醒消息。"""
    
    response = llm.chat([{"role": "user", "content": user_prompt}], system_prompt, temperature=0.8)
    
    return {
        "success": True,
        "type": "reminder",
        "original_title": reminder.get("event_name"),
        "generated_content": response,
        "priority": "high"
    }


@router.post("/analyze-priority", summary="AI智能优先级分析")
async def analyze_priority(
    content: str,
    context: Optional[str] = None
):
    """利用LLM分析内容优先级和重要性"""
    try:
        llm = QwenLLM()
        
        system_prompt = """你是一个智能分析助手，擅长判断信息的重要性。
        
        请根据提供的内容，分析其重要程度：
        - 返回JSON格式，包含 priority 和 reason
        - priority: high/medium/low
        - reason: 简短说明为什么是这个优先级
        """
        
        user_prompt = f"""内容：{content}
        
        上下文（可选）：{context or '无'}
        
        请分析这段内容的优先级。只返回JSON。"""
        
        response = llm.chat([{"role": "user", "content": user_prompt}], system_prompt, temperature=0.3)
        
        import json
        try:
            result = json.loads(response.strip())
            return {"success": True, **result}
        except:
            return {"success": True, "priority": "medium", "reason": "无法解析AI响应"}
    
    except Exception as e:
        logger.error(f"优先级分析失败: {e}")
        return {"success": False, "message": str(e)}


@router.get("/personalized-recommend", summary="个性化内容推荐")
async def personalized_recommend(
    user_id: Optional[int] = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """基于用户数据生成个性化推荐"""
    try:
        llm = QwenLLM()
        
        if user_id:
            user_schedules = db.query(Schedule).filter(
                Schedule.user_id == user_id,
                Schedule.status == "pending"
            ).order_by(Schedule.start_time).limit(10).all()
            
            schedule_titles = [s.event_name for s in user_schedules]
        else:
            schedule_titles = []
        
        recent_knowledge = db.query(KnowledgeBase).filter(
            KnowledgeBase.is_active == True
        ).order_by(KnowledgeBase.created_at.desc()).limit(10).all()
        
        knowledge_titles = [k.title or "无标题" for k in recent_knowledge]
        
        system_prompt = """你是一个校园AI秘书，擅长为学生推荐个性化内容。
        
        根据用户的日程安排和最新知识库内容，生成一份个性化推荐清单：
        - 每条推荐用序号列出
        - 使用emoji表情增加可读性
        - 推荐内容要与用户日程相关或有价值
        """
        
        user_prompt = f"""用户日程（最近10个）：
        {chr(10).join([f"- {s}" for s in schedule_titles]) or "暂无"}
        
        最新知识库（最近10条）：
        {chr(10).join([f"- {k}" for k in knowledge_titles]) or "暂无"}
        
        请根据以上信息，为用户生成{limit}条个性化推荐。"""
        
        response = llm.chat([{"role": "user", "content": user_prompt}], system_prompt, temperature=0.7)
        
        return {
            "success": True,
            "recommendations": response.strip().split("\n"),
            "user_id": user_id
        }
    
    except Exception as e:
        logger.error(f"个性化推荐失败: {e}")
        return {"success": False, "message": str(e)}
