"""日志工具"""

import sys
import io
import os
from loguru import logger
from typing import Optional


def get_logger(name: Optional[str] = None, level: str = "INFO"):
    """获取配置好的logger实例"""
    
    # 移除默认handler
    logger.remove()
    
    # 配置格式
    format_str = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{process.id: <6} | "
        "{thread.id: <6} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 错误日志格式（包含堆栈）
    error_format_str = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{process.id: <6} | "
        "{thread.id: <6} | "
        "{name}:{function}:{line} | "
        "{message}\n"
        "{exception}"
    )
    
    # Windows 控制台编码处理
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 兼容
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format=format_str,
        level=level,
        colorize=False,
        enqueue=True
    )
    
    # 确保日志目录存在
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # 添加主日志文件（按天轮转，保留30天）
    logger.add(
        os.path.join(log_dir, "app_{time:YYYY-MM-DD}.log"),
        format=format_str,
        level=level,
        rotation="00:00",
        retention="30 days",
        compression="zip",
        enqueue=True
    )
    
    # 添加错误日志文件（单独记录错误级别及以上）
    logger.add(
        os.path.join(log_dir, "error_{time:YYYY-MM-DD}.log"),
        format=error_format_str,
        level="ERROR",
        rotation="00:00",
        retention="90 days",
        compression="zip",
        enqueue=True
    )
    
    if name:
        return logger.bind(name=name)
    return logger


def log_request(request, response=None, duration=None):
    """记录请求日志"""
    log = get_logger("request")
    
    log.info(
        f"REQUEST | {request.method} {request.url.path} | "
        f"status={response.status_code if response else 'N/A'} | "
        f"duration={duration:.2f}ms" if duration else ""
    )


def log_error(exc, context=""):
    """记录错误日志"""
    log = get_logger("error")
    
    log.error(
        f"ERROR | {type(exc).__name__} | {exc} | context={context}"
    )


# 默认logger
log = get_logger("campus_ai")