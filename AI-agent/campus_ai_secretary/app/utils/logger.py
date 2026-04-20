"""日志工具"""

import sys
from loguru import logger
from typing import Optional


def get_logger(name: Optional[str] = None, level: str = "INFO"):
    """获取配置好的logger实例"""
    
    # 移除默认handler
    logger.remove()
    
    # 配置格式
    format_str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format=format_str,
        level=level,
        colorize=True,
        enqueue=True
    )
    
    # 添加文件输出（可选）
    # logger.add(
    #     "logs/app_{time:YYYY-MM-DD}.log",
    #     format=format_str,
    #     level=level,
    #     rotation="00:00",
    #     retention="7 days",
    #     compression="zip"
    # )
    
    if name:
        return logger.bind(name=name)
    return logger


# 默认logger
log = get_logger("campus_ai")