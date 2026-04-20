"""信息解析器

支持文字、图片（OCR）、转发消息的解析
提取时间、地点、事件等实体
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from ..models.schedule import ParseResult, Priority
from ..utils.time_utils import parse_time
from .llm import QwenLLM


class EntityParser:
    """实体解析器"""
    
    def __init__(self, llm: Optional[QwenLLM] = None):
        """初始化解析器
        
        Args:
            llm: LLM 实例，用于智能解析
        """
        self.llm = llm or QwenLLM()
        logger.info("EntityParser 初始化完成")
    
    def parse_text(self, content: str, user_id: str = "default") -> ParseResult:
        """解析文本内容
        
        Args:
            content: 待解析的文本
            user_id: 用户 ID
        
        Returns:
            解析结果
        """
        logger.info(f"解析文本：{content[:50]}...")
        
        # 使用 LLM 提取实体
        entities = self.llm.extract_entities(content)
        
        # 解析时间
        start_time = None
        end_time = None
        
        if entities.get("start_time"):
            start_time = parse_time(entities["start_time"])
        
        if entities.get("end_time"):
            end_time = parse_time(entities["end_time"])
        
        # 确定优先级
        priority = self._infer_priority(entities.get("event_name", ""), content)
        
        # 检查缺失字段
        missing_fields = []
        if not entities.get("event_name"):
            missing_fields.append("event_name")
        if not start_time:
            missing_fields.append("start_time")
        
        # 计算置信度
        confidence = 1.0 - (len(missing_fields) * 0.3)
        if self.llm:
            confidence = min(confidence + 0.2, 1.0)  # LLM 增强置信度
        
        return ParseResult(
            success=len(missing_fields) == 0,
            event_name=entities.get("event_name"),
            start_time=start_time,
            end_time=end_time,
            location=entities.get("location"),
            priority=priority,
            description=entities.get("description", content),
            confidence=confidence,
            missing_fields=missing_fields,
            raw_content=content
        )
    
    def _infer_priority(self, event_name: Optional[str], content: str) -> Priority:
        """推断事件优先级
        
        Args:
            event_name: 事件名称
            content: 原始内容
        
        Returns:
            优先级枚举
        """
        # 高优先级关键词
        high_keywords = ["考试", "期末", "期中", "答辩", "截止", "DDL", "报名截止"]
        
        # 中优先级关键词
        medium_keywords = ["作业", "报告", "论文", "实验", "会议", "面试"]
        
        text = (event_name or "") + " " + content
        
        for keyword in high_keywords:
            if keyword in text:
                return Priority.HIGH
        
        for keyword in medium_keywords:
            if keyword in text:
                return Priority.MEDIUM
        
        return Priority.LOW
    
    def parse_forwarded_message(self, content: str, source: str = "unknown") -> ParseResult:
        """解析转发消息
        
        Args:
            content: 转发的消息内容
            source: 消息来源（如"班级 QQ 群"）
        
        Returns:
            解析结果
        """
        logger.info(f"解析转发消息，来源：{source}")
        
        # 转发消息本质上也是文本，复用文本解析
        result = self.parse_text(content)
        
        # 附加来源信息
        if result.description:
            result.description = f"[来自 {source}] {result.description}"
        
        return result
    
    def parse_image(self, image_path: str) -> ParseResult:
        """解析图片（课表截图等）
        
        Args:
            image_path: 图片路径
        
        Returns:
            解析结果
        
        Note:
            完整实现需要接入 OCR 服务（如 PaddleOCR）
            Demo 版本暂不实现
        """
        logger.warning(f"图片解析功能需要 OCR 支持，当前路径：{image_path}")
        
        return ParseResult(
            success=False,
            confidence=0.0,
            missing_fields=["all"],
            raw_content=f"[图片] {image_path}",
            description="图片解析功能将在后续版本实现"
        )
    
    def needs_confirmation(self, result: ParseResult) -> bool:
        """判断是否需要用户确认
        
        Args:
            result: 解析结果
        
        Returns:
            是否需要确认
        """
        # 置信度低于阈值需要确认
        if result.confidence < 0.7:
            return True
        
        # 缺失关键字段需要确认
        if result.missing_fields:
            return True
        
        return False
    
    def format_confirmation_message(self, result: ParseResult) -> str:
        """格式化确认消息
        
        Args:
            result: 解析结果
        
        Returns:
            格式化的确认消息
        """
        from ..utils.time_utils import format_time_display
        
        lines = ["📅 我帮你解析了以下日程信息，请确认：\n"]
        
        if result.event_name:
            lines.append(f"**事件**：{result.event_name}")
        else:
            lines.append("**事件**：_待填写_")
        
        if result.start_time:
            lines.append(f"**时间**：{format_time_display(result.start_time)}")
            if result.end_time:
                lines.append(f"        至 {format_time_display(result.end_time)}")
        else:
            lines.append("**时间**：_待填写_")
        
        if result.location:
            lines.append(f"**地点**：{result.location}")
        
        lines.append(f"**优先级**：{result.priority.value if result.priority else '中'}")
        
        if result.missing_fields:
            lines.append(f"\n⚠️ 以下信息缺失：{', '.join(result.missing_fields)}")
            lines.append("请补充后再创建日程~")
        
        lines.append("\n回复「确认」创建日程，或直接告诉我需要修改的内容~")
        
        return "\n".join(lines)
