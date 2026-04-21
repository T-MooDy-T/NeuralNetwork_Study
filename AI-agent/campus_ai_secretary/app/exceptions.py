"""全局异常处理器"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from typing import Union
import traceback


class CampusAIError(Exception):
    """自定义业务异常"""
    
    def __init__(self, message: str, code: int = 400, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}


class AuthenticationError(CampusAIError):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, code=401)


class AuthorizationError(CampusAIError):
    """授权异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, code=403)


class ResourceNotFoundError(CampusAIError):
    """资源不存在异常"""
    def __init__(self, resource: str = "资源"):
        super().__init__(f"{resource}不存在", code=404)


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"全局异常: {type(exc).__name__} - {exc}")
    logger.error(f"请求路径: {request.url.path}")
    logger.error(f"请求方法: {request.method}")
    logger.error(f"完整堆栈:\n{traceback.format_exc()}")
    
    # 根据异常类型返回不同响应
    if isinstance(exc, CampusAIError):
        return JSONResponse(
            status_code=exc.code,
            content={
                "error": exc.message,
                "code": exc.code,
                "details": exc.details,
                "path": request.url.path
            }
        )
    
    if isinstance(exc, RequestValidationError):
        errors = []
        for err in exc.errors():
            errors.append({
                "field": err["loc"],
                "message": err["msg"],
                "type": err["type"]
            })
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "请求参数验证失败",
                "code": 422,
                "details": errors,
                "path": request.url.path
            }
        )
    
    if isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "数据验证失败",
                "code": 422,
                "path": request.url.path
            }
        )
    
    if isinstance(exc, SQLAlchemyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "数据库操作失败",
                "code": 500,
                "path": request.url.path
            }
        )
    
    # 未知异常
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "服务器内部错误",
            "code": 500,
            "path": request.url.path
        }
    )


async def http_exception_handler(request: Request, exc: Exception):
    """HTTP 异常处理器"""
    from fastapi import HTTPException as FastAPIHTTPException
    
    if isinstance(exc, FastAPIHTTPException):
        logger.warning(f"HTTP 异常: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "code": exc.status_code,
                "path": request.url.path
            }
        )
    
    return await global_exception_handler(request, exc)