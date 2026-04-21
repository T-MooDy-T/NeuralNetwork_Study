"""依赖注入模块

提供全局服务实例的获取方法
"""

from typing import Optional

from .core.scheduler import ScheduleManager
from .core.rag import RAGEngine
from .core.parser import EntityParser
from .core.llm import QwenLLM

# 全局实例引用（由 main.py 在启动时初始化）
_global_scheduler: Optional[ScheduleManager] = None
_global_rag_engine: Optional[RAGEngine] = None
_global_parser: Optional[EntityParser] = None
_global_llm: Optional[QwenLLM] = None


def set_scheduler(scheduler: ScheduleManager):
    """设置全局日程管理器"""
    global _global_scheduler
    _global_scheduler = scheduler


def get_scheduler() -> ScheduleManager:
    """获取全局日程管理器实例"""
    if _global_scheduler is None:
        from .core.scheduler import ScheduleManager
        return ScheduleManager(use_memory=True)
    return _global_scheduler


def set_rag_engine(rag_engine: RAGEngine):
    """设置全局 RAG 引擎"""
    global _global_rag_engine
    _global_rag_engine = rag_engine


def get_rag_engine() -> RAGEngine:
    """获取全局 RAG 引擎实例"""
    if _global_rag_engine is None:
        from .core.rag import RAGEngine
        return RAGEngine(use_memory=True)
    return _global_rag_engine


def get_parser() -> EntityParser:
    """获取全局实体解析器实例"""
    global _global_parser
    if _global_parser is None:
        from .core.parser import EntityParser
        from .core.llm import QwenLLM
        _global_parser = EntityParser(QwenLLM())
    return _global_parser


def get_llm() -> QwenLLM:
    """获取全局 LLM 实例"""
    global _global_llm
    if _global_llm is None:
        from .core.llm import QwenLLM
        _global_llm = QwenLLM()
    return _global_llm