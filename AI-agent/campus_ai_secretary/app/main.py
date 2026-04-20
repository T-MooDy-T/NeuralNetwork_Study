"""校园 AI 秘书 - 主服务入口

FastAPI 应用入口，提供 REST API 和提醒服务
"""

import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from .api.v1 import router as v1_router
from .api.v1.auth import router as auth_router
from .api.admin import router as admin_router
from .core.scheduler import ScheduleManager
from .core.reminder import ReminderService
from .database.connection import init_db
from .core.auth import init_admin_user
from .utils.logger import get_logger

# 配置日志
log = get_logger("campus_ai", os.getenv("LOG_LEVEL", "INFO"))

# 全局服务实例
scheduler: ScheduleManager = None
reminder_service: ReminderService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global scheduler, reminder_service
    
    # 启动时初始化
    log.info("🚀 校园 AI 秘书 启动中...")
    
    # 初始化数据库
    init_db()
    init_admin_user()
    log.info("✓ 数据库初始化完成")
    
    # 初始化日程管理器
    scheduler = ScheduleManager(use_memory=True)
    log.info("✓ 日程管理器初始化完成")
    
    # 初始化提醒服务
    reminder_service = ReminderService(
        scheduler=scheduler,
        check_interval=int(os.getenv("REMINDER_CHECK_INTERVAL", 60))
    )
    reminder_service.start()
    log.info("✓ 提醒服务启动完成")
    
    # 初始化示例数据（Demo 用）
    await init_demo_data()
    
    log.info("✅ 校园 AI 秘书 启动完成!")
    log.info(f"📡 API 地址：http://localhost:{os.getenv('APP_PORT', 8000)}")
    log.info(f"📚 API 文档：http://localhost:{os.getenv('APP_PORT', 8000)}/docs")
    log.info(f"🎨 管理后台：http://localhost:{os.getenv('APP_PORT', 8000)}/admin")
    
    yield
    
    # 关闭时清理
    log.info("👋 校园 AI 秘书 关闭中...")
    if reminder_service:
        reminder_service.stop()
    log.info("✅ 服务已关闭")


async def init_demo_data():
    """初始化示例数据（Demo 用）"""
    from .models.schedule import ScheduleCreate
    
    demo_schedules = [
        {
            "event_name": "高等数学期末考试",
            "start_time": "2024-06-15 09:00",
            "end_time": "2024-06-15 11:00",
            "location": "教学楼 A302",
            "priority": "high",
            "description": "请携带学生证和 2B 铅笔"
        },
        {
            "event_name": "计算机实验报告提交",
            "start_time": "2024-05-20 23:59",
            "priority": "high",
            "description": "第 5 次实验报告"
        },
        {
            "event_name": "社团招新宣讲",
            "start_time": "明天 19:00",
            "location": "学生活动中心 201",
            "priority": "medium"
        }
    ]
    
    for data in demo_schedules:
        try:
            schedule_create = ScheduleCreate(**data)
            scheduler.create_schedule("demo_user", schedule_create)
            log.info(f"添加示例日程：{data['event_name']}")
        except Exception as e:
            log.warning(f"添加示例日程失败：{e}")
    
    # 添加示例知识库
    from .core.rag import RAGEngine
    rag = RAGEngine(use_memory=True)
    
    demo_kb = [
        {
            "content": "图书馆开放时间：周一至周五 8:00-22:00，周六日 9:00-21:00。期末期间延长至 24 小时开放。",
            "metadata": {"source_type": "校园设施", "category": "图书馆"}
        },
        {
            "content": "教务处联系方式：电话 010-12345678，邮箱 jwc@university.edu.cn，办公时间工作日 9:00-17:00。",
            "metadata": {"source_type": "校园设施", "category": "教务处"}
        },
        {
            "content": "校医院位于校园北区，24 小时急诊服务。普通门诊时间：周一至周五 8:00-17:00。",
            "metadata": {"source_type": "校园设施", "category": "医院"}
        }
    ]
    
    for doc in demo_kb:
        rag.add_document(doc["content"], doc["metadata"])
    
    log.info(f"添加 {len(demo_kb)} 条示例知识库")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="校园 AI 秘书",
        description="基于 AI 的校园日程管理和智能问答服务",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Demo 环境，生产环境需要限制
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(v1_router)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/api")
    
    # 静态文件（管理后台）
    from fastapi.staticfiles import StaticFiles
    admin_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "admin")
    if os.path.exists(admin_path):
        app.mount("/admin", StaticFiles(directory=admin_path, html=True), name="admin")
        log.info(f"✅ 管理后台静态文件挂载成功: {admin_path}")
    else:
        log.warning(f"⚠️ 管理后台目录不存在: {admin_path}")
    
    # 健康检查
    @app.get("/health", tags=["health"])
    async def health_check():
        return {
            "status": "healthy",
            "scheduler": "initialized" if scheduler else "not_initialized",
            "reminder": "running" if reminder_service and reminder_service.running else "stopped"
        }
    
    # 根路径
    @app.get("/", tags=["root"])
    async def root():
        return {
            "name": "校园 AI 秘书",
            "version": "1.0.0",
            "docs": "/docs",
            "admin": "/admin",
            "health": "/health"
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )
