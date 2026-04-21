"""中间件模块"""

import time
from fastapi import Request, Response
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from typing import Callable


class RequestLogMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"REQUEST_START | {request.method} {request.url.path} | "
            f"client={request.client.host}:{request.client.port} | "
            f"headers={dict(request.headers)}"
        )
        
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录异常
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"REQUEST_ERROR | {request.method} {request.url.path} | "
                f"duration={duration:.2f}ms | error={type(e).__name__}: {e}"
            )
            raise
        
        # 记录响应信息
        duration = (time.time() - start_time) * 1000
        logger.info(
            f"REQUEST_END | {request.method} {request.url.path} | "
            f"status={response.status_code} | duration={duration:.2f}ms"
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 添加安全相关的响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class GZipMiddleware(BaseHTTPMiddleware):
    """GZip 压缩中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 检查是否支持 gzip 压缩
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" in accept_encoding.lower():
            response.headers["Content-Encoding"] = "gzip"
        
        return response