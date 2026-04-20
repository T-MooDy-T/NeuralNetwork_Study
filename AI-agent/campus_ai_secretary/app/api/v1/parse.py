"""信息解析 API"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from loguru import logger

from ...models.schedule import ParseResult, ScheduleCreate
from ...core.parser import EntityParser
from ...core.llm import QwenLLM

router = APIRouter()

# 全局解析器实例
_parser: Optional[EntityParser] = None


def get_parser() -> EntityParser:
    """获取解析器实例"""
    global _parser
    if _parser is None:
        llm = QwenLLM()
        _parser = EntityParser(llm)
    return _parser


@router.post("/text", response_model=ParseResult, summary="解析文本")
async def parse_text(content: str, user_id: str = "default"):
    """解析文本内容，提取日程实体"""
    try:
        parser = get_parser()
        result = parser.parse_text(content, user_id)
        
        logger.info(f"API: 解析文本 - 用户：{user_id}, 成功：{result.success}, 置信度：{result.confidence}")
        return result
    except Exception as e:
        logger.exception(f"解析文本失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forwarded", response_model=ParseResult, summary="解析转发消息")
async def parse_forwarded(content: str, source: str = "unknown", user_id: str = "default"):
    """解析转发的消息内容"""
    try:
        parser = get_parser()
        result = parser.parse_forwarded_message(content, source)
        
        logger.info(f"API: 解析转发消息 - 用户：{user_id}, 来源：{source}")
        return result
    except Exception as e:
        logger.exception(f"解析转发消息失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm-message", summary="生成确认消息")
async def generate_confirm_message(content: str, user_id: str = "default"):
    """解析文本并生成确认消息"""
    try:
        parser = get_parser()
        result = parser.parse_text(content, user_id)
        
        if parser.needs_confirmation(result):
            message = parser.format_confirmation_message(result)
        else:
            message = f"✅ 信息已解析完成，可以直接创建日程~\n\n事件：{result.event_name}\n时间：{result.start_time}"
        
        return {
            "message": message,
            "needs_confirmation": parser.needs_confirmation(result),
            "parse_result": result
        }
    except Exception as e:
        logger.exception(f"生成确认消息失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))
